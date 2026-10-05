"""Parse saved FIG/MLX/XLSX/PDF only; no MATLAB execution or new simulation."""
from pathlib import Path
import sys, json, hashlib, collections, zipfile, xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
sys.path[:0]=['E:/CodexData/tmp/dusty_audit_deps',str(Path(__file__).resolve().parents[3]/'项目维护/工具/运行依赖')]
import numpy as np
from scipy.io import loadmat
import pymupdf
OUT=Path(__file__).resolve().parent
SCRATCH=Path('E:/CodexData/tmp/dusty_audit_20261005')
def sha(b): return hashlib.sha256(b).hexdigest()
def js(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def walk(o,path=''):
    if isinstance(o,dict):
        if 'type' in o and 'properties' in o: yield path,o
        for k,v in o.items(): yield from walk(v,path+'/'+k)
    elif isinstance(o,(list,np.ndarray)):
        if isinstance(o,np.ndarray) and o.dtype!=object: return
        if isinstance(o,np.ndarray):
            if o.ndim==0: return
            o=o.reshape(-1)
        for i,v in enumerate(o): yield from walk(v,path+f'/{i}')
def simple(v):
    if isinstance(v,np.ndarray): return v.tolist()
    if isinstance(v,np.generic): return v.item()
    return v
figs=[]; arrays={}
for p in sorted(Path('E:/2024/data figure').rglob('*.fig')):
    ident=f'F{len(figs)+1:03d}'; f=loadmat(p,simplify_cells=True)
    row={'id':ident,'source':p.as_posix(),'header':f['__header__'].decode(errors='replace'),'objects':[]}
    for objpath,o in walk(f):
        props=o['properties']; entry={'path':objpath,'type':o['type']}
        for key in ['String','XLim','YLim','XLabel','YLabel','Title','UserData','Tag','XDataSource','YDataSource']:
            if key in props and isinstance(props[key],(str,float,int,np.ndarray,np.generic)): entry[key]=simple(props[key])
        for key in ['XData','YData','ZData']:
            if key not in props: continue
            v=np.asarray(props[key],dtype=float).reshape(-1)
            tag=ident+'_'+str(len(row['objects']))+'_'+key
            arrays[tag]=v
            entry[key]={'key':tag,'n':len(v),'min':float(np.nanmin(v)) if len(v) else None,'max':float(np.nanmax(v)) if len(v) else None,'first':v[:3].tolist(),'last':v[-3:].tolist(),'sha256_float64_le':sha(v.astype('<f8').tobytes())}
        row['objects'].append(entry)
    figs.append(row)
np.savez(SCRATCH/'fig_arrays.npz',**arrays)
js(OUT/'FIG数值对象索引.json',figs)

p=Path('E:/2024/yxy组代码/代码（偏振）去前段/李萨如图.xlsx')
z=zipfile.ZipFile(p); ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
root=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
cols=collections.defaultdict(list)
for c in root.findall('.//s:c',ns):
    v=c.find('s:v',ns)
    if v is not None:
        name=''.join(a for a in c.attrib['r'] if a.isalpha())
        try: cols[name].append((c.attrib['r'],float(v.text)))
        except ValueError: cols[name].append((c.attrib['r'],v.text))
js(OUT/'XLSX单元格与元数据.json',{'source':p.as_posix(),'metadata':{n:z.read(n).decode() for n in z.namelist() if n.startswith('docProps/') and n.endswith('.xml')},'columns':cols})

pdf=Path(__file__).resolve().parents[3]/'科研准备/晶格波研究/论文/论文2.pdf'
doc=pymupdf.open(pdf); items=[]
for i,page in enumerate(doc):
    for im in page.get_images(full=True):
        xref=im[0]; data=doc.extract_image(xref); dst=SCRATCH/f'paper_p{i+1}_xref{xref}.{data["ext"]}'
        dst.write_bytes(data['image'])
        items.append({'page':i+1,'xref':xref,'width':data['width'],'height':data['height'],'sha256':sha(data['image']),'file':str(dst)})
js(OUT/'论文内嵌图索引.json',items)
print('FIG',len(figs),'arrays',len(arrays),'XLSX',{k:len(v) for k,v in cols.items()},'PDF images',items)
print('FIG summary by folder')
for folder in sorted(set(str(Path(f['source']).parent) for f in figs)):
    ff=[f for f in figs if str(Path(f['source']).parent)==folder]
    print(folder,len(ff),collections.Counter(tuple((o.get('XData',{}).get('n'),o.get('YData',{}).get('n'))) for f in ff for o in f['objects'] if 'XData' in o))
