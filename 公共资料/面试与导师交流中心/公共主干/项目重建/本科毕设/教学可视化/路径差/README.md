# 两条传播路径的路程差

2026-10-03｜一般教学可视化；未运行CST、GA或毕设历史脚本，不属于R2/R3项目复现。

打开 `output/index.html`，先点击0°、45°、80°、90°，再拖动观察距离。蓝线AP，橙线BP；观察点始终为同一个P。所有长度以固定单元间距p为单位。静态图使用D=3p，明确展示有限距离精确值；p sinθ仅标为远处近似。中垂线严格等长，路径差上限来自三角不等式。

## 文件

- `output/index.html`：单文件离线交互图，原生SVG，不依赖网络。
- `output/figure.svg`、`output/figure.pdf`：三种观察方向的矢量图。
- `output/figure.png`：300 dpi静态预览。
- `source/build.py`：标准库Python生成源；`source/figure.svg`：可编辑SVG。
- `source/figure-plan.md`：图计划与模型假设。
- `source/check-browser.cjs`：交互检查；浏览器依赖路径对应本机现有运行时。

## 重新生成

在本目录运行 `python source/build.py`，会重建SVG、HTML及几何检查记录。PDF/PNG通过已安装Inkscape导出：

```powershell
& 'C:/Program Files/Inkscape/bin/inkscape.exe' 'output/figure.svg' --export-type=pdf --export-filename='output/figure.pdf'
& 'C:/Program Files/Inkscape/bin/inkscape.exe' 'output/figure.svg' --export-type=png --export-dpi=300 --export-filename='output/figure.png'
node source/check-browser.cjs
```

生成依赖：Python 3.11标准库。导出依赖：Inkscape与Microsoft YaHei字体。交互：现代浏览器。QA：本机Edge及已存在的Playwright运行时。

## QA

| 项目 | 状态 | 证据 |
|---|---|---|
| 几何 | PASS | 0..90°与D/p=2,3,10,30,100的上限、单调性、端点检查；远处近似误差随距离减小 |
| SVG | PASS | svg_check.py；文本保留、无外部资源、无嵌入位图 |
| PDF | PASS | 单页矢量PDF，零图像对象；渲染后人工查看 |
| 视觉 | PASS | 修复初版标签间距；最终静态、交互桌面与移动预览均已查看 |
| 交互 | PASS | 0/45/80/90°按钮、距离滑杆、D/p=30远场比较、390px视窗无横向溢出、无JavaScript异常 |
| 重建 | PASS | 修改标签后已重新运行生成与导出，重新验证 |

数值只描述明确给定的几何；不是实测值或毕设电磁性能。90°表示沿阵列表面方向，不据此声称存在非零法向出射功率。
