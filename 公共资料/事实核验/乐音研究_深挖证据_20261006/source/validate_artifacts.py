"""Check scientific invariants, exported figures, and reproducible regeneration."""
from pathlib import Path
import subprocess, sys, json, tempfile, hashlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, ImageOps, ImageDraw

OUT=Path(__file__).resolve().parent.parent
SKILL=Path('E:/CodexData/profile/.codex/skills/academic-figure/scripts')
QA=OUT/'qa';QA.mkdir(exist_ok=True)
def read(n):return json.loads((OUT/n).read_text(encoding='utf8'))
groups=read('历史表对应42组统计.json');gaps=read('各管几何与直接间距.json')
assert len(groups)==42 and sum(g['n'] for g in groups)==209
for g in groups:
    assert g['n']==len(g['values_hz'])
    assert np.isclose(np.mean(g['values_hz']),g['mean_hz'])
    assert np.isclose(np.std(g['values_hz'],ddof=1),g['sd_hz'])
for g in gaps:assert np.allclose(np.diff(g['means_hz']),g['gaps_hz'])
assert len(read('音符匹配支线18份文件.json'))==18
assert read('原件保护复核.json')['status']=='PASS'
chain=read('scale七段共享波形证据链.json')['matches']
assert len(chain)==7 and min(r['correlation'] for r in chain)>.95
assert all(abs(r['gap_from_previous_s'])<.01 for r in chain[1:])

def task(p):
    allowed=1 if p.stem.startswith('F03') else 0
    check=subprocess.run([sys.executable,str(SKILL/(p.suffix[1:]+'_check.py')),str(p),'--allow-raster',str(allowed),'--json'],capture_output=True,text=True,encoding='utf8')
    render=QA/(p.stem+'_'+p.suffix[1:]+'.png')
    rr=subprocess.run([sys.executable,str(SKILL/'render_preview.py'),str(p),str(render),'--dpi','110'],capture_output=True,text=True,encoding='utf8')
    return {'file':p.name,'check_code':check.returncode,'check':json.loads(check.stdout) if check.stdout.strip().startswith('{') else check.stdout+check.stderr,'render_code':rr.returncode,'render_log':rr.stdout+rr.stderr}
files=sorted(p for p in (OUT/'output').glob('*') if p.suffix in ['.pdf','.svg'])
with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(task,files))
temp=Path(tempfile.mkdtemp(prefix='music-fig-repro-'))
rr=subprocess.run([sys.executable,str(OUT/'source/deepen_and_plot.py'),str(temp)],capture_output=True,text=True,encoding='utf8')
repro=[]
for p in sorted((OUT/'output').glob('*.png')):
    target=temp/p.name
    repro.append({'file':p.name,'pixel_exact':bool(target.exists() and np.array_equal(np.array(Image.open(p)),np.array(Image.open(target))))})
sheet=Image.new('RGB',(1600,1640),'#e6e8ea');d=ImageDraw.Draw(sheet)
for i,p in enumerate(sorted(QA.glob('F*.png'))):
    im=Image.open(p).convert('RGB');im.thumbnail((790,360))
    x=(i%2)*800;y=(i//2)*410
    d.text((x+10,y+5),p.name[:3]+' '+('PDF' if '_pdf' in p.name else 'SVG'),fill='black')
    sheet.paste(im,(x+(800-im.width)//2,y+30+(360-im.height)//2))
sheet.save(QA/'全部SVG与PDF渲染总览.png')
report={'scientific_invariants':'PASS','figures':results,'regeneration_exit_code':rr.returncode,'png_regeneration':repro,'intentional_raster':'F03: original-audio-derived STFT heatmap; axes/text/ridge lines remain vector.','all_pass':all(x['check_code']==0 and x['render_code']==0 for x in results) and rr.returncode==0 and all(x['pixel_exact'] for x in repro)}
(QA/'自动核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'all_pass':report['all_pass'],'figures':[(x['file'],x['check_code'],x['render_code']) for x in results],'repro':repro},ensure_ascii=False,indent=2))
