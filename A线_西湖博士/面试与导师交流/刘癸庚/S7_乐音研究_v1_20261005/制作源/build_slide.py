"""Build the independent S7 v1 candidate with historical pixels and editable text.
Only crops UI margins and a video frame; never redraws historical research data.
"""
from pathlib import Path
import hashlib
import io
import json
import subprocess
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.oxml.xmlchemy import OxmlElement

OUT = Path(__file__).resolve().parent.parent
ROOT = next(p for p in OUT.parents if (p/'申请路线总览.md').exists())
MAIN = ROOT/'公共资料/事实核验/个人探索_20261004/素材/M01_历史波形与频谱.png'
VIDEO = Path('E:/2023/traindata/school data/2re.mp4')
ASSETS = OUT/'派生素材'
INK, MUTED, TEAL, LINE = '172B43', '5C6D7E', '007E86', 'D8E1E8'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

# Preserve every plotted sample, both axes, titles, frequency multiplier and cursor.
main_image = Image.open(MAIN).convert('RGB')
main_box = (22, 92, 546, 500)
main_crop = ASSETS/'M01_仅裁窗口工具栏.png'
main_image.crop(main_box).save(main_crop)
frame_bytes = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', '1.0', '-i', str(VIDEO), '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'])
frame = Image.open(io.BytesIO(frame_bytes)).convert('RGB')
frame_path = ASSETS/'2re_1秒原始截帧.png'
frame.save(frame_path)
frame_box = (0, 30, 1280, 720)
frame_crop = ASSETS/'2re_1秒现场裁切.png'
frame.crop(frame_box).save(frame_crop)
derived = [dict(source=MAIN.as_posix(), source_size=list(main_image.size), output=main_crop.relative_to(OUT).as_posix(), crop_box=list(main_box), sha256=sha(main_crop), operation='Only historical window/title/menu margins removed; waveform, spectrum, axes and cursor retained; no sharpening or pixel resynthesis.'),
           dict(source=VIDEO.as_posix(), frame_time_seconds=1.0, source_size=list(frame.size), original_frame=frame_path.relative_to(OUT).as_posix(), output=frame_crop.relative_to(OUT).as_posix(), crop_box=list(frame_box), sha256=sha(frame_crop), operation='FFmpeg decoded one historical frame; removed 30 pixels of top background only; no compositing, retouching, relabelling or stretching.')]
(OUT/'派生素材说明.json').write_text(json.dumps(derived,ensure_ascii=False,indent=2),encoding='utf8')

prs=Presentation();prs.slide_width=Inches(13.333333);prs.slide_height=Inches(7.5)
prs.core_properties.title='第一次把一个好奇的问题做成完整实验'
prs.core_properties.author='Zijing Zhou'
prs.core_properties.subject='S7 乐音研究｜INTERNAL / v1 CANDIDATE'
prs.core_properties.comments='One editable slide only; not merged with S2–S6.'
s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=RGBColor(255,255,255)

def text(name,x,y,w,h,content,size=20,color=INK,bold=False,align=PP_ALIGN.LEFT):
    shape=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));shape.name=name
    tf=shape.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    for i,line in enumerate(content.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.alignment=align
        p.space_before=p.space_after=Pt(0);p.line_spacing=1.15
        for r in p.runs:
            r.font.name='Microsoft YaHei';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
            ea=OxmlElement('a:ea');ea.set('typeface','Microsoft YaHei');r._r.get_or_add_rPr().append(ea)
    return shape

text('section',.55,.24,10,.24,'个人探索',11,MUTED)
text('title',.55,.65,12.25,.64,'第一次把一个好奇的问题做成完整实验',28,INK,True)
text('subtitle',.58,1.36,11.9,.30,'波纹管乐音研究 · 大二',13,MUTED)

picture=s.shapes.add_picture(str(main_crop),Inches(.60),Inches(1.66),width=Inches(6.40))
picture.name='historical_waveform_and_spectrum'
text('research_question',7.66,1.72,5.06,.90,'听起来稳定的乐音，\n能不能测量和比较？',22,INK,True)
text('workflow',7.66,2.86,5.06,.35,'录音 → 频谱分析 → 提取主要频率',16,MUTED)
text('observation',7.66,3.36,5.06,.38,'同组多次录音，主要频率相近',18,TEAL,True)
text('evidence_range',7.66,3.84,5.08,.28,'100 cm 管 · 01组的5段录音 · 主峰约1.49–1.53 kHz',11,MUTED)
onsite=s.shapes.add_picture(str(frame_crop),Inches(7.66),Inches(4.25),width=Inches(4.54));onsite.name='historical_demonstration_frame'
text('onsite_caption',7.66,6.75,5.06,.25,'气泵供气的答辩演示现场',11,MUTED)
text('contribution',.61,6.75,6.85,.29,'实验、分析与汇报，主要由我自主推进',15,INK)

line=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(.55),Inches(7.04),Inches(12.80),Inches(7.04))
line.name='footer_rule';line.line.color.rgb=RGBColor.from_string(LINE);line.line.width=Pt(.7)
text('source_footer',.55,7.15,11.54,.21,'历史录音与单边幅度谱 · 100 cm 管 · 01_1记录',9,MUTED)
text('slide_number',12.16,7.09,.65,.33,'S7',15,TEAL,True,PP_ALIGN.RIGHT)

notes=(OUT/'本页备注.md').read_text(encoding='utf8')
s.notes_slide.notes_text_frame.text=notes
prs.save(OUT/'S7_乐音研究_v1.pptx')
print(json.dumps(dict(slides=len(prs.slides),images=[list(Image.open(main_crop).size),list(Image.open(frame_crop).size)]),ensure_ascii=False))
