#!/usr/bin/env python3
"""
抖音视频采集与音频转写技能 v3

场景一：抖音视频转写（video_id 支持纯数字/完整链接/v.douyin.com 短链接）
  python scripts/douyin_fetch.py filter [--min-digg N] [--min-comment N] [--min-share N] [--keyword 关键字] [--audio-url URL]
  python scripts/douyin_fetch.py detail <video_id|链接> [--keyword 关键字]   # 默认方案：Playwright 拦截详情 API → 自动完成下载+转写+保存
  python scripts/douyin_fetch.py process <detail.json> [--keyword 关键字]     # 处理已保存的详情 JSON（detail 命令/Chrome MCP 拦截）

场景二：语音文件/音频 URL 转写（FunASR 平台 API）
  python scripts/douyin_fetch.py transcribe --audio <音频URL或平台fileId> [--subtitle] [--language zh] [--name 任务名] [--output-dir DIR]

文案提取策略：API 字幕优先，FunASR API 转写兜底（需公网音频 URL 或平台文件 ID）。

产物结构:
  output_dir/关键字/
    ├── yyyy-MM-dd 关键字.mp4
    ├── yyyy-MM-dd 关键字.txt
    └── yyyy-MM-dd 关键字.srt/.vtt   (FunASR 字幕任务时生成)
"""

import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

# ============================================================
# 配置模块
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
# 技能包根目录（脚本位于 scripts/ 子目录，配置在根目录）
SKILL_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = SKILL_ROOT / "config.json"

DEFAULT_CONFIG = {
    "output_dir": "",
    "ffmpeg_path": "",
    "api": {
        "base_url": "https://api.aipdd.work",
        "api_key": "",
    },
    "funasr": {
        "task_type": "aipdd_funasr_transcribe",
        "subtitle_task_type": "aipdd_funasr_subtitle",
        "language": "auto",
        "output_formats": ["json"],
        "subtitle_output_formats": ["json", "srt", "vtt"],
        "enable_emotion_labels": True,
        "enable_speaker_diarization": True,
        "max_duration_seconds": 3600,
        "poll_timeout": 1800,
        "save_subtitle_files": True,
    },
    "filter": {
        "rules": {
            "min_digg": 20000,
            "min_comment": 5000,
            "min_share": 5000,
            "logic": "digg AND (comment OR share)",
        },
        "process_count": 1,
        "candidates": [],
    },
    "browser": {
        "wait_timeout": 10,
        "api_pattern": "aweme/v1/web/aweme/detail/",
    },
    "download": {
        "timeout": 90,
        "chunk_size": 65536,
    },
    "subtitle": {
        "method": "api_first",
        "max_length": 0,
    },
}


def load_config() -> dict:
    """加载配置文件，缺失字段用默认值补全"""
    config = json.loads(json.dumps(DEFAULT_CONFIG))  # 深拷贝
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        _deep_merge(config, user_config)
    return config


def _deep_merge(base: dict, override: dict):
    """递归合并字典，override 的值覆盖 base"""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def get_output_dir(config: dict, keyword: str = "") -> str:
    """获取输出目录，按搜索关键字分组；keyword 为空时使用日期目录名"""
    output_base = config.get("output_dir", "").strip()
    if not output_base:
        output_base = os.path.join(os.path.expanduser("~"), "抖音下载")

    if keyword:
        group_dir = os.path.join(output_base, sanitize_filename(keyword))
    else:
        group_dir = os.path.join(output_base, date.today().strftime("%Y-%m-%d"))

    os.makedirs(group_dir, exist_ok=True)
    return group_dir


def get_video_filename(keyword: str, video_info: dict) -> str:
    """生成视频和文案文件名前缀：yyyy-MM-dd 关键字"""
    create_time = video_info.get("create_time", 0)
    if create_time:
        if create_time > 1e12:
            create_time = create_time // 1000
        from datetime import datetime
        date_str = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d")
    else:
        date_str = date.today().strftime("%Y-%m-%d")
    return f"{date_str} {keyword}"


def get_ffmpeg_path(config: dict) -> str:
    """获取 ffmpeg 可执行路径"""
    path = config.get("ffmpeg_path", "").strip()
    if path:
        return path
    for cmd in ["ffmpeg", "ffmpeg.exe"]:
        if shutil.which(cmd):
            return cmd
    return "ffmpeg"


# ============================================================
# 工具函数
# ============================================================


def extract_keyword(desc: str) -> str:
    """从标题提取关键字作为文件名前缀：去#标签，去emoji，取前12字"""
    text = re.sub(r"#\S+", "", desc).strip()
    text = re.sub(r"[\U00010000-\U0010ffff]", "", text)
    keyword = text[:12].strip()
    if keyword and keyword[-1] in "的了是在和与":
        keyword = keyword[:-1]
    return keyword or "视频"


def sanitize_filename(name: str) -> str:
    """清理文件名，移除不合法字符"""
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def format_stats(stats: dict) -> str:
    """格式化互动数据"""
    return (
        f"👍{stats.get('digg_count', 0):,} "
        f"💬{stats.get('comment_count', 0):,} "
        f"⭐{stats.get('collect_count', 0):,} "
        f"🔗{stats.get('share_count', 0):,}"
    )


async def resolve_video_id(input_str: str) -> str:
    """
    从用户输入解析 video_id，支持：
    - 纯数字 ID（如 7659806220995317046）
    - 完整链接（douyin.com/video/xxx 或 iesdouyin.com/share/video/xxx）
    - 抖音短链接（v.douyin.com/xxx，自动请求解析重定向）
    解析失败返回空字符串。
    """
    import httpx

    text = input_str.strip()
    if text.isdigit():
        return text

    # 从混合文本（可能含中文描述）中提取 URL
    url_match = re.search(r"https?://[^\s]+", text)
    if url_match:
        text = url_match.group(0).rstrip(".,;!?）)】]》")

    m = re.search(r"/(?:share/)?video/(\d+)", text)
    if m:
        return m.group(1)

    if "v.douyin.com" in text:
        url = text if text.startswith("http") else f"https://{text}"
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                resp = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                })
                final_url = str(resp.url)
            m2 = re.search(r"/(?:share/)?video/(\d+)", final_url)
            if m2:
                print(f"  ✅ 短链接解析成功: video_id={m2.group(1)}")
                return m2.group(1)
            print(f"  ⚠️ 短链接解析后未找到 video_id: {final_url[:100]}")
        except Exception as e:
            print(f"  ⚠️ 短链接解析失败: {e}")
    else:
        print(f"  ⚠️ 无法识别的输入: {input_str[:50]}")
    return ""


def check_dependencies() -> bool:
    """检查运行时依赖（httpx），缺失时打印安装指引"""
    try:
        import httpx  # noqa: F401
        return True
    except ImportError:
        print("❌ 缺少依赖 httpx，脚本无法运行")
        print("   推荐使用虚拟环境安装：")
        print("     python3 -m venv .venv")
        print(f"     .venv/bin/pip install -r {SKILL_ROOT / 'requirements.txt'}")
        print("     .venv/bin/python scripts/douyin_fetch.py <命令>")
        print("   若系统 Python 未受 PEP 668 保护，也可直接：pip3 install httpx")
        return False


def check_ffmpeg() -> bool:
    """检查 ffmpeg（抖音场景提取音频需要），缺失时提示安装；不阻断运行"""
    if shutil.which("ffmpeg") or shutil.which("ffmpeg.exe"):
        return True
    print("⚠️ 未检测到 ffmpeg（抖音视频提取音频/无原声兜底时需要）")
    print("   安装：brew install ffmpeg（macOS），或从 ffmpeg.org 下载 Windows 版")
    print("   也可在 config.json 的 ffmpeg_path 中指定可执行文件路径")
    return False


def ssr_guide(vid: str) -> None:
    """SSR 页面解析已被抖音反爬拦截，引导使用默认方案（detail 命令）"""
    print("⚠️ SSR 页面解析已被抖音反爬拦截，本命令不再支持该方案")
    print("   请改用默认方案 Playwright 自动拦截详情 API（无需 Chrome MCP）：")
    print(f"   python scripts/douyin_fetch.py detail {vid} [--keyword 搜索关键字]")
    print("   若 Playwright 不可用，用 Chrome MCP 拦截 aweme/v1/web/aweme/detail/ 后执行：")
    print("   python scripts/douyin_fetch.py process detail.json")


# ============================================================
# 浏览器模块 (Chrome MCP 交互)
# ============================================================

# 本脚本设计为被 AI 通过 Chrome MCP 调用：
# AI 负责操作浏览器（打开页面、拦截API、获取数据），脚本负责本地处理。
# parse_aweme_api_response() 接收 AI 从 MCP 拿到的 API 响应数据并解析为结构化信息。


def parse_aweme_api_response(api_data: dict) -> dict:
    """
    解析抖音 aweme/v1/web/aweme/detail/ API 的响应数据。
    参数 api_data 是从 Chrome DevTools 网络请求中拦截到的 JSON 响应体。
    """
    aweme = (
        api_data.get("aweme_detail")
        or (api_data.get("aweme_list", [{}])[0] if "aweme_list" in api_data else None)
        or (api_data.get("item_list", [{}])[0] if "item_list" in api_data else None)
        or {}
    )

    stats = aweme.get("statistics", {})
    video_info = aweme.get("video", {})
    play_addr = video_info.get("play_addr", {}) or video_info.get("download_addr", {})
    urls = play_addr.get("url_list", []) or video_info.get("url_list", [])

    subtitle_infos = aweme.get("subtitle_infos", [])
    if not subtitle_infos:
        subtitle_infos = video_info.get("subtitle", {}).get("subtitleInfos", [])

    # 原声音频直链：music.title 含“原声”时（如“@作者创作的原声”），
    # play_url 是 douyinstatic.com 的无防盗链 mp3，可直接提交 FunASR（视频直链有防盗链会被拒）
    music = aweme.get("music", {}) or {}
    music_audio_url = ""
    if "原声" in str(music.get("title", "") or ""):
        music_urls = (music.get("play_url", {}) or {}).get("url_list", [])
        if music_urls:
            music_audio_url = music_urls[0]

    best_url = _find_best_video_url(urls)

    return {
        "desc": aweme.get("desc", ""),
        "author": aweme.get("author", {}).get("nickname", ""),
        "stats": {
            "digg_count": stats.get("digg_count", 0),
            "comment_count": stats.get("comment_count", 0),
            "collect_count": stats.get("collect_count", 0),
            "share_count": stats.get("share_count", 0),
        },
        "duration": video_info.get("duration", 0) // 1000,
        "video_url": best_url,
        "all_video_urls": urls,
        "subtitle_infos": subtitle_infos,
        "music_audio_url": music_audio_url,
        "aweme_id": aweme.get("aweme_id", ""),
        "author_id": aweme.get("author", {}).get("uid", ""),
        "create_time": aweme.get("create_time", 0),
    }


def _find_best_video_url(urls: list) -> str:
    """找到最佳视频URL（优先选含音频的混合流）"""
    if not urls:
        return ""
    priority_keywords = ["ve", "audio", "playwm", "play_addr", "douyinvod"]
    for kw in priority_keywords:
        for u in urls:
            if kw in u.lower():
                return u
    return urls[0]


async def get_video_info_via_script(video_id: str, config: dict) -> dict:
    """
    备用方案：当没有 MCP 环境时，用 Python 脚本直接获取视频信息（需 httpx）。
    返回与 parse_aweme_api_response 相同格式的字典。
    """
    import httpx

    url = f"https://www.douyin.com/video/{video_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            html = resp.text

        match = re.search(r'<script id="RENDER_DATA"[^>]*>([^<]+)</script>', html)
        if match:
            import urllib.parse
            raw_data = urllib.parse.unquote(match.group(1))
            ssr_data = json.loads(raw_data)

            for key, value in ssr_data.items():
                if isinstance(value, dict):
                    for item in [value] + list(value.values()):
                        if isinstance(item, dict) and "aweme_detail" in item:
                            return parse_aweme_api_response(item)
                        if isinstance(item, dict) and "awemeId" in item:
                            stats = item.get("statistics", {})
                            video_info = item.get("video", {})
                            play_addr = video_info.get("playAddr", {})
                            urls = play_addr.get("urlList", []) if isinstance(play_addr, dict) else []
                            return {
                                "desc": item.get("desc", ""),
                                "author": item.get("author", {}).get("nickname", ""),
                                "stats": {
                                    "digg_count": stats.get("diggCount", 0),
                                    "comment_count": stats.get("commentCount", 0),
                                    "collect_count": stats.get("collectCount", 0),
                                    "share_count": stats.get("shareCount", 0),
                                },
                                "duration": (video_info.get("duration", 0) or 0) // 1000,
                                "video_url": _find_best_video_url(urls),
                                "all_video_urls": urls,
                                "subtitle_infos": item.get("subtitleInfos", []),
                                "aweme_id": item.get("awemeId", ""),
                                "author_id": item.get("author", {}).get("uid", ""),
                                "create_time": item.get("createTime", 0),
                            }

        print("⚠️ 未能从页面提取到视频数据（SSR 数据解析失败）")
        print("   请改用 Chrome MCP 兜底：打开 https://www.douyin.com/video/<video_id> 后，")
        print("   拦截 aweme/v1/web/aweme/detail/ 网络请求，将响应体交给 parse_aweme_api_response() 解析")
        return {}

    except Exception as e:
        print(f"❌ 获取视频信息失败: {e}")
        return {}


# ============================================================
# 下载模块
# ============================================================


async def download_video(video_url: str, out_file: str, config: dict) -> bool:
    """下载视频文件到指定路径"""
    import httpx

    timeout = config.get("download", {}).get("timeout", 90)
    chunk_size = config.get("download", {}).get("chunk_size", 65536)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(video_url, headers=headers, follow_redirects=True)
            total = int(resp.headers.get("content-length", 0))

            downloaded = 0
            with open(out_file, "wb") as f:
                async for chunk in resp.aiter_bytes(chunk_size=chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = downloaded * 100 // total
                        mb = downloaded / 1024 / 1024
                        print(f"\r  下载: {pct}% ({mb:.1f}MB)", end="", flush=True)
            print()

        size = os.path.getsize(out_file)
        print(f"  下载完成: {size / 1024 / 1024:.1f}MB → {out_file}")
        return True

    except Exception as e:
        print(f"  ❌ 下载失败: {e}")
        return False


# ============================================================
# FunASR API 模块
# ============================================================

DEFAULT_BASE_URL = "https://api.aipdd.work"


def get_api_headers(config: dict) -> dict:
    """获取 FunASR 接口鉴权头：环境变量 AIPDD_API_KEY 优先，其次 config.api.api_key"""
    api_key = os.environ.get("AIPDD_API_KEY", "").strip()
    if not api_key:
        api_key = str(config.get("api", {}).get("api_key", "")).strip()
    if not api_key:
        raise RuntimeError(
            "缺少 FunASR API Key：请设置环境变量 AIPDD_API_KEY，或在 config.json 的 api.api_key 中填写（sk-xxxx），获取指引见 SKILL.md「前置条件」。\n"
            "注意：本技能转写引擎唯一（FunASR 平台 API），不支持本地 Whisper 等替代转写方案，配置 Key 后重跑原命令即可"
        )
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def check_api_key(config: dict) -> bool:
    """开工前强制检查 FunASR API Key（转写唯一前提）：环境变量优先，其次 config.json；未配置返回 False"""
    api_key = os.environ.get("AIPDD_API_KEY", "").strip()
    if not api_key:
        api_key = str(config.get("api", {}).get("api_key", "")).strip()
    if api_key:
        return True
    print("❌ 未配置 FunASR API Key（转写唯一前提），请先配置后再运行")
    print("   请注册www.aipdd.work，并进入【全局设置-API Key 管理】中进行生成APIkey，即可获得")
    print("   配置方式：环境变量 AIPDD_API_KEY=sk-xxxx，或 config.json 的 api.api_key（环境变量优先）")
    print("   注意：本技能转写引擎唯一（FunASR 平台 API），不支持本地 Whisper 等替代转写方案")
    return False


def get_base_url(config: dict) -> str:
    """获取 FunASR 平台 Base URL"""
    return str(config.get("api", {}).get("base_url", "")).strip().rstrip("/") or DEFAULT_BASE_URL


async def _api_request(config: dict, method: str, path: str, **kwargs) -> dict:
    """发起 FunASR 平台 API 请求，校验统一响应结构 {code, message, data}，返回 data"""
    import httpx

    url = f"{get_base_url(config)}{path}"
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            resp = await client.request(method, url, headers=get_api_headers(config), **kwargs)
    except httpx.HTTPError as e:
        raise RuntimeError(f"请求 FunASR API 失败: {e}")

    if resp.status_code == 401:
        raise RuntimeError("FunASR 接口鉴权失败（401）：请检查 API Key 是否正确、账户是否有余额")
    if resp.status_code >= 400:
        raise RuntimeError(f"FunASR 接口错误（{resp.status_code}）: {resp.text[:300]}")

    try:
        data = resp.json()
    except Exception:
        raise RuntimeError(f"FunASR 接口响应不是合法 JSON: {resp.text[:300]}")

    if data.get("code") != 0:
        raise RuntimeError(f"FunASR 接口返回错误: {data.get('message', data)}")
    return data.get("data", {})


async def create_funasr_task(config: dict, audio: str, task_type: str = None, language: str = None,
                             output_formats: list = None, enable_emotion: bool = None,
                             enable_speaker: bool = None, task_name: str = "") -> dict:
    """
    创建 FunASR 转写任务（POST /shared-tasks/tasks）。
    audio 支持公网音频 URL 或平台文件 ID。
    返回任务详情 data（含 id/pollAfterMs/costAwcoin/_inputMedia 等）。
    """
    funasr = config.get("funasr", {})
    payload = {
        "requestId": f"funasr-{time.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}",
        "taskName": task_name or "音频转写",
        "taskTypeCode": task_type or funasr.get("task_type", "aipdd_funasr_transcribe"),
        "input": {
            "audio": audio,
            "language": language or funasr.get("language", "auto"),
            "outputFormats": output_formats or funasr.get("output_formats", ["json"]),
            "enableEmotionLabels": enable_emotion if enable_emotion is not None
            else funasr.get("enable_emotion_labels", True),
            "enableSpeakerDiarization": enable_speaker if enable_speaker is not None
            else funasr.get("enable_speaker_diarization", True),
            "maxDurationSeconds": funasr.get("max_duration_seconds", 3600),
        },
    }
    return await _api_request(config, "POST", "/shared-tasks/tasks", json=payload)


async def query_funasr_task(config: dict, task_id: str) -> dict:
    """查询任务状态（GET /shared-tasks/tasks/{taskId}）"""
    return await _api_request(config, "GET", f"/shared-tasks/tasks/{task_id}")


async def get_funasr_result(config: dict, task_id: str) -> dict:
    """获取任务结果（GET /shared-tasks/tasks/{taskId}/result）"""
    return await _api_request(config, "GET", f"/shared-tasks/tasks/{task_id}/result")


async def wait_funasr_result(config: dict, task_id: str, poll_after_ms: int = None,
                             timeout: int = None) -> dict:
    """
    轮询任务直到 resultReady=true，返回结果 data。
    进入 FAILED/CANCELED/EXPIRED 终态或超时则抛错。
    """
    timeout = timeout or config.get("funasr", {}).get("poll_timeout", 1800)
    poll_after_ms = poll_after_ms or 5000
    deadline = time.time() + timeout

    while time.time() < deadline:
        task = await query_funasr_task(config, task_id)
        status = task.get("status", "")
        if task.get("resultReady"):
            print(f"  ✅ 任务完成 (status={status}, stage={task.get('stage', '')})")
            return await get_funasr_result(config, task_id)
        if status in ("FAILED", "CANCELED", "EXPIRED"):
            raise RuntimeError(f"任务进入终态 {status}: stage={task.get('stage', '')}")
        print(f"  ⏳ 状态: {status} ({task.get('progress', 0)}%)，"
              f"{poll_after_ms / 1000:.0f}s 后重试...")
        await asyncio.sleep(poll_after_ms / 1000)

    raise RuntimeError(f"轮询超时（{timeout}秒），任务 {task_id} 仍在执行")


async def download_subtitle_files(result: dict, output_dir: str, base_name: str = "transcript") -> dict:
    """从结果 downloadRefs/objectRefs 下载 srt/vtt 字幕文件，返回 {format: 本地路径}"""
    import httpx

    saved = {}
    refs = result.get("downloadRefs") or result.get("objectRefs") or []
    for ref in refs:
        fmt = (ref.get("format") or "").lower()
        if fmt not in ("srt", "vtt"):
            continue
        url = ref.get("downloadUrl") or ref.get("url")
        if not url:
            continue
        out_file = os.path.join(output_dir, f"{base_name}.{fmt}")
        try:
            async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()
            with open(out_file, "wb") as f:
                f.write(resp.content)
            saved[fmt] = out_file
            print(f"  📄 字幕已保存: {out_file}")
        except Exception as e:
            print(f"  ⚠️ 下载 {fmt} 字幕失败: {e}")
    return saved


async def run_funasr_transcribe(config: dict, audio: str, task_type: str = None, language: str = None,
                                output_formats: list = None, enable_emotion: bool = None,
                                enable_speaker: bool = None, task_name: str = "",
                                subtitle_dir: str = None, subtitle_base: str = "transcript") -> dict:
    """
    完整 FunASR 转写流程：创建任务 → 轮询 → 获取结果。
    可指定 subtitle_dir 自动下载字幕文件。
    返回结果 data（含 output/objectRefs/downloadRefs）。
    转写按音频秒数计费，计费与数据去向见 SKILL.md「数据流向与安全说明」。
    """
    task = await create_funasr_task(config, audio, task_type, language, output_formats,
                                    enable_emotion, enable_speaker, task_name)
    task_id = task.get("id") or task.get("taskId")
    print(f"  ✅ 任务已创建: {task_id}")
    media = task.get("input", {}).get("_inputMedia", {}).get("audio", {})
    if media.get("durationSeconds"):
        print(f"     音频时长: {media['durationSeconds']}秒, 冻结费用: {task.get('costAwcoin', 0)} AWcoin")
    result = await wait_funasr_result(config, task_id, task.get("pollAfterMs"))
    if subtitle_dir and config.get("funasr", {}).get("save_subtitle_files", True):
        await download_subtitle_files(result, subtitle_dir, subtitle_base)
    return result


def extract_audio_from_video(video_path: str, config: dict, output_path: str = None) -> str:
    """用 FFmpeg 从视频提取音频（wav 16k 单声道），返回输出路径；失败返回空串"""
    if not output_path:
        output_path = os.path.splitext(video_path)[0] + ".wav"
    ffmpeg_path = get_ffmpeg_path(config)
    cmd = [ffmpeg_path, "-i", video_path, "-vn", "-acodec", "pcm_s16le",
           "-ar", "16000", "-ac", "1", "-y", output_path]
    try:
        print(f"  🔊 提取音频中... {output_path}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            return output_path
        print(f"  ⚠️ FFmpeg 提取音频失败: {result.stderr[:200]}")
    except Exception as e:
        print(f"  ⚠️ 提取音频失败: {e}")
    return ""


# ============================================================
# 字幕/文案提取模块（API 字幕优先 + FunASR 兜底）
# ============================================================


async def extract_subtitle_from_api(subtitle_infos: list) -> str:
    """
    方案一：从抖音 API 返回的 subtitle_infos 中提取字幕。

    subtitle_infos 格式示例:
    [
      {
        "LanguageCodeName": "zh",
        "Url": "https://...",
        "Format": "vtt",
        "SourceType": 1
      }
    ]
    返回字幕纯文本，失败返回空字符串。
    """
    if not subtitle_infos:
        return ""

    import httpx

    zh_subtitle = None
    any_subtitle = None

    for info in subtitle_infos:
        url = info.get("Url", "") or info.get("url", "")
        lang = info.get("LanguageCodeName", "") or info.get("languageCodeName", "")
        fmt = info.get("Format", "") or info.get("format", "vtt")

        if not url:
            continue

        if "zh" in lang.lower() or "cn" in lang.lower() or "chinese" in lang.lower():
            zh_subtitle = url
            break
        any_subtitle = url

    subtitle_url = zh_subtitle or any_subtitle
    if not subtitle_url:
        return ""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(subtitle_url)
            content = resp.text
        return _parse_subtitle_content(content)

    except Exception as e:
        print(f"  ⚠️ API字幕下载失败: {e}")
        return ""


def _parse_subtitle_content(content: str) -> str:
    """解析 VTT 或 SRT 字幕文件，返回纯文本"""
    lines = content.strip().split("\n")
    text_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("WEBVTT") or line.startswith("NOTE"):
            continue
        if re.match(r"^\d{2}:\d{2}:\d{2}[\.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[\.,]\d{3}", line):
            continue
        if re.match(r"^\d+$", line):
            continue
        if line.startswith("<") and not re.search(r"[\u4e00-\u9fff]", line):
            continue

        clean = re.sub(r"<[^>]+>", "", line).strip()
        if clean and len(clean) > 1:
            text_lines.append(clean)

    return "\n".join(text_lines)


async def extract_transcript(video_info: dict, video_path: str = None, config: dict = None,
                             audio_url: str = "") -> tuple:
    """
    双层文案提取：
    1. API 字幕优先（抖音视频自带字幕时直接解析）
    2. FunASR API 转写兜底（需要公网音频 URL 或平台文件 ID）

    返回 (text, source, funasr_result)；失败时 text 为空串。
    """
    if config is None:
        config = load_config()

    method = config.get("subtitle", {}).get("method", "api_first")
    max_length = config.get("subtitle", {}).get("max_length", 0)

    # 第一层：API 字幕
    if method == "api_first":
        subtitle_infos = video_info.get("subtitle_infos", [])
        if subtitle_infos:
            print("  📝 尝试 API 字幕提取...")
            text = await extract_subtitle_from_api(subtitle_infos)
            if text and len(text) > 10:
                print(f"  ✅ API 字幕提取成功 ({len(text)}字)")
                return text[:max_length] if max_length > 0 else text, "API字幕", {}
            print("  ⚠️ API 字幕内容为空或太短，尝试 FunASR")

    # 第二层：FunASR 兜底（原声音频直链优先，其次用户提供的公网音频 URL）
    # 实测：视频直链（douyinvod）有防盗链会被平台拒，music.play_url 原声 mp3 可直接转写
    funasr_audio = audio_url or video_info.get("music_audio_url", "")
    if funasr_audio:
        source_desc = "原声音频直链" if not audio_url else "用户提供音频URL"
        print(f"  🎙️ 提交 FunASR 语音转写（{source_desc}）: {funasr_audio[:60]}...")
        try:
            result = await run_funasr_transcribe(
                config, funasr_audio,
                task_name=f"抖音视频转写 {video_info.get('aweme_id', '') or video_info.get('desc', '')[:20]}",
            )
            text = (result.get("output") or {}).get("text", "").strip()
            if text:
                print(f"  ✅ FunASR 转写成功 ({len(text)}字)")
                return text[:max_length] if max_length > 0 else text, "FunASR API", result
            print("  ❌ FunASR 返回空文本")
        except Exception as e:
            print(f"  ❌ FunASR 转写失败: {e}")
    elif video_path and os.path.exists(video_path):
        print("  ⚠️ 无字幕且无原声音频直链（视频可能使用了 BGM），无法自动调用 FunASR")
        audio_path = extract_audio_from_video(video_path, config)
        if audio_path:
            print(f"     📁 本地音频已提取: {audio_path}")
            print("     请上传到公网（如 OSS）后重试：")
            print(f"     python scripts/douyin_fetch.py transcript {video_info.get('aweme_id', '')} --audio-url <公网URL或fileId>")
    elif not video_path:
        print("  ⚠️ 无视频文件且未提供音频 URL，无法执行 FunASR")

    return "", "FunASR API", {}


# ============================================================
# 文案保存模块
# ============================================================


def save_transcript_to_file(
    filepath: str,
    vid: str,
    desc: str,
    author: str,
    stats: dict,
    transcript_text: str,
    source: str = "unknown",
) -> str:
    """保存文案到指定文件路径，返回文件路径（语音转写场景可传空元信息）"""
    lines = []
    if vid:
        lines.append(f"视频ID: {vid}")
    if desc:
        lines.append(f"标题: {desc}")
    if author:
        lines.append(f"作者: {author}")
    if stats:
        lines.append(f"互动: {format_stats(stats)}")
    lines.append(f"文案来源: {source}")
    lines.append("=" * 50)
    lines.append("【口播文案】")
    lines.append("")
    lines.append(transcript_text)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath


# ============================================================
# 筛选模块
# ============================================================


def filter_candidates(config: dict) -> list:
    """根据筛选规则过滤候选视频列表"""
    rules = config.get("filter", {}).get("rules", {})
    min_digg = rules.get("min_digg", 0)
    min_comment = rules.get("min_comment", 0)
    min_share = rules.get("min_share", 0)

    candidates = config.get("filter", {}).get("candidates", [])

    if not candidates:
        print("⚠️ 配置文件中没有候选视频列表（filter.candidates）")
        print("   请在 config.json 中添加候选视频，或直接使用 download 模式指定 video_id")
        return []

    print("=" * 60)
    print(f"筛选规则：点赞≥{min_digg:,} AND (评论≥{min_comment:,} OR 分享≥{min_share:,})")
    print("=" * 60)

    passed = []
    for item in candidates:
        vid = item.get("video_id", item[0] if isinstance(item, (list, tuple)) else "")
        desc = item.get("desc", item[1] if isinstance(item, (list, tuple)) else "")
        author = item.get("author", item[2] if isinstance(item, (list, tuple)) else "")
        digg = item.get("digg_count", item[3] if isinstance(item, (list, tuple)) and len(item) > 3 else 0)
        comment = item.get("comment_count", item[4] if isinstance(item, (list, tuple)) and len(item) > 4 else 0)
        collect = item.get("collect_count", item[5] if isinstance(item, (list, tuple)) and len(item) > 5 else 0)
        share = item.get("share_count", item[6] if isinstance(item, (list, tuple)) and len(item) > 6 else 0)

        ok = digg >= min_digg and (comment >= min_comment or share >= min_share)
        status = "✅" if ok else ("⚠️" if digg >= min_digg else "❌")

        print(f"{status} [{vid}] {desc[:40]}")
        print(f"   作者: {author}  👍{digg:,}  💬{comment:,}  ⭐{collect:,}  🔗{share:,}")

        if ok:
            passed.append({"video_id": vid, "desc": desc, "author": author})

    return passed


# ============================================================
# 主流程
# ============================================================


async def process_video(vid: str, config: dict, output_dir: str = None, keyword: str = "",
                        audio_url: str = "") -> dict:
    """
    完整处理一个视频：获取信息 → 下载 → 提取文案（API字幕优先，FunASR兜底）→ 保存。

    audio_url：FunASR 兜底所需的公网音频 URL 或平台文件 ID（可选）。
    返回处理结果字典。
    """
    if keyword and output_dir is None:
        output_dir = get_output_dir(config, keyword=keyword)
    elif output_dir is None:
        output_dir = get_output_dir(config)

    print(f"\n{'='*60}")
    print(f"处理视频: {vid}")
    print(f"{'='*60}")

    print("📡 获取视频信息...")
    video_info = await get_video_info_via_script(vid, config)

    if not video_info or not video_info.get("desc"):
        print("❌ 无法获取视频信息")
        return {"success": False, "error": "无法获取视频信息"}

    desc = video_info["desc"]
    author = video_info["author"]
    stats = video_info["stats"]
    duration = video_info.get("duration", 0)
    video_url = video_info.get("video_url", "")

    if not keyword:
        keyword = extract_keyword(desc)

    file_prefix = get_video_filename(keyword, video_info)
    safe_prefix = sanitize_filename(file_prefix)

    print(f"  搜索关键字: {keyword}")
    print(f"  文件前缀: {safe_prefix}")
    print(f"  标题: {desc[:60]}")
    print(f"  作者: {author}")
    print(f"  时长: {duration}秒")
    print(f"  互动: {format_stats(stats)}")
    print(f"  字幕轨: {len(video_info.get('subtitle_infos', []))}个")

    result = {
        "success": True,
        "video_id": vid,
        "keyword": keyword,
        "desc": desc,
        "author": author,
        "stats": stats,
        "duration": duration,
    }

    # 下载视频
    mp4_file = None
    if video_url:
        mp4_file = os.path.join(output_dir, f"{safe_prefix}.mp4")

        if os.path.exists(mp4_file):
            print(f"  ⏭️  视频已存在，跳过下载: {mp4_file}")
        else:
            print("📥 下载视频...")
            ok = await download_video(video_url, mp4_file, config)
            if not ok:
                mp4_file = None
                print("  ⚠️ 视频下载失败，继续尝试提取文案")
    else:
        print("  ⚠️ 未获取到视频下载URL")

    # 提取文案（API字幕优先，FunASR兜底）
    print("\n📝 提取文案...")
    transcript, source, funasr_result = await extract_transcript(video_info, mp4_file, config, audio_url)

    if transcript:
        wenan_file = os.path.join(output_dir, f"{safe_prefix}.txt")
        save_transcript_to_file(wenan_file, vid, desc, author, stats, transcript, source)
        print(f"  ✅ 文案已保存: {wenan_file} ({len(transcript)}字)")
        result["transcript_file"] = wenan_file
        result["transcript_text"] = transcript
        result["transcript_source"] = source

        # FunASR 字幕任务生成的字幕文件同步保存
        if funasr_result:
            await download_subtitle_files(funasr_result, output_dir, safe_prefix)
    else:
        print("  ❌ 未能提取到文案")

    if mp4_file:
        result["video_file"] = mp4_file

    print(f"\n✅ 完成: {safe_prefix}")
    return result


# ============================================================
# 子命令入口
# ============================================================


def _parse_common_args(args: list, opts: dict) -> dict:
    """解析 --key value 形式的命令行参数，返回 {opt_name: value}；--flag 布尔参数直接查 args"""
    parsed = {}
    i = 0
    while i < len(args):
        if args[i] in opts and i + 1 < len(args):
            parsed[args[i]] = args[i + 1]
            i += 2
        else:
            i += 1
    return parsed


async def cmd_filter(config: dict, args: list):
    """筛选+下载模式"""
    if not args:
        print("⚠️ SSR 页面解析已被抖音反爬拦截，filter 模式不再可用")
        print("   请对候选视频逐个使用默认方案（Playwright 自动拦截）：")
        print("   python scripts/douyin_fetch.py detail <video_id> --keyword <搜索关键字>")
        return

    i = 0
    keyword = ""
    audio_url = ""
    while i < len(args):
        if args[i] == "--min-digg" and i + 1 < len(args):
            config["filter"]["rules"]["min_digg"] = int(args[i + 1])
            i += 2
        elif args[i] == "--min-comment" and i + 1 < len(args):
            config["filter"]["rules"]["min_comment"] = int(args[i + 1])
            i += 2
        elif args[i] == "--min-share" and i + 1 < len(args):
            config["filter"]["rules"]["min_share"] = int(args[i + 1])
            i += 2
        elif args[i] == "--keyword" and i + 1 < len(args):
            keyword = args[i + 1]
            i += 2
        elif args[i] == "--audio-url" and i + 1 < len(args):
            audio_url = args[i + 1]
            i += 2
        else:
            i += 1

    output_dir = get_output_dir(config, keyword=keyword) if keyword else get_output_dir(config)
    passed = filter_candidates(config)

    if not passed:
        print("\n无满足条件的候选视频")
        return

    process_count = config.get("filter", {}).get("process_count", 1)
    to_process = passed[:process_count]

    print(f"\n将处理 {len(to_process)} 个视频 → 输出目录: {output_dir}")
    results = []
    for item in to_process:
        result = await process_video(item["video_id"], config, output_dir=output_dir,
                                     keyword=keyword, audio_url=audio_url)
        results.append(result)

    return results


async def cmd_download(config: dict, args: list):
    """下载指定视频"""
    if not args:
        print("用法: python scripts/douyin_fetch.py download <video_id|抖音链接> [--keyword 关键字] [--audio-url URL]")
        return

    vid = await resolve_video_id(args[0])
    if not vid:
        print("❌ 无法解析视频 ID：请提供纯数字 video_id、完整链接或 v.douyin.com 短链接")
        return
    ssr_guide(vid)
    return
    keyword = ""
    audio_url = ""
    if "--keyword" in args:
        idx = args.index("--keyword")
        if idx + 1 < len(args):
            keyword = args[idx + 1]
    if "--audio-url" in args:
        idx = args.index("--audio-url")
        if idx + 1 < len(args):
            audio_url = args[idx + 1]

    output_dir = get_output_dir(config, keyword=keyword) if keyword else get_output_dir(config)
    result = await process_video(vid, config, output_dir=output_dir, keyword=keyword, audio_url=audio_url)
    return result


async def cmd_transcript(config: dict, args: list):
    """仅提取文案（API字幕优先，FunASR兜底）"""
    if not args:
        print("用法: python scripts/douyin_fetch.py transcript <video_id|抖音链接> [--file /path/to/video.mp4] [--audio-url URL]")
        return

    vid = await resolve_video_id(args[0])
    if not vid:
        print("❌ 无法解析视频 ID：请提供纯数字 video_id、完整链接或 v.douyin.com 短链接")
        return
    ssr_guide(vid)
    return
    video_path = None
    audio_url = ""

    if "--file" in args:
        idx = args.index("--file")
        if idx + 1 < len(args):
            video_path = args[idx + 1]
    if "--audio-url" in args:
        idx = args.index("--audio-url")
        if idx + 1 < len(args):
            audio_url = args[idx + 1]

    print(f"提取文案: {vid}")

    video_info = await get_video_info_via_script(vid, config)
    if not video_info:
        print("❌ 无法获取视频信息")
        return

    transcript, source, funasr_result = await extract_transcript(video_info, video_path, config, audio_url)
    if transcript:
        print(f"\n{'='*60}")
        print(f"📋 文案内容（{len(transcript)}字，来源: {source}）：")
        print(f"{'='*60}")
        print(transcript)
        return {"transcript": transcript, "source": source}
    else:
        print("❌ 未能提取到文案")
        return None


async def cmd_info(config: dict, args: list):
    """仅查看视频信息，不下载"""
    if not args:
        print("用法: python scripts/douyin_fetch.py info <video_id|抖音链接>")
        return

    vid = await resolve_video_id(args[0])
    if not vid:
        print("❌ 无法解析视频 ID：请提供纯数字 video_id、完整链接或 v.douyin.com 短链接")
        return
    ssr_guide(vid)
    return
    print(f"查询视频信息: {vid}\n")

    video_info = await get_video_info_via_script(vid, config)
    if not video_info:
        print("❌ 无法获取视频信息")
        return

    keyword = extract_keyword(video_info.get("desc", ""))
    print(f"视频ID: {vid}")
    print(f"关键字: {keyword}")
    print(f"标题: {video_info.get('desc', '')[:80]}")
    print(f"作者: {video_info.get('author', '')}")
    print(f"时长: {video_info.get('duration', 0)}秒")
    print(f"互动: {format_stats(video_info.get('stats', {}))}")
    print(f"视频URL: {'有' if video_info.get('video_url') else '无'}")
    print(f"字幕轨: {len(video_info.get('subtitle_infos', []))}个")

    if video_info.get("subtitle_infos"):
        for i, sub in enumerate(video_info["subtitle_infos"]):
            lang = sub.get("LanguageCodeName", sub.get("languageCodeName", "unknown"))
            url = sub.get("Url", sub.get("url", ""))
            print(f"  字幕[{i}]: 语言={lang}, URL={'有' if url else '无'}")

    return video_info


def _playwright_intercept(vid: str) -> list:
    """在线程中执行 Playwright 拦截详情 API（sync API 不能跑在 asyncio 循环里，用 to_thread 调用）"""
    from playwright.sync_api import sync_playwright

    captured = []
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, channel="chrome")
            print("   ✅ 已启动系统 Chrome")
        except Exception:
            browser = p.chromium.launch(headless=True)
            print("   ✅ 已启动 Playwright Chromium")
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )

        def on_response(resp):
            if "aweme/v1/web/aweme/detail/" in resp.url:
                try:
                    j = resp.json()
                    if isinstance(j, dict) and j.get("aweme_detail"):
                        captured.append(j)
                except Exception:
                    pass

        page.on("response", on_response)
        page.goto(f"https://www.douyin.com/video/{vid}", timeout=30000, wait_until="domcontentloaded")
        for _ in range(15):
            page.wait_for_timeout(2500)
            if captured:
                break
            # 未捕获时点击推荐视频触发 SPA 详情请求，再返回
            try:
                page.locator("a[href*='/video/']").first.click(timeout=3000)
                page.wait_for_timeout(2500)
                if captured:
                    break
                page.go_back()
                page.wait_for_timeout(2000)
            except Exception:
                pass
        browser.close()
    return captured


async def cmd_detail(config: dict, args: list):
    """
    默认方案：用 Playwright 打开视频页并拦截 aweme/v1/web/aweme/detail/ 详情 API（无需 Chrome MCP），
    拦截成功 → 保存 detail.json → 自动衔接 process 完成下载+转写+保存。
    用法: python scripts/douyin_fetch.py detail <video_id|链接> [--keyword 关键字] [--audio-url URL] [--output-dir DIR]
    """
    if not args:
        print("用法: python scripts/douyin_fetch.py detail <video_id|链接> [--keyword 关键字] [--audio-url URL] [--output-dir DIR]")
        return

    vid = await resolve_video_id(args[0])
    if not vid:
        print("❌ 无法解析视频 ID：请提供纯数字 video_id、完整链接或 v.douyin.com 短链接")
        return

    if not check_api_key(config):
        return

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 缺少 playwright，无法自动拦截详情 API")
        print("   安装：.venv/bin/pip install playwright")
        print("   （系统已装 Chrome 时无需下载 chromium，脚本自动使用 channel=chrome；否则执行 .venv/bin/playwright install chromium）")
        return

    detail_file = "detail.json"
    print(f"\n🌐 打开抖音视频页并拦截详情 API: {vid}")
    print("   （Playwright 默认方案，请耐心等待页面加载；可能需要几秒到几十秒）")
    captured = []
    try:
        captured = await asyncio.to_thread(_playwright_intercept, vid)
    except Exception as e:
        print(f"❌ Playwright 执行失败: {e}")
        print("   备选：用 Chrome MCP 拦截 aweme/v1/web/aweme/detail/ 响应体，保存为 detail.json 后执行 process 命令")
        return

    if not captured:
        print("❌ 未能拦截到详情 API（可能需要登录/验证）")
        print("   备选：用 Chrome MCP 拦截 aweme/v1/web/aweme/detail/ 响应体，保存为 detail.json 后执行 process 命令")
        return

    with open(detail_file, "w", encoding="utf-8") as f:
        json.dump(captured[0], f, ensure_ascii=False)
    print(f"   ✅ 已拦截详情 API 并保存: {os.path.abspath(detail_file)}")

    # 自动衔接 process 完成全流程
    process_args = [detail_file]
    for flag in ("--keyword", "--audio-url", "--output-dir"):
        if flag in args:
            idx = args.index(flag)
            if idx + 1 < len(args):
                process_args += [flag, args[idx + 1]]
    return await cmd_process(config, process_args)


async def cmd_process(config: dict, args: list):
    """
    处理详情 JSON（detail 命令/Chrome MCP 拦截的响应体）：
    解析 JSON → 下载视频 → 提取文案（API字幕优先，FunASR原声兑底）→ 保存
    用法: python scripts/douyin_fetch.py process <detail.json> [--keyword 关键字] [--audio-url URL] [--output-dir DIR]
    """
    if not args:
        print("用法: python scripts/douyin_fetch.py process <detail.json> [--keyword 关键字] [--audio-url URL] [--output-dir DIR]")
        print("      detail.json 为 detail 命令或 Chrome MCP 拦截 aweme/v1/web/aweme/detail/ 得到的响应体文件")
        return

    if not check_api_key(config):
        return

    json_path = args[0]
    if not os.path.exists(json_path):
        print(f"❌ JSON 文件不存在: {json_path}")
        return

    keyword = ""
    audio_url = ""
    output_dir = None
    i = 1
    while i < len(args):
        if args[i] == "--keyword" and i + 1 < len(args):
            keyword = args[i + 1]
            i += 2
        elif args[i] == "--audio-url" and i + 1 < len(args):
            audio_url = args[i + 1]
            i += 2
        elif args[i] == "--output-dir" and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        else:
            i += 1

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            api_data = json.load(f)
    except Exception as e:
        print(f"❌ JSON 解析失败: {e}")
        return

    video_info = parse_aweme_api_response(api_data)
    if not video_info or not video_info.get("desc"):
        print("❌ JSON 中未找到有效 aweme_detail 数据，请确认是 aweme/v1/web/aweme/detail/ 的响应体")
        return

    desc = video_info["desc"]
    author = video_info["author"]
    stats = video_info["stats"]
    video_url = video_info.get("video_url", "")

    if not keyword:
        keyword = extract_keyword(desc)
    if output_dir is None:
        output_dir = get_output_dir(config, keyword=keyword)

    print(f"\n{'='*60}")
    print(f"处理浏览器详情 JSON: {os.path.basename(json_path)}")
    print(f"{'='*60}")
    print(f"  标题: {desc[:60]}")
    print(f"  作者: {author}")
    print(f"  互动: {format_stats(stats)}")
    print(f"  字幕轨: {len(video_info.get('subtitle_infos') or [])}个")
    print(f"  原声音频: {'有' if video_info.get('music_audio_url') else '无'}")
    print(f"  视频URL: {'有' if video_url else '无'}")

    file_prefix = sanitize_filename(get_video_filename(keyword, video_info))
    result = {"success": True, "video_id": video_info.get("aweme_id", ""), "keyword": keyword,
              "desc": desc, "author": author, "stats": stats}

    # 下载视频
    mp4_file = None
    if video_url:
        mp4_file = os.path.join(output_dir, f"{file_prefix}.mp4")
        if os.path.exists(mp4_file):
            print(f"  ⏭️  视频已存在，跳过下载: {mp4_file}")
        else:
            print("📥 下载视频...")
            ok = await download_video(video_url, mp4_file, config)
            if not ok:
                mp4_file = None
                print("  ⚠️ 视频下载失败，继续尝试提取文案")
    else:
        print("  ⚠️ JSON 中无视频下载 URL")

    # 提取文案（API字幕优先，FunASR原声兑底）
    print("\n📝 提取文案...")
    transcript, source, funasr_result = await extract_transcript(video_info, mp4_file, config, audio_url)

    if transcript:
        wenan_file = os.path.join(output_dir, f"{file_prefix}.txt")
        save_transcript_to_file(wenan_file, result["video_id"], desc, author, stats, transcript, source)
        print(f"  ✅ 文案已保存: {wenan_file} ({len(transcript)}字)")
        result["transcript_file"] = wenan_file
        result["transcript_text"] = transcript
        result["transcript_source"] = source
        if funasr_result:
            await download_subtitle_files(funasr_result, output_dir, file_prefix)
    else:
        print("  ❌ 未能提取到文案")

    if mp4_file:
        result["video_file"] = mp4_file
    print(f"\n✅ 完成: {file_prefix}")
    return result


async def cmd_transcribe(config: dict, args: list):
    """语音文件/音频 URL 转写（FunASR 平台 API）"""
    if not args:
        print("用法: python scripts/douyin_fetch.py transcribe --audio <音频URL或平台fileId> "
              "[--subtitle] [--language zh] [--name 任务名] [--output-dir DIR] [--no-emotion] [--no-speaker]")
        return

    parsed = _parse_common_args(args, {"--audio", "--url", "--task-type", "--language", "--name", "--output-dir"})
    audio = parsed.get("--audio") or parsed.get("--url")
    if not audio:
        print("❌ 缺少 --audio 参数（公网音频 URL 或平台文件 ID）")
        return

    subtitle_mode = "--subtitle" in args
    enable_emotion = False if "--no-emotion" in args else None
    enable_speaker = False if "--no-speaker" in args else None

    funasr = config.get("funasr", {})
    task_type = parsed.get("--task-type") or (
        funasr.get("subtitle_task_type", "aipdd_funasr_subtitle") if subtitle_mode
        else funasr.get("task_type", "aipdd_funasr_transcribe")
    )
    output_formats = (
        funasr.get("subtitle_output_formats", ["json", "srt", "vtt"]) if subtitle_mode
        else funasr.get("output_formats", ["json"])
    )
    language = parsed.get("--language")
    name = parsed.get("--name", "音频转写")
    output_dir = parsed.get("--output-dir") or get_output_dir(config)

    print(f"\n{'='*60}")
    print(f"FunASR 音频转写: {audio}")
    print(f"任务类型: {task_type} | 语言: {language or 'auto'} | 字幕模式: {'是' if subtitle_mode else '否'}")
    print(f"输出目录: {output_dir}")
    print(f"{'='*60}")

    try:
        result = await run_funasr_transcribe(
            config, audio, task_type=task_type, language=language,
            output_formats=output_formats, enable_emotion=enable_emotion,
            enable_speaker=enable_speaker, task_name=name,
            subtitle_dir=output_dir if subtitle_mode else None,
            subtitle_base=sanitize_filename(f"{date.today().strftime('%Y-%m-%d')} {name}"),
        )
    except RuntimeError as e:
        print(f"❌ {e}")
        return None

    output = result.get("output", {})
    text = (output.get("text") or "").strip()
    if not text:
        print("❌ 未获取到转写文本")
        return None

    # 保存转写文本
    file_prefix = sanitize_filename(f"{date.today().strftime('%Y-%m-%d')} {name}")
    txt_file = os.path.join(output_dir, f"{file_prefix}.txt")
    save_transcript_to_file(txt_file, "", name, "", {}, text, f"FunASR API ({task_type})")
    print(f"  ✅ 转写文本已保存: {txt_file} ({len(text)}字)")

    # 展示转写结果
    segments = output.get("segments", [])
    speakers = output.get("speakers", [])
    duration = output.get("durationSeconds", 0)
    print(f"  时长: {duration}秒, 分段: {len(segments)}段, 说话人: {len(speakers)}人")
    print(f"\n{'='*60}")
    print(f"📋 转写内容（{len(text)}字）：")
    print(f"{'='*60}")
    print(text)

    return {"transcript": text, "source": f"FunASR API ({task_type})", "segments": segments}


def print_usage():
    print("""
抖音视频采集与音频转写技能 v3

场景一：抖音视频
  python scripts/douyin_fetch.py filter [--min-digg N] [--min-comment N] [--min-share N] [--keyword 关键字] [--audio-url URL]
      从配置文件的候选列表中筛选并下载高互动视频（SSR 已弃用，逐个视频请用 detail 命令）
      --audio-url 指定公网音频URL/平台fileId，供 FunASR 兜底转写使用

  python scripts/douyin_fetch.py detail <video_id|链接> [--keyword 关键字] [--audio-url URL] [--output-dir DIR]
      默认方案：Playwright 自动打开视频页并拦截 aweme/v1/web/aweme/detail/ 详情 API（无需 Chrome MCP），
      自动衔接 process 完成 解析 → 下载 → 提取文案（API字幕优先，FunASR原声兑底）→ 保存

  python scripts/douyin_fetch.py process <detail.json> [--keyword 关键字] [--audio-url URL] [--output-dir DIR]
      处理已保存的详情 JSON（detail 命令或 Chrome MCP 拦截的响应体）：解析 → 下载 → 提取文案 → 保存

  python scripts/douyin_fetch.py download/transcript/info <video_id|链接>
      SSR 页面解析已被抖音反爬拦截，这些命令已停用并引导改用 detail 命令

场景二：语音文件/音频 URL 转写
  python scripts/douyin_fetch.py transcribe --audio <音频URL或平台fileId> [--subtitle] [--language zh]
      [--name 任务名] [--output-dir DIR] [--no-emotion] [--no-speaker]
      FunASR 语音转写文字；--subtitle 生成 srt/vtt 字幕文件

输出结构:
  output_dir/关键字/
    ├── yyyy-MM-dd 关键字.mp4
    ├── yyyy-MM-dd 关键字.txt
    └── yyyy-MM-dd 关键字.srt/.vtt   (FunASR 字幕任务时生成)

鉴权: 环境变量 AIPDD_API_KEY 优先，其次 config.json 的 api.api_key
配置文件: config.json（技能包根目录）
""")


async def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    if not check_dependencies():
        return

    config = load_config()
    command = sys.argv[1].lower()
    args = sys.argv[2:]

    if command in ("download", "transcript", "filter", "process", "detail"):
        check_ffmpeg()

    commands = {
        "filter": cmd_filter,
        "download": cmd_download,
        "transcript": cmd_transcript,
        "info": cmd_info,
        "detail": cmd_detail,
        "process": cmd_process,
        "transcribe": cmd_transcribe,
    }

    if command in commands:
        await commands[command](config, args)
    else:
        print(f"未知命令: {command}")
        print_usage()


if __name__ == "__main__":
    asyncio.run(main())
