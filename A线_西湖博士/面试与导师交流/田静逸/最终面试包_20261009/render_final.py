from pathlib import Path
import json, zipfile, math
import win32com.client
import pymupdf
from PIL import Image, ImageDraw
OUT=Path(__file__).resolve().parent
PPT=OUT/'田静逸_最终面试PPT_20261009.pptx'
(OUT/'预览').mkdir(exist_ok=True)
app=win32com.client.DispatchEx('PowerPoint.Application')
p=app.Presentations.Open(str(PPT),True,False,False)
issues=[];notes=[]
try:
    for sl in p.Slides:
        for sh in sl.Shapes:
            if sh.Left<-.5 or sh.Top<-.5 or sh.Left+sh.Width>p.PageSetup.SlideWidth+.5 or sh.Top+sh.Height>p.PageSetup.SlideHeight+.5:
                issues.append({'page':sl.SlideIndex,'shape':sh.Name,'type':'out_of_bounds'})
            if sh.HasTextFrame and sh.TextFrame.HasText:
                tf=sh.TextFrame2
                if tf.TextRange.BoundHeight > sh.Height-tf.MarginTop-tf.MarginBottom+2:
                    issues.append({'page':sl.SlideIndex,'shape':sh.Name,'type':'overflow','text':sh.TextFrame.TextRange.Text,'bound':tf.TextRange.BoundHeight,'height':sh.Height})
        sl.Export(str(OUT/'预览'/f'{sl.SlideIndex:02d}.png'),'PNG',1920,1080)
        notes.append('\n'.join(sh.TextFrame.TextRange.Text for sh in sl.NotesPage.Shapes if sh.HasTextFrame and sh.TextFrame.HasText))
    p.SaveAs(str(OUT/'田静逸_最终面试PPT_20261009.pdf'),32)
finally:
    p.Close();app.Quit()
pdf=pymupdf.open(OUT/'田静逸_最终面试PPT_20261009.pdf')
assert len(pdf)==15
thumb=Image.new('RGB',(1500,5*300),(228,233,239))
for i in range(15):
    im=Image.open(OUT/'预览'/f'{i+1:02d}.png');im.thumbnail((488,274))
    x=6+(i%3)*500;y=6+(i//3)*300;thumb.paste(im,(x,y));ImageDraw.Draw(thumb).text((x+3,y+277),str(i+1),fill='black')
thumb.save(OUT/'15页总览.jpg',quality=91)
with zipfile.ZipFile(PPT) as z:
    external=[n for n in z.namelist() if n.endswith('.rels') and b'TargetMode="External"' in z.read(n)]
source=json.loads((OUT/'页面与备注源.json').read_text(encoding='utf-8'))
matched=[x['notes'].replace('\n','').replace('\r','') in n.replace('\n','').replace('\r','') for x,n in zip(source,notes)]
report={'pages':15,'pdf_pages':len(pdf),'render':'Microsoft PowerPoint','issues':issues,'notes_com_matched':matched,'external_relationships':external}
(OUT/'版式与备注验收.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
