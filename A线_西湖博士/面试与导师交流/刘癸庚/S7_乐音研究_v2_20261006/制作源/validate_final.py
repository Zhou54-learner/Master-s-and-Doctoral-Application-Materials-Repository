"""Verify read-only preservation, frozen sources, editable deck regeneration and links."""
from pathlib import Path
import hashlib, json, subprocess, sys, zipfile, io, re
from PIL import Image
OUT=Path(__file__).resolve().parent.parent
ROOT=next(p for p in OUT.parents if (p/'申请路线总览.md').exists())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def rec(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def check(rows):
 result=[]
 for r in rows:
  p=Path(r['path']);ok=p.exists() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
  result.append(dict(path=r['path'],unchanged=ok))
 return result
base=json.loads((OUT/'检查证据/接手保全基线.json').read_text(encoding='utf8'))
pi=check(base['existing_pi']);other=check(base['unrelated'])
# The full draft was already modified and open in the user's PowerPoint session.
# Never revert it or absorb its concurrent save into this task. Retain the original
# baseline and disclose its mismatch; only this explicit document is excepted.
concurrent_path=(OUT.parent/'FULL_DRAFT_v0.1_20261006/刘癸庚交流_INTERNAL_FULL_DRAFT_v0.1_20261006.pptx').as_posix()
concurrent=[r for r in pi if not r['unchanged'] and r['path']==concurrent_path]
for r in concurrent:
 p=Path(r['path']);r.update(current=rec(p),baseline=next(b for b in base['existing_pi'] if b['path']==r['path']),note='Already modified and open at handoff; changed during work. Cause not independently established. S7 tools never open/edit this deck. Preserved current bytes; excluded from commit.')
hist=[]
for name in ['原件索引.json','追加原件索引.json']:
 hist.extend(json.loads((ROOT/'公共资料/事实核验/乐音研究_考古证据_20261005'/name).read_text(encoding='utf8')))
preserved=check(hist)
current=check(json.loads((OUT/'历史资产核查/当轮原件清单.json').read_text(encoding='utf8')))
sourcepaths=[ROOT/'公共资料/事实核验'/n for n in ['乐音研究_音调台阶与几何影响深挖_20261006.md','乐音研究_历史内容与独立贡献考古_20261005.md','乐音研究_实验现场补充确认_20261005.md','乐音研究_深挖证据_20261006/README.md','乐音研究_深挖证据_20261006/历史表对应42组统计.csv','乐音研究_深挖证据_20261006/各管几何与直接间距.json','乐音研究_深挖证据_20261006/scale七段共享波形证据链.json','乐音研究_考古证据_20261005/COMSOL静态模型摘要.json']]
sourcepaths += [Path(p) for p in ['E:/2023/traindata/数据处理/长度关系比较/数据图表1.jpg','E:/2023/traindata/数据处理/长度关系比较/数据图表3.jpg','E:/2023/traindata/数据处理/内外半径关系比较/比较1.jpg','E:/2023/traindata/R11.6mm_r8.0mm/60cm/R11.6mmr8mm_60mm_scale.fig','E:/2023/traindata/R11.6mm_r8.0mm/80cm/R11.6mmr8mm_80mm_scale.fig','E:/COMSOL 6.2/test/parameters.txt']]
sourcepaths += [OUT.parent/'S6_尘埃等离子体_v1_20261005/预览/S6_1920x1080.png',OUT.parent/'S8_项目级AI协作_v1_20261005/预览/S8_1920x1080.png']
dump(OUT/'来源清单.json',[rec(p) for p in sourcepaths])

# Rebuild only the two authorized candidates, compare every ZIP member payload,
# then restore the identical original package bytes to preserve rendered artifacts.
decks=sorted(OUT.glob('*.pptx'));saved={p:p.read_bytes() for p in decks}
subprocess.run([sys.executable,str(OUT/'制作源/build_slides.py')],check=True,capture_output=True)
regen=[]
for p,before in saved.items():
 with zipfile.ZipFile(io.BytesIO(before)) as a,zipfile.ZipFile(p) as b:
  diffs=[n for n in set(a.namelist())|set(b.namelist()) if n not in a.namelist() or n not in b.namelist() or a.read(n)!=b.read(n)]
 regen.append(dict(file=p.name,changed_package_members=diffs))
 p.write_bytes(before)
crop=Image.open(OUT/'派生素材/历史长度比较_仅裁顶端图题.png').convert('RGB')
original=Image.open(OUT/'派生素材/历史长度比较_完整原图.jpg').convert('RGB')
crop_ok=crop.tobytes()==original.crop((0,100,1200,1020)).tobytes()
pdfs=[]
for p in sorted(OUT.glob('*.pdf')):
 proc=subprocess.run(['pdfinfo',str(p)],capture_output=True,text=True,encoding='utf8',errors='replace',check=True)
 pdfs.append(dict(file=p.name,info=proc.stdout))
 assert re.search(r'Pages:\s+1\b',proc.stdout)
 assert 'PowerPoint' in proc.stdout
broken=[]
for p in OUT.rglob('*.md'):
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf8')):
  if '://' in target or target.startswith('#'):continue
  q=target.split('#')[0]
  target_path=(p.parent/q).resolve()
  if q and not target_path.exists() and target_path!=(OUT/'检查证据/最终保全与复现.json').resolve():broken.append(dict(file=p.relative_to(OUT).as_posix(),target=target))
reports=json.loads((OUT/'检查证据/PowerPoint实际渲染检查.json').read_text(encoding='utf8'))
sizes={p.name:list(Image.open(p).size) for p in (OUT/'预览').glob('*.png')}
result=dict(existing_pi_files=pi,unrelated_files=other,historical_baseline=preserved,current_historical_files=current,concurrent_workspace_changes=concurrent,historical_crop_pixel_exact=crop_ok,rebuild=regen,broken_local_links=broken,pdfs=pdfs,preview_sizes=sizes,summary=dict(pi_count=len(pi),pi_unchanged=sum(r['unchanged'] for r in pi),unrelated_count=len(other),historical_count=len(preserved),current_history_count=len(current),all_preserved=all(r['unchanged'] for r in pi+other+preserved+current),protected_files_preserved=all(r['unchanged'] or r['path']==concurrent_path for r in pi+other+preserved+current),concurrent_changes=len(concurrent),rebuild_same=all(not r['changed_package_members'] for r in regen),text_overflow=sum(len(r['text_overflow']) for r in reports),outside=sum(len(r['outside_canvas']) for r in reports),notes_all_match=all(r['notes_match'] for r in reports)))
dump(OUT/'检查证据/最终保全与复现.json',result)
print(json.dumps(result['summary'],ensure_ascii=False));print('broken links:',broken)
assert result['summary']['protected_files_preserved'] and result['summary']['rebuild_same'] and crop_ok and not broken
