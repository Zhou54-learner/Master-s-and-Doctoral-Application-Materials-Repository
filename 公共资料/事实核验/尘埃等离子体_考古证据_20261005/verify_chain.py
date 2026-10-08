"""2026 audit calculations on archived files; no dynamics simulation.

Run audit_sources.py and inspect_data.py first. This preserves the distinction
between exact data/byte identity and image-content correspondence.
"""
from pathlib import Path
import sys, json, hashlib, zipfile, difflib, itertools, io
sys.dont_write_bytecode=True
sys.path[:0]=['E:/CodexData/tmp/dusty_audit_deps',str(Path(__file__).resolve().parents[3]/'项目维护/工具/运行依赖')]
import numpy as np
from PIL import Image
import pymupdf
OUT=Path(__file__).resolve().parent
SCRATCH=Path('E:/CodexData/tmp/dusty_audit_20261005')
def sha(b):return hashlib.sha256(b).hexdigest()
def js(n,o):(OUT/n).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
for a,b in [('C30','C10'),('C24','C10'),('C10','C17'),('C17','C39')]:
    p=next((OUT/'代码文本').glob(a+'_*'));q=next((OUT/'代码文本').glob(b+'_*'))
    left=[line+'\n' for line in p.read_text(encoding='utf-8').splitlines()]
    right=[line+'\n' for line in q.read_text(encoding='utf-8').splitlines()]
    (OUT/f'{a}_to_{b}.diff.txt').write_text(''.join(difflib.unified_diff(left,right,fromfile=p.name,tofile=q.name)),encoding='utf-8')

base=Path('E:/2024/data figure/data figure x tc-5')
crop=[];bmap={}
for p in Path('E:/2024/data figure').rglob('*.jpg'):bmap.setdefault(sha(p.read_bytes()),[]).append(p.as_posix())
for p in sorted((base/'no line').glob('*.jpg')):
    a=np.asarray(Image.open(base/'square fig line_L(jpg)'/p.name).convert('RGB'))[8:-8,8:-8]
    b=np.asarray(Image.open(p).convert('RGB'))
    crop.append({'file':p.name,'crop_shape':list(a.shape),'output_shape':list(b.shape),'mae_8bit':float(np.mean(np.abs(a.astype(float)-b))) if a.shape==b.shape else None})
js('裁图像素验证.json',crop)
z=zipfile.ZipFile('E:/2024/yxy组代码/代码（偏振）去前段/李萨如图.xlsx');media=[]
for n in z.namelist():
    if n.startswith('xl/media/'):
        b=z.read(n);media.append({'member':n,'sha256':sha(b),'bytes_match':bmap.get(sha(b),[]),'size':Image.open(io.BytesIO(b)).size})
js('XLSX图件逐项匹配.json',media)

fs=read('FIG数值对象索引.json');ar=np.load(SCRATCH/'fig_arrays.npz');same=[];paired=[]
def data(o,k):return ar[o[k]['key']]
for f in fs:
    ll=[o for o in f['objects'] if 'XData' in o and o['XData']['n']]
    # Locate two time plots + a Cartesian trajectory independent of object order.
    if len(ll)==3:
        for a,b,c in itertools.permutations(ll):
            if np.array_equal(data(a,'XData'),data(b,'XData')) and np.array_equal(data(a,'YData'),data(c,'XData')) and np.array_equal(data(b,'YData'),data(c,'YData')):
                t=data(a,'XData');same.append({'id':f['id'],'n':len(t),'dt':float(t[1]-t[0]),'tfirst':float(t[0]),'tlast':float(t[-1]),'trajectory_equals_time_series':True});break
    if not f['source'].endswith(' xy.fig'):continue
    g=next(g for g in fs if g['source']==f['source'].replace(' xy.fig','.fig'))
    ts=[o for o in ll if o['XData']['first'][0]>=5]
    tr=next(o for o in g['objects'] if 'XData' in o)
    x=data(tr,'XData');y=data(tr,'YData');ys=[data(o,'YData') for o in ts]
    eq=any(np.array_equal(x,ys[i]) and np.array_equal(y,ys[1-i]) for i in [0,1]);t=data(ts[0],'XData')
    pol=next(o for o in ll if o not in ts);err=float(np.max(np.abs(data(pol,'YData')-np.arctan2(y,x))))
    paired.append({'time_fig':f['id'],'trajectory_fig':g['id'],'exact_xy_match':eq,'n':len(t),'tfirst':float(t[0]),'tlast':float(t[-1]),'dt':float(t[1]-t[0]),'polar_radius_max_error_vs_atan2':err})
js('时序轨迹一致性.json',same);js('分离FIG时序与轨迹匹配.json',paired)
for ident in ['F013','F015','F059','F088','F105']:
    f=next(f for f in fs if f['id']==ident)
    o=[o for o in f['objects'] if 'XData' in o and o['XData']['n']][-1]
    np.savetxt(OUT/f'{ident}_存档轨迹恢复.csv',np.column_stack((data(o,'XData'),data(o,'YData'))),delimiter=',',header='x_m,y_m',comments='')

pdf=Path(__file__).resolve().parents[3]/'科研准备/晶格波研究/论文/论文2.pdf'
doc=pymupdf.open(pdf);pymupdf.Pixmap(doc,78).save(str(OUT/'论文Fig12_原PDF内嵌图.png'))
(OUT/'C04_存档输出_非本轮仿真.png').write_bytes((SCRATCH/'C04_output_1.png').read_bytes())
summary={'exact_xlsx_images':sum(bool(r['bytes_match']) for r in media),'xlsx_images':len(media),'crop_pairs':len(crop),'crop_mae_range_8bit':[min(r['mae_8bit'] for r in crop),max(r['mae_8bit'] for r in crop)],'same_file_exact_time_trajectory_pairs':len(same),'separate_exact_time_trajectory_pairs':sum(r['exact_xy_match'] for r in paired),'separate_pairs':len(paired),'interpretation':'Identity checks only; they do not identify the human simulation operator or prove the paper image came from a particular saved executable version.'}
js('追溯验收汇总.json',summary);print(json.dumps(summary,ensure_ascii=False))
