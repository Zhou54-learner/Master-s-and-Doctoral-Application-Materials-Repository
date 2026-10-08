"""Read-only historical inventory/extraction; never executes MATLAB source.

Requires Python; PDF/FIG inspection in separate read-only steps. Outputs are
derived audit material, not new historical results. Paths are explicit.
"""
from pathlib import Path
import base64, collections, datetime, hashlib, io, json, zipfile
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
SCRATCH = Path('E:/CodexData/tmp/dusty_audit_20261005')
SCRATCH.mkdir(parents=True, exist_ok=True)
(OUT/'代码文本').mkdir(exist_ok=True)
ROOTS = [Path('E:/2024/yxy组代码'), Path('E:/2024/data figure')]
def sha(b): return hashlib.sha256(b).hexdigest()
def decode(b):
    for enc in ['utf-8-sig','gb18030','utf-16']:
        try: return b.decode(enc)
        except UnicodeError: pass
    return b.decode('utf-8',errors='replace')
def local(t): return datetime.datetime.fromtimestamp(t,datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def jsonsave(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
inventory=[]; codes=[]; zips=[]; outputs=[]
def code_entry(path,b,stamp):
    ident=f'C{len(codes)+1:02d}'
    d={'id':ident,'source':path,'sha256':sha(b),'source_time':stamp}
    if path.lower().endswith('.mlx'):
        z=zipfile.ZipFile(io.BytesIO(b))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        root=ET.fromstring(z.read('matlab/document.xml'))
        txt='\n'.join(''.join(p.itertext()) for p in root.findall('.//w:p',ns))
        d['metadata']={}
        for n in z.namelist():
            if n.startswith('metadata/') and n.endswith('.xml'):
                rr=ET.fromstring(z.read(n))
                d['metadata'][n]={e.tag.split('}')[-1]:e.text for e in rr.iter() if e.text and e.text.strip()}
        if 'matlab/output.xml' in z.namelist():
            rr=ET.fromstring(z.read('matlab/output.xml'))
            figs=[]
            for i,e in enumerate(rr.iter('figureUri')):
                if e.text and e.text.startswith('data:image/'):
                    raw=base64.b64decode(e.text.split(',',1)[1]); dst=SCRATCH/f'{ident}_output_{i+1}.png'; dst.write_bytes(raw)
                    figs.append({'file':str(dst),'sha256':sha(raw)})
            texts=[e.text for e in rr.iter() if e.text and e.text.strip() and not e.text.startswith('data:image/')]
            d['saved_output_figures']=len(figs)
            outputs.append({'id':ident,'source':path,'figures':figs,'texts':texts})
    else: txt=decode(b)
    txt=txt.replace('\r\n','\n')
    dest=OUT/'代码文本'/f'{ident}_{Path(path).stem}.txt'
    dest.write_text(txt,encoding='utf-8')
    d.update({'text_path':dest.relative_to(OUT).as_posix(),'text_sha256':sha(txt.encode()),'lines':len(txt.splitlines())})
    codes.append(d)

for root in ROOTS:
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        b=p.read_bytes(); st=p.stat()
        row={'path':p.as_posix(),'size':len(b),'sha256':sha(b),'creation_time_local':local(st.st_ctime),'mtime_local':local(st.st_mtime)}
        inventory.append(row)
        if p.suffix.lower() in ['.m','.mlx']: code_entry(p.as_posix(),b,row['mtime_local'])
        if p.suffix.lower()=='.zip':
            z=zipfile.ZipFile(io.BytesIO(b))
            for info in z.infolist():
                if info.is_dir(): continue
                n=info.filename
                if not info.flag_bits&0x800:
                    try: n=n.encode('cp437').decode('gb18030')
                    except (UnicodeError,LookupError): pass
                bb=z.read(info)
                item={'archive':p.as_posix(),'member':n,'size':len(bb),'sha256':sha(bb),'zip_time_no_timezone':str(info.date_time)}
                zips.append(item)
                if n.lower().endswith(('.m','.mlx')): code_entry(p.as_posix()+'!/'+n,bb,item['zip_time_no_timezone'])

jsonsave(OUT/'原件索引.json',inventory)
jsonsave(OUT/'代码索引.json',codes)
jsonsave(OUT/'压缩包成员索引.json',zips)
jsonsave(SCRATCH/'mlx_outputs.json',outputs)
print(json.dumps({'files':len(inventory),'extensions':dict(collections.Counter(Path(r['path']).suffix for r in inventory)),'codes':len(codes),'unique_code_text':len(set(r['text_sha256'] for r in codes)),'zip_members':len(zips),'saved_figures':sum(len(o['figures']) for o in outputs)},ensure_ascii=False))
for c in codes:
    print(c['id'],c['source'],c['lines'],c.get('saved_output_figures',''),c['text_sha256'][:12])
