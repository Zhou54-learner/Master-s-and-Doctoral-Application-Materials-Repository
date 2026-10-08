"""Read-only historical asset audit. All outputs stay in this candidate directory."""
from pathlib import Path
import hashlib, json, zipfile, collections, subprocess, io, re
from PIL import Image, ImageDraw, ImageFont
OUT=Path(__file__).resolve().parent.parent
ROOT=next(p for p in OUT.parents if (p/'申请路线总览.md').exists())
AUD=OUT/'历史资产核查'
SRC=Path('E:/2023/traindata')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def rec(p): return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha(p))
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15)
def sheet(items,name,cols=4,w=400,h=385):
    im=Image.new('RGB',(cols*w,((len(items)+cols-1)//cols)*h),'#E9EEF2');d=ImageDraw.Draw(im)
    for i,(path,label) in enumerate(items):
        img=Image.open(path).convert('RGB');img.thumbnail((w-12,h-58))
        x=(i%cols)*w;y=(i//cols)*h
        im.paste(img,(x+(w-img.width)//2,y))
        for j,t in enumerate(label.split('\n')):d.text((x+5,y+h-55+j*18),t,font=font,fill='#172B43')
    im.save(AUD/name)

# Capture only once; never silently reset preservation baselines on regeneration.
baseline=OUT/'检查证据/接手保全基线.json'
if not baseline.exists():
    existing=[p for p in OUT.parent.rglob('*') if p.is_file() and OUT not in p.parents and not p.name.startswith('~$')]
    extras=[ROOT/'公共资料/面试与导师交流中心/公共主干/README.md',ROOT/'公共资料/面试与导师交流中心/公共主干/项目重建/本科毕设/README.md',ROOT/'公共资料/面试与导师交流中心/公共主干/项目重建/本科毕设/13_实际工作梳理与研究叙事底稿.md']
    dump(baseline,dict(existing_pi=[rec(p) for p in existing],unrelated=[rec(p) for p in extras if p.exists()],note='Pre-existing FULL_DRAFT modification preserved; volatile Office owner-lock excluded.'))
files=sorted(p for p in SRC.rglob('*') if p.is_file())
index=[rec(p) for p in files];dump(AUD/'当轮原件清单.json',index)
bysha=collections.defaultdict(list)
for x in index:bysha[x['sha256']].append(x)
image_groups=[v for v in bysha.values() if Path(v[0]['path']).suffix.lower() in ['.png','.jpg','.jpeg']]
image_groups.sort(key=lambda v:v[0]['path'])
dump(AUD/'全部历史图片去重索引.json',[dict(id=f'H{i+1:03}',**v[0],aliases=[x['path'] for x in v],size=list(Image.open(v[0]['path']).size)) for i,v in enumerate(image_groups)])
for start in range(0,len(image_groups),24):
    items=[]
    for i,v in enumerate(image_groups[start:start+24],start):
        p=Path(v[0]['path']);label=f'H{i+1:03} '+str(p.parent.parent.name)+'/'+p.name
        items.append((p,label))
    sheet(items,f'历史图片总览_{start//24+1:02}.jpg')
# Inspect every workbook for native charts and embedded images, including duplicates.
books=[];containers=[]
for p in files:
    if p.suffix.lower()=='.xlsx':
        with zipfile.ZipFile(p) as z:
            charts=[n for n in z.namelist() if re.fullmatch(r'xl/charts/chart\d+\.xml',n)]
            media=[n for n in z.namelist() if n.startswith('xl/media/')]
            books.append(dict(path=p.as_posix(),charts=charts,media=media,sha256=sha(p)))
    if p.suffix.lower()=='.zip':
        with zipfile.ZipFile(p) as z: containers.append(dict(path=p.as_posix(),members=[n for n in z.namelist() if Path(n).suffix.lower() in ['.fig','.jpg','.png','.ppt','.pptx','.doc','.docx','.xlsx']]))
dump(AUD/'全部工作簿图件核查.json',books);dump(AUD/'压缩包图件成员核查.json',containers)
# Re-run focused text/image checks in archived historical PPT/Word locations.
prior=json.loads((ROOT/'公共资料/事实核验/乐音研究_考古证据_20261005/定向正文检索.json').read_text(encoding='utf8'))
docs=[];seen=set()
for folder in prior['roots']:
    root=Path(folder)
    if not root.exists():continue
    for p in root.rglob('*'):
        if p.suffix.lower() not in ['.pptx','.docx'] or p.name.startswith('~$') or not p.is_file():continue
        if p.as_posix() in seen:continue
        seen.add(p.as_posix())
        try:
            with zipfile.ZipFile(p) as z:
                ns=[n for n in z.namelist() if n=='word/document.xml' or re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
                hits=[n for n in ns if any(k in z.read(n).decode('utf8',errors='ignore') for k in ['波纹管','龙之鸣','魔音','乐音研究'])]
                if hits:docs.append(dict(path=p.as_posix(),sha256=sha(p),hits=hits,media=[n for n in z.namelist() if n.startswith(('word/media/','ppt/media/'))]))
        except (OSError,zipfile.BadZipFile):pass
dump(AUD/'当轮比赛文档定向复搜.json',dict(count=len(seen),hits=docs,roots=prior['roots'],scope='Targeted content search; not a deleted-file recovery.'))
videos=[]
for p in files:
    if p.suffix.lower()=='.mp4':
        data=subprocess.check_output(['ffmpeg','-v','error','-ss','1','-i',str(p),'-frames:v','1','-f','image2pipe','-vcodec','png','-'])
        target=AUD/(p.stem+'_1秒.png');Image.open(io.BytesIO(data)).save(target);videos.append((target,p.name+' · t=1s'))
sheet(videos,'全部演示视频截帧.jpg',cols=3,w=560,h=365)
dump(AUD/'检索摘要.json',dict(files=len(files),extensions=dict(collections.Counter(p.suffix.lower() for p in files)),unique_images=len(image_groups),workbooks=len(books),native_charts=sum(len(b['charts']) for b in books),figs=[rec(p) for p in files if p.suffix.lower()=='.fig'],target_document_hits=len(docs)))
print(json.dumps(dict(files=len(files),images=len(image_groups),workbooks=len(books),charts=sum(len(b['charts']) for b in books),documents=docs),ensure_ascii=False))
