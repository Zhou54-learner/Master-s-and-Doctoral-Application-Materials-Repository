"""Paired S8/S9 candidate. Only lossless crops of verified historical screenshots.
Run from any directory: python build_pair.py --only both|s8|s9.
The first run freezes the preservation baseline; subsequent runs never replace it.
Dependencies: python-pptx, Pillow. PowerPoint export is separate.
"""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.oxml.xmlchemy import OxmlElement

HERE = Path(__file__).resolve()
S8 = HERE.parent.parent
PI = S8.parent
ROOT = next(p for p in PI.parents if (p/'申请路线总览.md').exists())
S9 = PI/'S9_长期AI协作_v1_20261005'
SOURCES = ROOT/'公共资料/事实核验/个人探索_20261004'
INK, MUTED, TEAL, LINE = '172B43', '5C6D7E', '007E86', 'D8E1E8'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def record(path):
    return dict(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size, sha256=sha(path))

def freeze_baseline():
    ref_dirs = [p for p in PI.iterdir() if p.is_dir() and
                (p.name.startswith('本科毕设_S2-S5_') or p.name.startswith(('S6_', 'S7_')))]
    references = [record(p) for d in ref_dirs for p in sorted(d.rglob('*')) if p.is_file()]
    source_files = [SOURCES/'核验记录.md', SOURCES/'来源清单.json',
                    PI/'Personal_Explorations叙事与设计语言_20261005.md',
                    PI/'S8-S9_人AI协作双页联动设计_20261005.md']
    source_files += [SOURCES/'素材'/n for n in ['S02_物理学习助手.png','S06_课程图谱.png','S05_执行驾驶舱.png']]
    unrelated = [ROOT/'公共资料/面试与导师交流中心/公共主干'/p for p in
                 ['README.md','项目重建/本科毕设/README.md','项目重建/本科毕设/13_实际工作梳理与研究叙事底稿.md']]
    baseline = dict(date='2026-10-05', base_commit='edc1e3c',
                    sources=[record(p) for p in source_files], reference_files=references,
                    unrelated_work=[record(p) for p in unrelated],
                    operation='Read only. No historical software run; no research simulation; no source editing.')
    archived = json.loads((SOURCES/'来源清单.json').read_text(encoding='utf8'))
    for entry in archived:
        if entry['id'] in ('S02','S05','S06'):
            assert sha(ROOT/entry['copy']) == entry['sha256']
    for out in [S8,S9]:
        for sub in ['制作源','派生素材','预览']:
            (out/sub).mkdir(parents=True,exist_ok=True)
        target=out/'来源与保全.json'
        if not target.exists():
            target.write_text(json.dumps(baseline,ensure_ascii=False,indent=2),encoding='utf8')

def crop(out, source_name, box, name, explanation):
    source = SOURCES/'素材'/source_name
    original = Image.open(source)
    target = out/'派生素材'/name
    original.crop(box).save(target)
    return target, dict(source=source.relative_to(ROOT).as_posix(), source_sha256=sha(source),
                       source_pixels=list(original.size), crop_box=list(box),
                       output=target.relative_to(out).as_posix(), pixels=list(Image.open(target).size),
                       sha256=sha(target), operation='Lossless rectangular crop only; no resizing, redrawing, sharpening, compositing or generated UI.',
                       reason=explanation)

def text(slide,name,x,y,w,h,content,size=20,color=INK,bold=False,align=PP_ALIGN.LEFT):
    shape=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));shape.name=name
    tf=shape.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    for i,line in enumerate(content.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.text=line;p.alignment=align;p.space_before=p.space_after=Pt(0);p.line_spacing=1.15
        for run in p.runs:
            run.font.name='Microsoft YaHei';run.font.size=Pt(size)
            run.font.bold=bold;run.font.color.rgb=RGBColor.from_string(color)
            ea=OxmlElement('a:ea');ea.set('typeface','Microsoft YaHei');run._r.get_or_add_rPr().append(ea)
    return shape

def deck(title,subject):
    p=Presentation();p.slide_width=Inches(13.333333);p.slide_height=Inches(7.5)
    p.core_properties.title=title;p.core_properties.author='Zijing Zhou'
    p.core_properties.subject=subject+' | INTERNAL / v1 CANDIDATE'
    return p

def base(p,title,subtitle,number,stage,footer):
    s=p.slides.add_slide(p.slide_layouts[6]);s.background.fill.solid()
    s.background.fill.fore_color.rgb=RGBColor(255,255,255)
    text(s,'section',.55,.24,4,.24,'个人探索',11,MUTED)
    text(s,'stage',7.1,.27,5.7,.22,stage,9.5,MUTED,False,PP_ALIGN.RIGHT)
    text(s,'title',.55,.65,12.25,.64,title,28,INK,True)
    text(s,'subtitle',.58,1.36,12,.30,subtitle,13,MUTED)
    line=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(.55),Inches(7.04),Inches(12.8),Inches(7.04))
    line.name='footer_rule';line.line.color.rgb=RGBColor.from_string(LINE);line.line.width=Pt(.7)
    text(s,'source_footer',.55,7.15,11.54,.21,footer,9,MUTED)
    text(s,'slide_number',12.16,7.09,.65,.33,number,15,TEAL,True,PP_ALIGN.RIGHT)
    return s

def image_fit(s,path,name,x,y,w,h):
    im=Image.open(path);scale=min(w/im.width,h/im.height)
    iw,ih=im.width*scale,im.height*scale
    shape=s.shapes.add_picture(str(path),Inches(x+(w-iw)/2),Inches(y+(h-ih)/2),width=Inches(iw))
    shape.name=name
    return shape

def build_s8():
    pic, info=crop(S8,'S02_物理学习助手.png',(0,30,1322,852),'S02_仅裁窗口标题栏.png',
                   'Only the 30 px Windows title bar is removed; full historic application content remains.')
    (S8/'派生素材说明.json').write_text(json.dumps([info],ensure_ascii=False,indent=2),encoding='utf8')
    p=deck('项目级协作：组织 AI 完成一个具体结果','S8 项目级人–AI协作')
    s=base(p,p.core_properties.title,'物理学习 Agent · 第一次较系统的人–AI项目协作尝试','S8',
           '协作  /  PROJECT COLLABORATION','本人历史原型截图 S02 · 协作过程与复盘依本人确认')
    image_fit(s,pic,'historical_agent',.60,1.91,7.45,4.70)
    text(s,'image_caption',.61,6.74,7.4,.23,'物理学习 Agent · 历史原型界面',11,MUTED)
    x=8.48;w=4.30
    text(s,'goal',x,1.89,w,.34,'明确目标',19,INK,True)
    text(s,'goal_detail',x,2.29,w,.29,'先拆解任务',14,MUTED)
    text(s,'arrow1',x,2.65,.3,.26,'↓',14,MUTED)
    text(s,'orchestration',x,2.96,w,.35,'组织 / 调度 AI',19,INK,True)
    text(s,'iteration',x,3.36,w,.29,'组织 Agent · 多轮迭代',14,MUTED)
    text(s,'arrow2',x,3.72,.3,.26,'↓',14,MUTED)
    text(s,'prototype',x,4.04,w,.35,'形成原型',19,INK,True)
    text(s,'arrow3',x,4.48,.3,.26,'↓',14,MUTED)
    text(s,'reflection',x,4.79,w,.32,'复盘 · 回头看',16,MUTED)
    text(s,'limits',x,5.18,w,.36,'过度设计 / 重复造轮子',18,INK,True)
    text(s,'takeaway_label',x,5.87,w,.26,'真正留下',12,TEAL)
    text(s,'takeaway',x,6.15,w,.80,'人–AI协作方法\n与项目复盘',20,TEAL,True)
    s.notes_slide.notes_text_frame.text=(S8/'本页备注.md').read_text(encoding='utf8')
    p.save(S8/'S8_项目级AI协作_v1.pptx')

def build_s9():
    map_pic,map_info=crop(S9,'S06_课程图谱.png',(699,160,1874,791),'S06_知识地图局部.png',
                         'Retains course selector, current-position summary and four connected topic regions; removes browser chrome and other course regions. Not the whole map.')
    task_pic,task_info=crop(S9,'S05_执行驾驶舱.png',(493,297,1437,698),'S05_执行驾驶舱局部.png',
                           'Retains main task and pending status, material references, associated topics and complete pass-condition block. Omits sidebars, browser and empty margins.')
    (S9/'派生素材说明.json').write_text(json.dumps([map_info,task_info],ensure_ascii=False,indent=2),encoding='utf8')
    p=deck('长期协作：让 AI 进入自己的日常工作流','S9 同一主题的 A/B 连续帧')
    for frame,pic,label in [('A',map_pic,'知识地图'),('B',task_pic,'执行驾驶舱')]:
        s=base(p,p.core_properties.title,'考研学习系统 · 长期任务、状态与连续性的组织尝试','S9',
               '整合  /  LONG-TERM COLLABORATION','本人历史学习界面 S06 / S05 · 原图局部裁切 · 同一 S9 主题')
        text(s,'evidence_label',.61,1.82,8.9,.28,f'{label} · 历史界面局部',12,MUTED)
        image_fit(s,pic,'historical_map' if frame=='A' else 'historical_cockpit',.60,2.17,8.92,4.61)
        x,w=9.88,2.90
        for i,(y,question,detail) in enumerate([
            (2.34,'我长期在做什么？','目标 · 知识结构'),
            (3.61,'我现在做到哪里？','状态 · 上下文'),
            (4.88,'我下一步做什么？','材料 · 任务 · 通过条件')]):
            active=(frame=='A' and i<2) or (frame=='B' and i==2)
            text(s,f'question_{i+1}',x,y,w,.36,question,18,TEAL if active else INK,True)
            text(s,f'detail_{i+1}',x,y+.44,w,.30,detail,13,MUTED)
        text(s,'continuity',x,6.15,w,.72,'让协作不必\n每次从零开始',17,INK,True)
        all_notes=(S9/'本页备注.md').read_text(encoding='utf8')
        cue=('当前为 A 帧：知识地图。说到“再用执行驾驶舱”之前点击一次进入 B；不要重新介绍项目。' if frame=='A' else
             '当前为 B 帧：从“再用执行驾驶舱”接着说，不重读开场和过渡。总口述仍属于同一个 S9。')
        s.notes_slide.notes_text_frame.text=cue+'\n\n'+all_notes
    p.save(S9/'S9_长期AI协作_v1.pptx')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--only',choices=['both','s8','s9'],default='both')
    args=parser.parse_args();freeze_baseline()
    if args.only in ('both','s8'):build_s8()
    if args.only in ('both','s9'):build_s9()
    print('Built requested paired candidate:',args.only)
