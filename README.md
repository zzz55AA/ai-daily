# AI 科技日报

公开档案共 22 份：10月24–30日周报、11月1日和2日增量、11月3–4日试刊，以及 11月5–22日第 1–18 期。

- [周报 · 2026-10-24 – 10-30](2026/10/24-30.html)
- [试刊 · 2026-11-03 – 11-04](2026/11/03-04.html)
- [第 18 期 · 2026年11月22日](2026/11/22.html)
- [第 17 期 · 2026年11月21日](2026/11/21.html)
- [第 16 期 · 2026年11月20日](2026/11/20.html)
- [第 15 期 · 2026年11月19日](2026/11/19.html)
- [第 14 期 · 2026年11月18日](2026/11/18.html)
- [第 13 期 · 2026年11月17日](2026/11/17.html)
- [第 12 期 · 2026年11月16日](2026/11/16.html)

首页 `index.html` 是档案。桌面左侧按年、月、日和期号浏览；窄屏用「历史日报」抽屉。搜索使用 `archive/index.json`，不加载整期图片。报告正文、内嵌图片和折叠交互仍在日期路径里。

每期正式路径是 `年/月/日.html`。原来的 `年-月-日.html` 会转到该页。报告正文、内嵌图片和折叠交互保持原文件内容。

## 深度研究

专题长文专栏，与日报分开计数，不并入日报归档，也不占用日报期号。目前 12 篇：

- [深度研究专栏首页](research.html)
- [大模型如何训练、蒸馏，又如何防止被蒸馏](research-training-distillation.html) — 2026-11-22（源码静态解析与教学复算，非模型实测；防蒸馏不是绝对保证）
- [AI如何理解连续视频，而不只是几张截图](research-continuous-video.html) — 2026-11-22（Qwen3-VL / StreamingVLM 与 Gemini Live 公开契约边界）
- [拆解宇树G1：从仿真训练、遥操作到真机控制](research-unitree-g1.html) — 2026-11-22（宇树 G1 主线；NVIDIA Isaac Lab / Physical Intelligence openpi 为训练平台与策略对照）
- [长任务 Agent 如何可靠接续工作](research-long-running-agents.html) — 2026-11-21（跨会话交接与崩溃恢复）
- [上下文工程：每一步给模型看什么](research-context-engineering.html) — 2026-11-21（上下文选择、检索与压缩损失）
- [实时WebRTC深度讲义｜协议、会话、播放与恢复](research-realtime-webrtc.html) — 2026-11-21（协议、会话、播放与恢复）
- [Karpathy 2023 Intro to LLMs 独立深读](research-karpathy-intro-2023.html) — 2026-11-21（2023 短讲座 Intro to Large Language Models）
- [从预测下一个词，到成为 AI 助手——Karpathy LLM 讲座深度图解](research-karpathy-llm-2025.html) — 2026-11-21（2025 长讲座 Deep Dive into LLMs like ChatGPT，讲座发布于 2025-02-05）
- [OpenSpec 深度报告](research-openspec.html) — 2026-11-21（OpenSpec 2.1.1）
- [Superpowers 深度报告](research-superpowers.html) — 2026-11-21（Superpowers v7.0.2）
- [图解 poteto 的 AI Engineer 演讲与 pstack](research-pstack.html) — 2026-11-15（pstack v0.15.42 历史快照）
- [Matt Pocock Skills 深度研究](research-matt-pocock-skills.html) — 2026-11-21

正式路径是 `research.html` 与 `research-<文章名>.html`。日报首页 `index.html` 顶部有「日报 / 深度研究」入口，专栏首页有返回日报的链接。专题正文保留自带的图文与脚本，不引用日报的归档脚本。

页面不引用外部脚本、字体或统计。没有定时发布。历史回填只做一次：把已经核对过的 HTML 交给

```bash
python3 scripts/import-reports.py --manifest 清单.json
```

清单里的 `file` 是该期选定的终稿，不按文件修改时间取舍。同一天可以有多份报告，跨日期的专刊也单独保留。Markdown 和 PDF 先原样留下并标明尚未转换。公开作者邮箱可以保留；疑似收件人、本机路径或密钥只报告类别和数量，不打印内容，对应的已批准稿也不会被悄悄丢掉。11 月 8 日必须是 83 条的终稿，11 月 10 日必须是补入 Anthropic 的 61 条终稿。

## 发布

GitHub Pages 已从 `main` 发布。合并本变更后，现有工作流会发布首页、`archive/`、各年份目录和日期跳转页：

https://zzz55aa.github.io/ai-daily/

不需要另改仓库权限或 Pages 设置。合并前线上仍是现在的首页。
