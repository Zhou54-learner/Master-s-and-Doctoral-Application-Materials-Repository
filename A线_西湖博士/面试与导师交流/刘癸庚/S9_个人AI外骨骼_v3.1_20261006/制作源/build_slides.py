"""Build S9 v3.1. Editable text, real captured app viewports, no fabricated UI.
Usage: python build_slides.py --only s9
Dependencies: python-pptx, Pillow. Input originals are packaged beside this source.
"""
from pathlib import Path
import argparse,hashlib,json,shutil
from PIL import Image
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN,MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.oxml.xmlchemy import OxmlElement

S9=Path(__file__).resolve().parents[1];PI=S9.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
SRC=ROOT/'公共资料/事实核验/个人探索_20261004/素材'
INK,MUTED,TEAL,LINE='172B43','5C6D7E','007E86','D8E1E8'
TITLE8='从一个突然冒出来的想法，到一套协作方法'
TITLE9='我想做的，是一套真正跟着我一起工作的 AI 外骨骼'
VIEWPORT=(.40,1.57,10.12,10.12*953/1920)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tx(s,name,x,y,w,h,content,size,color=INK,bold=False,align=PP_ALIGN.LEFT):
    shape=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));shape.name=name
    tf=shape.text_frame;tf.clear();tf.word_wrap=False;tf.auto_size=MSO_AUTO_SIZE.NONE
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    for n,t in enumerate(content.split('\n')):
        p=tf.paragraphs[0] if n==0 else tf.add_paragraph();p.text=t;p.alignment=align
        p.space_before=p.space_after=Pt(0);p.line_spacing=1.18
        for r in p.runs:
            r.font.name='Microsoft YaHei';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
            ea=OxmlElement('a:ea');ea.set('typeface','Microsoft YaHei');r._r.get_or_add_rPr().append(ea)
    return shape
def crop(out,source,box,name):
    for d in ['派生素材','预览','检查证据','制作源/输入']:(out/d).mkdir(parents=True,exist_ok=True)
    packaged=out/'制作源/输入'/source
    if not packaged.exists():shutil.copyfile(SRC/source,packaged)
    if (SRC/source).exists():assert sha(packaged)==sha(SRC/source)
    target=out/'派生素材'/name
    with Image.open(packaged) as im:
        dimensions=list(im.size);im.crop(box).save(target)
    return target,dict(source=(SRC/source).relative_to(ROOT).as_posix(),source_sha256=sha(packaged),
        packaged_original=packaged.relative_to(out).as_posix(),source_pixels=dimensions,crop_box=list(box),
        output=target.relative_to(out).as_posix(),pixels=list(Image.open(target).size),sha256=sha(target),
        operation='Remove only OS/browser chrome; retain every captured app pixel. No UI reconstruction or local detail crop.')
def deck(title,subject):
    p=Presentation();p.slide_width=Inches(13.333333);p.slide_height=Inches(7.5)
    p.core_properties.title=title;p.core_properties.author='Zijing Zhou'
    p.core_properties.subject=subject+' | INTERNAL / v3.1 CANDIDATE | 2026-10-06'
    return p
def base(p,title):
    s=p.slides.add_slide(p.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=RGBColor(255,255,255)
    tx(s,'section',.55,.24,4,.28,'个人探索',11,MUTED)
    tx(s,'candidate',8.5,.27,4.3,.26,'INTERNAL / v3.1 CANDIDATE',9.5,MUTED,align=PP_ALIGN.RIGHT)
    tx(s,'title',.55,.65,12.25,.70,title,28,INK,True)
    return s
def build_s9():
    mp,mi=crop(S9,'S06_课程图谱.png',(0,80,1920,1033),'S06_完整知识地图_仅去浏览器栏.png')
    ep,ei=crop(S9,'S05_执行驾驶舱.png',(0,38,1848,952),'S05_完整执行页面_仅去浏览器栏.png')
    p=deck(TITLE9,'S9 A/B');geometries=[]
    for frame,pic in [('A',mp),('B',ep)]:
        s=base(p,TITLE9);x,y,w,h=VIEWPORT
        with Image.open(pic) as im:scale=min(w/im.width,h/im.height);iw,ih=im.width*scale,im.height*scale
        sh=s.shapes.add_picture(str(pic),Inches(x+(w-iw)/2),Inches(y+(h-ih)/2),width=Inches(iw));sh.name='full_application_viewport'
        geometries.append(dict(frame=frame,viewport_inches=VIEWPORT,picture_inches=[x+(w-iw)/2,y+(h-ih)/2,iw,ih]))
        if frame=='A':
            tx(s,'view_label',10.77,2.53,2.45,.32,'长期状态',12,MUTED)
            tx(s,'state_question',10.77,2.99,2.45,.46,'系统持续维护什么？',17.5,TEAL,True)
            tx(s,'time_progress',10.77,3.86,2.45,.35,'时间进度',15.5,TEAL,True)
            tx(s,'time_detail',10.78,4.27,2.45,.33,'剩余时间 · 阶段 · 学习容量',11.5,MUTED)
            tx(s,'knowledge_space',10.77,4.94,2.45,.35,'知识 / 能力空间',15.5,TEAL,True)
            tx(s,'knowledge_detail',10.78,5.35,2.45,.52,'范围 · 关系 · 当前真正走到哪里',11.5,MUTED)
        else:
            tx(s,'view_label',10.77,2.30,2.45,.32,'我负责：理解 · 推导 · 作答',11.5,MUTED)
            tx(s,'protocol_title',10.77,2.74,2.45,.46,'一次学习动作之后',17.5,TEAL,True)
            tx(s,'protocol_step_1',10.77,3.41,2.45,.30,'学习结果',15.5,INK,True)
            tx(s,'protocol_arrow_1',10.77,3.75,2.45,.24,'↓',14,MUTED,True)
            tx(s,'protocol_step_2',10.77,4.03,2.45,.30,'批改 / 分析',15.5,INK,True)
            tx(s,'protocol_arrow_2',10.77,4.37,2.45,.24,'↓',14,MUTED,True)
            tx(s,'protocol_step_3',10.77,4.65,2.45,.30,'归档 / 状态更新',15.5,INK,True)
            tx(s,'protocol_arrow_3',10.77,4.99,2.45,.24,'↓',14,MUTED,True)
            tx(s,'protocol_step_4',10.77,5.27,2.45,.30,'复习 / 后续训练',15.5,TEAL,True)
            tx(s,'protocol_detail',10.78,5.78,2.45,.42,'事件触发 · 按既定协议接续',11.5,MUTED)
        label='知识地图' if frame=='A' else '执行页面'
        tx(s,'source_caption',.55,6.76,11.5,.27,f'{label} · 同一套个人工作系统的两个视角 · 本人真实页面截图',10,MUTED)
        line=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(.55),Inches(7.04),Inches(12.8),Inches(7.04))
        line.name='footer_rule';line.line.color.rgb=RGBColor.from_string(LINE);line.line.width=Pt(.7)
        line._element.spPr.append(OxmlElement('a:effectLst'))
        tx(s,'source_footer',.55,7.15,11.5,.24,'AI 协助整理与执行 · 理解、核对与取舍由我负责',9,MUTED)
        tx(s,'slide_number',12.16,7.09,.65,.35,'S9',15,TEAL,True,PP_ALIGN.RIGHT)
        s.notes_slide.notes_text_frame.text=(S9/f'speaker_notes_{frame}.md').read_text(encoding='utf8').strip()
    p.save(S9/'S9_个人AI外骨骼_v3.1.pptx')
    (S9/'派生素材说明.json').write_text(json.dumps([mi,ei],ensure_ascii=False,indent=2),encoding='utf8')
    (S9/'检查证据/截图放置.json').write_text(json.dumps(geometries,ensure_ascii=False,indent=2),encoding='utf8')
    print('Built S9 v3.1, A/B frames')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--only',choices=['s9'],default='s9');parser.parse_args()
    build_s9()
