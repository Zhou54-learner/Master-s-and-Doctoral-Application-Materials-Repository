"""Open and render S8 + both S9 frames in Microsoft PowerPoint; verify historical pixels.
Dependencies: pywin32, Pillow. Run after build_pair.py.
Only opens the new candidates; S2-S7 files remain read only.
"""
from pathlib import Path
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import win32com.client

S8=Path(__file__).resolve().parent.parent
PI=S8.parent;S9=PI/'S9_长期AI协作_v1_20261005'
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

app=win32com.client.DispatchEx('PowerPoint.Application')
version=str(app.Version)
previous_security=app.AutomationSecurity;app.AutomationSecurity=3
summaries=[]
try:
    for out,stem,frames in [(S8,'S8_项目级AI协作_v1',['S8']),
                            (S9,'S9_长期AI协作_v1',['S9-A','S9-B'])]:
        path=out/(stem+'.pptx');deck=None
        overflow=[];outside=[];shape_records=[];pictures=[]
        try:
            deck=app.Presentations.Open(str(path),True,False,False)
            assert deck.Slides.Count==len(frames)
            for i,frame in enumerate(frames,1):
                slide=deck.Slides(i)
                for w,h in [(3840,2160),(1920,1080)]:
                    slide.Export(str(out/'预览'/f'{frame}_{w}x{h}.png'),'PNG',w,h)
                for j in range(1,slide.Shapes.Count+1):
                    shape=slide.Shapes(j)
                    x,y,w,h=[float(getattr(shape,a)) for a in ['Left','Top','Width','Height']]
                    rec=dict(frame=frame,name=shape.Name,rect_pt=[x,y,w,h])
                    if x<-.1 or y<-.1 or x+w>float(deck.PageSetup.SlideWidth)+.1 or y+h>float(deck.PageSetup.SlideHeight)+.1:
                        outside.append(rec)
                    if shape.HasTextFrame and shape.TextFrame.HasText:
                        tf=shape.TextFrame2;tr=tf.TextRange
                        actual=[float(tr.BoundWidth),float(tr.BoundHeight)]
                        allowed=[w-float(tf.MarginLeft+tf.MarginRight),h-float(tf.MarginTop+tf.MarginBottom)]
                        rec.update(text=shape.TextFrame.TextRange.Text,text_bound_pt=actual,available_pt=allowed,font_name=tr.Font.Name)
                        if actual[0]>allowed[0]+1 or actual[1]>allowed[1]+1:overflow.append(rec)
                    if shape.Type==13:
                        rec['crop_pt']=[float(getattr(shape.PictureFormat,'Crop'+a)) for a in ['Left','Top','Right','Bottom']]
                        pictures.append(rec)
                    shape_records.append(rec)
            deck.SaveAs(str(out/(stem+'.pdf')),32)
        finally:
            if deck is not None:deck.Close()
        baseline=json.loads((out/'来源与保全.json').read_text(encoding='utf8'))
        preserved=[dict(path=x['path'],unchanged=(ROOT/x['path']).stat().st_size==x['bytes'] and sha(ROOT/x['path'])==x['sha256'])
                   for key in ['sources','reference_files','unrelated_work'] for x in baseline[key]]
        with zipfile.ZipFile(path) as z:
            media={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('ppt/media/')}
            note_xml=[n for n in z.namelist() if n.startswith('ppt/notesSlides/notesSlide') and n.endswith('.xml')]
            note_texts=[''.join(ET.fromstring(z.read(n)).itertext()) for n in note_xml]
        transition='但项目做完以后，我又遇到一个新的问题：如果 AI 真要进入我的日常工作，它不能每一次都从零开始。'
        notes_ok=len(note_xml)==len(frames) and all(transition in n for n in note_texts)
        derived=json.loads((out/'派生素材说明.json').read_text(encoding='utf8'))
        names=['historical_agent'] if out==S8 else ['historical_map','historical_cockpit']
        images=[]
        for info,name in zip(derived,names):
            crop=Image.open(out/info['output']);source=Image.open(ROOT/info['source'])
            original_crop=source.crop(tuple(info['crop_box']))
            identical=crop.mode==original_crop.mode and crop.tobytes()==original_crop.tobytes()
            pic=next(x for x in pictures if x['name']==name)
            w,h=pic['rect_pt'][2:]
            error=abs((w/h)/(crop.width/crop.height)-1)
            images.append(dict(name=name,source_sha256_matches=sha(ROOT/info['source'])==info['source_sha256'],
                               crop_pixels_match=identical,aspect_relative_error=error,embedded_bytes_match=info['sha256'] in media))
        exports=[dict(frame=f,size=list(Image.open(out/'预览'/f'{f}_{w}x{h}.png').size)) for f in frames for w,h in [(3840,2160),(1920,1080)]]
        report=dict(renderer='Microsoft PowerPoint '+version,slides=len(frames),logical_topics=1,
                    export_sizes=exports,text_overflow=overflow,shapes_outside_canvas=outside,
                    notes_and_exact_transition_present=notes_ok,images=images,
                    source_and_reference_preservation=preserved,shapes=shape_records)
        (out/'排版与保全检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
        assert all(x['unchanged'] for x in preserved)
        assert notes_ok
        assert all(x['crop_pixels_match'] and x['aspect_relative_error']<1e-5 and x['embedded_bytes_match'] and x['source_sha256_matches'] for x in images)
        assert not overflow and not outside,(overflow,outside)
        summaries.append(dict(folder=out.name,renderer=report['renderer'],frames=frames,overflow=len(overflow),outside=len(outside),preserved=len(preserved)))
finally:
    app.AutomationSecurity=previous_security
    if app.Presentations.Count==0:app.Quit()

# Review artifacts are made from actual PowerPoint exports; no combined deck.
font_path='C:/Windows/Fonts/msyh.ttc'
font=ImageFont.truetype(font_path,44);small=ImageFont.truetype(font_path,26)
paths=[PI/'S7_乐音研究_v1_20261005/预览/S7_1920x1080.png', S8/'预览/S8_1920x1080.png']
for frame in ['A','B']:
    sheet=Image.new('RGB',(3840,890),'#EAF0F3');draw=ImageDraw.Draw(sheet)
    labels=[('S7 · 探究','把好奇的问题做成真实研究'),('S8 · 项目级协作','组织 AI，形成结果，再复盘'),('S9 · 长期协作','长期目标 → 当前状态 → 下一步')]
    for i,(path,(label,caption)) in enumerate(zip(paths+[S9/'预览'/f'S9-{frame}_1920x1080.png'],labels)):
        x=24+i*1280
        draw.text((x+4,20),label,font=font,fill='#172B43')
        im=Image.open(path).convert('RGB').resize((1232,693),Image.Resampling.LANCZOS)
        sheet.paste(im,(x,91))
        draw.text((x+4,808),caption,font=small,fill='#007E86')
    sheet.save(S8/'预览'/f'S7-S9_三页叙事对照_{frame}.png')
print(json.dumps(summaries,ensure_ascii=False))
