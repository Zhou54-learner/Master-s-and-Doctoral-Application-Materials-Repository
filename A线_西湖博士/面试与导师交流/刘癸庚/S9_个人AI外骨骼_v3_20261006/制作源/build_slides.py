"""Build only S8/S9 v3. Editable text, real captured app viewports, no fabricated UI.
Usage: python build_slides.py --only both|s8|s9
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
S8=PI/'S8_项目AI协作_v3_20261006'
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
SRC=ROOT/'公共资料/事实核验/个人探索_20261004/素材'
INK,MUTED,TEAL,LINE='172B43','5C6D7E','007E86','D8E1E8'
TITLE8='从一个突然冒出来的想法，到一套协作方法'
TITLE9='后来，我开始围绕自己设计一套 AI 外骨骼'
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
    p.core_properties.subject=subject+' | INTERNAL / v3 CANDIDATE | 2026-10-06'
    return p
def base(p,title):
    s=p.slides.add_slide(p.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=RGBColor(255,255,255)
    tx(s,'section',.55,.24,4,.28,'个人探索',11,MUTED)
    tx(s,'candidate',8.5,.27,4.3,.26,'INTERNAL / v3 CANDIDATE',9.5,MUTED,align=PP_ALIGN.RIGHT)
    tx(s,'title',.55,.65,12.25,.70,title,28,INK,True)
    return s
def build_s8():
    pic,info=crop(S8,'S02_物理学习助手.png',(0,30,1322,852),'S02_完整应用_仅去窗口标题栏.png')
    p=deck(TITLE8,'S8');s=base(p,TITLE8)
    sh=s.shapes.add_picture(str(pic),Inches(.55),Inches(1.34),width=Inches(9.4));sh.name='historical_agent_full_application'
    tx(s,'demo_label',10.25,2.30,2.54,.40,'从想法到 Demo',16,TEAL,True)
    tx(s,'demo_detail',10.25,2.89,2.54,.97,'Codex 大幅降低\n实现门槛',18)
    tx(s,'complex_label',10.25,4.48,2.54,.40,'项目复杂以后',16,TEAL,True)
    tx(s,'division_detail',10.25,5.05,2.54,.38,'分角色 · 分窗口 · 分证据',13.5)
    tx(s,'human_decision',10.25,5.60,2.54,.92,'人负责目标、边界\n与最终裁决',17)
    tx(s,'source_footer',.55,7.27,11.5,.18,'Physics Learning Assistant · 本人历史原型；协作方法在后续迭代与复盘中形成',8.5,MUTED)
    tx(s,'slide_number',12.15,7.21,.65,.28,'S8',13,TEAL,True,PP_ALIGN.RIGHT)
    s.notes_slide.notes_text_frame.text=(S8/'speaker_notes.md').read_text(encoding='utf8').strip()
    p.save(S8/'S8_项目AI协作_v3.pptx')
    (S8/'派生素材说明.json').write_text(json.dumps([info],ensure_ascii=False,indent=2),encoding='utf8')
    print('Built S8 v3')
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
            tx(s,'view_label',10.77,2.59,2.45,.32,'长期状态',12,MUTED)
            tx(s,'long_term',10.77,3.12,2.45,.42,'我长期要完成什么？',17.5,TEAL,True)
            tx(s,'current_position',10.77,4.17,2.45,.42,'我现在走到哪里？',17.5,TEAL,True)
            tx(s,'detail',10.78,4.85,2.45,.33,'目标 · 知识结构 · 当前状态',11.5,MUTED)
        else:
            tx(s,'view_label',10.77,3.15,2.45,.32,'当前执行',12,MUTED)
            tx(s,'next_action',10.77,3.75,2.45,.43,'我下一步具体做什么？',17,TEAL,True)
            tx(s,'detail',10.78,4.40,2.45,.32,'材料 · 任务 · 通过条件',12,MUTED)
        label='知识地图' if frame=='A' else '执行页面'
        tx(s,'source_caption',.55,6.76,11.5,.27,f'{label} · 同一套个人工作系统的两个视角 · 本人真实页面截图',10,MUTED)
        line=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(.55),Inches(7.04),Inches(12.8),Inches(7.04))
        line.name='footer_rule';line.line.color.rgb=RGBColor.from_string(LINE);line.line.width=Pt(.7)
        line._element.spPr.append(OxmlElement('a:effectLst'))
        tx(s,'source_footer',.55,7.15,11.5,.24,'AI 协助整理与执行 · 理解、核对与取舍由我负责',9,MUTED)
        tx(s,'slide_number',12.16,7.09,.65,.35,'S9',15,TEAL,True,PP_ALIGN.RIGHT)
        s.notes_slide.notes_text_frame.text=(S9/f'speaker_notes_{frame}.md').read_text(encoding='utf8').strip()
    p.save(S9/'S9_个人AI外骨骼_v3.pptx')
    (S9/'派生素材说明.json').write_text(json.dumps([mi,ei],ensure_ascii=False,indent=2),encoding='utf8')
    (S9/'检查证据/截图放置.json').write_text(json.dumps(geometries,ensure_ascii=False,indent=2),encoding='utf8')
    print('Built S9 v3, A/B frames')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--only',choices=['both','s8','s9'],default='both');a=parser.parse_args()
    if a.only in ['both','s8']:build_s8()
    if a.only in ['both','s9']:build_s9()
