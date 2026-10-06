"""Read-only Microsoft PowerPoint 16.0 export and full-deck/source comparison."""
from pathlib import Path
import json, math, hashlib, re
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat
from pptx import Presentation
import win32com.client
import pymupdf
from merge_lossless import OUT, PI, ROOT, STEM, V4, sha, write_json

PREVIEW=OUT/'预览'
SOURCE=OUT/'检查证据'/'源候选渲染'

def note_from_com(slide):
    result=[]
    for i in range(1,slide.NotesPage.Shapes.Count+1):
        sh=slide.NotesPage.Shapes(i)
        try:
            if sh.PlaceholderFormat.Type==2 and sh.HasTextFrame:
                result.append(sh.TextFrame.TextRange.Text)
        except Exception:pass
    assert len(result)==1,len(result)
    return result[0].replace('\r\n','\n').replace('\r','\n')

def inspect_shapes(slide,width,height):
    records=[];outside=[];overflow=[]
    def walk(sh,path):
        x,y,w,h=[float(getattr(sh,a)) for a in ['Left','Top','Width','Height']]
        rec={'path':path,'name':sh.Name,'type':int(sh.Type),'rect_pt':[x,y,w,h],'rotation':float(sh.Rotation)}
        # These selected candidates do not use rotated/grouped visual geometry.
        if x<-.1 or y<-.1 or x+w>width+.1 or y+h>height+.1:outside.append(rec)
        if sh.Type==6:
            for j in range(1,sh.GroupItems.Count+1):walk(sh.GroupItems(j),path+f'/{j}')
        if sh.HasTextFrame and sh.TextFrame.HasText:
            tf=sh.TextFrame2;tr=tf.TextRange
            actual=[float(tr.BoundWidth),float(tr.BoundHeight)]
            allowed=[w-float(tf.MarginLeft+tf.MarginRight),h-float(tf.MarginTop+tf.MarginBottom)]
            rec.update(text=sh.TextFrame.TextRange.Text,text_bound_pt=actual,available_pt=allowed,
                       font_name=tr.Font.Name,font_size_pt=float(tr.Font.Size),
                       font_far_east=tr.Font.NameFarEast)
            if actual[0]>allowed[0]+1 or actual[1]>allowed[1]+1:overflow.append(rec)
        records.append(rec)
    for i in range(1,slide.Shapes.Count+1):walk(slide.Shapes(i),str(i))
    return {'shapes':records,'text_overflow':overflow,'objects_outside':outside}

def images_check(path):
    prs=Presentation(path);records=[]
    for n,s in enumerate(prs.slides,1):
        for sh in s.shapes:
            if sh.shape_type!=13:continue
            width,height=sh.image.size
            effective=width*(1-sh.crop_left-sh.crop_right)/(height*(1-sh.crop_top-sh.crop_bottom))
            display=sh.width/sh.height
            error=abs(display/effective-1)
            records.append({'page':n,'name':sh.name,'native_px':[width,height],
                'crop':[sh.crop_left,sh.crop_top,sh.crop_right,sh.crop_bottom],
                'display_ratio':display,'effective_image_ratio':effective,'relative_ratio_error':error,
                'pass':error<.003})
    return records

def render():
    PREVIEW.mkdir(exist_ok=True);SOURCE.mkdir(parents=True,exist_ok=True)
    rows=json.loads((OUT/'页码与来源映射.json').read_text(encoding='utf-8'))
    pptx=OUT/(STEM+'.pptx');before=sha(pptx)
    expected=Presentation(pptx)
    app=win32com.client.DispatchEx('PowerPoint.Application')
    version=str(app.Version);assert version=='16.0',version
    security=app.AutomationSecurity;app.AutomationSecurity=3
    pres=None;results=[];pdf=OUT/(STEM+'.pdf')
    try:
        pres=app.Presentations.Open(str(pptx),True,False,False)
        assert pres.Slides.Count==15
        size=[float(pres.PageSetup.SlideWidth),float(pres.PageSetup.SlideHeight)]
        for n,row in enumerate(rows,1):
            s=pres.Slides(n);key=row['logical']
            r=inspect_shapes(s,*size)
            r.update(page=n,logical=key,hidden=int(s.SlideShowTransition.Hidden)!=0,
                notes_exact_match=note_from_com(s)==expected.slides[n-1].notes_slide.notes_text_frame.text)
            for w,h in [(1920,1080),(3840,2160)]:
                s.Export(str(PREVIEW/f'{n:02d}_{key}_{w}x{h}.png'),'PNG',w,h)
            results.append(r)
            print(f'PowerPoint {version}: {n:02d} {key}; overflow={len(r["text_overflow"])} outside={len(r["objects_outside"])} notes={r["notes_exact_match"]}',flush=True)
        pres.SaveAs(str(pdf),32)
        pres.Close();pres=None
        # Render every selected source page in this same PowerPoint session.
        # Equal PNG pixels validate preservation of layout, fonts, images and themes.
        for source in dict.fromkeys(r['source'] for r in rows):
            src=PI/source;src_before=sha(src)
            pres=app.Presentations.Open(str(src),True,False,False)
            assert [float(pres.PageSetup.SlideWidth),float(pres.PageSetup.SlideHeight)]==size
            for row in [r for r in rows if r['source']==source]:
                n=row['page'];key=row['logical'];path=SOURCE/f'{n:02d}_{key}_source_1920x1080.png'
                s=pres.Slides(row['source_page'])
                s.Export(str(path),'PNG',1920,1080)
                source_notes=Presentation(src).slides[row['source_page']-1].notes_slide.notes_text_frame.text
                assert note_from_com(s)==source_notes
                a=Image.open(path).convert('RGB');b=Image.open(PREVIEW/f'{n:02d}_{key}_1920x1080.png').convert('RGB')
                assert a.size==b.size==(1920,1080)
                diff=ImageChops.difference(a,b);box=diff.getbbox()
                results[n-1]['source_render_comparison']={'pixel_identical':box is None,'difference_bbox':box,
                    'source_png_sha256':sha(path),'full_png_sha256':sha(PREVIEW/f'{n:02d}_{key}_1920x1080.png')}
                print(f'Source comparison {n:02d} {key}: pixel_identical={box is None}',flush=True)
            pres.Close();pres=None
            assert sha(src)==src_before
    finally:
        if pres is not None:pres.Close()
        app.AutomationSecurity=security
        if app.Presentations.Count==0:app.Quit()
    assert sha(pptx)==before,'Rendering must not rewrite the PPTX'
    doc=pymupdf.open(pdf);assert len(doc)==15
    pdf_records=[]
    for i,page in enumerate(doc):
        rect=page.rect
        fonts=sorted({f[3] for f in page.get_fonts(full=True)})
        embedded=[]
        for f in page.get_fonts(full=True):
            font=doc.extract_font(f[0]);embedded.append({'font':f[3],'embedded':bool(font[3]),'format':font[1]})
        pdf_records.append({'page':i+1,'size_pt':[rect.width,rect.height],
            'text_chars':len(page.get_text()),'fonts':fonts,'font_embedding':embedded})
        assert abs(rect.width-size[0])<.01 and abs(rect.height-size[1])<.01
    doc.close()
    images=images_check(pptx)
    report={'renderer':'Microsoft PowerPoint '+version,'opened_in_real_powerpoint':True,
        'checked_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),
        'pdf_export':'PowerPoint Presentation.SaveAs ppSaveAsPDF (32)',
        'pptx_sha256_before':before,'pptx_sha256_after':sha(pptx),'pptx_unchanged_by_render':True,
        'physical_slides':15,'slide_size_pt':size,'pdf_pages':pdf_records,'slides':results,
        'images':images,'text_overflow_count':sum(len(r['text_overflow']) for r in results),
        'objects_outside_count':sum(len(r['objects_outside']) for r in results),
        'notes_matches':sum(r['notes_exact_match'] for r in results),
        'pixel_identical_slides':sum(r['source_render_comparison']['pixel_identical'] for r in results),
        'image_ratio_failures':sum(not r['pass'] for r in images),'pdf_sha256':sha(pdf)}
    write_json(OUT/'PowerPoint实际导出与排版检查.json',report)
    assert report['text_overflow_count']==report['objects_outside_count']==report['image_ratio_failures']==0
    assert report['notes_matches']==report['pixel_identical_slides']==15
    assert not any(r['hidden'] for r in results)
    return rows,report

def overviews(rows):
    fontfile='C:/Windows/Fonts/msyh.ttc'
    title_font=ImageFont.truetype(fontfile,36);small_font=ImageFont.truetype(fontfile,23)
    cols=3;tilew=960;tileh=540;gap=24;labelh=46;header=100
    width=gap+cols*(tilew+gap);height=header+5*(tileh+labelh+gap)+gap
    overview=Image.new('RGB',(width,height),'#EAF0F3');draw=ImageDraw.Draw(overview)
    draw.text((24,22),'INTERNAL / FULL DRAFT v0.1 · S0–S13 · 15 frames',font=title_font,fill='#172B43')
    for j,row in enumerate(rows):
        x=gap+(j%cols)*(tilew+gap);y=header+(j//cols)*(tileh+labelh+gap)
        label=f'{j+1:02d} / 15  ·  {row["logical"]}'
        if row['logical']=='S10':label+=' · 方案 A'
        if row['logical']=='S13':label+=' · 页面 v2 / 口述 v4'
        draw.text((x,y),label,font=small_font,fill='#172B43')
        img=Image.open(PREVIEW/f'{j+1:02d}_{row["logical"]}_1920x1080.png').convert('RGB')
        overview.paste(img.resize((tilew,tileh),Image.Resampling.LANCZOS),(x,y+labelh))
    overview.save(PREVIEW/'全部15页_总览.png')
    tilew=1920;tileh=1080;labelh=64;gap=24;header=96
    strip=Image.new('RGB',(1968,header+len(rows)*(tileh+labelh+gap)+24),'#EAF0F3')
    draw=ImageDraw.Draw(strip);draw.text((24,20),'INTERNAL / FULL DRAFT v0.1 · 全部页面连续审阅',font=title_font,fill='#172B43')
    for j,row in enumerate(rows):
        y=header+j*(tileh+labelh+gap)
        draw.text((24,y),f'{j+1:02d} / 15 · {row["logical"]}'+(' · 页面 v2 / speaker notes v4' if row['logical']=='S13' else ''),font=title_font,fill='#172B43')
        strip.paste(Image.open(PREVIEW/f'{j+1:02d}_{row["logical"]}_1920x1080.png').convert('RGB'),(24,y+labelh))
    strip.save(PREVIEW/'全部15页_连续审阅_纵向.png')
    # Local, self-contained review navigation. All images are native PowerPoint exports.
    sections=[]
    for r in rows:
        n=r['page'];key=r['logical'];name=f'{n:02d}_{key}_1920x1080.png'
        sections.append(f'<section id="p{n}"><h2>{n:02d} / 15 · {key}</h2><a href="{n:02d}_{key}_3840x2160.png"><img loading="lazy" src="{name}" alt="第{n}页 {key}"></a><p><a href="../逐页备注/{n:02d}_{key}.md">逐页备注</a></p></section>')
    html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FULL DRAFT v0.1 连续审阅</title><style>body{margin:0;background:#eaf0f3;color:#172b43;font:16px "Microsoft YaHei",sans-serif}header{position:sticky;top:0;background:#fff;padding:12px 24px;box-shadow:0 2px 8px #0001}nav{display:flex;gap:12px;flex-wrap:wrap}a{color:#176b80}main{max-width:1440px;margin:auto;padding:24px}section{scroll-margin-top:120px;margin:0 0 36px}img{width:100%;height:auto;box-shadow:0 4px 18px #0001}h1{font-size:20px;margin:0 0 10px}h2{font-size:20px}p{margin:10px 0}</style><header><h1>INTERNAL / FULL DRAFT v0.1 · 全部 15 页</h1><nav>'''+''.join(f'<a href="#p{r["page"]}">{r["page"]:02d} {r["logical"]}</a>' for r in rows)+'''</nav></header><main>'''+''.join(sections)+'''</main></html>'''
    (PREVIEW/'连续审阅.html').write_text(html,encoding='utf-8')
    print(f'Overview {overview.size}; continuous strip {strip.size}; local HTML exported',flush=True)

if __name__=='__main__':
    rows,report=render();overviews(rows)
    print(json.dumps({k:report[k] for k in ['renderer','physical_slides','notes_matches','pixel_identical_slides','text_overflow_count','objects_outside_count','image_ratio_failures']},ensure_ascii=False),flush=True)
