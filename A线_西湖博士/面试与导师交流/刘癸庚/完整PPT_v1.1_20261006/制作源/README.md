# v1.1 制作与复核

本轮使用已安装的 Python、python-pptx、lxml、Pillow、pywin32、PyMuPDF 和 Microsoft PowerPoint 16.0，未安装依赖。具体版本见 `运行环境.json`。

1. `build_v1_1.py` 从指定、哈希锁定的本人微调 v1 复制包，只编辑 S12/S13 的页面和备注四个 XML 部件。已有交付 PPTX 时拒绝覆盖；后续修订另建版本目录。
2. `render_v1_1.py` 只读打开 PPTX，以真实 PowerPoint 导出 PDF、全页 PNG，核对备注、溢出、越界及未改页面的像素一致性，生成审阅图与 HTML。
3. `finalize_v1_1.py` 核对用户指定文案、v5 备注、文件保全与导出尺寸，并写出交付报告、映射与文件清单。

上述脚本保留为本轮制作记录。不得对本人后续编辑的 PPTX 直接运行生成脚本；复现应在新的工作副本中进行。用 `python -B` 运行可避免产生缓存文件。
