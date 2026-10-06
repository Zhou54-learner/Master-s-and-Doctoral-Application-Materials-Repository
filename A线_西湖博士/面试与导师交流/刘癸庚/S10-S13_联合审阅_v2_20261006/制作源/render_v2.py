"""Read-only Microsoft PowerPoint 16.0 render of five independent v2 PPTX files.
The existing S9 PNGs are read only for the contact sheet; no deck is merged.
"""
from pathlib import Path
import hashlib,json,zipfile,re,argparse
_parser=argparse.ArgumentParser()
_parser.add_argument("--only",choices=["S10","S11","S12","S13"])
ONLY=_parser.parse_args().only
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
import win32com.client

REVIEW=Path(__file__).resolve().parent.parent
PI=REVIEW.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
NAMES=json.loads((REVIEW/'候选目录.json').read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')

def preserved():
    baseline=json.loads((REVIEW/'制作前保全基线.json').read_text(encoding='utf8'))
    checks=[dict(path=x['path'],unchanged=(ROOT/x['path']).stat().st_size==x['bytes'] and sha(ROOT/x['path'])==x['sha256'])
            for key in ['protected_candidates','sources','unrelated'] for x in baseline[key]]
    assert all(x['unchanged'] for x in checks),'Previously existing file changed'
    return checks

def render():
    app=win32com.client.DispatchEx('PowerPoint.Application')
    version=str(app.Version);assert version=='16.0',version
    security=app.AutomationSecurity;app.AutomationSecurity=3
    summaries=[]
    try:
        for key,dirname in NAMES.items():
            out=PI/dirname
            if ONLY is not None and ONLY!=key:continue
            for path in sorted(out.glob('*.pptx')):
                stem=path.stem;preview_key='S10-B' if stem.endswith('_方案B') else key
                before=sha(path);deck=None;overflow=[];outside=[];records=[];pictures={}
                try:
                    deck=app.Presentations.Open(str(path),True,False,False)
                    assert deck.Slides.Count==1
                    slide=deck.Slides(1)
                    for w,h in [(3840,2160),(1920,1080)]:
                        slide.Export(str(out/'预览'/f'{preview_key}_{w}x{h}.png'),'PNG',w,h)
                    for j in range(1,slide.Shapes.Count+1):
                        sh=slide.Shapes(j)
                        x,y,w,h=[float(getattr(sh,a)) for a in ['Left','Top','Width','Height']]
                        rec=dict(name=sh.Name,rect_pt=[x,y,w,h])
                        if x<-.1 or y<-.1 or x+w>float(deck.PageSetup.SlideWidth)+.1 or y+h>float(deck.PageSetup.SlideHeight)+.1:outside.append(rec)
                        if sh.HasTextFrame and sh.TextFrame.HasText:
                            tf=sh.TextFrame2;tr=tf.TextRange
                            actual=[float(tr.BoundWidth),float(tr.BoundHeight)]
                            allowed=[w-float(tf.MarginLeft+tf.MarginRight),h-float(tf.MarginTop+tf.MarginBottom)]
                            rec.update(text=sh.TextFrame.TextRange.Text,text_bound_pt=actual,available_pt=allowed,font_name=tr.Font.Name,font_size=float(tr.Font.Size))
                            if actual[0]>allowed[0]+1 or actual[1]>allowed[1]+1:overflow.append(rec)
                        if sh.Type==13:pictures[sh.Name]=rec
                        records.append(rec)
                    deck.SaveAs(str(out/(stem+'.pdf')),32)
                finally:
                    if deck is not None:deck.Close()
                assert sha(path)==before
                with zipfile.ZipFile(path) as z:
                    media={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('ppt/media/')}
                    parts=[n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)]
                    ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
                    paragraphs=[p for n in parts for p in ET.fromstring(z.read(n)).findall('.//a:p',ns)]
                    note_text='\n'.join(''.join(p.itertext()) for p in paragraphs)
                    actual_notes=(out/'本页备注.md').read_text(encoding='utf8').strip()
                    notes_ok=actual_notes in note_text
                    original=(PI/'Why_PhD母稿_用户原文_20261005.md').read_text(encoding='utf8').strip()
                    original_ok=(original in note_text if key=='S12' else None)
                image_checks=[]
                for info in json.loads((out/(stem+'_图片索引.json')).read_text(encoding='utf8')):
                    rec=pictures[info['shape_name']]
                    img=Image.open(out/info['output']);crop=Image.open(ROOT/info['source']).crop(tuple(info['crop_box']))
                    w,h=rec['rect_pt'][2:]
                    image_checks.append(dict(name=rec['name'],crop_pixels_match=img.mode==crop.mode and img.tobytes()==crop.tobytes(),
                        source_sha256_matches=sha(ROOT/info['source'])==info['source_sha256'],
                        aspect_relative_error=abs((w/h)/(img.width/img.height)-1),embedded_bytes_match=info['sha256'] in media))
                sizes=[dict(size=list(Image.open(out/'预览'/f'{preview_key}_{w}x{h}.png').size),expected=[w,h]) for w,h in [(3840,2160),(1920,1080)]]
                pdf=out/(stem+'.pdf');page_count=len(re.findall(rb'/Type\s*/Page\b',pdf.read_bytes()))
                report=dict(renderer='Microsoft PowerPoint '+version,slides=1,pdf_pages=page_count,logical_slide=key,variant=preview_key,
                    pptx_unchanged_by_readonly_render=True,export_sizes=sizes,text_overflow=overflow,shapes_outside_canvas=outside,
                    notes_complete=notes_ok,whyphd_original_verbatim=original_ok,image_checks=image_checks,shapes=records)
                write(out/(stem+'_排版检查.json'),report)
                summary=dict(slide=key,variant=preview_key,renderer=report['renderer'],overflow=len(overflow),outside=len(outside),
                    pdf_pages=page_count,notes_complete=notes_ok,whyphd_original_verbatim=original_ok,pptx_sha256=sha(path),pdf_sha256=sha(pdf))
                summaries.append(summary);print(json.dumps(summary,ensure_ascii=False),flush=True)
                assert notes_ok and original_ok is not False and page_count==1
                assert all(x['size']==x['expected'] for x in sizes)
                assert all(x['crop_pixels_match'] and x['source_sha256_matches'] and x['embedded_bytes_match'] and x['aspect_relative_error']<1e-5 for x in image_checks)
    finally:
        app.AutomationSecurity=security
        if app.Presentations.Count==0:app.Quit()
    checks=preserved()
    if ONLY:
        prior=json.loads((REVIEW/'PowerPoint渲染汇总.json').read_text(encoding='utf8'))['presentations']
        summaries=sorted([x for x in prior if x['slide']!=ONLY]+summaries,key=lambda x:x['variant'])
    write(REVIEW/'PowerPoint渲染汇总.json',dict(renderer='Microsoft PowerPoint '+version,presentations=summaries,preserved_files=len(checks),preservation=checks))
    return summaries

def contact_sheets():
    out=REVIEW/'预览';out.mkdir(exist_ok=True)
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',35)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
    sources=[]
    def pic(k):return PI/NAMES[k.split('-')[0]]/'预览'/f'{k}_1920x1080.png'
    def panel(canvas,path,label,caption,x,y,w):
        im=Image.open(path).convert('RGB');h=round(w*im.height/im.width)
        draw=ImageDraw.Draw(canvas);draw.text((x,y),label,font=font,fill='#172B43')
        canvas.paste(im.resize((w,h),Image.Resampling.LANCZOS),(x,y+58))
        draw.text((x,y+58+h+12),caption,font=small,fill='#5C6D7E')
        sources.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path)))
    labels={'S10':('S10 · A 首篇完整条目','个人问题 → 留下记录'),
            'S10-B':('S10 · B 列表上下文 + 标题局部','同一真实截图的两个裁切'),
            'S11':('S11 · 整站首页','本人新补真实首页 / 1919×989'),
            'S12':('S12 · 继续深造','三句话 / 完整原文备注'),
            'S13':('S13 · 继续追问物理','数值工具 → 物理问题 → 长期训练')}
    sheet=Image.new('RGB',(3840,2450),'#EAF0F3')
    for i,k in enumerate(['S10','S11','S12','S13']):panel(sheet,pic(k),*labels[k],40+(i%2)*1920,20+(i//2)*1220,1840)
    sheet.save(out/'S10-S13_联合审阅_v2.png')
    pair=Image.new('RGB',(3840,1225),'#EAF0F3')
    for i,k in enumerate(['S10','S10-B']):panel(pair,pic(k),*labels[k],40+i*1920,20,1840)
    pair.save(out/'S10_A-B_裁切审阅_v2.png')
    s9=PI/'S9_长期AI协作_v1_20261005/预览'
    seq=[(s9/'S9-A_1920x1080.png','S9-A · 现有候选','S9 同一逻辑主题，A/B 两帧'),
         (s9/'S9-B_1920x1080.png','S9-B · 现有候选','原图只读引用，S9 未修改')]
    seq += [(pic(k),*labels[k]) for k in ['S10','S11','S12','S13']]
    sequence=Image.new('RGB',(3840,1640),'#EAF0F3')
    for i,(path,title,caption) in enumerate(seq):panel(sequence,path,title,caption,30+(i%3)*1280,16+(i//3)*820,1220)
    sequence.save(out/'S9-S13_连续审阅_v2.png')
    # Pair strips preserve more detail and make the two key transitions easy to review.
    for name,items in [('S9B-S10_衔接', [seq[1],seq[2]]),('S11-S12_衔接',[seq[3],seq[4]])]:
        pair=Image.new('RGB',(3840,1225),'#EAF0F3')
        for i,(path,title,caption) in enumerate(items):panel(pair,path,title,caption,40+i*1920,20,1840)
        pair.save(out/(name+'_v2.png'))
    write(REVIEW/'预览来源.json',dict(operation='Contact sheets of actual PowerPoint PNGs; proportional resizing only; no merged deck.',
        logical_slides=5,frames=6,existing_s9='Both existing S9 frames read only.',sources=sources,
        files=[dict(path=p.relative_to(REVIEW).as_posix(),size=list(Image.open(p).size),sha256=sha(p)) for p in sorted(out.glob('*.png'))]))

if __name__=='__main__':
    summaries=render();contact_sheets()
    assert all(x['overflow']==0 and x['outside']==0 for x in summaries),'Repair geometry before delivery'
