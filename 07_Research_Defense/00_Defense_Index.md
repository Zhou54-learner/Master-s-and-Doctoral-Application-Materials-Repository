# Research Defense 地图

2026-09-26 建档｜DEFENSE｜本地内部工作区。本轮仅整理，不表示已完成技术训练、复现或贡献鉴定。

## 打开后从这里进入

1. [申请 claim 与版本边界](00_Application_Claims/00_Claims_Readme.md)：先确认当前 CV 究竟写了什么。
2. [毕设代码来源与版本关系](01_Thesis_Microwave_Absorber/90_Defense_Workspace/01_Code_Ownership_and_Versions.md)：明天建议先从这里开始。
3. [缺件与断链](99_Missing_or_To_Confirm/00_Gaps_and_TODO.md)：区分缺文件、缺贡献证明和待理解事项。
4. [来源总清单](00_Source_Manifest.md)：每份副本可追溯到原路径；详细文件表在 `98_Archive_Records`。

## A. 电阻膜微波吸收结构的仿真与优化

| 项目项 | 当前材料地图 |
|---|---|
| 时间 | 毕设2026.05完成；不由文件时间推定研究起始月 |
| CV claim | 使用并扩展 Python-CST 参数化电磁仿真与遗传算法优化流程；扩展几何、图案与双向片阻变量，构建分阶段搜索及几何约束筛选；比较薄实体膜与 Ohmic Sheet，处理和可视化结果。原文见申请claim索引 |
| 原始入口 | `F:/biyesheji`；`E:/360MoveData/Users/zzj/OneDrive/桌面/毕业设计` |
| 文档副本 | [完整毕业设计文档树](01_Thesis_Microwave_Absorber/00_Original_Documents/E_毕业设计)：开题、中期、结题、论文历版、终稿PDF/Word、答辩PPT/PDF、讲稿、参考论文均保留 |
| 代码/模型/输出 | [Python与TXT脚本](01_Thesis_Microwave_Absorber/02_Python_Code/Origin_Unresolved/F_biyesheji/code)；[CST模型](01_Thesis_Microwave_Absorber/03_CST_Models)；[原保存导出](01_Thesis_Microwave_Absorber/04_Raw_and_Processed_Exports)；[图件](01_Thesis_Microwave_Absorber/06_Figures)；[完整工程快照](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot) |
| 完整程度 | 两个已知源目录中的文件均纳入快照；核心论文—脚本—模型—结果链已具备。首次参考交付包、部分被命令记录引用的脚本和精确运行环境仍缺 |
| 本人贡献 | 以既有框架为基础修改脚本、扩展变量、调整搜索/筛选、处理结果；本人此前确认使用在线资料及AI辅助。导师/学长提供初始课题、结构、参考代码与CST环境 |
| 后续复习领域 | 周期边界与频域求解；片阻/薄实体膜假设；编码、目标函数与筛选；S参数与功率；文件读写及版本覆盖 |
| 风险 | 文件功能不等于本人独立实现；13.20 GHz为同模反射采样带宽，82.5%为频窗覆盖比例；全端口功率及收敛待核；运行脚本中的绝对路径会写回历史科研目录 |
| 训练入口 | 先对照当前CV三条与原文件，恢复“接手什么→改什么→运行哪版→保存什么”；然后选一条最终流程静态walkthrough。需重跑时另立授权与隔离方案，本次不重跑 |

## B. 二维尘埃等离子体晶格波

| 项目项 | 当前材料地图 |
|---|---|
| 时间 | 2025为论文发表年；个人参与起止未确认，不以文件时间替代 |
| CV claim | v1.2候选：使用MATLAB处理模拟数据、分析偏振特征；绘制粒子运动轨迹，输出用于合作论文的部分数据与图件。v1.1冻结版将贡献写在论文条目下 |
| 原始入口 | `E:/2024/yxy组代码`；`E:/2024/data figure`；相邻 `E:/2024/data figure.zip`；申请目录 `个人资料/论文2.pdf` |
| 副本入口 | [正式论文](02_Dusty_Plasma/00_Paper/论文2.pdf)；[源码原目录树](02_Dusty_Plasma/01_MATLAB_Code/E_yxy组代码)；[全部输出图](02_Dusty_Plasma/03_Figures/E_data_figure)；[外层原压缩包](02_Dusty_Plasma/04_Original_Archives) |
| 完整程度 | 已知两目录全复制，含MATLAB程序、历史ZIP、说明DOC、FIG/JPG/SVG及`李萨如图.xlsx`。未找到完整独立时序数据集/明确最终交付清单；FIG与Excel不能自动当成全部原始模拟数据 |
| 本人贡献 | MATLAB偏振相关处理、轨迹可视化、部分数据与图件；第六作者不证明全部理论和求解器归属 |
| 后续复习领域 | 数组索引与粒子位置；时窗、平衡位置与坐标；偏振轨迹；MATLAB依赖；数值积分实现与图号对应 |
| 风险 | 多版`xlg.m`不同；`set_axis_length`跨目录；取样位置/图标题和驱动参数存在版本差异；图12与具体输出未逐点溯源；哪些改动出自本人仍需确认 |
| 训练入口 | 从`代码（偏振）去前段/main.mlx`、同目录轨迹汇总JPG和论文图12建立文件对应，不预设该版本可重现整篇论文 |

## C. 磁纳米合金/石墨烯吸波材料论文及对应项目

| 项目项 | 当前材料地图 |
|---|---|
| 时间 | 正式论文2025；结题证书2024.12；个人参与起止待确认；不同题名项目的对应仍待核 |
| CV claim | 数据处理与可视化、部分论文图件制作及稿件撰写；未写主导实验或国家级已结题 |
| 原始入口 | 申请目录论文1及三份大创图像；毕业设计终稿中的培育验收书；已知桌面入口中的修改稿/论文版本；相邻`E:/2024/大创` |
| 副本入口 | [论文](03_Absorbing_Materials_Project/00_Paper)；[项目材料](03_Absorbing_Materials_Project/01_Project_Documents)；[稿件](03_Absorbing_Materials_Project/04_Manuscript)；[稿件内原嵌入图](03_Absorbing_Materials_Project/03_Figures) |
| 完整程度 | 正式论文、带修订批注的DOCX、项目证据和XMind已找到；个人数据处理源文件、独立原始测量数据及图号分工仍不完整 |
| 本人贡献 | 本人本轮及既有确认：数据处理、可视化、部分图件和稿件撰写，实验参与有限；验收书列“统计分析员”，不能扩大为全部实验 |
| 后续复习领域 | 数据到图的处理链、坐标/单位与比较条件、自己修改的文字和图号、实验团队分工 |
| 风险 | 修订作者账户不能直接映射本人；稿件图像不等于可重算数据；国家级截图、结题证书、培育验收书题名不同，不拼接为同编号国家级已结题 |
| 训练入口 | 先用正式论文+修订稿+验收书圈定具体图/文字的个人参与范围，再补数据入口；不把团队实验讲成本人主导 |

## 后续1–2天的建议顺序（未开始）

先毕设ownership与版本定位，再毕设单条工作流；随后晶格波数据—轨迹—论文图对应；最后材料项目的个人图件/文字贡献。物理复习、技术追问、讲述训练和PI模拟面试均留待用户下一步指令。原始副本只读，新笔记写入各项目的`90_Defense_Workspace`，不得覆盖快照。
