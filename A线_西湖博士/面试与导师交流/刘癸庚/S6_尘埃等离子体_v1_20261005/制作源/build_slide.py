"""Build only the S6 candidate. Research originals and S2–S5 remain read-only.
No simulation, data reconstruction, or image redrawing is performed.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageChops
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.oxml.xmlchemy import OxmlElement

OUT = Path(__file__).resolve().parent.parent
ROOT = next(p for p in OUT.parents if (p / '申请路线总览.md').exists())
REFERENCE = OUT.parent / '本科毕设_S2-S5_v2.1_20261005'
MAIN = ROOT / '科研准备/晶格波研究/分析代码/原始代码/代码（偏振）去前段/1725198103735.jpg'
DETAIL = ROOT / '科研准备/晶格波研究/图件/原始图件/data figure x tc-5/no line/53,53.jpg'
REPORT = ROOT / '公共资料/事实核验/尘埃等离子体_历史贡献与代码考古_20261005.md'
PAPER = ROOT / '科研准备/晶格波研究/论文/论文2.pdf'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

baseline_path = OUT / '来源与保全.json'
if not baseline_path.exists():
    baseline = {
        'date': '2026-10-05',
        'sources': [
            {'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
            for p in (MAIN, DETAIL, REPORT, PAPER)
        ],
        'reference_files': [
            {'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
            for p in sorted(REFERENCE.rglob('*')) if p.is_file()
        ],
        'original_size_px': list(Image.open(MAIN).size),
        'image_operation': 'original JPEG bytes embedded; no crop, stretch, recolour, or redraw',
    }
    baseline_path.write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding='utf-8')
baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
for item in baseline['sources'] + baseline['reference_files']:
    assert sha(ROOT / item['path']) == item['sha256'], item['path']

INK, MUTED, TEAL, LINE = '172B43', '5C6D7E', '007E86', 'D8E1E8'
prs = Presentation()
prs.slide_width = Inches(13.333333)
prs.slide_height = Inches(7.5)
prs.core_properties.title = 'S6｜合作研究：二维尘埃等离子体中的偏振与粒子运动'
prs.core_properties.author = 'Zijing Zhou'
prs.core_properties.subject = '导师交流中文PPT｜S6 v1候选页'
prs.core_properties.comments = 'INTERNAL / CANDIDATE; not merged into the full presentation.'
s = prs.slides.add_slide(prs.slide_layouts[6])
s.background.fill.solid()
s.background.fill.fore_color.rgb = RGBColor(255, 255, 255)

def text(name, x, y, w, h, content, size=20, color=INK, bold=False, align=PP_ALIGN.LEFT):
    z = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    z.name = name
    f = z.text_frame
    f.clear()
    f.word_wrap = True
    f.margin_left = f.margin_right = f.margin_top = f.margin_bottom = 0
    for i, value in enumerate(content.split('\n')):
        p = f.paragraphs[0] if i == 0 else f.add_paragraph()
        p.text = value
        p.alignment = align
        p.space_before = p.space_after = Pt(0)
        p.line_spacing = 1.15
        for run in p.runs:
            run.font.name = 'Microsoft YaHei'
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = RGBColor.from_string(color)
            ea = OxmlElement('a:ea')
            ea.set('typeface', 'Microsoft YaHei')
            run._r.get_or_add_rPr().append(ea)
    return z

text('section', .55, .24, 10, .24, '合作研究', 11, MUTED)
text('title', .55, .65, 12.25, .64, '合作研究：二维尘埃等离子体中的偏振与粒子运动', 28, INK, True)
text('polarization_definition', .58, 1.40, 11.9, .30,
     '这里的“偏振”指颗粒在平面内的振动方向与二维轨迹', 13, MUTED)

# Original aspect ratio, preserved by supplying only the image height.
picture = s.shapes.add_picture(str(MAIN), Inches(1.00), Inches(1.67), height=Inches(5.28))
picture.name = 'historical_41_position_trajectories'

text('research_question', 7.62, 2.03, 5.04, .96,
     '中心颗粒振动向外传播后，\n为什么各位置的轨迹形状不同？', 20)
text('my_work_label', 7.62, 3.24, 4.98, .37, '我的工作', 17, TEAL, True)
text('my_work', 7.62, 3.72, 5.04, .92,
     'MATLAB 偏振相关数据处理、\n粒子轨迹可视化与多位置图组整理', 18)

# Local enlargement from the user's optional historical single-particle image.
# Crop only its white margins. Preserve all curve pixels, colour and aspect ratio.
detail_image = Image.open(DETAIL).convert('RGB')
r, g, b = detail_image.split()
mask = ImageChops.subtract(b, ImageChops.lighter(r, g)).point(lambda value: 255 if value > 80 else 0)
box = mask.getbbox()
box = (max(0, box[0]-65), max(0, box[1]-65), min(detail_image.width, box[2]+65), min(detail_image.height, box[3]+65))
assets = OUT/'派生素材'
assets.mkdir(exist_ok=True)
detail_crop = assets/'53_53_原图裁白边.png'
detail_image.crop(box).save(detail_crop)
enlargement = s.shapes.add_picture(str(detail_crop), Inches(7.52), Inches(5.02), width=Inches(1.63))
enlargement.name = 'historical_53_53_local_enlargement'
text('detail_label', 7.52, 6.01, 1.70, .46, '局部放大\n(53,53)', 11, MUTED, False, PP_ALIGN.CENTER)
text('observations', 9.44, 5.10, 3.21, .96,
     '对称位置多为线状\n其他位置出现椭圆', 18)
text('paper_explanation', 7.62, 6.58, 5.08, .29,
     '论文解释：不同振动分量之间的相位延迟', 13, MUTED)
(OUT/'派生素材说明.json').write_text(json.dumps({'source': DETAIL.relative_to(ROOT).as_posix(), 'source_size_px': list(detail_image.size), 'crop_box_px': list(box), 'derived_size_px': list(Image.open(detail_crop).size), 'operation': 'white-margin crop only; no redraw, recolour, rotation or stretching; enlarged independently of main image', 'sha256': sha(detail_crop)}, ensure_ascii=False, indent=2), encoding='utf-8')

line = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(.55), Inches(7.04), Inches(12.80), Inches(7.04))
line.name = 'footer_rule'
line.line.color.rgb = RGBColor.from_string(LINE)
line.line.width = Pt(.7)
text('figure_reference', .55, 7.15, 11.54, .21, '历史 41 个位置轨迹汇总图 · 对应论文 Fig.12', 9, MUTED)
text('slide_number', 12.16, 7.09, .65, .33, 'S6', 15, TEAL, True, PP_ALIGN.RIGHT)

script = '''除了毕业设计，我还参与过一项二维尘埃等离子体晶格波的合作研究。我的任务主要是做偏振相关的数据处理和粒子轨迹可视化。

这里的偏振指的是颗粒在平面内怎么振动。我用 MATLAB 把粒子的 x、y 两个运动分量组合成二维轨迹，再去比较不同空间位置的差别。最后整理出了这里这组 41 个位置的轨迹图，也进入了论文的 Fig.12。

比较直观的现象是，一些对称位置上的轨迹接近直线，而其他位置会出现明显的椭圆。论文把它解释成不同方向振动分量之间存在相位延迟。

这项工作对我来说比较重要的一点，是让我第一次比较完整地接触了团队科研里面从模拟数据到物理图像，再到论文图件这一段工作。'''
notes = f'''S6｜v1候选｜口述目标40–50秒，未本人计时

口述稿（本轮用户提供，原文保留；只存入本页备注，不覆盖母稿）
{script}

指图与被打断时
先指中央横向线状轨迹，再指附近椭圆状轨迹，必要时用右侧小放大图说明椭圆形状。放大图是历史(53,53)单图，单独放大显示，不与主图比较振幅。每个位置的一条轨迹表示该颗粒随时间的二维运动，图组不是单粒子向外传播的路径。图组排布不直接当作精确物理坐标系，不从拼图测偏振角、椭圆率或振幅。被问到团队分工时，先说已确认的数据处理、可视化和图组整理，再区分尚未核实的核心模拟运行与代码修改。

来源与边界（备查，不逐条朗读）
事实依据：公共资料/事实核验/尘埃等离子体_历史贡献与代码考古_20261005.md，尤其§3、§7.1、§8、§9链1、§11和§12。主图为科研准备/晶格波研究/分析代码/原始代码/代码（偏振）去前段/1725198103735.jpg，整张原图原比例嵌入；对应正式论文Fig.12（论文2.pdf，第8页），机制解释见第7页末至第8页首。局部放大来自科研准备/晶格波研究/图件/原始图件/data figure x tc-5/no line/53,53.jpg，仅裁白边，颜色、方向和轨迹比例不变。
已确认本人参与MATLAB偏振相关数据处理、二维轨迹可视化与图组整理。41图进入本人名下工作簿及与论文图12的对应，不证明本人独立完成全部模拟。本人是否运行哪些核心模拟、具体改到核心代码哪层、是否设计求解算法、是否撰写正文/图注、是否首先提出机制解释，仍未核实。不得认领独立模型或求解器开发。2025协方差/PCA后续版本不属于本页主讲素材。
线状/椭圆状是图形观察；相位延迟是论文归因。这里不主张本人提取了相位差、验证了收敛或独立证实了机制。用户口述中的“第一次比较完整地接触”保留为本人当轮提供的体验性回顾，不由图件档案独立证明。
'''
s.notes_slide.notes_text_frame.text = notes
prs.save(OUT / 'S6_尘埃等离子体_v1.pptx')
(OUT / '本页备注.md').write_text(notes, encoding='utf-8')
print(json.dumps({'slides': len(prs.slides), 'main_image': list(Image.open(MAIN).size), 'main_placement_inches': [round(picture.left/914400, 4), round(picture.top/914400, 4), round(picture.width/914400, 4), round(picture.height/914400, 4)]}, ensure_ascii=False))
