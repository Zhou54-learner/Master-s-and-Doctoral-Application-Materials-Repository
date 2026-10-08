# Floquet 端口专项核验证据包

核验日期：2026-10-06（北京时间）
对应报告：[本科毕设_Floquet端口_偏振_衍射通道专项核验_20261006.md](../本科毕设_Floquet端口_偏振_衍射通道专项核验_20261006.md)

## 用途与边界

本目录保存本轮对已存在 CST 工程、历史结果、配套代码和官方帮助的只读导出与算术核对结果。它支持报告中标记为“已从工程直接验证”“由公式计算”和“合理物理解释”的结论；它不把本轮分析升级为历史本科阶段已经完成的工作，也不证明模型、网格或端口截断已经独立收敛。

原始 `.cst` 工程、伴随目录、PPT 和历史结果未在本轮修改。读取使用了工程副本；没有运行优化器、求解器、History 重建或保存操作。目录中的 Python 文件是复查脚本和导出脚本，默认只对副本或已导出的文本工作，运行前仍需检查脚本参数和路径。

## 复查顺序

1. 先读报告结论、证据等级和 UNKNOWN 边界。
2. 用 `parameters.json`、`history_selected.bas.txt`、`solver_original.log.txt` 和 `history_port_and_solver.json`核对边界、端口和激励设置。
3. 用 `port_mode_metadata.json`、`port_field_selection.json` 与 `port_Zmax_*` / `ga_winner/*` 场样本核对 TE/TM 到全局 x/y 分量的映射。
4. 用四份 `1D_Results_S-Parameters_SZmax(i),Zmax(j).csv`、`run_ids_comparison.json` 和 `saved_results_analysis.json`复核矩阵、频带与功率闭合。
5. 用 `native_result_tree.json`、`cst_full_tree.json`、`native_results_export.json` 和 `floquet_readback.txt`区分结果树、候选模式列表与实际 considered 模式数。
6. 用 `ga_winner/summary.json`、四份 `S*.csv`、`ga_winner_trace_excerpt.json` 和 `ga_code_numbered_excerpt.txt`复核 GA 获选临时工程、201 点曲线和 fitness 读取路径。

## 文件分组

- **工程设置与原生读回**：`parameters.json`、`history_selected.bas.txt`、`history_port_and_solver.json`、`solver_original.log.txt`、`floquet_readback.bas.txt`、`floquet_readback.txt`、`port_mode_metadata.json`。
- **端口场与模式证据**：`port_field_selection.json`、`port_export_log.json`、`port_Zmax_In_*.txt`、`port_Zmax_Out_*.txt`，以及 `ga_winner/In_*.txt`。
- **保存结果导出**：四份 `1D_Results_S-Parameters_*.csv`、自适应曲线、Gamma、波阻抗、参考阻抗、功率与损耗 CSV。
- **结果树与交叉核对**：`native_result_tree.json`、`cst_full_tree.json`、`native_results_export.json`、`run_ids_comparison.json`、`saved_results_analysis.json`。
- **GA 归属核验**：`ga_winner/`、`ga_winner_trace_excerpt.json`、`ga_code_numbered_excerpt.txt`。
- **来源与保全**：`source_manifest_before.json`、`source_preservation_check.json`、`ga_winner/source_manifest_before.json`、`software_documentation_sources.json`、`ppt_reference.json`。
- **复查脚本**：`floquet_audit_20261006.py`、`analyze_saved_results_20261006.py`、`audit_ga_winner_20261006.py`、`export_port_fields_20261006.py`。脚本只作实现记录，不是运行原件的授权。

## 证据解读限制

- `Sij` 采用第一索引为输出、第二索引为入射；四项曲线都属于同一 Zmax 端口的两个模式，不是上下两个空间端口。
- `22.813693 GHz` 及更高阶 cutoff 是由已核参数代入 Floquet 公式得到的数值，不是 CST 对未 considered 模式的直接数值读回。
- `GetNumberOfModes=18` 与 `GetNumberOfModesConsidered=2` 必须分开理解；候选列表不等于高阶模式已经参与求解或有保存 S 参数。
- `ga_winner` 是 GA 获选临时工程的独立证据子集；后期最终工程的结果另存于上层 CSV，二者不能混作同一条收敛曲线。
- 本目录不包含原始工程副本，也不替代来源保全清单中的路径、大小和 SHA-256 记录。
