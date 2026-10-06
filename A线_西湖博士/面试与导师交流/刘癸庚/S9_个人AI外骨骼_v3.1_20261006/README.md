# S9｜我想做的，是一套真正跟着我一起工作的 AI 外骨骼

2026-10-06｜**INTERNAL / v3.1 CANDIDATE**｜在 S9 v3 基础上的概念修正版；A/B 两帧，保留完整真实页面截图。

## 交付

- [可编辑 PPTX（A/B 两页）](S9_个人AI外骨骼_v3.1.pptx) · [PowerPoint 16.0 PDF](S9_个人AI外骨骼_v3.1.pdf)
- A：[4K PNG](预览/S9-A_3840x2160.png) · [1080p PNG](预览/S9-A_1920x1080.png) · [speaker notes](speaker_notes_A.md)
- B：[4K PNG](预览/S9-B_3840x2160.png) · [1080p PNG](预览/S9-B_1920x1080.png) · [speaker notes](speaker_notes_B.md)
- [完整 S9 权威口述副本](speaker_notes_S9_full.md)
- S7A → S8v3.1 → S9A-v3.1 → S9B-v3.1 → S10：[横向连续审阅](预览/S7A-S8v3.1-S9Av3.1-S9Bv3.1-S10_连续审阅_横向.png) · [纵向连续审阅](预览/S7A-S8v3.1-S9Av3.1-S9Bv3.1-S10_连续审阅_纵向.png)
- [来源与 provenance](来源与provenance.md) · [实际渲染验收](render_validation.md) · [交付核验](检查证据/交付核验.json)
- [页面制作源](制作源/build_slides.py) · [PowerPoint 导出](制作源/render_pair.py) · [连续审阅制作源](制作源/review_sequence.py) · [交付检查源](制作源/validate_delivery.py)

## 本轮修正

S9 v3.1 不再把系统中心放在“做事前先判断哪些任务交给 AI”。它表达的是：本人专注读题、理解、推导和作答；真实学习动作完成后，协议文件预先定义的后续处理自然接续。

| 帧 | 页面承担的一个问题 | 可见表达 |
|---|---|---|
| A：长期状态／空间进度 | 系统持续维护什么？ | 时间进度；知识 / 能力空间。两条轴刻意分开，不把周次机械映射到章节，也不由界面状态替本人宣布掌握。 |
| B：执行接续 | 一次学习动作之后发生什么？ | 学习结果 → 批改 / 分析 → 归档 / 状态更新 → 复习 / 后续训练。右侧是轻量协议触发链，不是产品架构图或功能清单。 |

两帧标题统一为“我想做的，是一套真正跟着我一起工作的 AI 外骨骼”。真实 S06 课程图谱与 S05 执行驾驶舱均完整保留，仅去浏览器 / 窗口栏；截图没有局部重绘、缩小塞入列表或修改内部文字。

## 口述与范围

speaker notes 直接从远端最新权威稿 [`S8-S11_完整讲稿_当前确认版_20261006.md`](../S8-S11_完整讲稿_当前确认版_20261006.md) 的 S9 全文切分而来；A/B 备注保持原句顺序，完整副本便于逐字核对。S9 → S10 只保留“把实践产生的思考写下来”的最新轻转场，不引入旧稿的 Agent Native 强转场。

“自动 / 静默”仅指学习事件或 block 完成后按既定协议进入后续处理；不宣称 24/7 常驻后台、无条件实时运行、学习效果或成熟统一平台。系统状态也不替本人判断是否真正掌握。

S8 v3.1 只作为连续审阅中的既有候选读取，未在本轮重建或修改；S10、S11、S12、S13、FULL_DRAFT、main 与已发送材料均未修改。本目录保留 S9 v3 原目录，未覆盖旧稿。

## 复现

在本目录执行：

1. `python 制作源/build_slides.py --only s9`：从本目录打包的真实截图重建可编辑 PPTX。
2. `python 制作源/render_pair.py`：用 Microsoft PowerPoint 16.0 只读打开本候选，导出 PDF、4K/1080p PNG 和渲染证据；不保存回 PPTX。
3. `python 制作源/review_sequence.py`：只读取 S7A、S8 v3.1、S10 的既有 PNG，与本轮 A/B 组合连续审阅图，不合并 PPT。
4. `python 制作源/validate_delivery.py`：检查页面比例、文字边界、备注、图片字节与放置、PDF 页数、连续审阅来源和 Markdown 链接。

依赖为 python-pptx、Pillow、pywin32、Microsoft PowerPoint 16.0、pdfinfo 与 pdftoppm。当前状态是 **INTERNAL / v3.1 CANDIDATE**，待本人审阅和实际试讲；不表示 READY、SENT、SUBMITTED 或 OFFER。
