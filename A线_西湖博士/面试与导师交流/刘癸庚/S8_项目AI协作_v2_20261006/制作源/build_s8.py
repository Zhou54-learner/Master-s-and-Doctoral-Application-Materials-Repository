"""Rebuild only S8 v2, with native editable text and one actual screenshot.

Run from any directory: python build_s8.py
Dependencies: python-pptx 1.0.2, Pillow 12.3.0.
PowerPoint 16.0 exports are produced separately by the delivery coordinator.
No historical source or sibling slide package is written by this script.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parent.parent
ROOT = next((p for p in OUT.parents if (p / '申请路线总览.md').exists()), None)
SOURCE_PATH = '公共资料/事实核验/个人探索_20261004/素材/S02_物理学习助手.png'
SOURCE = ROOT / SOURCE_PATH if ROOT is not None else None
LOCAL_SOURCE = OUT / '制作源/输入/S02_物理学习助手_原图.png'
INK, TEAL, MUTED = '172B43', '007E86', '5C6D7E'
TITLE = '第一次比较系统地和 AI 一起做一个项目'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(slide, name, x, y, w, h, content, size, color=INK, bold=False, align=PP_ALIGN.LEFT):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    shape.name = name
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, line in enumerate(content.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.alignment = align
        p.space_before = p.space_after = Pt(0)
        p.line_spacing = 1.25
        for run in p.runs:
            run.font.name = 'Microsoft YaHei'
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = RGBColor.from_string(color)
            rpr = run._r.get_or_add_rPr()
            ea = OxmlElement('a:ea')
            ea.set('typeface', 'Microsoft YaHei')
            rpr.append(ea)
    return shape


def build():
    for name in ['派生素材', '预览', '制作源/输入']:
        (OUT / name).mkdir(parents=True, exist_ok=True)
    if not LOCAL_SOURCE.exists():
        assert SOURCE is not None and SOURCE.exists(), 'Original input is required for the first build.'
        LOCAL_SOURCE.write_bytes(SOURCE.read_bytes())
    if SOURCE is not None and SOURCE.exists():
        assert sha(LOCAL_SOURCE) == sha(SOURCE), 'Packaged original must equal verified source.'
    original = Image.open(LOCAL_SOURCE)
    assert original.size == (1322, 852)
    box = (0, 30, 1322, 852)
    screenshot = OUT / '派生素材/S02_完整应用_仅去窗口标题栏.png'
    original.crop(box).save(screenshot)
    crop_im = Image.open(screenshot)
    assert crop_im.size == (1322, 822)
    assert crop_im.tobytes() == original.crop(box).tobytes()
    p = Presentation()
    p.slide_width = Inches(13.333333)
    p.slide_height = Inches(7.5)
    p.core_properties.title = TITLE
    p.core_properties.subject = 'S8 | INTERNAL / v2 CANDIDATE'
    p.core_properties.author = 'Zijing Zhou'
    p.core_properties.comments = 'Actual historical application screenshot; no generated or reconstructed UI.'
    s = p.slides.add_slide(p.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = RGBColor(255, 255, 255)
    text(s, 'section', .55, .24, 4, .24, '个人探索', 11, MUTED)
    text(s, 'status', 7.1, .27, 5.7, .22, 'INTERNAL / v2 CANDIDATE', 9.5, MUTED, align=PP_ALIGN.RIGHT)
    text(s, 'title', .55, .65, 12.25, .64, TITLE, 28, INK, True)
    pic = s.shapes.add_picture(str(screenshot), Inches(.55), Inches(1.34), width=Inches(9.4))
    pic.name = 'historical_agent_full_application'
    text(s, 'my_role_label', 10.25, 2.30, 2.54, .35, '我负责', 15, TEAL, True)
    text(s, 'my_role', 10.25, 2.85, 2.54, .92, '目标 · 拆任务\n看结果 · 决定下一步', 18, INK)
    text(s, 'retrospect_label', 10.25, 4.48, 2.54, .35, '做完以后再看', 15, TEAL, True)
    text(s, 'retrospect', 10.25, 5.03, 2.54, .93, '过度设计\n重复造轮子', 19, INK)
    text(s, 'source_footer', .55, 7.27, 11.50, .18, '本人历史原型截图 S02 · 协作过程与复盘依本人确认', 8.5, MUTED)
    text(s, 'slide_number', 12.15, 7.21, .65, .25, 'S8', 13, TEAL, True, PP_ALIGN.RIGHT)
    notes = (OUT / '本页备注.md').read_text(encoding='utf-8').strip()
    s.notes_slide.notes_text_frame.text = notes
    pptx = OUT / 'S8_项目AI协作_v2.pptx'
    p.save(pptx)
    readback = Presentation(pptx)
    assert len(readback.slides) == 1
    assert readback.slides[0].notes_slide.notes_text_frame.text == notes
    shapes = list(readback.slides[0].shapes)
    beyond = [sh.name for sh in shapes if sh.left < 0 or sh.top < 0 or
              sh.left + sh.width > p.slide_width or sh.top + sh.height > p.slide_height]
    assert not beyond, beyond
    forbidden = ['PROJECT COLLABORATION', '项目级协作', '人–AI 协作方法', 'Agent orchestration', '明确目标 →']
    visible = '\n'.join(sh.text for sh in shapes if sh.has_text_frame)
    assert not any(token in visible for token in forbidden)
    derived = {
        'source': SOURCE_PATH,
        'source_sha256': sha(LOCAL_SOURCE),
        'packaged_original': LOCAL_SOURCE.relative_to(OUT).as_posix(),
        'source_pixels': [1322, 852],
        'crop_box_xyxy': list(box),
        'output': screenshot.relative_to(OUT).as_posix(),
        'output_pixels': [1322, 822],
        'output_sha256': sha(screenshot),
        'operation': 'Only remove the 30 px native Windows title bar; retain all application UI.',
        'resizing': 'PowerPoint proportional placement only; no pixel resize, redraw, sharpening or compositing.',
        'placement_inches': {'x': .55, 'y': 1.34, 'width': 9.4, 'height': 9.4 * 822 / 1322},
        'body_width_fraction': 9.4 / 12.25,
        'whole_slide_area_fraction': (9.4 * 9.4 * 822 / 1322) / (13.333333 * 7.5),
        'expected_1080p_image_pixels': [1354, 842],
        'content_boundary': 'Screenshot supports historical prototype existence, not answer/reference accuracy or learning efficacy.'
    }
    (OUT / '派生素材说明.json').write_text(json.dumps([derived], ensure_ascii=False, indent=2), encoding='utf-8')
    report = {
        'status': 'INTERNAL / v2 CANDIDATE',
        'slide_count': 1,
        'native_editable_textboxes': sum(sh.has_text_frame for sh in shapes),
        'screenshot_count': 1,
        'notes_exact_match': True,
        'out_of_bounds': beyond,
        'screenshot_crop_pixel_equal': True,
        'screenshot_aspect_ratio_error': abs((pic.width / pic.height) / (1322 / 822) - 1),
        'prohibited_visible_labels': [],
        'font': 'Microsoft YaHei',
        'powerpoint_render_status': 'Pending centralized PowerPoint 16.0 export and actual render inspection.',
        'notes_characters': len(notes),
        'pptx_sha256': sha(pptx)
    }
    (OUT / '制作源静态检查.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    build()
