# 项目页v5：经验与学习意愿

2026-09-28｜待本人审查；状态仅记在内部索引，PDF不带内部标记

[PDF](../../output_v5/周子靖_毕设项目页_刘癸庚版_v5.pdf) · [预览](../../output_v5/周子靖_毕设项目页_刘癸庚版_v5.png) · [文字](../../周子靖_毕设项目页_刘癸庚版_v5.md) · [图文计划](figure-plan.md)

本轮将末节改为“研究经验与进一步学习”，不再预定复杂波体系及几何/损耗分布课题；删除页脚候选标记。主体科研内容、原始数据、结构图及曲线原样保留。

生成入口为[build_page.py](build_page.py)，复用v4输出目录中的geometry.pdf与reflection.pdf；两幅面板的可编辑SVG、源代码及数据仍在[v4来源说明](../v4/README.md)。这是明确的数据依赖，不复制一份新的事实母版。旧CST截图问题未重诊断；新图继续标为结构示意。未运行任何科研求解器。

复建（项目根目录；输出目录应为空）：

```powershell
& 'E:/CodexData/profile/cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'A线工作区/联系/刘癸庚/03_Project_Sheet/source/v5/build_page.py' --output-dir "$env:TEMP/liu-project-v5-review"
```

依赖：既有ReportLab、PyMuPDF、Source Han Sans CN字体，以及v4两幅矢量PDF。输出一页A4全矢量PDF及300dpi PNG。

QA：正文边界通过、无图片XObject、无候选/内部字样；已查看整页，无截断或遮挡；另一个空目录复建后渲染像素一致。科学数据和面板未修改，既有数据核验继续适用。状态仍为待本人审查，不把排版通过等同于本人最终认可。
