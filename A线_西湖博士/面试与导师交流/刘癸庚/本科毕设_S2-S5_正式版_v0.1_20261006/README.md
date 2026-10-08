# 本科毕设 S2–S5｜当前正式留档版

2026-10-06｜**INTERNAL / FORMAL v0.1**

本目录保留用户当前编辑完整稿中的 S2–S5，作为目前本科毕设四页的正式版本。四页均为可编辑 PowerPoint 页面，原对象与当前修改原样保留。

## 交付

- [可编辑正式版 PPTX](本科毕设_S2-S5_正式版_v0.1.pptx)
- [PowerPoint 16.0 导出 PDF](本科毕设_S2-S5_正式版_v0.1.pdf)
- [四页连续总览](预览/四页总览.png)
- [S2 1920×1080](预览/S2_1920x1080.png) · [S3](预览/S3_1920x1080.png) · [S4](预览/S4_1920x1080.png) · [S5](预览/S5_1920x1080.png)
- [来源与版本登记](来源与版本登记.json)
- [当前正式版本变更登记](S2-S5_当前正式版本变更登记.md)
- [PowerPoint 排版检查](PowerPoint排版检查.json)
- [交付文件清单](交付文件清单.json)

## 验收结果

- 4 页实体幻灯片，16:9，PowerPoint 实际读取尺寸 960 × 540 pt。
- 溢出 0、对象越界 0、图片比例异常 0。
- 4/4 页 speaker notes 由 PowerPoint 16.0 实际读回并匹配。
- 4/4 页正式版与来源完整稿对应页的 PowerPoint PNG 渲染逐像素一致。
- 18 个图片对象均保留原始可编辑图片资源与裁切信息；PDF 字体已嵌入：BCDEEE+MicrosoftYaHei, BCDFEE+MicrosoftYaHei-Bold, BCDGEE+MicrosoftYaHei-Bold, BCDHEE+MicrosoftYaHei, BCDIEE+CambriaMath, BCDJEE+ArialMT。
- 正式版 PPTX 在 PowerPoint 只读打开和导出前后 SHA-256 不变。

## 当前状态和后续合并规则

本目录是 **INTERNAL / FORMAL v0.1**，用于当前版本留档和审阅，不代表已发送或 READY。后续合并完整交流 PPT 时，应以本目录四页替换旧完整稿中的 S2–S5；在用户明确发出合并指令之前，不自动改写完整稿，也不把其他页面并入本目录。

S0、S1、S6–S13 保持在各自候选/工作版本中；本轮不处理它们。旧 v1/v2/v2.1 文件保留，不删除、不覆盖。

来源完整稿当前仍有未提交工作副本修改；本轮只推送本正式四页版本和索引，不推送完整稿工作副本本身。

## 制作源

- [抽取源](制作源/extract_current_s2s5.py)：只做 OPC 页面/备注抽取、关系重映射与文档属性更新，不重绘页面。
- [实际渲染检查](制作源/render_check.py)：使用 Microsoft PowerPoint 16.0 打开来源和正式版，导出 PDF/PNG，核对备注、边界、字体和渲染一致性。
- [交付收尾](制作源/finalize_delivery.py)：核对来源字节、生成登记和交付清单。
