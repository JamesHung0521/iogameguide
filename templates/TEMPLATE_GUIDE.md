# 攻略站HTML模板使用说明

## 模板文件
- `guide-template.html` — 完整HTML脚手架，包含所有固定结构

## 使用方式
1. 复制 `guide-template.html` 并重命名为 `{game-id}-guide.html`
2. 替换所有 `{{变量}}` 为实际值
3. 在 `<article class="article-content">` 标签内写正文内容
4. 验证HTML标签闭合后上传

## 需要替换的变量

### 必填变量
| 变量名 | 说明 | 示例 |
|--------|------|------|
| `{{GAME_NAME}}` | 游戏名 | `Hordes.io` |
| `{{GAME_NAME_SCHEMA}}` | Schema用的游戏名(无标点) | `Hordes Io` |
| `{{GAME_ID}}` | 游戏标识(小写+短横线) | `hordes-io` |
| `{{SUBTITLE}}` | 副标题 | `Master 4 Classes & PvP Combat` |
| `{{META_DESCRIPTION}}` | SEO描述 | `Complete guide for Hordes.io...` |
| `{{DATE}}` | 发布日期(YYYY-MM-DD) | `2026-06-13` |
| `{{DATE_DISPLAY}}` | 显示日期 | `June 13, 2026` |
| `{{READ_TIME}}` | 阅读时间 | `10 min` |
| `{{GENRE}}` | 游戏类型 | `MMORPG` |
| `{{GAME_EMOJI}}` | 游戏emoji | `⚔️` |
| `{{BADGE}}` | 标签 | `New` |
| `{{PLAY_URL}}` | 游戏链接 | `https://hordes.io` |
| `{{PLAY_TEXT}}` | 按钮文字 | `Play Hordes.io Now` |
| `{{TAGS}}` | 关键词(逗号分隔) | `MMORPG, PvP, Fantasy` |

### 文章内容变量(在article内替换)
| 变量名 | 说明 |
|--------|------|
| `{{SECTION_1_TITLE}}` | 第一节标题 |
| `{{SECTION_1_CONTENT}}` | 第一节内容 |
| `{{TOC_1}}` ~ `{{TOC_5}}` | 目录项 |
| `{{SCREENSHOT_1_CAPTION}}` | 截图说明 |
| `{{TIP_ICON}}` | Tip图标 |
| `{{TIP_TITLE}}` | Tip标题 |
| `{{TIP_CONTENT}}` | Tip内容 |
| `{{WARNING_TITLE}}` | 警告标题 |
| `{{WARNING_CONTENT}}` | 警告内容 |
| `{{FAQ_1_QUESTION}}` | FAQ问题 |
| `{{FAQ_1_ANSWER}}` | FAQ答案 |

## 固定结构(不要修改)

以下部分的HTML结构是固定的，**不要修改**：
1. `<nav>` — 导航栏（包含SVG logo + hamburger menu）
2. `<footer>` — 页脚（包含Quick Links / Popular Games / Legal）
3. CSS引用 — `../css/style.css`
4. AdSense ID — `ca-pub-1074835585646908`
5. GA ID — `G-3SFHCK9FDP`
6. Schema.org JSON-LD 结构

## CSS类名规范

| 元素 | Class名 |
|------|---------|
| 导航容器 | `.container` |
| Logo | `.logo` |
| 汉堡菜单 | `.hamburger` |
| 主内容区 | `.guide-page` |
| Header | `.guide-header` |
| 游戏徽章 | `.game-badge` |
| 元信息 | `.meta` (不是guide-meta!) |
| Hero图 | `.game-hero` |
| 文章 | `.article-content` |
| 目录 | `.tip-box` + `.tip-title` |
| 提示框 | `.tip-box` / `.tip-box.warning` |
| 截图 | `.game-screenshot` |
| FAQ | `.faq-item` + `h3` + `p` |
| 相关攻略卡片 | `.guide-card` / `.guide-thumb` / `.guide-content` / `.guide-meta` / `.guide-excerpt` |
| Footer容器 | `.container` + `.footer-content` |

## 相关链接路径规范
- 首页: `../index.html`
- 游戏列表: `../games.html`
- 攻略列表: `../guides.html`
- 关于: `../about.html`
- 其他攻略: `agar-io-guide.html` (相对路径，无../)
- 隐私政策: `../privacy-policy.html`
