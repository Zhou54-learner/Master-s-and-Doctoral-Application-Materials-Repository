# Source Manifest — 来源与复制总清单

2026-09-26｜DEFENSE｜本地归档，不外发。仅复制/容器成员提取/索引；原文件未移动、改名、覆盖或删除。

覆盖 **605423 个不同原始路径**；其中F毕设源目录 **604,870个文件**（11.282 GiB），保存为20个分目录ZIP快照（含一个空目录包）。另有3677份便于直接打开的文件副本，以及48个稿件原嵌入媒体对象。便利副本与ZIP中的同源文件不重复计科研资产。

## 怎么查任一文件

- [松散副本逐文件表](98_Archive_Records/Loose_Files.csv)：名称、类型、原绝对路径、副本相对路径、项目、分类、原件/整理稿、版本、成功状态、大小、mtime、SHA-256。
- F完整工程按下表对应CSV逐文件登记；`archive.zip::member`表示ZIP内的完整副本位置，`accessible_copy`表示另有可直接打开的便利副本。每个内部文件都登记，不以一个总路径替代清单。
- [原ZIP成员目录](98_Archive_Records/Original_Zip_Members.csv)与[F原图包成员目录](98_Archive_Records/F_Original_Zip_Members.csv)：保留原包，成员单列，不把压缩成员重复算松散文件。旧ZIP名称乱码保留原值，候选GBK显示名只用于导航。
- [稿件媒体逐对象表](98_Archive_Records/Embedded_Media.csv)：来源为`原DOCX::word/media/...`，复制字节未更改。
- [两份Office锁文件线索](98_Archive_Records/Lockfile_Clues.csv)：已复制，但不是PPT/验收书正文；真实正文仍缺，另见TODO。
- [复制校验](98_Archive_Records/Copy_Verification.json)、[统计口径](98_Archive_Records/Summary.json)、[原20件不变核验](98_Archive_Records/Original_20_Verification.json)、[版本与重复关系](98_Archive_Records/Version_Relations.json)。

## 源范围与最可信版本

| 资料组 | 原入口 | 副本入口/当前基准 | 完整性与版本判断 |
|---|---|---|---|
| 毕设文档 | `E:/360MoveData/Users/zzj/OneDrive/桌面/毕业设计` | `01_Thesis_Microwave_Absorber/00_Original_Documents/E_毕业设计` | 131文件全复制；保留开题/中期/各终稿/模板/锁文件，不按mtime定稿。取证PDF为终稿“...-物理学院.pdf”，SHA-256见下文 |
| 毕设仿真全部资产 | `F:/biyesheji` | 下表ZIP完整快照；代码/模型/导出另有便利副本 | 604870文件全部纳入；临时求解结果未删除。原空目录保留快照标记，不声称目录名就是一次完整成功求解 |
| 晶格波代码 | `E:/2024/yxy组代码` | `02_Dusty_Plasma/01_MATLAB_Code/E_yxy组代码` | 33文件全复制；25份松散MATLAB源码/Live Script、3个代码ZIP、Excel及说明/图件；未确认唯一最终版 |
| 晶格波输出 | `E:/2024/data figure`及相邻`data figure.zip` | `02_Dusty_Plasma/03_Figures`与`04_Original_Archives` | 331文件及外层ZIP全复制；119 FIG、164 JPG、40 SVG、1 PNG、7 ZIP；输出图不是完整独立原始时序数据集 |
| 晶格波正式论文 | `F:/1A硕博申请/个人资料/论文2.pdf` | `02_Dusty_Plasma/00_Paper/论文2.pdf` | 出版信息优先此正式PDF；具体图的个人贡献另核 |
| 材料论文和项目 | 申请目录论文1/证书/截图；已知桌面稿件；毕设终稿验收书；`E:/2024/大创` | `03_Absorbing_Materials_Project` | 正式出版信息优先论文1；DOCX修订稿和年会稿为历史版本，非新的正式发表；缺独立测量数据/个人处理工程 |
| 申请基准 | 项目CV/事实审计/旧总表及画像记录 | `00_Application_Claims` | Master v1.1冻结基线；v1.2为候选；旧英文不自动变为当前版；APPLICATION不是科研原始记录 |

## 分类规则

- **ORIGINAL**：从既有科研资料入口原样取得的文件/输出，说明档案来源，不代表本人原创、独立制作或已验证科学正确性；具体生成时间/后期修订若不确定标unconfirmed。
- **REFERENCE**：可辨认的外部参考论文/模板；最初学长交付代码包仍未确定。
- **USER_MODIFIED**：需要前后版本与本人确认才能落实到具体文件；本轮不将所有混合代码强行贴此标签。
- **APPLICATION**：申请阶段CV、审计、画像、贡献底稿、PI分析等；其“原始路径”只是这份申请文档的来源。
- **DEFENSE**：本轮新建的地图、TODO、manifest、校验表和归档工具。它们不是科研时期的记录。
- **ORIGINAL_CONTAINER_MEMBER**：从历史稿件取出的原媒体字节；不新画、不改图，归属/图号未自动确认。

## 当前可信版本与缺失原件

毕设取证PDF（`...-物理学院.pdf`及`...-物理学院-孟庆鑫.pdf`）SHA-256：`3e630eba9001bfed451efba271af1c2af6a97534a3f21c45fc3b04c8888f77fd`。配套multitemplate代码SHA-256：`844421f6c9f68f9eb4698991afb3c895e139e979f0b3bb6ae4496d435a81ce72`。以既有核验及原字节相同关系选为阅读基准，不凭“最终版”文件名推断所有结果。

最初参考代码包、两份被引用但缺失的文件、精确运行环境、晶格波完整时序/最终交付对应、材料项目个人源数据和贡献对应详见[缺件表](99_Missing_or_To_Confirm/00_Gaps_and_TODO.md)。现存条目的`missing_original=no`只表示该源文件本轮可读，不表示整个项目无缺件。

## F源完整快照与逐文件索引

| 原子目录/文件 | 文件数 | 源字节量 | 完整副本 | 每文件manifest |
|---|---:|---:|---|---|
| `F:/biyesheji/best_design` | 62 | 2,231,564 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/best_design.zip) | [CSV](98_Archive_Records/F_biyesheji_best_design.csv) |
| `F:/biyesheji/branch1_surface_ohmic_sheet_comparison_v6` | 11 | 538,794 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/branch1_surface_ohmic_sheet_comparison_v6.zip) | [CSV](98_Archive_Records/F_biyesheji_branch1_surface_ohmic_sheet_comparison_v6.csv) |
| `F:/biyesheji/code` | 22 | 2,043,060 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/code.zip) | [CSV](98_Archive_Records/F_biyesheji_code.csv) |
| `F:/biyesheji/error_log.txt` | 1 | 6,829 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/_root_error_log.txt.zip) | [CSV](98_Archive_Records/F_biyesheji__root_error_log.txt.csv) |
| `F:/biyesheji/ohmic_sheet_12x12_coverage85_ga` | 9,532 | 204,449,908 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/ohmic_sheet_12x12_coverage85_ga.zip) | [CSV](98_Archive_Records/F_biyesheji_ohmic_sheet_12x12_coverage85_ga.csv) |
| `F:/biyesheji/ohmic_sheet_12x12_fixed_topology_lf_refine` | 20,507 | 465,863,582 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/ohmic_sheet_12x12_fixed_topology_lf_refine.zip) | [CSV](98_Archive_Records/F_biyesheji_ohmic_sheet_12x12_fixed_topology_lf_refine.csv) |
| `F:/biyesheji/ohmic_sheet_12x12_hf_compensation_ga` | 24,941 | 566,663,361 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/ohmic_sheet_12x12_hf_compensation_ga.zip) | [CSV](98_Archive_Records/F_biyesheji_ohmic_sheet_12x12_hf_compensation_ga.csv) |
| `F:/biyesheji/ohmic_sheet_12x12_hybrid_coverage85_ga` | 31,806 | 707,781,172 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/ohmic_sheet_12x12_hybrid_coverage85_ga.zip) | [CSV](98_Archive_Records/F_biyesheji_ohmic_sheet_12x12_hybrid_coverage85_ga.csv) |
| `F:/biyesheji/ohmic_sheet_12x12_multitemplate_topology_ga` | 0 | 0 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/ohmic_sheet_12x12_multitemplate_topology_ga.zip) | [CSV](98_Archive_Records/F_biyesheji_ohmic_sheet_12x12_multitemplate_topology_ga.csv) |
| `F:/biyesheji/ohmic_sheet_12x12_quarter_symmetric_ga` | 450 | 12,527,615 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/ohmic_sheet_12x12_quarter_symmetric_ga.zip) | [CSV](98_Archive_Records/F_biyesheji_ohmic_sheet_12x12_quarter_symmetric_ga.csv) |
| `F:/biyesheji/ohmic_sheet_12x12_template_coverage85_ga` | 8,696 | 226,080,229 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/ohmic_sheet_12x12_template_coverage85_ga.zip) | [CSV](98_Archive_Records/F_biyesheji_ohmic_sheet_12x12_template_coverage85_ga.csv) |
| `F:/biyesheji/ohmic_sheet_6x6_ga_stable` | 14,702 | 181,523,996 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/ohmic_sheet_6x6_ga_stable.zip) | [CSV](98_Archive_Records/F_biyesheji_ohmic_sheet_6x6_ga_stable.csv) |
| `F:/biyesheji/ohmic_sheet_9x9_best_122587_recheck` | 440 | 8,254,409 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/ohmic_sheet_9x9_best_122587_recheck.zip) | [CSV](98_Archive_Records/F_biyesheji_ohmic_sheet_9x9_best_122587_recheck.csv) |
| `F:/biyesheji/ohmic_sheet_9x9_fixed_ph_ga` | 10,964 | 174,735,687 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/ohmic_sheet_9x9_fixed_ph_ga.zip) | [CSV](98_Archive_Records/F_biyesheji_ohmic_sheet_9x9_fixed_ph_ga.csv) |
| `F:/biyesheji/ohmic_sheet_9x9_ph_micro_only_ga` | 7,659 | 128,550,363 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/ohmic_sheet_9x9_ph_micro_only_ga.zip) | [CSV](98_Archive_Records/F_biyesheji_ohmic_sheet_9x9_ph_micro_only_ga.csv) |
| `F:/biyesheji/report_figures` | 45 | 28,547,933 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/report_figures.zip) | [CSV](98_Archive_Records/F_biyesheji_report_figures.csv) |
| `F:/biyesheji/test` | 110 | 2,127,139 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/test.zip) | [CSV](98_Archive_Records/F_biyesheji_test.csv) |
| `F:/biyesheji/数据存档` | 1,360 | 62,858,495 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/数据存档.zip) | [CSV](98_Archive_Records/F_biyesheji_数据存档.csv) |
| `F:/biyesheji/最终结果ohmic_sheet_12x12_multitemplate_topology_ga` | 43,844 | 1,049,360,158 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/最终结果ohmic_sheet_12x12_multitemplate_topology_ga.zip) | [CSV](98_Archive_Records/F_biyesheji_最终结果ohmic_sheet_12x12_multitemplate_topology_ga.csv) |
| `F:/biyesheji/temp` | 429,718 | 8,290,154,245 | [ZIP](01_Thesis_Microwave_Absorber/80_Full_Source_Snapshot/temp.zip) | [CSV](98_Archive_Records/F_biyesheji_temp.csv) |

## 验收和使用

所有松散副本SHA-256与读取源字节一致，并二次校验；ZIP全部成员CRC已检验，每个源成员另记SHA-256，各ZIP另记整包SHA-256。读取复制前后检查源文件大小/mtime稳定。原20件与接手清单SHA-256一致。只读属性加在副本及ZIP上，源文件属性未改。

科研代码保留了原绝对路径与历史行为，即使副本只读，运行仍可能向原科研目录写入。因此本工作区当前用于静态阅读；各项目`90_Defense_Workspace`用于新训练笔记，后续如需运行应另做隔离，不直接执行原代码。

本轮搜索限于项目目录、四个已知科研入口及其已查看父目录中的同主题候选；没有全盘搜索、云端上传、外部发信或后台监控。归档工具是本次实现记录，独占创建文件，非可反复覆盖运行的入口。

副本内历史Markdown链接保持原字节，需按本manifest原路径解释。新建DEFENSE导航链接另行校验。完整快照服务版本追溯，不保证所有源工程都可运行。
