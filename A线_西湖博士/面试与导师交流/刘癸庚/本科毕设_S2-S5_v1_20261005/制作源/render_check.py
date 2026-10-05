"""Open this deck only, export with installed PowerPoint, inspect text bounds.
No changes to the user's open presentations. No macro execution.
"""
from pathlib import Path
import json
import win32com.client
from PIL import Image, ImageOps, ImageDraw

out=Path(__file__).resolve().parent.parent
preview=out/'预览';preview.mkdir(exist_ok=True)
app=win32com.client.DispatchEx('PowerPoint.Application')
app.AutomationSecurity=3
deck=None
try:
    deck=app.Presentations.Open(str(out/'本科毕设_S2-S5_v1.pptx'),True,False,False)
    records=[]
    for i in range(1,deck.Slides.Count+1):
        slide=deck.Slides(i)
        slide.Export(str(preview/f'S{i+1}.png'),'PNG',1920,1080)
        for j in range(1,slide.Shapes.Count+1):
            sh=slide.Shapes(j)
            if sh.HasTextFrame and sh.TextFrame.HasText:
                tf=sh.TextFrame2; tr=tf.TextRange
                bh,bw=float(tr.BoundHeight),float(tr.BoundWidth)
                allowed_h=float(sh.Height-tf.MarginTop-tf.MarginBottom)
                allowed_w=float(sh.Width-tf.MarginLeft-tf.MarginRight)
                if bh>allowed_h+1.5 or bw>allowed_w+1.5:
                    records.append({'slide':i+1,'shape':j,'text':sh.TextFrame.TextRange.Text,'bound':[bw,bh],'available':[allowed_w,allowed_h]})
    deck.SaveAs(str(out/'本科毕设_S2-S5_v1.pdf'),32)
    (out/'排版检查.json').write_text(json.dumps({'renderer':'Microsoft PowerPoint '+app.Version,'slides':deck.Slides.Count,'canvas':[1920,1080],'text_overflow':records},ensure_ascii=False,indent=2),encoding='utf-8')
finally:
    if deck is not None: deck.Close()
    app.Quit()
sheet=Image.new('RGB',(1600,940),'#e5eaf0')
for i in range(4):
    im=Image.open(preview/f'S{i+2}.png'); im.thumbnail((784,441))
    sheet.paste(im,(8+(i%2)*800,8+(i//2)*465))
sheet.save(preview/'四页总览.png')
print(json.dumps({'slide_count':4,'overflow_count':len(records)},ensure_ascii=False))
