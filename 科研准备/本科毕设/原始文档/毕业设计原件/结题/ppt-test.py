"""
使用 python-pptx 生成毕业论文答辩 PPT
运行前请安装: pip install python-pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH, MSO_FILL
from pptx.enum.text import PP_ALIGN

# ==================== 颜色定义 ====================
DARK_BLUE = RGBColor(22, 52, 110)  # 主色调：深蓝
LIGHT_BLUE = RGBColor(41, 98, 177)  # 辅助蓝
GOLD = RGBColor(197, 160, 89)  # 点缀金
DARK_GRAY = RGBColor(51, 51, 51)
LIGHT_GRAY = RGBColor(245, 246, 250)
WHITE = RGBColor(255, 255, 255)
RED = RGBColor(180, 50, 50)
GREEN = RGBColor(40, 130, 80)

# ==================== 创建 PPT ====================
prs = Presentation()

# 设置幻灯片尺寸为 16:9
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)


# ==================== 辅助函数 ====================
def add_slide(layout_type=6):
    """添加空白幻灯片 (layout_type=6 为空白)"""
    slide_layout = prs.slide_layouts[layout_type]
    slide = prs.slides.add_slide(slide_layout)
    return slide


def add_title(slide, title_text, subtitle=None):
    """添加标题（左上角）"""
    left = Inches(0.7)
    top = Inches(0.5)
    width = Inches(10)
    height = Inches(1.2)

    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP

    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE
    p.font.name = "Arial"
    p.alignment = PP_ALIGN.LEFT

    if subtitle:
        p = tf.add_paragraph()
        p.text = subtitle
        p.font.size = Pt(18)
        p.font.bold = False
        p.font.color.rgb = DARK_GRAY
        p.font.name = "Arial"
        p.space_before = Pt(6)
        p.alignment = PP_ALIGN.LEFT

    # 加一条装饰线
    line = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT,
        left,
        top + height + Inches(0.05),
        left + Inches(6),
        top + height + Inches(0.05),
    )
    line.line.color.rgb = GOLD
    line.line.width = Pt(3)


def add_text_box(slide, text, left, top, width, height, font_size=16, color=DARK_GRAY, bold=False):
    """添加文本框"""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = "Arial"
    p.alignment = PP_ALIGN.LEFT
    tf.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
    return tb


def add_bullet_box(slide, items, left, top, width, height, font_size=16):
    """添加带项目符号的文本框"""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(font_size)
        p.font.color.rgb = DARK_GRAY
        p.font.name = "Arial"
        p.level = 0
        p.space_before = Pt(4)
    tf.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
    return tb


def add_figure_placeholder(slide, label, left, top, width, height):
    """添加图表占位框（带边框和标注）"""
    # 灰色背景
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    rect.fill.solid()
    rect.fill.fore_color.rgb = LIGHT_GRAY
    rect.line.color.rgb = DARK_BLUE
    rect.line.width = Pt(1.5)

    # 中间文字 "图 X"
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = label
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = DARK_GRAY
    p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    return rect, tb


def add_table_placeholder(slide, label, left, top, width, height):
    """添加表格占位框"""
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    rect.fill.solid()
    rect.fill.fore_color.rgb = LIGHT_GRAY
    rect.line.color.rgb = DARK_BLUE
    rect.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = label
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = DARK_GRAY
    p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    return rect, tb


def add_deco_line(slide, y_pos):
    """添加底部装饰线"""
    line = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT,
        Inches(0.5),
        y_pos,
        Inches(12.8),
        y_pos,
    )
    line.line.color.rgb = GOLD
    line.line.width = Pt(1.5)
    line.line.dash_style = MSO_LINE_DASH.ROUND_DOT


# ==================== 第 1 页：封面 ====================
slide = add_slide(6)

# 背景装饰 - 大色块
rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
rect.fill.solid()
rect.fill.fore_color.rgb = WHITE
rect.line.fill.background()

# 左上角装饰条
rect2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(2), Inches(7.5))
rect2.fill.solid()
rect2.fill.fore_color.rgb = DARK_BLUE
rect2.line.fill.background()

# 底部装饰条
rect3 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(6.8), Inches(13.333), Inches(0.7))
rect3.fill.solid()
rect3.fill.fore_color.rgb = DARK_BLUE
rect3.line.fill.background()

# 标题
tb = slide.shapes.add_textbox(Inches(3), Inches(2), Inches(8), Inches(1.5))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "基于电阻膜超材料的\n宽带微波吸收结构设计"
p.font.size = Pt(44)
p.font.bold = True
p.font.color.rgb = DARK_BLUE
p.font.name = "Arial"
p.alignment = PP_ALIGN.CENTER

# 副标题
tb2 = slide.shapes.add_textbox(Inches(3), Inches(3.8), Inches(8), Inches(0.8))
tf2 = tb2.text_frame
p2 = tf2.paragraphs[0]
p2.text = "本科毕业论文答辩"
p2.font.size = Pt(24)
p2.font.bold = False
p2.font.color.rgb = GOLD
p2.font.name = "Arial"
p2.alignment = PP_ALIGN.CENTER

# 个人信息
info = "汇报人：周子靖  学号：2022112550\n专业：应用物理学（中外合作）\n指导教师：孟庆鑫 教授\n哈尔滨工业大学 · 物理学院\n2026年5月"
tb3 = slide.shapes.add_textbox(Inches(3), Inches(5.2), Inches(8), Inches(1.5))
tf3 = tb3.text_frame
p3 = tf3.paragraphs[0]
p3.text = info
p3.font.size = Pt(18)
p3.font.bold = False
p3.font.color.rgb = DARK_GRAY
p3.font.name = "Arial"
p3.alignment = PP_ALIGN.CENTER

# ==================== 第 2 页：研究背景与需求 ====================
slide = add_slide(6)
add_title(slide, "研究背景与需求", "复杂电磁环境下的宽带微波吸收挑战")

# 左侧文本
bullet_items = [
    "  无线通信、雷达探测、电子对抗等技术快速发展，2-18 GHz（S/C/X/Ku波段）为典型工作频段",
    "  传统吸波材料存在“厚则重、薄则窄”的矛盾，难以同时满足宽带、轻薄需求",
    "  超材料通过亚波长人工结构调控等效电磁参数，为突破传统材料限制提供新途径",
    "  电阻膜超材料兼具轻质、可图案化、欧姆损耗特性，是宽带吸波结构的重要研究方向"
]
add_bullet_box(slide, bullet_items, Inches(0.8), Inches(2.2), Inches(6.5), Inches(3.5))

# 右侧图片占位
add_figure_placeholder(slide, "图2-2 金属背板吸波结构示意图", Inches(8), Inches(1.8), Inches(4.5), Inches(3.5))

add_deco_line(slide, Inches(6.8))

# ==================== 第 3 页：研究目标与技术路线 ====================
slide = add_slide(6)
add_title(slide, "研究目标与技术路线", "以连续有效带宽为核心指标")

# 目标框
tb = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(0.9))
tb.fill.solid()
tb.fill.fore_color.rgb = DARK_BLUE
tb.line.fill.background()
tb_tf = tb.text_frame
p = tb_tf.paragraphs[0]
p.text = "目标：设计基于电阻膜超材料的金属背板型吸波单元，2-18 GHz 内 RL < -10 dB"
p.font.size = Pt(20)
p.font.bold = True
p.font.color.rgb = WHITE
p.font.name = "Arial"
p.alignment = PP_ALIGN.CENTER

# 路线图 - 用5个形状表示
x_start = Inches(1.5)
y_start = Inches(3.2)
step_width = Inches(1.8)
step_height = Inches(0.9)
gap = Inches(0.3)

steps = [
    ("理论分析", "阻抗匹配与欧姆损耗机制"),
    ("建模对比", "薄实体膜 vs Ohmic Sheet"),
    ("算法构建", "CST-Python + 遗传算法"),
    ("分阶段优化", "6×6 → 9×9 → 12×12"),
    ("机理分析", "场分布与损耗机制")
]

for i, (title, sub) in enumerate(steps):
    x = x_start + i * (step_width + gap)
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y_start, step_width, step_height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = LIGHT_BLUE if i % 2 == 0 else DARK_BLUE
    shape.line.fill.background()

    tf = shape.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

    # 小箭头连接
    if i < 4:
        arrow_x = x + step_width + Inches(0.05)
        arrow_y = y_start + step_height / 2 - Inches(0.1)
        arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, arrow_x, arrow_y, Inches(0.2), Inches(0.2))
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = GOLD
        arrow.line.fill.background()

add_deco_line(slide, Inches(6.8))

# ==================== 第 4 页：结构设计与三维建模 ====================
slide = add_slide(6)
add_title(slide, "结构设计与三维建模", "双正交电阻膜吸波单元")

# 左侧文本
bullet_items = [
    "结构组成：金属背板 + 两片正交PET基底（0.188 mm）+ 单面图案化电阻膜",
    "关键设计：X/Y方向独立图案化，引入双通道调节能力",
    "CST模型：周期单元，周期性边界 + Floquet端口",
    "仿真频率：2-18 GHz，覆盖S/C/X/Ku波段",
    "主评价指标：连续有效带宽（RL < -10 dB）"
]
add_bullet_box(slide, bullet_items, Inches(0.8), Inches(2.2), Inches(6.0), Inches(3.5))

# 右图
add_figure_placeholder(slide, "图3-1 正交电阻膜吸波单元概念图", Inches(7.5), Inches(1.8), Inches(5.0), Inches(3.0))

add_deco_line(slide, Inches(6.8))

# ==================== 第 5 页：两种建模方法对比 ====================
slide = add_slide(6)
add_title(slide, "◆ 重点工作量：两种建模方法的对比与筛选", "薄实体膜模型 vs Ohmic Sheet 表面片阻模型")

# 左：对比表占位
add_table_placeholder(slide, "表3-4 两种模型特性对比", Inches(0.8), Inches(2.2), Inches(5.5), Inches(2.5))

# 右：曲线图占位
add_figure_placeholder(slide, "图3-4 两种模型反射损耗曲线对比", Inches(7.0), Inches(2.2), Inches(5.5), Inches(2.8))

# 底部结论
tb = slide.shapes.add_textbox(Inches(0.8), Inches(5.2), Inches(11.7), Inches(0.8))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "结论：Ohmic Sheet 模型更符合工程片阻材料表征，效率更高，适合高分辨率像素化拓扑优化"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = DARK_BLUE
p.font.name = "Arial"
p.alignment = PP_ALIGN.CENTER

add_deco_line(slide, Inches(6.8))

# ==================== 第 6 页：CST-Python联合仿真 ====================
slide = add_slide(6)
add_title(slide, "◆ 重点工作量：CST-Python 联合仿真与自建优化框架", "全自动闭环优化流程")

# 流程图占位 - 大图
add_figure_placeholder(slide, "图4-1 CST-Python联合仿真与遗传算法优化流程图", Inches(1.5), Inches(2.0), Inches(10.0), Inches(3.5))

# 底部关键点
bullet_items = [
    "Python控制脚本：生成参数 → 调用CST建模 → 求解 → 导出S11 → 计算RL → 评估适应度",
    "无需手动调参，实现全自动迭代优化"
]
add_bullet_box(slide, bullet_items, Inches(1.5), Inches(5.8), Inches(10.0), Inches(0.8))

add_deco_line(slide, Inches(6.8))

# ==================== 第 7 页：遗传算法编码 ====================
slide = add_slide(6)
add_title(slide, "◆ 重点工作量：遗传算法编码与遗传操作逻辑", "二进制矩阵编码 + 定制化适应度")

# 左：编码示意图占位
add_figure_placeholder(slide, "图2-6 二进制像素编码原理", Inches(0.8), Inches(2.2), Inches(5.5), Inches(3.5))

# 右：文本说明
bullet_items = [
    "编码方式：二进制矩阵（1=保留，0=去除）",
    "12×12图案：单面144位，双面共288位",
    "连续变量：p, h, Rs,x, Rs,y 实数编码",
    "适应度函数：以连续有效带宽为主要权重",
    "遗传操作：选择、交叉、变异、精英保留"
]
add_bullet_box(slide, bullet_items, Inches(7.0), Inches(2.2), Inches(5.5), Inches(3.5))

add_deco_line(slide, Inches(6.8))

# ==================== 第 8 页：分阶段优化策略 ====================
slide = add_slide(6)
add_title(slide, "◆ 重点工作量：分阶段拓扑优化策略", "从低分辨率到高分辨率的递进式搜索")

# 示意图占位
add_figure_placeholder(slide, "图4-3 设计空间层级扩展示意（6×6 → 9×9 → 12×12）", Inches(2.0), Inches(2.0), Inches(9.0), Inches(2.5))

# 下方三个阶段描述
stages = [
    ("6×6 预试验", "验证方法可行性，粗筛结构"),
    ("9×9 精细优化", "增加边缘/窗口，提升表达能力"),
    ("12×12 最终优化", "X/Y独立片阻 + 半约束多模板策略")
]

x_start = Inches(1.5)
y_start = Inches(5.0)
w = Inches(3.0)
h = Inches(0.8)

for i, (title, desc) in enumerate(stages):
    x = x_start + i * (w + Inches(0.5))
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y_start, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = DARK_BLUE if i == 2 else LIGHT_BLUE
    shape.line.fill.background()

    tf = shape.text_frame
    p = tf.paragraphs[0]
    p.text = f"{title}\n{desc}"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = "Arial"
    p.alignment = PP_ALIGN.CENTER

add_deco_line(slide, Inches(6.8))

# ==================== 第 9 页：各阶段结果对比 ====================
slide = add_slide(6)
add_title(slide, "各阶段结果对比", "有效带宽与覆盖率的逐步提升")

# 表格占位
add_table_placeholder(slide, "表5-2 各阶段优化结果对比", Inches(0.8), Inches(2.0), Inches(11.7), Inches(2.5))

# 下方柱状图占位
add_figure_placeholder(slide, "图5-11 有效带宽柱状图", Inches(0.8), Inches(5.0), Inches(5.5), Inches(1.8))
add_figure_placeholder(slide, "图5-12 覆盖率柱状图", Inches(7.0), Inches(5.0), Inches(5.5), Inches(1.8))

add_deco_line(slide, Inches(6.8))

# ==================== 第 10 页：最终结构展示 ====================
slide = add_slide(6)
add_title(slide, "最终结构展示", "12×12 半约束多模板优化结果")

# 左侧参数
params = [
    "周期 p = 13.1409 mm",
    "高度 h = 10.0731 mm",
    "X方向片阻 Rs,x = 140.79 Ω/sq",
    "Y方向片阻 Rs,y = 35.461 Ω/sq"
]
add_bullet_box(slide, params, Inches(0.8), Inches(2.0), Inches(4.5), Inches(2.5))

# 中间拓扑图
add_figure_placeholder(slide, "图6-1 最终X/Y方向像素拓扑", Inches(5.8), Inches(2.0), Inches(3.8), Inches(3.5))

# 右侧RL曲线
add_figure_placeholder(slide, "图5-8 最终结构反射损耗曲线", Inches(10.0), Inches(2.0), Inches(2.8), Inches(3.5))

add_deco_line(slide, Inches(6.8))

# ==================== 第 11 页：多物理场机理分析 ====================
slide = add_slide(6)
add_title(slide, "◆ 重点工作量：多物理场机理分析", "电场/磁场/损耗密度分布")

bullet_items = [
    "选择三个代表性频率：8.8 GHz（中低频）、12.0 GHz（过渡）、15.5 GHz（高频）",
    "电场分布：低频依赖大尺度连续路径 → 高频集中在局部边缘",
    "磁场分布：电阻膜与金属背板形成磁耦合环路，调节输入阻抗",
    "功率损耗密度：能量在边缘、窗口、通道区域转化为欧姆发热"
]
add_bullet_box(slide, bullet_items, Inches(0.8), Inches(2.2), Inches(6.5), Inches(3.5))

# 右侧三个小图占位
add_figure_placeholder(slide, "图6-3/6-4/6-5 电场分布", Inches(7.8), Inches(2.0), Inches(4.7), Inches(3.8))

add_deco_line(slide, Inches(6.8))

# ==================== 第 12 页：X/Y功能分工 ====================
slide = add_slide(6)
add_title(slide, "X/Y 功能分工与宽带吸收机制", "协同机制揭示")

# 左右分工
left_items = [
    "Y层（低阻 35.5 Ω/sq）：",
    "  • 主损耗通道",
    "  • 低频延伸骨架",
    "  • 连续电流路径"
]
add_bullet_box(slide, left_items, Inches(0.8), Inches(2.2), Inches(5.5), Inches(3.0))

right_items = [
    "X层（高阻 140.8 Ω/sq）：",
    "  • 阻抗调节",
    "  • 高频补偿",
    "  • 局部结构" 
]
add_bullet_box(slide, right_items, Inches(6.8), Inches(2.2), Inches(5.5), Inches(3.0))

# 底部机制总结
tb = slide.shapes.add_textbox(Inches(0.8), Inches(5.5), Inches(11.7), Inches(0.8))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "宽带吸收 = 透射抑制 + 正交耦合 + 多模连接 + 欧姆损耗"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = DARK_BLUE
p.font.name = "Arial"
p.alignment = PP_ALIGN.CENTER

add_deco_line(slide, Inches(6.8))

# ==================== 第 13 页：创新点与工作量总结 ====================
slide = add_slide(6)
add_title(slide, "创新点与工作量总结", "")

points = [
    "1. 结构创新：提出“双正交 + 独立片阻 + 差异化拓扑”结构，实现功能分工",
    "2. 方法创新：独立完成CST-Python联合仿真与遗传算法全流程自动化编程",
    "3. 策略创新：提出“半约束多模板”高分辨率优化策略，平衡效率与可解释性",
    "4. 机理创新：系统揭示宽带吸收的多物理协同机制"
]
add_bullet_box(slide, points, Inches(0.8), Inches(2.2), Inches(11.7), Inches(3.5))

# 装饰
shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.3))
shape.fill.solid()
shape.fill.fore_color.rgb = GOLD
shape.line.fill.background()

add_deco_line(slide, Inches(6.8))

# ==================== 第 14 页：不足与展望 ====================
slide = add_slide(6)
add_title(slide, "不足与展望", "")

items = [
    "当前不足：",
    "  • 低频边界尚未突破 2 GHz 以下",
    "  • 目前仅考虑垂直入射，未系统研究斜入射与极化稳定性",
    "未来方向：",
    "  • 进一步优化结构，向 2 GHz 以下扩展有效吸收频段",
    "  • 开展斜入射与多极化性能分析，评估工程适用性",
    "  • 引入制造误差分析，开展多目标优化（宽带、轻薄、鲁棒性）"
]
add_bullet_box(slide, items, Inches(0.8), Inches(2.2), Inches(11.7), Inches(3.5))

add_deco_line(slide, Inches(6.8))

# ==================== 第 15 页：致谢 ====================
slide = add_slide(6)

# 背景装饰
rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
rect.fill.solid()
rect.fill.fore_color.rgb = LIGHT_GRAY
rect.line.fill.background()

# 底部色块
rect2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(6.0), Inches(13.333), Inches(1.5))
rect2.fill.solid()
rect2.fill.fore_color.rgb = DARK_BLUE
rect2.line.fill.background()

# 中心文字
tb = slide.shapes.add_textbox(Inches(2), Inches(2.5), Inches(9.333), Inches(2))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "感谢指导"
p.font.size = Pt(48)
p.font.bold = True
p.font.color.rgb = DARK_BLUE
p.font.name = "Arial"
p.alignment = PP_ALIGN.CENTER

tb2 = slide.shapes.add_textbox(Inches(2), Inches(4.0), Inches(9.333), Inches(1.5))
tf2 = tb2.text_frame
p2 = tf2.paragraphs[0]
p2.text = "感谢孟庆鑫教授在选题、仿真、论文写作中的悉心指导\n感谢课题组同学与家人的支持\n\n汇报完毕，请各位老师批评指正"
p2.font.size = Pt(20)
p2.font.bold = False
p2.font.color.rgb = DARK_GRAY
p2.font.name = "Arial"
p2.alignment = PP_ALIGN.CENTER

# ==================== 保存 ====================
output_path = "毕业论文答辩PPT_周子靖.pptx"
try:
    prs.save(output_path)
    print(f"✅ PPT 已生成：{output_path}")
except Exception as e:
    print(f"❌ 保存失败: {e}")