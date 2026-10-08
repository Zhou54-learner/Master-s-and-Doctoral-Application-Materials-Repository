"""Render only S7 in Microsoft PowerPoint 16.0 and audit layout/source integrity."""
from pathlib import Path
import hashlib
import json
import zipfile
from PIL import Image
import win32com.client

OUT=Path(__file__).resolve().parent.parent
ROOT=next(p for p in OUT.parents if (p/'申请路线总览.md').exists())
PREVIEW=OUT/'预览'
path=OUT/'S7_乐音研究_v1.pptx'
app=win32com.client.DispatchEx('PowerPoint.Application')
version=str(app.Version)
assert version=='16.0',version
previous_security=app.AutomationSecurity;app.AutomationSecurity=3
deck=None;overflow=[];outside=[];shapes=[];pictures=[]
try:
    deck=app.Presentations.Open(str(path),True,False,False)
    assert deck.Slides.Count==1
    slide=deck.Slides(1)
    slide.Export(str(PREVIEW/'S7_3840x2160.png'),'PNG',3840,2160)
    slide.Export(str(PREVIEW/'S7_1920x1080.png'),'PNG',1920,1080)
    deck.SaveAs(str(OUT/'S7_乐音研究_v1.pdf'),32)
    for i in range(1,slide.Shapes.Count+1):
        shape=slide.Shapes(i)
        x,y,w,h=[float(getattr(shape,a)) for a in ['Left','Top','Width','Height']]
        rec=dict(name=shape.Name,rect_pt=[x,y,w,h])
        if x<-.1 or y<-.1 or x+w>float(deck.PageSetup.SlideWidth)+.1 or y+h>float(deck.PageSetup.SlideHeight)+.1:outside.append(rec)
        if shape.HasTextFrame and shape.TextFrame.HasText:
            tf=shape.TextFrame2;tr=tf.TextRange
            actual=[float(tr.BoundWidth),float(tr.BoundHeight)]
            allowed=[float(w-tf.MarginLeft-tf.MarginRight),float(h-tf.MarginTop-tf.MarginBottom)]
            rec.update(text=shape.TextFrame.TextRange.Text,text_bound_pt=actual,available_pt=allowed,font_name=tr.Font.Name)
            if actual[0]>allowed[0]+1 or actual[1]>allowed[1]+1:overflow.append(rec)
        if shape.Type==13:
            rec['crop_pt']=[float(getattr(shape.PictureFormat,'Crop'+a)) for a in ['Left','Top','Right','Bottom']]
            pictures.append(rec)
        shapes.append(rec)
finally:
    if deck is not None:deck.Close()
    app.AutomationSecurity=previous_security
    if app.Presentations.Count==0:app.Quit()

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((OUT/'来源与保全.json').read_text(encoding='utf8'))
preserved=[dict(path=x['path'],unchanged=Path(x['path']).stat().st_size==x['bytes'] and sha(Path(x['path']))==x['sha256']) for key in ['sources','reference_files','unrelated_work'] for x in baseline[key]]
assert all(x['unchanged'] for x in preserved)
with zipfile.ZipFile(path) as archive:
    media={hashlib.sha256(archive.read(n)).hexdigest() for n in archive.namelist() if n.startswith('ppt/media/')}
derived=json.loads((OUT/'派生素材说明.json').read_text(encoding='utf8'))
image_checks=[]
for info,name in zip(derived,['historical_waveform_and_spectrum','historical_demonstration_frame']):
    crop=Image.open(OUT/info['output']).convert('RGB')
    original=Image.open(OUT/info['original_frame'] if 'original_frame' in info else info['source']).convert('RGB')
    identical=original.crop(tuple(info['crop_box'])).tobytes()==crop.tobytes()
    shape=next(x for x in pictures if x['name']==name)
    w,h=shape['rect_pt'][2:]
    error=abs((w/h)/(crop.width/crop.height)-1)
    image_checks.append(dict(name=name,crop_pixels_match=identical,aspect_relative_error=error,embedded_bytes_match=info['sha256'] in media))
    assert identical and error<1e-5 and info['sha256'] in media
assert all(all(abs(v)<.01 for v in x['crop_pt']) for x in pictures)
report=dict(renderer='Microsoft PowerPoint '+version,slides=1,export_sizes=[list(Image.open(PREVIEW/n).size) for n in ['S7_3840x2160.png','S7_1920x1080.png']],text_overflow=overflow,shapes_outside_canvas=outside,images=image_checks,source_and_reference_preservation=preserved,shapes=shapes)
(OUT/'排版与保全检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(renderer=report['renderer'],overflow=overflow,outside=outside,preserved=len(preserved)),ensure_ascii=False))
assert not overflow and not outside

# Review-only contact sheet; do not create or modify a combined presentation.
ref=OUT.parent/'本科毕设_S2-S5_v2.1_20261005/预览'
comparison=[ref/'S4.png',ref/'S5.png',OUT.parent/'S6_尘埃等离子体_v1_20261005/预览/S6_1920x1080.png',PREVIEW/'S7_1920x1080.png']
sheet=Image.new('RGB',(1944,1116),'#e5eaf0')
for i,p in enumerate(comparison):
    im=Image.open(p).convert('RGB');im.thumbnail((954,537))
    sheet.paste(im,(12+(i%2)*972,12+(i//2)*558))
sheet.save(PREVIEW/'S4-S7_风格对照.png')
