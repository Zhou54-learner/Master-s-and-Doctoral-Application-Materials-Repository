from pathlib import Path
import json, hashlib, ast, re
import numpy as np
import pymupdf
from pptx import Presentation

ROOT=Path('F:/1A硕博申请')
OUT=Path(__file__).resolve().parent
SRC=Path('F:/biyesheji')
FINAL=SRC/'最终结果ohmic_sheet_12x12_multitemplate_topology_ga'
CODE=SRC/'code/ohmic_sheet_12x12_multitemplate_topology_ga_code.py'
EVID=ROOT/'A线_西湖博士/面试与导师交流/刘癸庚/事实核验/evidence'
manifest=[]
def record(p):
    b=p.read_bytes(); manifest.append(dict(path=str(p),size=len(b),sha256=hashlib.sha256(b).hexdigest())); return b
text=record(CODE).decode('utf-8-sig')
tree=ast.parse(text)
funcs={n.name:dict(start=n.lineno,end=n.end_lineno) for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
(OUT/'有效函数定位.json').write_text(json.dumps(funcs,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'源码带行号.txt').write_text('\n'.join(f'{i}: {s}' for i,s in enumerate(text.splitlines(),1)),encoding='utf-8')
theses=list(Path('E:/360MoveData/Users/zzj/OneDrive/桌面/毕业设计/结题/终稿').glob('*物理学院.pdf'))
for p in theses:
    record(p); doc=pymupdf.open(p)
    (OUT/'论文逐页提取.txt').write_text('\n\n'.join(f'=== PDF PAGE {i+1} ===\n{page.get_text()}' for i,page in enumerate(doc)),encoding='utf-8')
    for i in [22,26,46,48,55,60]:
        doc[i].get_pixmap(matrix=pymupdf.Matrix(1.3,1.3)).save(OUT/f'thesis_p{i+1}.png')
for p in FINAL.glob('*.txt'): record(p)
for p in [FINAL/'best_design_ohmic_sheet_12x12.cst',FINAL/'temp/temp_ohmic_sheet_20260503_180023_9979.cst']:
    record(p)
    stem=p.with_suffix('')
    for suffix in ['Model/3D/ModelHistory.json','Model/Parameters.json','Result/Model.log']:
        q=stem/suffix
        if q.exists(): record(q)
curves={}
def bands(f,v,threshold=-10):
    chunks=np.split(np.flatnonzero(v<=threshold),np.where(np.diff(np.flatnonzero(v<=threshold))>1)[0]+1)
    return [[float(f[c[0]]),float(f[c[-1]]),float(f[c[-1]]-f[c[0]])] for c in chunks if len(c)]
for group in ['ga','adaptive']:
    for ij in ['11','12','21','22']:
        p=EVID/'ga_winner'/f'S{ij}.csv' if group=='ga' else EVID/f'1D_Results_S-Parameters_SZmax({ij[0]}),Zmax({ij[1]}).csv'
        record(p); a=np.genfromtxt(p,delimiter=',',skip_header=1)
        f=a[:,0]; mag=np.hypot(a[:,1],a[:,2]); db=20*np.log10(np.maximum(mag,1e-15))
        curves[f'{group}_S{ij}']=dict(n=len(f),bands=bands(f,db),min_db=float(db.min()),max_db=float(db.max()))
(OUT/'曲线复算.json').write_text(json.dumps(curves,ensure_ascii=False,indent=2),encoding='utf-8')
ppts=[]
for base in [ROOT,Path('E:/360MoveData/Users/zzj/OneDrive/桌面'),Path('F:/biyesheji')]:
    for p in base.rglob('*.pptx'):
        try:
            prs=Presentation(p)
            ppts.append(dict(path=str(p),pages=len(prs.slides)))
            if len(prs.slides)==12 or ('完整PPT_v1.1' in str(p) and 'mianshi' not in str(p)):
                record(p)
                dest=OUT/('12页_'+p.stem+'.txt' if len(prs.slides)==12 else '现有15页PPT_文字与备注.txt')
                dest.write_text('\n\n'.join(f'=== SLIDE {i+1} ===\n'+'\n'.join(s.text for s in sl.shapes if s.has_text_frame)+'\nNOTES:\n'+sl.notes_slide.notes_text_frame.text for i,sl in enumerate(prs.slides)),encoding='utf-8')
        except Exception as e: ppts.append(dict(path=str(p),error=str(e)))
(OUT/'PPT搜索清单.json').write_text(json.dumps(ppts,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'来源哈希.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'theses':[str(x) for x in theses],'ppt_count':len(ppts),'12page':[x for x in ppts if x.get('pages')==12],'curves':curves},ensure_ascii=False,indent=2))
