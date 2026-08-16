#!/usr/bin/env python3
"""
QQ邮箱 IMAP IDLE 实时监听脚本
- 使用 IMAP IDLE 扩展实时感知新邮件
- 新邮件到达时自动触发 read_emails.py 处理
- 支持 macOS 系统通知
- 支持断线自动重连
"""

import os
import sys
import time
import json
import signal
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger('foxmail-listener')

# ===== 配置 =====
IMAP_SERVER = os.environ.get("MAIL_IMAP_SERVER", "imap.qq.com")
IMAP_PORT = 993
EMAIL_ADDR = os.environ.get("MAIL_ADDR", "")
AUTH_CODE = os.environ.get("MAIL_AUTH_CODE", "")
FOLDER = "INBOX"

PROJECT_ROOT = os.environ.get(
    "PROJECT_ROOT",
    os.path.expanduser("~")
)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
READ_SCRIPT = os.path.join(SCRIPT_DIR, "read_emails.py")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "mails")
PID_FILE = os.path.join(PROJECT_ROOT, ".runtime", "mail_listener.pid")
LOG_FILE = os.path.join(PROJECT_ROOT, ".runtime", "mail_listener.log")

# IDLE 超时（秒），轮询间隔
POLL_INTERVAL = 30  # 每30秒主动检查一次新邮件
IDLE_TIMEOUT = 30   # IDLE 等待30秒，不依赖服务器推送
MAX_IDLE_CYCLES = 50  # 50次轮询后（约25分钟）重连刷新连接

# 全局标志
running = True


def signal_handler(sig, frame):
    """优雅退出"""
    global running
    log.info("收到退出信号，正在停止...")
    running = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def send_notification(title, message):
    """发送 macOS 系统通知"""
    try:
        # 使用 osascript 发送通知
        escaped_msg = message.replace('"', '\\"')
        escaped_title = title.replace('"', '\\"')
        script = f'display notification "{escaped_msg}" with title "{escaped_title}"'
        subprocess.run(['osascript', '-e', script], timeout=5, capture_output=True)
        log.info(f"📬 通知: {title} - {message}")
    except Exception as e:
        log.warning(f"发送通知失败: {e}")


def process_new_email():
    """处理新到达的邮件"""
    log.info("🔄 触发邮件处理...")
    try:
        # 只获取最近1天的邮件（避免重复处理）
        cmd = [
            sys.executable, READ_SCRIPT,
            "--days", "1",
            "--output-dir", OUTPUT_DIR,
            "--body-length", "3000"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=PROJECT_ROOT
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            count = data.get("total", 0)
            emails = data.get("emails", [])
            
            if count > 0:
                latest = emails[0]
                subject = latest.get("subject", "(无主题)")
                from_addr = latest.get("from", "(未知)")
                
                log.info(f"✅ 处理完成: {count} 封邮件")
                log.info(f"   最新: {subject} | From: {from_addr}")
                
                # 发送系统通知
                send_notification(
                    f"📬 新邮件 ({count}封)",
                    f"{subject} - {from_addr}"
                )
                
                # 自动生成 sum.md
                for email_info in emails:
                    output_dir = email_info.get("output_dir", "")
                    if output_dir and os.path.isdir(output_dir):
                        sum_path = os.path.join(output_dir, "sum.md")
                        if not os.path.exists(sum_path):
                            generate_sum_md(email_info, sum_path)
            else:
                log.info("ℹ️  没有新邮件")
        else:
            log.error(f"处理失败: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        log.error("处理超时（120秒）")
    except json.JSONDecodeError:
        log.error("解析输出 JSON 失败")
    except Exception as e:
        log.error(f"处理异常: {e}")


def generate_sum_md(email_info, sum_path):
    """为单封邮件生成 sum.md"""
    body = email_info.get("body_preview", "").strip()
    if len(body) > 1500:
        body = body[:1500] + "..."
    
    attachments = email_info.get("attachments", [])
    att_str = ", ".join([a["filename"] for a in attachments]) if attachments else "无"
    att_list = "\n".join([f"- {a['filename']} ({a['size']} bytes)" for a in attachments]) if attachments else "无"
    
    # 图片信息
    images = email_info.get("inline_images", [])
    img_list = "\n".join([f"- ![[images/{img['filename']}]]" for img in images]) if images else "无"
    img_count = len(images)
    
    content = f"""---
subject: "{email_info.get('subject', '')}"
from: "{email_info.get('from', '')}"
to: "{email_info.get('to', '')}"
date: {email_info.get('date', '')}
attachments: [{att_str}]
images: {img_count}
---

# {email_info.get('subject', '')}

## 邮件信息

| 项目 | 内容 |
|------|------|
| 发件人 | {email_info.get('from', '')} |
| 收件人 | {email_info.get('to', '')} |
| 时间 | {email_info.get('date', '')} |

## 正文预览

{body}

## 附件

{att_list}

## 正文图片

{img_list}
"""
    with open(sum_path, 'w', encoding='utf-8') as f:
        f.write(content)
    log.info(f"📝 生成 sum.md: {sum_path} (图片: {img_count})")


def listen():
    """IMAP 轮询 + IDLE 混合监听主循环
    
    QQ邮箱的 IMAP IDLE 推送不可靠，改用短轮询：
    每30秒主动检查新邮件，同时用 IDLE 辅助感知。
    """
    from imapclient import IMAPClient
    
    global running
    
    while running:
        client = None
        try:
            log.info(f"📡 连接 {IMAP_SERVER}:{IMAP_PORT} ...")
            client = IMAPClient(IMAP_SERVER, port=IMAP_PORT, ssl=True, timeout=30)
            client.login(EMAIL_ADDR, AUTH_CODE)
            log.info(f"✅ 登录成功: {EMAIL_ADDR}")
            
            client.select_folder(FOLDER, readonly=True)
            
            # 获取当前最大 UID，用于判断新邮件
            existing_uids = client.search('ALL')
            max_uid = max(existing_uids) if existing_uids else 0
            log.info(f"📊 当前最大 UID: {max_uid}")
            log.info(f"👂 进入轮询监听模式（每{POLL_INTERVAL}秒检查一次）...")
            
            cycle = 0
            while running:
                cycle += 1
                
                # 尝试 IDLE（短超时，辅助感知）
                try:
                    client.idle()
                    responses = client.idle_check(timeout=POLL_INTERVAL)
                    client.idle_done()
                    if responses:
                        log.debug(f"IDLE 事件: {responses}")
                except Exception as idle_err:
                    # IDLE 失败则纯轮询
                    log.debug(f"IDLE 不可用，改用纯轮询: {idle_err}")
                    time.sleep(POLL_INTERVAL)
                
                # 主动检查新邮件
                try:
                    new_uids = client.search('ALL')
                except Exception:
                    # 连接可能断开，重新选择文件夹
                    log.warning("搜索失败，尝试重新选择文件夹...")
                    client.select_folder(FOLDER, readonly=True)
                    new_uids = client.search('ALL')
                
                new_emails = [uid for uid in new_uids if uid > max_uid]
                
                if new_emails:
                    log.info(f"🆕 发现 {len(new_emails)} 封新邮件!")
                    max_uid = max(new_uids)
                    process_new_email()
                    cycle = 0  # 重置计数
                
                # 定期重连刷新连接（约25分钟）
                if cycle >= MAX_IDLE_CYCLES:
                    log.info("⏰ 周期重连刷新...")
                    break
                    
        except KeyboardInterrupt:
            log.info("用户中断")
            running = False
        except Exception as e:
            log.error(f"连接异常: {e}")
            if running:
                log.info("⏳ 5秒后重连...")
                time.sleep(5)
        finally:
            if client:
                try:
                    client.logout()
                except Exception:
                    pass


def write_pid():
    """写入 PID 文件"""
    os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))


def remove_pid():
    """删除 PID 文件"""
    try:
        os.remove(PID_FILE)
    except FileNotFoundError:
        pass


def main():
    import argparse
    parser = argparse.ArgumentParser(description="QQ邮箱 IMAP IDLE 实时监听")
    parser.add_argument("--start", action="store_true", help="启动前台监听")
    parser.add_argument("--daemon", action="store_true", help="启动后台监听")
    parser.add_argument("--stop", action="store_true", help="停止后台监听")
    parser.add_argument("--status", action="store_true", help="查看监听状态")
    parser.add_argument("--once", action="store_true", help="只处理一次新邮件（测试用）")
    
    args = parser.parse_args()
    
    if args.status:
        if os.path.exists(PID_FILE):
            with open(PID_FILE) as f:
                pid = f.read().strip()
            # 检查进程是否存在
            try:
                os.kill(int(pid), 0)
                print(f"✅ 监听运行中 (PID: {pid})")
            except ProcessLookupError:
                print(f"❌ 进程已不存在 (PID: {pid})，PID 文件过期")
                remove_pid()
        else:
            print("❌ 监听未运行")
        return
    
    if args.stop:
        if os.path.exists(PID_FILE):
            with open(PID_FILE) as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"✅ 已发送停止信号 (PID: {pid})")
            except ProcessLookupError:
                print(f"❌ 进程已不存在")
            remove_pid()
        else:
            print("❌ 监听未运行")
        return
    
    if args.daemon:
        # 后台运行
        write_pid()
        # 设置日志输出到文件
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        log.addHandler(file_handler)
        
        log.info(f"🚀 后台监听启动 (PID: {os.getpid()})")
        try:
            listen()
        finally:
            remove_pid()
        return
    
    if args.once:
        # 测试模式：只处理一次
        process_new_email()
        return
    
    # 默认前台运行
    write_pid()
    log.info(f"🚀 前台监听启动 (PID: {os.getpid()})")
    log.info("按 Ctrl+C 停止")
    try:
        listen()
    finally:
        remove_pid()


if __name__ == "__main__":
    main()
