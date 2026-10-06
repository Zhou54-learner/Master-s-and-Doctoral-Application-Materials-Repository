"""Build only S1 v2: an editable, ordered agenda. Never executes old builders."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.oxml.xmlchemy import OxmlElement

OUT = Path(__file__).resolve().parents[1]
INK, MUTED, TEAL, LINE = '172B43', '5C6D7E', '007E86', 'D8E1E8'

def tx(slide, name, x, y, w, h, text, size, color=INK, bold=False, align=PP_ALIGN.LEFT):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    shape.name = name
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = False
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for n, paragraph in enumerate(text.split('\n')):
        p = tf.paragraphs[0] if n == 0 else tf.add_paragraph()
        p.text = paragraph
        p.alignment = align
        p.space_before = p.space_after = Pt(0)
        p.line_spacing = 1.1
        for r in p.runs:
            r.font.name = 'Microsoft YaHei'
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.color.rgb = RGBColor.from_string(color)
            ea = OxmlElement('a:ea')
            ea.set('typeface', 'Microsoft YaHei')
            r._r.get_or_add_rPr().append(ea)
    return shape

def line(slide, name, x, y1, y2):
    shape = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y1), Inches(x), Inches(y2))
    shape.name = name
    shape.line.color.rgb = RGBColor.from_string(LINE)
    shape.line.width = Pt(.8)
    # Explicitly suppress the default theme's shadow effect.
    shape._element.spPr.append(OxmlElement('a:effectLst'))

def main():
    p = Presentation()
    p.slide_width, p.slide_height = Inches(13.333333), Inches(7.5)
    p.core_properties.title = '本科这几年，我主要做过这些事情'
    p.core_properties.author = 'Zijing Zhou'
    p.core_properties.subject = 'S1 | INTERNAL / v2 CANDIDATE | 2026-10-06'
    s = p.slides.add_slide(p.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = RGBColor(255,255,255)
    tx(s, 'section', .55,.24,4,.28, '个人背景',11,MUTED)
    tx(s, 'candidate', 8.5,.27,4.3,.26,'INTERNAL / v2 CANDIDATE',9.5,MUTED,align=PP_ALIGN.RIGHT)
    tx(s, 'title', .55,.65,12.2,.7,'本科这几年，我主要做过这些事情',28,INK,True)
    tx(s, 'education', .58,1.40,11.8,.36,'哈尔滨工业大学 · 物理学院 · 应用物理学',14,MUTED)

    # Four sections follow the presentation order, not calendar chronology.
    # Size, weight, space and accent establish a descending visual hierarchy.
    tx(s, 'number_01',.62,1.97,.55,.44,'01',21,TEAL,True)
    tx(s, 'section_01',1.28,1.98,10.8,.30,'本科毕业设计',14,TEAL,True)
    tx(s, 'project_01',1.26,2.31,11.5,.55,'三维周期电阻膜吸波结构',27,INK,True)
    tx(s, 'detail_01',1.28,2.87,11.2,.39,'结构设计、仿真与优化',17,MUTED)
    line(s,'sequence_01',.83,2.49,3.25)

    tx(s, 'number_02',.65,3.46,.53,.39,'02',18,MUTED)
    tx(s, 'section_02',1.28,3.45,10.8,.27,'合作科研',12.5,MUTED)
    tx(s, 'project_02',1.27,3.75,11.4,.46,'二维尘埃等离子体晶格波',22,INK,True)
    tx(s, 'detail_02',1.28,4.19,11.2,.35,'偏振数据处理与粒子轨迹可视化',15.5,MUTED)
    line(s,'sequence_02',.83,3.93,4.47)

    tx(s, 'number_03',.66,4.66,.53,.36,'03',17,MUTED)
    tx(s, 'section_03',1.28,4.65,10.8,.27,'一次较早的自主探索',12.5,MUTED)
    tx(s, 'project_03',1.27,4.95,11.4,.43,'波纹管乐音研究',20,INK,True)
    tx(s, 'detail_03',1.28,5.36,11.2,.33,'实验、录音与频谱分析',15,MUTED)
    line(s,'sequence_03',.83,5.11,5.64)

    tx(s, 'number_04',.66,5.84,.53,.35,'04',16,MUTED)
    tx(s, 'section_04',1.28,5.84,10.8,.26,'后来的一些个人探索',12,MUTED)
    tx(s, 'project_04a',1.27,6.14,11.4,.39,'物理学习 Agent / 长期学习系统',17.5,INK,True)
    tx(s, 'project_04b',1.27,6.51,11.4,.37,'写作 / 个人网页',17.5,INK,True)
    tx(s,'slide_number',12.16,7.09,.65,.35,'S1',15,TEAL,True,PP_ALIGN.RIGHT)
    s.notes_slide.notes_text_frame.text = (OUT/'本页备注.md').read_text(encoding='utf-8').strip()
    dest = OUT/'S1_个人背景_v2.pptx'
    p.save(dest)
    print('Built S1 v2:', len(s.shapes), 'editable objects')

if __name__ == '__main__':
    main()
