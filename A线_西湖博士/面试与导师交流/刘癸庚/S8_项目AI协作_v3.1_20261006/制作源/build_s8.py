"""Build only S8 v3.1 from three packaged original captures. No redraws."""
from pathlib import Path
import hashlib, json
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
from pptx.oxml.xmlchemy import OxmlElement

OUT = Path(__file__).resolve().parents[1]
INK, MUTED, TEAL = '172B43', '5C6D7E', '007E86'
TITLE = '从一个突然冒出来的想法，到一套协作方法'
STEM = 'S8_项目AI协作_v3.1'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def text(slide, name, x, y, w, h, value, size, color=INK, bold=False, align=PP_ALIGN.LEFT):
    sh = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    sh.name = name
    tf = sh.text_frame
    tf.clear()
    tf.word_wrap = False
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text, p.alignment = value, align
    p.space_before = p.space_after = Pt(0)
    p.line_spacing = 1.18
    for r in p.runs:
        r.font.name, r.font.size, r.font.bold = 'Microsoft YaHei', Pt(size), bold
        r.font.color.rgb = RGBColor.from_string(color)
        ea = OxmlElement('a:ea')
        ea.set('typeface', 'Microsoft YaHei')
        r._r.get_or_add_rPr().append(ea)
    return sh

def main():
    for folder in ['派生素材', '预览', '检查证据']:
        (OUT / folder).mkdir(parents=True, exist_ok=True)
    records = json.loads((OUT / '制作源/输入/输入来源.json').read_text(encoding='utf8'))
    # Each crop is a single rectangular crop. All original diagram arrows are inside it.
    specs = [
        ('application', 'S02_物理学习助手.png', (0, 30, 1322, 852), 'S02_完整应用_仅去窗口标题栏.png',
         (.55, 1.55, 7.03), 'Remove only OS title bar; retain full captured application viewport.'),
        ('roles', '九部门模型_用户原图.png', (20, 60, 1163, 377), '九部门模型_结构与首行语境.png',
         (7.95, 2.47, 4.85), 'Retain human control, all nine role nodes, all arrows and labels, table header and first row.'),
        ('lifecycle', '七阶段生命周期_用户原图.png', (24, 60, 1167, 383), '七阶段生命周期_完整回路与首行语境.png',
         (7.95, 4.82, 4.85), 'Retain all seven stages, both return loops, repair node, labels, table header and first row.'),
    ]
    deck = Presentation()
    deck.slide_width, deck.slide_height = Inches(13.333333), Inches(7.5)
    deck.core_properties.title = TITLE
    deck.core_properties.author = 'Zijing Zhou'
    deck.core_properties.subject = 'S8 | INTERNAL / v3.1 CANDIDATE | 2026-10-06'
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = RGBColor(255, 255, 255)
    text(slide, 'section', .55, .24, 4, .28, '个人探索', 11, MUTED)
    text(slide, 'candidate', 8.5, .27, 4.3, .26, 'INTERNAL / v3.1 CANDIDATE', 9.5, MUTED, align=PP_ALIGN.RIGHT)
    text(slide, 'title', .55, .65, 12.25, .70, TITLE, 28, bold=True)

    derived = []
    for key, filename, box, targetname, geometry, operation in specs:
        source = OUT / '制作源/输入' / filename
        original_info = next(r for r in records if r['packaged_file'] == filename)
        assert sha(source) == original_info['sha256']
        with Image.open(source) as im:
            original_pixels = list(im.size)
            crop = im.crop(box)
            target = OUT / '派生素材' / targetname
            crop.save(target)
        x, y, w = geometry
        sh = slide.shapes.add_picture(str(target), Inches(x), Inches(y), width=Inches(w))
        sh.name = key + '_original_capture'
        derived.append({'key': key, 'packaged_original': source.relative_to(OUT).as_posix(),
                        'source_sha256': sha(source), 'source_pixels': original_pixels,
                        'crop_box': list(box), 'output': target.relative_to(OUT).as_posix(),
                        'pixels': list(crop.size), 'sha256': sha(target),
                        'geometry_inches': [x, y, w, w * crop.height / crop.width], 'operation': operation})

    text(slide, 'demo_label', .65, 6.20, 3.40, .34, '从想法到 Demo', 15.5, TEAL, True)
    text(slide, 'demo_detail', .65, 6.65, 3.40, .34, 'Codex 降低实现门槛', 14)
    text(slide, 'complex_label', 4.37, 6.20, 3.20, .34, '项目复杂以后', 15.5, TEAL, True)
    text(slide, 'division_detail', 4.37, 6.65, 3.20, .34, '分角色 · 分窗口 · 分证据', 13.5)
    text(slide, 'framework_heading', 7.95, 1.55, 4.85, .42, '后来继续整理出的协作框架', 17, bold=True)
    text(slide, 'roles_label', 7.95, 2.09, 4.85, .34, '角色拆分 · 九部门模型', 14.5, TEAL, True)
    text(slide, 'lifecycle_label', 7.95, 4.40, 4.85, .34, '阶段闭环 · 七阶段生命周期', 14.5, TEAL, True)
    text(slide, 'source_footer', .55, 7.27, 11.5, .18,
         'Physics Learning Assistant · 本人历史原型与协作方法文档；右侧为原图局部裁切', 8.5, MUTED)
    text(slide, 'slide_number', 12.15, 7.21, .65, .28, 'S8', 13, TEAL, True, PP_ALIGN.RIGHT)
    slide.notes_slide.notes_text_frame.text = (OUT / 'speaker_notes.md').read_text(encoding='utf8').strip()
    deck.save(OUT / (STEM + '.pptx'))
    (OUT / '派生素材说明.json').write_text(json.dumps(derived, ensure_ascii=False, indent=2), encoding='utf8')
    print('Built only S8 v3.1; full app at 57.4% of content width, two unredrawn methodology crops.')

if __name__ == '__main__':
    main()
