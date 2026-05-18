# 博客引导文件

这个博客现在的定位是：学生个人博客，用来分享学习、生活、兴趣和日常思考。

首页是一个单屏切换界面：顶部导航里的“首页 / 文章 / 项目文件存储”不会跳到长页面，而是在同一个首页里用滑动动画切换分支内容，同时背景图也会切换。

---

## 启动项目

```bash
cd /Users/sakiko/Public/blog
npm run dev
```

常用命令：

```bash
npm run check
npm run build
```

- `npm run dev`：本地预览
- `npm run check`：检查 Astro 和类型问题
- `npm run build`：生成正式站点

---

## 最常改的地方

- [src/pages/index.astro](/Users/sakiko/Public/blog/src/pages/index.astro)：首页三个分支的内容和切换脚本
- [src/styles/global.css](/Users/sakiko/Public/blog/src/styles/global.css)：整体视觉、毛玻璃、背景图和滑动动画
- [src/data/site.ts](/Users/sakiko/Public/blog/src/data/site.ts)：站点名称、描述、顶部导航、社交链接
- [src/data/resources.ts](/Users/sakiko/Public/blog/src/data/resources.ts)：资源链接、emoji 和用途说明
- [src/lib/fileStore.ts](/Users/sakiko/Public/blog/src/lib/fileStore.ts)：项目文件仓库配置
- [src/content/blog](/Users/sakiko/Public/blog/src/content/blog)：文章内容
- [public/images/backgrounds](/Users/sakiko/Public/blog/public/images/backgrounds)：首页三个分支使用的背景图
- [public/project-storage](/Users/sakiko/Public/blog/public/project-storage)：项目文件存储的真实文件

---

## 首页分支怎么工作

首页目前有三个分支：

- `#home`：首页介绍
- `#articles`：最近文章
- `#files`：项目文件存储

对应文件是 [src/pages/index.astro](/Users/sakiko/Public/blog/src/pages/index.astro)。

每个分支是一段这样的结构：

```astro
<article class="stage-panel glass-panel" id="files" data-panel="files">
  ...
</article>
```

背景图对应的是：

```astro
<div class="stage-bg" data-bg="files"></div>
```

切换逻辑会根据 `data-panel` 和 `data-bg` 的名字匹配，所以如果新增分支，两个名字要一致。

---

## 如果你想改项目文件存储内容

改 [src/pages/index.astro](/Users/sakiko/Public/blog/src/pages/index.astro) 里这段：

```astro
<article class="stage-panel glass-panel files-panel" id="files" data-panel="files">
```

现在里面包含：

- 在线工具入口：`本地学术学习助手`，跳转到独立部署的在线应用，不复制工具工程文件
- 仓库卡片：课程笔记 `deeplearning`
- 资源链接：从书签 HTML 整理出来的网站，带 emoji 和用途说明
- 返回首页按钮

当前文件仓库页面：

- `/files/deeplearning/`：课程笔记

文件仓库页面会自动读取 [public/project-storage](/Users/sakiko/Public/blog/public/project-storage) 里的目录和文件，并显示成类似 GitHub 仓库的文件列表。

注意：公开博客目录里不要放论文编写、未公开项目、token、API key 或其他不适合公开展示的资料。本地备份可以继续放在博客目录外，但不要复制到 `public/project-storage/`。

在线工具入口当前指向：

```text
https://academic-learning-assistant.vercel.app
```

如果以后重新部署这个工具，只需要改 [src/pages/index.astro](/Users/sakiko/Public/blog/src/pages/index.astro) 里的 `externalProjects` 链接，不要把工具项目文件夹复制进博客。

---

## 如果你想更新文章分区

文章都放在 [src/content/blog](/Users/sakiko/Public/blog/src/content/blog)。

当前文章页有两个分区：

- `i write`：你自己写的站内文章，会生成博客详情页
- `i prefer`：你推荐的外部阅读，只显示卡片并跳转到原网站，不复制原文

站内文章示例：

```md
---
title: "一篇新的学习笔记"
description: "这篇文章记录我最近学到的东西。"
pubDate: 2026-05-18
section: "i write"
tags: ["Learning"]
---

正文写在这里。
```

外部推荐示例：

```md
---
title: "The AI Revolution"
description: "一篇值得反复阅读的 AI 长文。"
pubDate: 2026-05-18
section: "i prefer"
externalUrl: "https://waitbutwhy.com/2015/01/artificial-intelligence-revolution-1.html"
tags: ["AI", "Essay"]
---

这只是推荐卡片说明，不复制原文。
```

---

## 如果你想添加新的文件仓库

第一步：把文件放到公开目录里。

示例：

```text
public/project-storage/math/
```

第二步：修改 [src/lib/fileStore.ts](/Users/sakiko/Public/blog/src/lib/fileStore.ts)，在 `repositories` 里加一项：

```ts
{
  slug: "math",
  title: "数学资料",
  category: "课程笔记",
  description: "数学课程、习题、讲义和复习资料。",
  root: "math"
}
```

第三步：如果希望首页“项目文件存储”里出现它，不需要额外改页面。首页会自动读取 `repositories` 并生成仓库卡片。

---

## 如果你想更新资源链接

改 [src/data/resources.ts](/Users/sakiko/Public/blog/src/data/resources.ts)。

每个资源是这样的：

```ts
{
  emoji: "📘",
  title: "动手学深度学习",
  href: "https://zh.d2l.ai/",
  purpose: "系统学习深度学习理论、代码实践和模型实现。"
}
```

字段说明：

- `emoji`：显示在资源卡片前面的图标
- `title`：网站名称
- `href`：网站链接
- `purpose`：这个网站的作用说明

---

## 如果你想新增一个首页分支

需要改三个地方。

1. 在 [src/data/site.ts](/Users/sakiko/Public/blog/src/data/site.ts) 加导航：

```ts
{ href: "/#notes", label: "随笔" }
```

2. 在 [src/pages/index.astro](/Users/sakiko/Public/blog/src/pages/index.astro) 加背景和面板：

```astro
<div class="stage-bg" data-bg="notes"></div>

<article class="stage-panel glass-panel" id="notes" data-panel="notes">
  <p class="eyebrow">Notes</p>
  <h2>随笔</h2>
  <p>这里可以放临时想法和生活记录。</p>
</article>
```

3. 在同一个文件的脚本里更新顺序：

```js
const stageOrder = ["home", "articles", "files", "notes"];
```

如果这个分支需要新背景图，再去 [src/styles/global.css](/Users/sakiko/Public/blog/src/styles/global.css) 里加：

```css
.stage-bg[data-bg="notes"] {
  background-image: url("/images/backgrounds/your-image.jpg");
  background-position: center;
}
```

---

## 如果你想换首页背景图

把图片放进：

- [public/images/backgrounds](/Users/sakiko/Public/blog/public/images/backgrounds)

然后改 [src/styles/global.css](/Users/sakiko/Public/blog/src/styles/global.css)：

```css
.stage-bg[data-bg="home"] {
  background-image: url("/images/backgrounds/43281250_p0_master1200.jpg");
}
```

当前背景对应关系：

- `home`：`43281250_p0_master1200.jpg`
- `articles`：`43650801_p0_master1200.jpg`
- `files`：`30757230_p0_master1200.jpg`

---

## 如果你想发布新文章

在 [src/content/blog](/Users/sakiko/Public/blog/src/content/blog) 新建 `.mdx` 文件。

示例：

```mdx
---
title: "我的第一篇学习记录"
description: "今天整理了一些复习方法和学习计划。"
pubDate: 2026-05-08
tags:
  - 学习
  - 日常
hero: "/images/mesh-hero.svg"
---

正文从这里开始。

## 今天学到了什么

写下具体内容。
```

不想发布时加：

```md
draft: true
```

---

## 如果你想改整体视觉

主要改 [src/styles/global.css](/Users/sakiko/Public/blog/src/styles/global.css)。

常见入口：

- `.site-header`：顶部半透明导航
- `.glass-panel`：毛玻璃文字框
- `.stage-panel`：分支面板和滑动动画
- `.stage-bg`：背景图淡入切换
- `.repo-shell` / `.repo-row`：仓库式文件页面
- `.resource-card`：资源链接卡片
- `.file-card` / `.file-row`：项目文件存储样式

例如让文字框更透明：

```css
:root {
  --card: rgba(242, 247, 244, 0.32);
}
```

例如让背景切换更慢：

```css
.stage-bg {
  transition: opacity 900ms ease, transform 1300ms ease;
}
```

---

## 当前设计逻辑

- 首页只有一个主视觉舞台，不再是多个长滚动板块。
- 点击顶部小分支会在同一页面切换内容。
- 切换时内容面板左右滑动，背景图淡入切换。
- “文章”分支展示最近文章，也保留完整文章页 `/blog`。
- “项目文件存储”分支现在包含真实文件仓库和资源链接。
- 仓库页面读取 `public/project-storage`，文件会以类似 GitHub 仓库的方式展示。
