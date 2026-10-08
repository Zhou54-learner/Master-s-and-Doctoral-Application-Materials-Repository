"""Actual Microsoft PowerPoint 16.0 rendering and geometry verification.
Read-only opens. Never saves or opens S2-S9 decks. No full-deck merge.
"""
from pathlib import Path
import hashlib, json, zipfile
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import win32com.client

REVIEW=Path(__file__).resolve().parent.parent
PI=REVIEW.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
NAMES=json.loads((REVIEW/'候选目录.json').read_text(encoding='utf8'))

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')

def render():
    app=win32com.client.DispatchEx('PowerPoint.Application')
    version=str(app.Version)
    assert version=='16.0',version
    previous_security=app.AutomationSecurity;app.AutomationSecurity=3
    summaries=[]
    try:
        for key,dirname in NAMES.items():
            out=PI/dirname;stem=json.loads((out/'制作源/config.json').read_text(encoding='utf8'))['stem']
            path=out/(stem+'.pptx');before=sha(path);deck=None
            overflow=[];outside=[];records=[];pictures=[]
            try:
                deck=app.Presentations.Open(str(path),True,False,False)
                assert deck.Slides.Count==1
                slide=deck.Slides(1)
                for w,h in [(3840,2160),(1920,1080)]:
                    slide.Export(str(out/'预览'/f'{key}_{w}x{h}.png'),'PNG',w,h)
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
                    if sh.Type==13:pictures.append(rec)
                    records.append(rec)
                deck.SaveAs(str(out/(stem+'.pdf')),32)
            finally:
                if deck is not None:deck.Close()
            assert sha(path)==before,'Source PPTX changed by render'
            baseline=json.loads((out/'来源与保全.json').read_text(encoding='utf8'))
            preservation=[dict(path=x['path'],unchanged=(ROOT/x['path']).stat().st_size==x['bytes'] and sha(ROOT/x['path'])==x['sha256'])
                          for category in ['sources','reference_files','unrelated_work'] for x in baseline[category]]
            with zipfile.ZipFile(path) as z:
                media={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('ppt/media/')}
                note_parts=[n for n in z.namelist() if n.startswith('ppt/notesSlides/notesSlide') and n.endswith('.xml')]
                ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
                note_paragraphs=[p for n in note_parts for p in ET.fromstring(z.read(n)).findall('.//a:p',ns)]
                note_text='\n'.join(''.join(p.itertext()) for p in note_paragraphs)
                actual_notes=(out/'本页备注.md').read_text(encoding='utf8')
                notes_ok=all(line in note_text for line in actual_notes.splitlines() if line.strip())
                original=(PI/'Why_PhD母稿_用户原文_20261005.md').read_text(encoding='utf8').strip()
                whyphd_verbatim=(all(line in note_text for line in original.splitlines() if line.strip()) if key=='S12' else None)
            derived=json.loads((out/'派生素材说明.json').read_text(encoding='utf8'))
            image_checks=[]
            for info,rec in zip(derived,pictures):
                img=Image.open(out/info['output']);source=Image.open(ROOT/info['source']);crop=source.crop(tuple(info['crop_box']))
                w,h=rec['rect_pt'][2:]
                image_checks.append(dict(name=rec['name'],crop_pixels_match=img.mode==crop.mode and img.tobytes()==crop.tobytes(),
                                         source_sha256_matches=sha(ROOT/info['source'])==info['source_sha256'],
                                         aspect_relative_error=abs((w/h)/(img.width/img.height)-1),embedded_bytes_match=info['sha256'] in media))
            sizes=[dict(size=list(Image.open(out/'预览'/f'{key}_{w}x{h}.png').size),expected=[w,h]) for w,h in [(3840,2160),(1920,1080)]]
            report=dict(renderer='Microsoft PowerPoint '+version,slides=1,logical_slide=key,
                        pptx_unchanged_by_readonly_render=True,export_sizes=sizes,text_overflow=overflow,
                        shapes_outside_canvas=outside,notes_complete=notes_ok,whyphd_original_verbatim=whyphd_verbatim,
                        image_checks=image_checks,source_and_reference_preservation=preservation,shapes=records)
            write(out/'排版与保全检查.json',report)
            summaries.append(dict(slide=key,renderer=report['renderer'],overflow=len(overflow),outside=len(outside),
                                  preserved=len(preservation),notes_complete=notes_ok,whyphd_original_verbatim=whyphd_verbatim))
            assert all(x['unchanged'] for x in preservation)
            assert notes_ok and whyphd_verbatim is not False
            assert all(x['size']==x['expected'] for x in sizes)
            assert all(x['crop_pixels_match'] and x['source_sha256_matches'] and x['embedded_bytes_match'] and x['aspect_relative_error']<1e-5 for x in image_checks)
            print(json.dumps(summaries[-1],ensure_ascii=False),flush=True)
    finally:
        app.AutomationSecurity=previous_security
        if app.Presentations.Count==0:app.Quit()
    write(REVIEW/'PowerPoint渲染汇总.json',summaries)
    return summaries

def contact_sheets():
    preview=REVIEW/'预览';preview.mkdir(exist_ok=True)
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',40)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25)
    def panel(canvas,im,label,caption,x,y,w=1840):
        draw=ImageDraw.Draw(canvas);draw.text((x,y),label,font=font,fill='#172B43')
        image=Image.open(im).convert('RGB');h=round(w*image.height/image.width)
        canvas.paste(image.resize((w,h),Image.Resampling.LANCZOS),(x,y+64))
        draw.text((x,y+64+h+18),caption,font=small,fill='#5C6D7E')
    def pic(k):return PI/NAMES[k]/'预览'/f'{k}_1920x1080.png'
    labels={'S10':('S10 · 反思','真实问题 / 保留 AI 对话语境'),
            'S11':('S11 · 表达','真实网页主视觉 / 个人艺术表达'),
            'S12':('S12 · Why PhD','四段索引 / speaker notes 完整保留本人原文'),
            'S13':('S13 · Why Liu','已有起点 → 希望深入 / 学习边界明确')}
    sheet=Image.new('RGB',(3840,2490),'#EAF0F3')
    for i,k in enumerate(['S10','S11','S12','S13']):panel(sheet,pic(k),*labels[k],40+(i%2)*1920,24+(i//2)*1230)
    sheet.save(preview/'S10-S13_联合审阅.png')
    for a,b in [('S10','S11'),('S12','S13')]:
        pair=Image.new('RGB',(3840,1240),'#EAF0F3')
        for i,k in enumerate([a,b]):panel(pair,pic(k),*labels[k],40+i*1920,24)
        pair.save(preview/f'{a}-{b}_双页审阅.png')
    pair=Image.new('RGB',(3840,1240),'#EAF0F3')
    panel(pair,pic('S1'),'S1 · 个人起点','背景 → 本科毕设 / 数据分析 / 个人探索',40,24)
    s2=PI/'本科毕设_S2-S5_v2.1_20261005/预览/S2.png'
    panel(pair,s2,'S2 · 本科毕设（现有 v2.1）','引用既有 PowerPoint 预览，未重做或修改 S2',1960,24)
    pair.save(preview/'S1-S2_衔接审阅.png')
    records=[dict(file=p.relative_to(REVIEW).as_posix(),size=list(Image.open(p).size),sha256=sha(p)) for p in sorted(preview.glob('*.png'))]
    write(REVIEW/'预览来源.json',dict(operation='Contact sheets of actual PowerPoint exports. Uniform proportional downsampling only; no merged PPT.',
                                    existing_s2_source=s2.relative_to(ROOT).as_posix(),existing_s2_sha256=sha(s2),files=records))

if __name__=='__main__':
    summaries=render();contact_sheets()
    assert all(x['overflow']==0 and x['outside']==0 for x in summaries), 'Repair reported typography before final delivery.'
