from pathlib import Path
import json,zipfile
import win32com.client
from PIL import Image,ImageOps,ImageDraw
OUT=Path(__file__).resolve().parent
PPT=OUT/'周子靖_田静逸交流_12页修订版_v1_20261008.pptx'
app=win32com.client.DispatchEx('PowerPoint.Application')
p=app.Presentations.Open(str(PPT),True,False,False)
(OUT/'预览').mkdir(exist_ok=True)
issues=[]
try:
    for sl in p.Slides:
        for sh in sl.Shapes:
            if sh.Left<-.5 or sh.Top<-.5 or sh.Left+sh.Width>p.PageSetup.SlideWidth+.5 or sh.Top+sh.Height>p.PageSetup.SlideHeight+.5:
                issues.append({'page':sl.SlideIndex,'shape':sh.Name,'type':'out_of_bounds'})
            if sh.HasTextFrame and sh.TextFrame.HasText:
                tf=sh.TextFrame2
                if tf.TextRange.BoundHeight > sh.Height-tf.MarginTop-tf.MarginBottom+2:
                    issues.append({'page':sl.SlideIndex,'shape':sh.Name,'type':'text_overflow','text':sh.TextFrame.TextRange.Text,'bound':tf.TextRange.BoundHeight,'height':sh.Height})
        sl.Export(str(OUT/'预览'/f'{sl.SlideIndex:02d}.png'),'PNG',1600,900)
    p.SaveAs(str(OUT/'周子靖_田静逸交流_12页修订版_v1_20261008.pdf'),32)
finally:
    p.Close();app.Quit()
with zipfile.ZipFile(PPT) as z:
    external=[n for n in z.namelist() if n.endswith('.rels') and b'TargetMode="External"' in z.read(n)]
thumb=Image.new('RGB',(1600,6*470),(227,234,239))
for i in range(12):
    im=Image.open(OUT/'预览'/f'{i+1:02d}.png');im.thumbnail((780,439));x=10+(i%2)*800;y=10+(i//2)*470;thumb.paste(im,(x,y));ImageDraw.Draw(thumb).text((x+3,y+442),str(i+1),fill='black')
thumb.save(OUT/'12页总览.jpg',quality=90)
report={'pages':12,'render':'Microsoft PowerPoint','issues':issues,'external_relationships':external}
(OUT/'版式检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
