# 07 · 交付检查与任务审查结论

2026-09-27｜INTERNAL｜**材料已准备 / 待本人学习**

本页为 **INTERPRETATION（助理执行与检查记录）**，不是本人学习证明。

## PR #2 审查结论

任务设计没有明显阻碍执行的问题：范围集中于邮件点名的一篇论文，产物和时间预算明确，也禁止代发、复现与代认定掌握。实际执行采用三项限定：

1. 将“损耗配置→复谱绕行→NHSE→局域化”作为需要用具体结构与图证明的链条，不作普遍公理；增加均匀标量损耗反例。
2. 以2024正式主文为主，不混用2023预印本的实验处理说明。
3. Supplemental Material访问受限就留下明确缺口；正文转引补图不等于已读补图。

任务原文v1保留作依据，以上限定落实在实际学习包中；未改写既有邮件。新增Checklist v3，原v2仍为既有投递包报告/claim映射所用，保留原路径以便追溯。没有覆盖或搬动科研原件。

## 交付范围

- 七项必需文档齐全；另有README、本文、来源日志/哈希清单。
- Fig.2–4提供原图注、逐面板解释、证据限制和自测问题；概念图提供可编辑SVG、PDF和300-dpi PNG。
- 14题问答、30秒/2分钟表达模板、15分钟口述评分表均已准备；评分记录为空。
- 同步Research Defense总索引、刘癸庚Checklist v3、投递包README及工作台。
- 正式主文与组官网说明已取得；SM未取得，**来源获取要求尚未全部完成**。

## 文件与证据检查

[机器检查记录](figures/qa/verification.json)记录本轮结果；[来源哈希](sources/source_manifest.json)与[获取日志](sources/acquisition_log.json)记录实际留存文件。检查包括新增材料及同步入口相对链接、PDF页数/文字层、原20件SHA-256；原20件均未改变。PI联系表、邮件、CV及项目页没有本轮内容改动。

来源日志中的失败请求不是已取得文件；manifest仅收录现存文件。提取的TXT是检索辅助，双栏排序可能错位；正式PDF及图像为准。预印本只作版本警示，不作为SM替身。

## 图件检查

| Gate | 状态 | 证据 |
|---|---|---|
| Scientific fidelity | PASS | Fig.2–4直接裁原页并保留图注；图号、方向、GHz坐标和计算/测量分类已对正文；概念图标为INTERPRETATION |
| Source completeness | WARN | S1未取得；未绘补图、未补造数值与实验参数 |
| Visual | PASS | 三张300-dpi原图裁剪与概念SVG渲染均逐张查看；无裁掉面板/图注、遮挡或缺字；PDF另渲染核对 |
| SVG structure | PASS | academic-figure的svg_check.py通过；27个文本节点、0张位图、无foreignObject |
| PDF | PASS | [pdf_checks.json](figures/qa/pdf_checks.json)；概念图无图像XObject；原图裁剪允许源论文自带位图资源，不冒称纯矢量数据图 |
| Reproducibility | PASS | [build_figures.py](figures/source/build_figures.py)记录页码与裁剪坐标；SVG为可编辑源，导出指令见下；重复生成不改原论文 |

生成环境：Python 3.11、PyMuPDF 1.28.2、Inkscape 1.4.4；PDF检查使用已有academic-figure运行时及pypdf。没有安装新依赖、运行CST或运行科研优化器。

在本包`figures`目录执行的命令（PowerShell）：

```powershell
python -B source/build_figures.py
& 'C:/Program Files/Inkscape/bin/inkscape.com' source/concept_map.svg --export-type=pdf --export-filename=output/concept_map.pdf
& 'C:/Program Files/Inkscape/bin/inkscape.com' source/concept_map.svg --export-type=png --export-dpi=300 --export-filename=output/concept_map.png
```

脚本通过仓库内既有`a4_runtime`读取PDF；它只生成本包图件，不触碰历史仿真输出。SVG中的示意箭头是概念关系，不是数值时间演化。

## 仍需用户学习 / 未声称

完成首轮精读、图解复盘与本人口述；另需合法取得正式SM后补核材料参数、拓扑算法、阵列幅相和局部缺陷对照。不得将材料准备解释为本人已读、已掌握或面试READY。本轮未发送、未改变PI联系状态、未做完整课程、未复现论文；2026-09-27 经用户授权，PR #2已合并（`9ebc659`），本地已切回main同步；以上学习和来源边界不变。
