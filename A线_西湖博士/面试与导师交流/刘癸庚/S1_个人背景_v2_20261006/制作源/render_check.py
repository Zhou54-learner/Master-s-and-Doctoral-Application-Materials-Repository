"""Read-only PowerPoint 16.0 exports, geometric checks and S0-S2 contact sheets.
No slides are merged. All previously existing slide assets remain read only.
"""
from pathlib import Path
import hashlib,json,re,zipfile
from pptx import Presentation
from PIL import Image,ImageDraw,ImageFont
import win32com.client

OUT=Path(__file__).resolve().parents[1]
PI=OUT.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
S12=PI/'S12_WhyPhD_v2.1_20261006'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def check_preservation():
    base=json.loads((OUT/'制作前保全基线.json').read_text(encoding='utf-8'))
    checks=[]
    for group in ['protected_candidates','unrelated']:
        for item in base[group]:
            path=ROOT/item['path']
            checks.append(dict(path=item['path'],unchanged=path.exists() and path.stat().st_size==item['bytes'] and sha(path)==item['sha256']))
    write(OUT/'保全检查.json',dict(checked_files=len(checks),unchanged_files=sum(x['unchanged'] for x in checks),checks=checks))
    assert all(x['unchanged'] for x in checks),'An existing protected file changed'
    return len(checks)

def render():
    app=win32com.client.DispatchEx('PowerPoint.Application')
    version=str(app.Version)
    assert version=='16.0',version
    security=app.AutomationSecurity
    app.AutomationSecurity=3
    summary=[]
    try:
        for folder,stem,key in [(OUT,'S1_个人背景_v2','S1'),(S12,'S12_WhyPhD_v2.1','S12')]:
            preview=folder/'预览';preview.mkdir(exist_ok=True)
            path=folder/(stem+'.pptx');before=sha(path)
            pres=None;overflow=[];outside=[];records=[]
            try:
                pres=app.Presentations.Open(str(path),True,False,False)
                assert pres.Slides.Count==1
                slide=pres.Slides(1)
                for w,h in [(3840,2160),(1920,1080)]:
                    slide.Export(str(preview/f'{key}_{w}x{h}.png'),'PNG',w,h)
                pres.SaveAs(str(folder/(stem+'.pdf')),32)
                for i in range(1,slide.Shapes.Count+1):
                    sh=slide.Shapes(i)
                    x,y,w,h=[float(getattr(sh,a)) for a in ['Left','Top','Width','Height']]
                    rec=dict(name=sh.Name,rect_pt=[x,y,w,h])
                    if x<-.1 or y<-.1 or x+w>float(pres.PageSetup.SlideWidth)+.1 or y+h>float(pres.PageSetup.SlideHeight)+.1:outside.append(rec)
                    if sh.HasTextFrame and sh.TextFrame.HasText:
                        tf=sh.TextFrame2;tr=tf.TextRange
                        actual=[float(tr.BoundWidth),float(tr.BoundHeight)]
                        allowed=[w-float(tf.MarginLeft+tf.MarginRight),h-float(tf.MarginTop+tf.MarginBottom)]
                        rec.update(text=sh.TextFrame.TextRange.Text,text_bound_pt=actual,available_pt=allowed,font_name=tr.Font.Name,font_size=float(tr.Font.Size))
                        if actual[0]>allowed[0]+1 or actual[1]>allowed[1]+1:overflow.append(rec)
                    records.append(rec)
            finally:
                if pres is not None:pres.Close()
            assert sha(path)==before,'Read-only render must preserve PPTX bytes'
            ppt=Presentation(path)
            notes=ppt.slides[0].notes_slide.notes_text_frame.text
            wanted=(folder/'本页备注.md').read_text(encoding='utf-8').strip()
            assert notes.strip()==wanted,'External and embedded notes differ'
            pdf=folder/(stem+'.pdf')
            pages=len(re.findall(rb'/Type\s*/Page\b',pdf.read_bytes()))
            assert pages==1
            sizes=[dict(actual=list(Image.open(preview/f'{key}_{w}x{h}.png').size),expected=[w,h]) for w,h in [(3840,2160),(1920,1080)]]
            assert all(x['actual']==x['expected'] for x in sizes)
            why_original=None
            if key=='S12':
                original=(PI/'Why_PhD母稿_用户原文_20261005.md').read_text(encoding='utf-8').strip()
                why_original=original in notes
                assert why_original
            report=dict(renderer='Microsoft PowerPoint '+version,slides=1,pdf_pages=pages,
                        pptx_unchanged_by_readonly_render=True,notes_exact_match=True,whyphd_original_verbatim=why_original,
                        text_overflow=overflow,shapes_outside_canvas=outside,export_sizes=sizes,shapes=records)
            write(folder/'PowerPoint排版检查.json',report)
            summary.append(dict(slide=key,renderer=report['renderer'],overflow=len(overflow),outside=len(outside),
                                notes_exact_match=True,pdf_pages=pages,pptx_sha256=before,pdf_sha256=sha(pdf)))
            print(json.dumps(summary[-1],ensure_ascii=False),flush=True)
    finally:
        app.AutomationSecurity=security
        if app.Presentations.Count==0:app.Quit()
    write(OUT/'PowerPoint导出汇总.json',dict(presentations=summary,preserved_files=check_preservation()))
    assert all(x['overflow']==0 and x['outside']==0 for x in summary),'Fix geometry before delivery'

def contacts():
    paths=[PI/'S0_封面_v1_20261005/预览/S0_1920x1080.png',
           OUT/'预览/S1_1920x1080.png',
           PI/'本科毕设_S2-S5_v2.1_20261005/预览/S2.png']
    labels=['S0 · 现有封面 v1','S1 · 个人背景 v2 CANDIDATE','S2 · 现有毕设开场 v2.1']
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',32)
    tilew=1880;tileh=round(tilew*9/16)
    horizontal=Image.new('RGB',(5760,1160),'#EAF0F3')
    vertical=Image.new('RGB',(1920,3480),'#EAF0F3')
    for i,(path,label) in enumerate(zip(paths,labels)):
        img=Image.open(path).convert('RGB')
        assert abs(img.width/img.height-16/9)<1e-3
        img=img.resize((tilew,tileh),Image.Resampling.LANCZOS)
        for canvas,x,y in [(horizontal,20+i*1920,18),(vertical,20,18+i*1160)]:
            ImageDraw.Draw(canvas).text((x,y),label,font=font,fill='#172B43')
            canvas.paste(img,(x,y+59))
    hp=OUT/'预览/S0-S2_连续审阅_横向.png';vp=OUT/'预览/S0-S2_连续审阅_纵向.png'
    horizontal.save(hp);vertical.save(vp)
    write(OUT/'连续审阅来源.json',dict(operation='Existing PowerPoint exports, proportional resizing and contact-sheet composition only; no merged PPT.',
        order=['S0 v1','S1 v2','S2 v2.1'],sources=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),pixels=list(Image.open(p).size)) for p in paths],
        outputs=[dict(path=p.relative_to(OUT).as_posix(),sha256=sha(p),pixels=list(Image.open(p).size)) for p in [hp,vp]]))
    print('S0-S2 continuous review sheets exported: 5760x1160 and 1920x3480')

if __name__=='__main__':
    render()
    contacts()
