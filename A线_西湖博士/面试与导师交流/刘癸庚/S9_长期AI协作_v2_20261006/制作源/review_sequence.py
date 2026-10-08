"""Compose review images from actual exported PNGs only; no merged slide deck."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parents[1];PI=OUT.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
PRE=OUT/'预览';QA=OUT/'检查证据'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25)
refs=[
    (PI/'S7_乐音研究_v2_20261006/预览/S7_v2_A_1920x1080.png','S7 v2 A · 并发任务推荐候选，仅供节奏审阅'),
    (PI/'S8_项目AI协作_v2_20261006/预览/S8_1920x1080.png','S8 v2 · 第一次比较系统地与 AI 做项目'),
    (PRE/'S9-A_1920x1080.png','S9-A v2 · 留下长期目标与当前状态'),
    (PRE/'S9-B_1920x1080.png','S9-B v2 · 接上这一轮的具体行动'),
    (PI/'S10_反思_v2_20261006/预览/S10_1920x1080.png','S10 v2 A · 原候选，仅供节奏审阅')]
if not refs[0][0].exists():
    refs[0]=(PI/'S7_乐音研究_v1_20261005/预览/S7_1920x1080.png','S7 v1 · 占位，仅供节奏审阅')
vertical=Image.new('RGB',(1944,5*1130+24),'#E8EDF2');d=ImageDraw.Draw(vertical)
horizontal=Image.new('RGB',(5*972+12,610),'#E8EDF2');dh=ImageDraw.Draw(horizontal)
records=[]
for i,(path,label) in enumerate(refs):
    im=Image.open(path).convert('RGB');assert im.size==(1920,1080)
    y=12+i*1130;d.text((18,y),label,font=font,fill='#172B43');vertical.paste(im,(12,y+38))
    x=12+i*972;dh.text((x,10),label,font=font,fill='#172B43')
    horizontal.paste(im.resize((960,540),Image.Resampling.LANCZOS),(x,54))
    records.append(dict(order=i+1,label=label,path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        operation='Read existing PNG; no source PPTX opened or edited.'))
vertical.save(PRE/'S7-S8-S9A-S9B-S10_连续审阅_纵向.png')
horizontal.save(PRE/'S7-S8-S9A-S9B-S10_连续审阅_横向.png')
(QA/'连续审阅来源.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
print('Review sequence created from five actual PowerPoint PNGs; S7 =',refs[0][1])
