# AI 科技日报

公开试刊静态站，目前只有两期：

- [第 12 期 · 2026年11月16日](2026-11-16.html)
- [第 11 期 · 2026年11月15日](2026-11-15.html)

首页 `index.html` 按时间从新到旧链接这两期。报告正文、内嵌图片和折叠交互保持原样。页面不引用外部脚本、字体或统计。

发布前已核对：报告中没有私人联系方式、邮件收件人、投递记录、本机路径或密钥。文章里的公开作者和来源仍保留。

## 发布到 GitHub Pages

仓库已是公开仓库 `zzz55AA/ai-daily`。站点文件在仓库根目录，并带有 `.nojekyll`。

当前令牌没有 `pages=write` 与 `administration=write`，因此无法从这里打开 Pages。站点地址 **尚未上线**。合并本变更后，预期地址是：

https://zzz55AA.github.io/ai-daily/

仓库所有者还需要完成下面其中一条。

### 方式 A：合并后由 Actions 发布

`.github/workflows/pages.yml` 只在推送到 `main` 时运行。合并拉取请求后，若仓库允许 Actions，且 Workflow permissions 为读写，该工作流会发布根目录里的三个 HTML 文件。

若工作流因权限失败：

1. 打开 [Actions 权限设置](https://github.com/zzz55AA/ai-daily/settings/actions)。
2. 在 Workflow permissions 中选择 **Read and write permissions** 并保存。
3. 在 Actions 里重新运行 **Deploy GitHub Pages**。

### 方式 B：从分支发布，不依赖 Actions

1. 先把拉取请求合并到 `main`。
2. 打开 [Pages 设置](https://github.com/zzz55AA/ai-daily/settings/pages)。
3. Build and deployment 选择 **Deploy from a branch**。
4. Branch 选择 `main`，文件夹选择 `/ (root)`，保存。
5. 等到设置页显示站点已发布，再打开 https://zzz55AA.github.io/ai-daily/ 确认首页是「近期刊期」，而不是只有本说明文件。

两种方式不要同时启用。若已用方式 B，可忽略方式 A 的工作流失败。
