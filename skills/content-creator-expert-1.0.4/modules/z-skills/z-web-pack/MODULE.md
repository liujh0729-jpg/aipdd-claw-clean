---
name: z-web-pack
description: 当用户提供一个或多个同主题网页链接，并要求“采集网页素材”“把链接正文拿到本地”“正文相关链接也下载”“配图保存到本地”“做成备用写作素材包”“z-web-pack”时必须使用。会逐个阅读入口链接正文和正文内高价值相关链接，过滤导航、页脚、广告和社交分享，把 Markdown、链接清单、阅读地图、图片及视频链接清单保存到 Clippings/Reading；支持懒加载图片、srcset 高清档、防盗链 Referer、受限来源说明与公开支持来源补充；发现视频链接只登记到 04-media-inventory.md，下载交给 z-video-downloader；常规抓取失败后才使用 r.jina.ai 兜底。
---
> **EN:** Web asset collection: batch-save page text, related links and images from one or more same-topic URLs as reusable writing material.
>

# 网页素材包采集

把若干同主题链接整理成可直接供后续写文章使用的本地资料包。

## 依赖说明

- 必须用 miniconda 的 Python 运行（系统 python3 缺 readability-lxml）：`/Users/zz/miniconda3/bin/python3`
- 本 skill 已随包携带基础采集模块：`scripts/collect_web_research_pack.py`

## 输出目录

默认保存到：

```bash
/Users/zz/Library/Mobile Documents/iCloud~md~obsidian/Documents/zhangAI/Clippings/Reading/
```

每次任务创建独立文件夹：

```text
YYYY-MM-DD-主题名/
├── README.md
├── 00-research-brief.md
├── 01-link-inventory.md
├── 02-image-inventory.md
├── 03-reading-map.md
├── 04-media-inventory.md
├── 05-access-notes.md（存在受限来源时生成）
├── MAIN-01-入口正文.md
├── LINKED-02-正文相关链接.md
└── assets/
```

## 完成标准

1. 每个用户入口链接都要生成 `MAIN-*.md`；受限来源也要生成清楚的受限说明，不能只留下空壳
2. 入口正文里的相关链接要尽量展开成 `LINKED-*.md`
3. 只采正文、正文表格、正文图片、正文代码和正文里的相关链接
4. 跳过侧边栏、页脚、广告、登录、订阅、招聘、隐私政策、服务条款、社交分享链接
5. 图片下载到 `assets/`，Markdown 中使用本地相对路径；懒加载图取真实地址，srcset 取最大档，badge/tracking 像素自动跳过
6. 正文 `<video>`、直链视频、平台视频和 m3u8 只记录到 `04-media-inventory.md`；需要下载时转用 `z-video-downloader`
7. 生成 `README.md`、`00-research-brief.md`、`01-link-inventory.md`、`02-image-inventory.md`、`03-reading-map.md`、`04-media-inventory.md`
8. 记录失败、受限、跳过和兜底情况
9. 收尾检查不得留下非 `r2blog.zhanglearning.com` / `r2.zhanglearning.com` 的外链图片；如果留下，必须调用 `1-upload-images-to-picgo`
10. `pages_restricted` 大于 0 时，继续寻找公开转载、官方材料或可信二次报道，至少补入一条成功保存的 `--support-url`

## 推荐命令

单篇文章先采用保守模式，避免新闻站导航链接污染资料包：

```bash
/Users/zz/miniconda3/bin/python3 .agent/skills/z-web-pack/scripts/collect_web_pack.py \
  --out-root "/Users/zz/Library/Mobile Documents/iCloud~md~obsidian/Documents/zhangAI/Clippings/Reading" \
  --title "主题名" \
  --max-depth 0 \
  --max-pages 1 \
  "https://example.com/article"
```

明确要扩展正文相关资料时使用研究模式：

```bash
/Users/zz/miniconda3/bin/python3 .agent/skills/z-web-pack/scripts/collect_web_pack.py \
  --out-root "/Users/zz/Library/Mobile Documents/iCloud~md~obsidian/Documents/zhangAI/Clippings/Reading" \
  --title "主题名" \
  --max-depth 1 \
  --max-pages 40 \
  "https://example.com/a" \
  "https://example.com/b"
```

注意：脚本路径是相对项目根的，运行前先 `cd` 到 zhangAI 目录，或改用绝对路径。

参数建议：

- `--max-depth 1`：入口链接 + 入口正文相关链接
- `--max-depth 2`：用户明确要求尽量深挖时使用
- `--max-pages 40`：普通主题
- `--max-pages 80`：用户明确要求尽量多采集时使用
- `--same-domain-only`：只采同域资料时使用
- `--no-jina`：调试时禁用 `r.jina.ai` 兜底
- `--max-image-mb 20`：单张图片大小上限，默认 20MB
- `--support-url URL`：给受限入口补充公开来源，可重复使用

## 受限来源恢复

遇到付费墙、Cloudflare、DataDome、CAPTCHA、登录提示或 `pages_restricted` 大于 0 时：

1. 保留脚本生成的 `MAIN-*.md` 受限说明和 `05-access-notes.md`。
2. 搜索公开转载、监管机构原文、公司公告、论文、官方博客或可信二次报道。
3. 用 `--support-url` 加入公开来源；这些来源会作为 `LINKED-*.md` 保存。
4. 检查 `05-access-notes.md`：成功来源应对应真实的 `LINKED-*.md`，失效或受限来源会单独列出，不能计作有效补充。

```bash
/Users/zz/miniconda3/bin/python3 .agent/skills/z-web-pack/scripts/collect_web_pack.py \
  --title "主题名" \
  --max-depth 0 \
  --max-pages 4 \
  --support-url "https://public.example.org/report" \
  --support-url "https://official.example.com/source" \
  "https://restricted.example.com/article"
```

## 抓取顺序

每个页面按这个顺序尝试：

1. GitHub repo/blob 链接优先走 GitHub API / raw / README（已内置实现）
2. 常规 HTTP 抓取正文（图片带 Referer 防盗链）
3. Markdown、JSON、纯文本资源直接保存
4. 如果失败、受限、正文明显为空或只抓到登录提示，再使用 `r.jina.ai` 兜底

`r.jina.ai` 只能作为兜底。不要一开始就用它。

## 图片采集能力

- 懒加载：自动识别 `data-src` / `data-original` / `data-lazy-src` / `data-actualsrc` / `data-echo`，跳过 base64 占位图
- 响应式：`srcset` / `<picture><source>` 自动识别 `w` 和 `x` 描述并选择高清档
- 防盗链：所有图片请求带页面 `Referer`
- 纠错：按文件魔数（magic bytes）纠正扩展名，CDN 给错 Content-Type 也能存对
- 去重：相同内容（sha256）的图片只存一份
- 过滤：1x1 tracking 像素、shields.io badge、favicon 等装饰图自动跳过

## 视频链接处理

- 页面 `<video>` / `<source>` / 正文直链 `.mp4/.webm/.mov` 会被识别并写入 `04-media-inventory.md`
- 入口或正文里的 YouTube / B站 / Vimeo / X / 抖音页面和 m3u8 会被识别并写入 `04-media-inventory.md`
- YouTube Live、B站短链、Instagram、Facebook 和抖音嵌入链接也会被识别
- 入口本身就是视频链接时只生成登记说明和媒体清单，不会误下载视频
- `z-web-pack` 不下载任何视频，不调用 `yt-dlp`，不读取浏览器 cookie
- 用户明确要下载视频时，切换到 `z-video-downloader`，把 `04-media-inventory.md` 里的 Source URL 作为输入

## 相关链接判断

优先展开：

- 官方文档、博客、论文、模型卡、仓库、README、release、issue、PR
- 与主题直接相关的 benchmark、评测、数据表、cookbook、示例代码
- 正文里用于支撑核心观点的数据源、图表源、产品页

跳过：

- 导航菜单、页脚、广告位、推荐阅读区里的泛链接
- 登录、注册、订阅、招聘、隐私、条款、Cookie
- 分享到 X / LinkedIn / Facebook 等社交分享链接
- logo、favicon、头像、装饰图、徽章

## 收尾检查

交付前至少运行：

```bash
find "资料包目录" -maxdepth 2 -type f | sort
rg -n '!\[[^]]*\]\(https?://' "资料包目录" || true
find "资料包目录" -maxdepth 1 -name 'MAIN-*.md' -print
test -f "资料包目录/03-reading-map.md" && sed -n '1,120p' "资料包目录/03-reading-map.md"
find "资料包目录/assets" -type f | wc -l
test -f "资料包目录/04-media-inventory.md" && rg -c '^\| detected \|' "资料包目录/04-media-inventory.md"
```

最终回复说明：

- `z-web-pack` skill 的路径
- 本次资料包路径
- Markdown 数量、主文数量、关联资料数量、图片数量、视频链接数量
- 失败、受限或使用 Jina 兜底的链接
- 如发现视频链接，提示使用 `z-video-downloader` 下载
- 如存在受限来源，说明已补入哪些公开支持来源；如果仍无公开来源，明确标注资料包仍需补充
