# 毕设代码来源与版本关系

2026-09-26｜DEFENSE｜仅静态定位。代码未执行、未修改；以下是待本人核对的版本地图，不是逐行作者鉴定。

## 目前可以连接的链条

| 层次 | 文件或证据 | 当前判断 |
|---|---|---|
| 原始框架交付 | 本人此前确认导师给课题，学长给结构、参考代码与CST环境 | 尚未找到可单独确认为“学长首次交付且未改”的完整文件；不把最短脚本自动当原版 |
| 参考代码痕迹 | `code01-05存档.txt`第48行、`run_optimizer.py`第68行及多份脚本中的“学长原版 Type()/gaoshang()/newc()”注释 | 支持继承框架的线索；注释不能证明整文件作者或相关函数从未再修改 |
| 早期研究存档 | `code01-05存档.txt`、`code06-07存档.txt`、`code09存档.txt`、条带/工字/拓扑TXT、`run_optimizer.py`、`code_run_v2.py` | 全保留；具体先后关系和个人修改点待确认。TXT包含代码，不只算普通数据 |
| 分阶段/分支版本 | 6×6、9×9、12×12 template/hybrid/hf/multitemplate/fixed/quarter-symmetric等PY | 代码和同名输出目录提供分支关系线索，不仅按文件名排成唯一线性版本史 |
| 最终论文取证脚本 | `ohmic_sheet_12x12_multitemplate_topology_ga_code.py` | F代码与E终稿所附同名代码字节一致，SHA-256为`844421f6c9f68f9eb4698991afb3c895e139e979f0b3bb6ae4496d435a81ce72`。此为当前最可信论文配套脚本，不等于已证明它正是某次求解时的字节版本 |
| 最终结果存档 | `最终结果ohmic_sheet_12x12_multitemplate_topology_ga`中的best_result、best_s11、mask、ga_log、individual_trace和CST工程 | 保存输出与既有论文核验关联；缺运行时源码哈希/版本提交记录，不能制造精确run provenance |
| 后续尝试 | fixed_topology_lf_refine、quarter_symmetric等 | 源码包含此前multitemplate层次，不据此称其结果优于论文版或替代论文基准 |

快捷位置：[全部代码](../仿真代码/来源待确认/原始工程/code)、[最终输出](../仿真结果/原始工程/最终结果ohmic_sheet_12x12_multitemplate_topology_ga)、[模型](../仿真模型/原始工程/最终结果ohmic_sheet_12x12_multitemplate_topology_ga)、[E终稿材料](../原始文档/毕业设计原件/结题/终稿)。

## 版本关系的证据强度

- `code拓扑12.89最终存档.txt`与`临时代码文件.txt`同SHA-256，为字节相同副本；两个文件名均保留。
- 12×12长脚本多次重定义函数及SAVE_PATH。multitemplate脚本的路径赋值依次出现在第27、2360、3340、4272行。不能只看文件开头就决定实际输出目录；详见[静态定位JSON](../../来源记录/Thesis_Code_Static_Map.json)。
- 静态路径指向`ohmic_sheet_12x12_multitemplate_topology_ga`，已有取证结果位于带“最终结果”前缀的目录。归档/改名过程及确切运行版本尚无日志证明，不人为补一条确定因果箭头。
- 当前论文取证PDF为终稿中的“...-物理学院.pdf”，与“...-物理学院-孟庆鑫.pdf”同哈希；其他PDF/Word及FQW版均保留，不按“终稿”字样删除其他版本。论文封面登记导师与实际科研指导的区别沿用事实基准。

## 分类与隔离

`02_Python_Code/Origin_Unresolved`保存原位置既存脚本；目录名明确其作者划分尚未完成。`07_Reference_Code`只放参考来源索引，`08_User_Modified_To_Confirm`只放待确认说明；目前不将混合继承脚本整份标成REFERENCE或USER_MODIFIED。

以后如取得学长初始包，可单独复制到REFERENCE；具体本人改动需以源版本、差异及本人确认连接，不以AI生成文本或文件mtime替代。AI辅助的具体段落及调试案例目前没有可靠逐段记录。

## 环境和执行断链

脚本显式依赖NumPy、Matplotlib、CST Python接口，记录的库路径`F:/CST Studio Suite 2025/AMD64/python_cst_libraries`本轮确认存在；未启动软件或验证许可证、接口兼容性、Python版本及依赖锁。源码含创建CST环境、自动求解及清理/写入逻辑，**只读副本并不能阻止运行后按硬编码路径写回原目录**。后续训练先静态阅读；需要执行时必须另建隔离副本并检查路径，不能直接运行归档代码。

`base.txt`引用的`branch1_surface_ohmic_sheet_comparison_code_v6.py`未在已知目录找到；对照输出及两份CST仍在。脚本提示的`ohmic_sheet_material_history.txt`也未找到。不能据输出存在宣称工作流所有依赖已齐全。
