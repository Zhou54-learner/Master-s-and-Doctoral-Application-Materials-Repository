"""Actual PowerPoint 16.0 export and geometry/notes/media QA for S7 only."""
from pathlib import Path
import json, hashlib, zipfile, subprocess
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
import win32com.client
OUT=Path(__file__).resolve().parent.parent
PRE=OUT/'预览';QA=OUT/'检查证据'
names={'A':'S7_乐音研究_v2_A_历史资产优先','B':'S7_乐音研究_v2_B_历史与复盘并置'}
app=win32com.client.DispatchEx('PowerPoint.Application');version=str(app.Version)
assert version=='16.0'
security=app.AutomationSecurity;app.AutomationSecurity=3
allreports=[]
try:
 for key,name in names.items():
  path=OUT/(name+'.pptx');before=hashlib.sha256(path.read_bytes()).hexdigest();deck=None
  try:
   deck=app.Presentations.Open(str(path),True,False,False);assert deck.Slides.Count==1
   s=deck.Slides(1)
   s.Export(str(PRE/f'S7_v2_{key}_3840x2160.png'),'PNG',3840,2160)
   s.Export(str(PRE/f'S7_v2_{key}_1920x1080.png'),'PNG',1920,1080)
   deck.SaveAs(str(OUT/(name+'.pdf')),32)
   outside=[];overflow=[];shapes=[];notes=[]
   for i in range(1,s.Shapes.Count+1):
    sh=s.Shapes(i);x,y,w,h=[float(getattr(sh,a)) for a in ['Left','Top','Width','Height']]
    r=dict(name=sh.Name,rect_pt=[x,y,w,h],type=sh.Type)
    if x<-.1 or y<-.1 or x+w>float(deck.PageSetup.SlideWidth)+.1 or y+h>float(deck.PageSetup.SlideHeight)+.1:outside.append(r)
    if sh.HasTextFrame and sh.TextFrame.HasText:
     tf=sh.TextFrame2;tr=tf.TextRange
     actual=[float(tr.BoundWidth),float(tr.BoundHeight)];allowed=[w-float(tf.MarginLeft+tf.MarginRight),h-float(tf.MarginTop+tf.MarginBottom)]
     r.update(text=sh.TextFrame.TextRange.Text,bound_pt=actual,available_pt=allowed,font=tr.Font.Name)
     if actual[0]>allowed[0]+1 or actual[1]>allowed[1]+1:overflow.append(r)
    shapes.append(r)
   for sh in s.NotesPage.Shapes:
    if sh.HasTextFrame and sh.TextFrame.HasText:notes.append(sh.TextFrame.TextRange.Text)
   expected=(OUT/f'speaker_notes_{key}.md').read_text(encoding='utf8')
   norm=lambda t:t.replace('\r\n','\n').replace('\r','\n').replace('\x0b','\n').strip()
   notes_match=any(norm(n)==norm(expected) for n in notes)
   (QA/f'{key}_PowerPoint备注读回.txt').write_text('\n\n'.join(notes),encoding='utf8')
   rep=dict(candidate=key,renderer='Microsoft PowerPoint '+version,slide_count=1,text_overflow=overflow,outside_canvas=outside,notes_match=notes_match,shapes=shapes,export_sizes=[list(Image.open(PRE/f'S7_v2_{key}_{size}.png').size) for size in ['3840x2160','1920x1080']])
   allreports.append(rep)
  finally:
   if deck is not None:deck.Close()
  assert hashlib.sha256(path.read_bytes()).hexdigest()==before,'Original PPTX changed during render'
finally:
 app.AutomationSecurity=security
 if app.Presentations.Count==0:app.Quit()

for rep in allreports:
 key=rep['candidate'];name=names[key];ppt=Presentation(OUT/(name+'.pptx'))
 rep['editable_textboxes']=sum(sh.has_text_frame for sh in ppt.slides[0].shapes)
 rep['picture_ratios']=[]
 for sh in ppt.slides[0].shapes:
  if sh.shape_type==13:
   iw,ih=sh.image.size
   err=abs((sh.width/sh.height)/(iw/ih)-1)
   rep['picture_ratios'].append(dict(name=sh.name,relative_error=err,original_pixels=[iw,ih]))
   assert err<1e-5
 with zipfile.ZipFile(OUT/(name+'.pptx')) as z:
  media=[hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('ppt/media/')]
 expected_image=OUT/('派生素材/历史长度比较_仅裁顶端图题.png' if key=='A' else '历史资产核查/历史FIG_80cm_原标签.png')
 rep['media_bytes_match']=hashlib.sha256(expected_image.read_bytes()).hexdigest() in media
 assert rep['media_bytes_match']
 # PDF is produced by PowerPoint; Poppler is used only to inspect that PDF.
 dest=QA/f'S7_{key}_PDF实际渲染'
 subprocess.run(['pdftoppm','-png','-scale-to-x','1920','-scale-to-y','1080','-singlefile',str(OUT/(name+'.pdf')),str(dest)],check=True,capture_output=True)
(QA/'PowerPoint实际渲染检查.json').write_text(json.dumps(allreports,ensure_ascii=False,indent=2),encoding='utf8')

font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25)
ref6=OUT.parent/'S6_尘埃等离子体_v1_20261005/预览/S6_1920x1080.png'
ref8=OUT.parent/'S8_项目级AI协作_v1_20261005/预览/S8_1920x1080.png'
for key in names:
 imgs=[ref6,PRE/f'S7_v2_{key}_1920x1080.png',ref8]
 sheet=Image.new('RGB',(1944,3*1130+24),'#E8EDF2');d=ImageDraw.Draw(sheet)
 for i,(p,label) in enumerate(zip(imgs,['S6 · 现有页',f'S7 v2 {key} · INTERNAL / CANDIDATE','S8 · 现有页'])):
  y=12+i*1130;d.text((18,y),label,font=font,fill='#172B43');sheet.paste(Image.open(p).convert('RGB'),(12,y+38))
 sheet.save(PRE/f'S6-S7v2{key}-S8_连续审阅_纵向.png')
 row=Image.new('RGB',(3*972+12,602),'#E8EDF2');d=ImageDraw.Draw(row)
 for i,(p,label) in enumerate(zip(imgs,['S6',f'S7 v2 {key}','S8'])):
  x=12+i*972;d.text((x,10),label,font=font,fill='#172B43');im=Image.open(p).convert('RGB').resize((960,540),Image.Resampling.LANCZOS);row.paste(im,(x,50))
 row.save(PRE/f'S6-S7v2{key}-S8_连续审阅_横向.png')
print(json.dumps([dict(candidate=r['candidate'],overflow=r['text_overflow'],outside=r['outside_canvas'],notes=r['notes_match']) for r in allreports],ensure_ascii=False))
assert all(not r['text_overflow'] and not r['outside_canvas'] and r['notes_match'] for r in allreports)
