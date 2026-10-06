"""Build S9 v2 only. Full captured application viewports; no UI reconstruction.
Dependencies: python-pptx, Pillow. Output limited to this new candidate folder.
"""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.oxml.xmlchemy import OxmlElement

OUT = Path(__file__).resolve().parents[1]
PI = OUT.parent
ROOT = next(p for p in PI.parents if (p/'申请路线总览.md').exists())
SRC = ROOT/'公共资料/事实核验/个人探索_20261004/素材'
INK, MUTED, TEAL, LINE, QUIET = '172B43','5C6D7E','007E86','D8E1E8','8C99A5'
TITLE = '后来，我想让这种协作不要每次都从零开始'
VIEWPORT = (.40, 1.57, 10.12, 10.12*953/1920)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def tx(s, name, x, y, w, h, content, size, color=INK, bold=False, align=PP_ALIGN.LEFT):
    shape=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    shape.name=name
    tf=shape.text_frame; tf.clear(); tf.word_wrap=False; tf.auto_size=MSO_AUTO_SIZE.NONE
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    for n, text in enumerate(content.split('\n')):
        p=tf.paragraphs[0] if n==0 else tf.add_paragraph()
        p.text=text; p.alignment=align; p.space_before=p.space_after=Pt(0); p.line_spacing=1.12
        for r in p.runs:
            r.font.name='Microsoft YaHei'; r.font.size=Pt(size); r.font.bold=bold
            r.font.color.rgb=RGBColor.from_string(color)
            ea=OxmlElement('a:ea');ea.set('typeface','Microsoft YaHei');r._r.get_or_add_rPr().append(ea)
    return shape

def crop(source,box,name):
    target=OUT/'派生素材'/name
    packaged=OUT/'制作源/输入'/source
    packaged.parent.mkdir(exist_ok=True)
    if not packaged.exists():shutil.copyfile(SRC/source,packaged)
    if (SRC/source).exists():assert sha(packaged)==sha(SRC/source)
    with Image.open(packaged) as im:
        original_size=list(im.size)
        im.crop(box).save(target)
    return target,dict(source=(SRC/source).relative_to(ROOT).as_posix(),source_sha256=sha(packaged),
        packaged_original=packaged.relative_to(OUT).as_posix(),
        source_pixels=original_size,crop_box=list(box),output=target.relative_to(OUT).as_posix(),
        pixels=list(Image.open(target).size),sha256=sha(target),
        operation='Lossless rectangle crop of browser chrome only; full captured application viewport retained.',
        reason='Remove browser tabs/address bar; keep app navigation, header, sidebars and every captured content area.')

def build():
    for d in ['派生素材','预览','检查证据']:(OUT/d).mkdir(exist_ok=True)
    mp,mi=crop('S06_课程图谱.png',(0,80,1920,1033),'S06_完整知识地图_仅去浏览器栏.png')
    ep,ei=crop('S05_执行驾驶舱.png',(0,38,1848,952),'S05_完整执行页面_仅去浏览器栏.png')
    (OUT/'派生素材说明.json').write_text(json.dumps([mi,ei],ensure_ascii=False,indent=2),encoding='utf8')
    p=Presentation();p.slide_width=Inches(13.333333);p.slide_height=Inches(7.5)
    p.core_properties.title=TITLE;p.core_properties.author='Zijing Zhou'
    p.core_properties.subject='S9 A/B | INTERNAL / v2 CANDIDATE | 2026-10-06'
    geometries=[]
    for frame,pic in [('A',mp),('B',ep)]:
        s=p.slides.add_slide(p.slide_layouts[6]);s.background.fill.solid()
        s.background.fill.fore_color.rgb=RGBColor(255,255,255)
        tx(s,'section',.55,.24,4,.28,'个人探索',11,MUTED)
        tx(s,'candidate',8.5,.27,4.3,.26,'INTERNAL / v2 CANDIDATE',9.5,MUTED,align=PP_ALIGN.RIGHT)
        tx(s,'title',.55,.65,12.25,.70,TITLE,28,INK,True)
        x,y,w,h=VIEWPORT
        with Image.open(pic) as im:
            scale=min(w/im.width,h/im.height);iw,ih=im.width*scale,im.height*scale
        # The same viewport on both frames; less than 3 px white letterbox at 1080p
        # accommodates the source aspect-ratio difference without stretching either UI.
        shape=s.shapes.add_picture(str(pic),Inches(x+(w-iw)/2),Inches(y+(h-ih)/2),width=Inches(iw))
        shape.name='full_application_viewport'
        geometries.append(dict(frame=frame,viewport_inches=VIEWPORT,
            picture_inches=[x+(w-iw)/2,y+(h-ih)/2,iw,ih],letterbox_1080p_px=(h-ih)*144))
        for i,(qy,q,detail) in enumerate([
            (2.34,'我长期在做什么？','目标 · 知识结构'),
            (3.68,'我现在做到哪里？','状态 · 上下文'),
            (5.02,'我下一步做什么？','材料 · 任务 · 通过条件')]):
            active=(frame=='A' and i<2) or (frame=='B' and i==2)
            tx(s,f'question_{i+1}',10.77,qy,2.35,.40,q,17.5,TEAL if active else QUIET,active)
            tx(s,f'detail_{i+1}',10.78,qy+.47,2.35,.30,detail,11.7,MUTED if active else QUIET)
        label='知识地图' if frame=='A' else '执行页面'
        tx(s,'source_caption',.55,6.76,11.5,.25,f'{label} · 本人真实页面截图，仅去浏览器栏',10,MUTED)
        line=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(.55),Inches(7.04),Inches(12.8),Inches(7.04))
        line.name='footer_rule';line.line.color.rgb=RGBColor.from_string(LINE);line.line.width=Pt(.7)
        line._element.spPr.append(OxmlElement('a:effectLst'))
        tx(s,'source_footer',.55,7.15,11.5,.22,'考研学习中的组织尝试 · 界面状态不作为当前掌握程度证明',9,MUTED)
        tx(s,'slide_number',12.16,7.09,.65,.35,'S9',15,TEAL,True,PP_ALIGN.RIGHT)
        s.notes_slide.notes_text_frame.text=(OUT/f'speaker_notes_{frame}.md').read_text(encoding='utf8').strip()
    (OUT/'检查证据/截图放置.json').write_text(json.dumps(geometries,ensure_ascii=False,indent=2),encoding='utf8')
    p.save(OUT/'S9_长期AI协作_v2.pptx')
    print('Built S9 v2, two frames; all slide text and notes editable.')

if __name__=='__main__':build()
