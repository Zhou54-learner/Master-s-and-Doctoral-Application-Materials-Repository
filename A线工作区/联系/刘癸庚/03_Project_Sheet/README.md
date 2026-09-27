# Thesis Project Sheet v1 — editable sources

**最新精修候选（2026-09-27）：** [v4一页PDF](output_v4_CANDIDATE/周子靖_毕设项目页_刘癸庚版_v4_CANDIDATE.pdf)、[v4文字](周子靖_毕设项目页_刘癸庚版_v4_CANDIDATE.md)、[来源、可编辑源与验收](source/v4/README.md)。面向PI初次联系重排，结果口径移至图注，结尾改为方向联系；以最终掩码和参数绘制的结构示意替换显示不清的CST截图。未重新运行CST，原截图显示原因未确诊。v3以下为对照候选，均未发送。

**当前审查候选（2026-09-27）：** [v3一页PDF](output_v3_CANDIDATE/周子靖_毕设项目页_刘癸庚版_v3_CANDIDATE.pdf)、[v3文字](周子靖_毕设项目页_刘癸庚版_v3_CANDIDATE.md)、[v3排版源](source/build_project_sheet_v3_candidate.py)。沿用既有结构图、曲线PDF和工作流，仅更新文字与图注，独立输出至`output_v3_CANDIDATE`；待本人审查，未发送。下面v1为对照及来源记录；不得运行旧脚本覆盖新版，v3脚本也拒绝覆盖已有候选PDF。

[一页PDF](output/周子靖_毕设项目页_刘癸庚版_v1_INTERNAL.pdf) · [300dpi预览](output/周子靖_毕设项目页_刘癸庚版_v1_INTERNAL.png) · [Markdown内容源](周子靖_毕设项目页_刘癸庚版_v1_INTERNAL.md)

可编辑源：[页面排版Python](source/build_project_sheet.py)、[曲线Matplotlib源](source/plot_reflection.py)、[工作流SVG](source/workflow.svg)。文字保留中文文本，曲线/箭头/文字在PDF中为矢量；CST结构原图是唯一有意使用的栅格面板。[figure-plan](source/figure-plan.md)记录阅读顺序和证据类型。内容Markdown便于审稿；若改正文需同步页面脚本的对应文字后再导出，不声称只改Markdown会自动改PDF。

来源：structure_original.png逐字节复制自终稿的fig6_2_final_3d_model.png；已对照72页论文第6.2节及图6.2。reflection_archived.tsv和result_archived.txt来自原保存的最终multitemplate结果目录，哈希及精确源路径见[复制清单](../04_Background_Notes/本地复制与基线哈希_v1.json)。图不重建几何，曲线不平滑、不补点、不运行求解器。原代码/论文与运行版本的精确对应仍存在Defense记录中的断链，图示不掩盖这一点。

Windows PowerShell本机复现命令（先曲线、再页面；只写输出目录）：

```powershell
& 'E:/CodexData/profile/.codex/runtimes/academic-figure-py311/Scripts/python.exe' 'F:/1A硕博申请/A线工作区/联系/刘癸庚/03_Project_Sheet/source/plot_reflection.py' --output-dir 'F:/1A硕博申请/A线工作区/联系/刘癸庚/03_Project_Sheet/qa_regenerated'
& 'E:/CodexData/profile/cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'F:/1A硕博申请/A线工作区/联系/刘癸庚/03_Project_Sheet/source/build_project_sheet.py' --output-dir 'F:/1A硕博申请/A线工作区/联系/刘癸庚/03_Project_Sheet/qa_regenerated'
```

依赖：第一步NumPy/Matplotlib，第二步ReportLab、PyMuPDF（本地`A线工作区/核验/a4_runtime`）；字体`C:/Windows/Fonts/SourceHanSansCNRegular.ttf`和`SourceHanSansCNBold.ttf`、Arial。运行版本与校验见[文件验收](../05_Send_Readiness/文件验收_v1.md)。无需LaTeX、MATLAB或CST。

| QA | 结果与边界 |
|---|---|
| Scientific fidelity | 旧数据直绘、真实结构图；同模反射/总吸收边界明确。未新增科研验证 |
| Visual | 已查看整页PDF渲染；标题、两个面板、循环箭头和正文均可读，无重叠 |
| SVG/PDF | 流程SVG、曲线SVG静态检查和一页PDF检查见验收记录；允许一个原始栅格面板 |
| Reproducibility | 在独立qa_regenerated目录重建后比较渲染像素，不以PDF时间戳造成的字节差异判失败 |

当前版本保留INTERNAL页脚，供人工审查。后续生成新版本后才按项目规则归档被替代版本，不覆盖原科研材料。
