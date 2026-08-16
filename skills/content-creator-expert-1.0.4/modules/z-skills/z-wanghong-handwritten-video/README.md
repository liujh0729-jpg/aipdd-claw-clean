# z-wanghong-handwritten-video

把 `z-wanghong-handwritten-ppt` 生成的 HTML 原样做成动画 MP4。渲染器直接打开原 HTML DOM，只增加元素进入顺序、荧光揭示、SVG 描边和纸张转场；字形锁定为原 PPT Skill 预览封面的手写字，字号、颜色和布局继续使用原 HTML/CSS。

## 快速开始

```bash
npm install
scripts/render_html_video.sh \
  "/absolute/path/to/index.html" \
  "/absolute/path/to/output.mp4" \
  --seconds-per-slide 4 \
  --font-file "/absolute/path/to/Hanzipen.ttc"
```

输出固定为 1920×1080、30fps、H.264、`yuv420p`，含一条视频流和零条音频流，同目录生成 `cover.png`。

## 典型触发

- 动画版王虹PPT
- 王虹手写动画
- Notability 手写视频
- 手写 PPT 转 MP4
- 保留原 HTML 风格做成无声视频

## 目录

- `MODULE.md`：完整工作流与验收规则
- `scripts/render_html_video.mjs`：原 HTML DOM 逐帧渲染器
- `scripts/render_html_video.sh`：检查与交付入口
- `references/motion-injection.md`：动效注入规则
- `examples/handwritten-html-motion-demo/`：真实 MP4 样片
- `tests/`：字体/排版不重做与零音轨契约测试
