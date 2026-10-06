"""Read-only PowerPoint export and preservation checks for the v1.1 revision."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json, html
from PIL import Image, ImageChops, ImageDraw, ImageFont
from pptx import Presentation
import win32com.client
import pymupdf
from build_v1_1 import OUT, PI, SOURCE, STEM, DECK, KEYS, sha, jwrite

PREVIEW=OUT/'预览'
EVIDENCE=OUT/'检查证据'

def notes(slide):
    found=[]
    for sh in slide.NotesPage.Shapes:
        try:
            if sh.PlaceholderFormat.Type==2 and sh.HasTextFrame:found.append(sh.TextFrame.TextRange.Text)
        except Exception:pass
    assert len(found)==1
    return found[0].replace('\r\n','\n').replace('\r','\n')

def geometry(slide,width,height):
    shapes=[];outside=[];overflow=[]
    def walk(sh,path):
        x,y,w,h=[float(getattr(sh,a)) for a in ['Left','Top','Width','Height']]
        r={'path':path,'name':sh.Name,'type':int(sh.Type),'rect_pt':[x,y,w,h]}
        if x<-.1 or y<-.1 or x+w>width+.1 or y+h>height+.1:outside.append(r)
        if sh.Type==6:
            for i in range(1,sh.GroupItems.Count+1):walk(sh.GroupItems(i),path+f'/{i}')
        if sh.HasTextFrame and sh.TextFrame.HasText:
            tf=sh.TextFrame2;tr=tf.TextRange
            actual=[float(tr.BoundWidth),float(tr.BoundHeight)]
            available=[w-float(tf.MarginLeft+tf.MarginRight),h-float(tf.MarginTop+tf.MarginBottom)]
            r.update(text=sh.TextFrame.TextRange.Text,text_bound_pt=actual,available_pt=available)
            if actual[0]>available[0]+1 or actual[1]>available[1]+1:overflow.append(r)
        shapes.append(r)
    for i in range(1,slide.Shapes.Count+1):walk(slide.Shapes(i),str(i))
    return {'shapes':shapes,'objects_outside':outside,'text_overflow':overflow}

def export():
    PREVIEW.mkdir(exist_ok=True)
    (EVIDENCE/'基线全页').mkdir(exist_ok=True)
    (EVIDENCE/'PowerPoint备注读回').mkdir(exist_ok=True)
    source_hash=sha(SOURCE);out_hash=sha(DECK)
    expected=Presentation(DECK)
    app=win32com.client.Dispatch('PowerPoint.Application')
    version=app.Version;security=app.AutomationSecurity;app.AutomationSecurity=3
    pres=None;rows=[]
    try:
        pres=app.Presentations.Open(str(DECK),True,False,False)
        assert pres.Slides.Count==15
        size=[float(pres.PageSetup.SlideWidth),float(pres.PageSetup.SlideHeight)]
        for n,key in enumerate(KEYS,1):
            s=pres.Slides(n)
            r=geometry(s,*size)
            readback=notes(s)
            r.update(page=n,logical=key,notes_exact=readback==expected.slides[n-1].notes_slide.notes_text_frame.text,
                     hidden=int(s.SlideShowTransition.Hidden)!=0)
            (EVIDENCE/'PowerPoint备注读回'/f'{n:02d}_{key}.txt').write_text(readback,encoding='utf-8')
            for w,h in [(1920,1080),(3840,2160)]:s.Export(str(PREVIEW/f'{n:02d}_{key}_{w}x{h}.png'),'PNG',w,h)
            rows.append(r)
            print(f'{n:02d} {key}: overflow={len(r["text_overflow"])}; outside={len(r["objects_outside"])}; notes={r["notes_exact"]}',flush=True)
        pres.SaveAs(str(OUT/(STEM+'.pdf')),32)
        pres.Close();pres=None
        pres=app.Presentations.Open(str(SOURCE),True,False,False)
        for n,key in enumerate(KEYS,1):
            p=EVIDENCE/'基线全页'/f'{n:02d}_{key}_1920x1080.png'
            pres.Slides(n).Export(str(p),'PNG',1920,1080)
            diff=ImageChops.difference(Image.open(p).convert('RGB'),Image.open(PREVIEW/f'{n:02d}_{key}_1920x1080.png').convert('RGB'))
            rows[n-1]['source_comparison']={'pixel_identical':diff.getbbox() is None,'difference_bbox':diff.getbbox()}
            if n<=13:assert diff.getbbox() is None,(n,key,diff.getbbox())
        pres.Close();pres=None
    finally:
        if pres is not None:pres.Close()
        app.AutomationSecurity=security
        if app.Presentations.Count==0:app.Quit()
    assert sha(SOURCE)==source_hash and sha(DECK)==out_hash
    pdf=pymupdf.open(OUT/(STEM+'.pdf'));assert len(pdf)==15
    pages=[]
    for n,p in enumerate(pdf,1):
        fonts=[{'name':f[3],'embedded':bool(pdf.extract_font(f[0])[3])} for f in p.get_fonts(full=True)]
        pages.append({'page':n,'size_pt':[p.rect.width,p.rect.height],'fonts':fonts})
        assert abs(p.rect.width-size[0])<.01 and abs(p.rect.height-size[1])<.01
    pdf.close()
    report={'checked_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'renderer':'Microsoft PowerPoint '+version,
      'source_sha256':source_hash,'output_sha256':out_hash,'pdf_sha256':sha(OUT/(STEM+'.pdf')),
      'opened_read_only_and_originals_unchanged':True,'slide_count':15,'png_count':30,
      'text_overflow_count':sum(len(r['text_overflow']) for r in rows),
      'objects_outside_count':sum(len(r['objects_outside']) for r in rows),
      'notes_matches':sum(r['notes_exact'] for r in rows),
      'S0_S11_pixel_identical':all(r['source_comparison']['pixel_identical'] for r in rows[:13]),
      'pdf_all_fonts_embedded':all(f['embedded'] for p in pages for f in p['fonts']),
      'pdf_pages':pages,'slides':rows}
    jwrite(OUT/'PowerPoint导出与检查.json',report)
    assert report['text_overflow_count']==report['objects_outside_count']==0
    assert report['notes_matches']==15 and report['pdf_all_fonts_embedded']
    assert not any(r['hidden'] for r in rows)
    return report

def overviews():
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',36)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
    gap=24;tw=960;th=540;lh=46;header=100
    sheet=Image.new('RGB',(2976,3174),'#EAF0F3');draw=ImageDraw.Draw(sheet)
    draw.text((24,22),'完整 PPT v1.1 · S0–S13 · 15 页',font=font,fill='#172B43')
    for i,key in enumerate(KEYS):
        x=gap+(i%3)*(tw+gap);y=header+(i//3)*(th+lh+gap)
        draw.text((x,y),f'{i+1:02d} / 15 · {key}',font=small,fill='#172B43')
        im=Image.open(PREVIEW/f'{i+1:02d}_{key}_1920x1080.png').convert('RGB')
        sheet.paste(im.resize((tw,th),Image.Resampling.LANCZOS),(x,y+lh))
    sheet.save(PREVIEW/'全部15页_总览.png')
    strip=Image.new('RGB',(1968,17640),'#EAF0F3');draw=ImageDraw.Draw(strip)
    draw.text((24,20),'完整 PPT v1.1 · 全部页面连续审阅',font=font,fill='#172B43')
    for i,key in enumerate(KEYS):
        y=96+i*(1080+64+24)
        draw.text((24,y),f'{i+1:02d} / 15 · {key}',font=font,fill='#172B43')
        strip.paste(Image.open(PREVIEW/f'{i+1:02d}_{key}_1920x1080.png').convert('RGB'),(24,y+64))
    strip.save(PREVIEW/'全部15页_连续审阅_纵向.png')
    closing=Image.new('RGB',(1968,3624),'#EAF0F3');draw=ImageDraw.Draw(closing)
    draw.text((24,20),'S11 → S12 → S13 · v1.1 结尾连续审阅',font=font,fill='#172B43')
    for j,n in enumerate([13,14,15]):
        y=96+j*1168;key=KEYS[n-1]
        draw.text((24,y),f'{n:02d} / 15 · {key}',font=font,fill='#172B43')
        closing.paste(Image.open(PREVIEW/f'{n:02d}_{key}_1920x1080.png').convert('RGB'),(24,y+64))
    closing.save(PREVIEW/'S11-S13_连续审阅.png')
    nav=''.join(f'<a href="#p{i+1}">{key}</a>' for i,key in enumerate(KEYS))
    sections=''.join(f'<section id="p{i+1}"><h2>{i+1:02d} / 15 · {key}</h2><a href="{i+1:02d}_{key}_3840x2160.png"><img loading="lazy" src="{i+1:02d}_{key}_1920x1080.png" alt="{key}"></a><p><a href="{i+1:02d}_{key}_1920x1080.png">1080p PNG</a> · <a href="{i+1:02d}_{key}_3840x2160.png">4K PNG</a> · <a href="../逐页备注/{i+1:02d}_{key}.md">Speaker notes</a></p></section>' for i,key in enumerate(KEYS))
    markup='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>完整 PPT v1.1 连续审阅</title><style>body{margin:0;background:#eaf0f3;color:#172b43;font:16px "Microsoft YaHei",sans-serif}header{position:sticky;top:0;background:white;padding:12px 24px;box-shadow:0 2px 8px #0001}nav{display:flex;gap:14px;flex-wrap:wrap}a{color:#007e86}main{max-width:1440px;margin:auto;padding:24px}section{scroll-margin-top:120px;margin-bottom:36px}img{width:100%;height:auto}h1,h2{font-size:20px}h1{margin:0 0 10px}</style><header><h1>完整 PPT v1.1 · 15 页</h1><nav>'''+nav+'</nav></header><main>'+sections+'</main></html>'
    (PREVIEW/'连续审阅.html').write_text(markup,encoding='utf-8')
    print('30 PNGs, full overview, continuous strip, closing strip and review HTML ready.',flush=True)

if __name__=='__main__':
    export()
    overviews()
