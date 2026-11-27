# 共享页面资源

完整版与 TLDR 共用 site.css、site.js、market.css、market.js、visuals.css、visuals.js 和 social.css。

site.js 提供事件和来源筛选、历史锚点兼容与章节导航；market.js 提供收盘价格比较。所有页面内容及静态数据表在禁用 JavaScript 时仍可阅读。

visuals.js 提供人物／机构筛选、直接关系浏览及深链接恢复。卡片由 `data/relationships.json` 构建，保持真实动作方向和常显的证据限定；数量仅表示收录条目。social.css 为可见的社交档案、回应卡片及历史统计表提供响应式样式。

## 照片授权

`jensen-portrait.jpg`：Anders Eidesvik 于2026年4月30日在斯坦福大学拍摄；采用 Wikimedia Commons 已有裁剪版，文件为 `Jensen huang stanford 2026-04-30 009 (cropped).jpg`。许可 CC BY 4.0。原文件未再次编辑，仅使用CSS适配版面。

- 来源：https://commons.wikimedia.org/wiki/File:Jensen_huang_stanford_2026-04-30_009_(cropped).jpg
- 许可：https://creativecommons.org/licenses/by/4.0/
- 页面说明这是资料照片，不能作为11月事件现场影像。

## 官方文件预览

三个PNG由官方PDF第一页直接渲染，保留整页，每张600×777。

- `document-cotton.png`：Cotton信函，2025-10-13，原PDF2页。https://www.cotton.senate.gov/wp-content/uploads/media/doc/101325lutnickletter.pdf
- `document-doj.png`：商务部/司法部联合声明，署日2026-11-16，原PDF2页。https://www.justice.gov/opa/media/1472536/dl?inline
- `document-entity-list.png`：《联邦公报》76148页，2026-11-25刊登、11-23生效，原PDF3页。第一页同页保留前项FAA规则，BIS标题在中栏下部。https://www.govinfo.gov/content/pkg/FR-2026-11-25/pdf/2026-23999.pdf

原始PDF SHA-256分别为 `31444f0a31b5f30996b602ad5c5bd491ae060a39639499c222169212a0cf298d`、`b4113d688a02f682d82ceae2ed339a1ccdbe91783ec833ec89e2fe9f2d8a7e9b`、`c7601db5e3db0fee2405af5ae4cf25cf3ba1effa374a7b69b923977fbcdd3af1`。
