"""2026-10-05 static archaeology. Never executes or writes historical sources."""
from pathlib import Path
import collections, datetime, hashlib, json, re, subprocess, zipfile
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
ROOT = Path('E:/2023/traindata')
MODEL = Path('E:/COMSOL 6.2/test')
def save(name, obj):
    (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
def record(p):
    s=p.stat()
    return dict(path=p.as_posix(), bytes=s.st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest(), mtime=datetime.datetime.fromtimestamp(s.st_mtime, datetime.timezone(datetime.timedelta(hours=8))).isoformat())
files=sorted(p for root in (ROOT,MODEL) for p in root.rglob('*') if p.is_file())
rows=[record(p) for p in files]
save('原件索引.json', rows)
print('inventory',len(rows),dict(collections.Counter(p.suffix.lower() for p in files)))
archives=[]
for p in files:
    if p.suffix.lower() not in ('.zip','.mlapp','.mph'): continue
    if not zipfile.is_zipfile(p):
        archives.append(dict(path=p.as_posix(), zip=False)); continue
    with zipfile.ZipFile(p) as z:
        a=dict(path=p.as_posix(), members=[dict(name=i.filename,bytes=i.file_size,date=i.date_time,crc=i.CRC) for i in z.infolist()])
        archives.append(a)
        if p.suffix=='.mlapp':
            for n in z.namelist():
                if n.endswith('.xml') and ('document' in n or 'coreProperties' in n):
                    t=z.read(n).decode('utf-8',errors='replace')
                    (OUT/(p.stem+'_'+Path(n).name+'.txt')).write_text(t,encoding='utf-8')
        # MPH settings are selectively summarized by inspect_chain.py.
        # Do not export whole model XML, license data, or internal machine details.
save('压缩与工程容器索引.json',archives)

S={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
books=[]
for p in files:
    if p.suffix.lower()!='.xlsx': continue
    with zipfile.ZipFile(p) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        sheets=[]
        for n in z.namelist():
            if re.fullmatch(r'xl/worksheets/sheet\d+.xml',n):
                cells=[]
                for c in ET.fromstring(z.read(n)).findall('.//s:c',S):
                    v=c.find('s:v',S); f=c.find('s:f',S)
                    value=v.text if v is not None else None
                    if c.get('t')=='s' and value is not None: value=strings[int(value)]
                    if c.get('t')=='inlineStr': value=''.join(c.find('s:is',S).itertext())
                    if value is not None or f is not None: cells.append(dict(cell=c.get('r'),value=value,formula=f.text if f is not None else None))
                sheets.append(dict(member=n,cells=cells))
        books.append(dict(path=p.as_posix(),core=z.read('docProps/core.xml').decode('utf-8') if 'docProps/core.xml' in z.namelist() else None,sheets=sheets))
save('表格单元格与元数据.json',books)
print('archives',len(archives),'books',len(books))

search_roots=['E:/2022','E:/2023','E:/2024','E:/QQ Files','E:/xwechat_files','F:/OneDrive','C:/Users/zzj/Documents','C:/Users/zzj/Desktop','C:/Users/zzj/Downloads','E:/Autosave','E:/Backup','E:/Unsaved']
cmd=['rg','--files','--hidden',*search_roots,'-g','*.pptx','-g','*.docx','-g','*.m','-g','*.mlx','-g','*.asv','-g','*.py']
r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf-8',errors='replace')
hits=[]; count=collections.Counter(); errors=[]
pat=re.compile('波纹管|乐音|traindata|pitchtest|R11.6mm|音阶|频谱')
for name in r.stdout.splitlines():
    p=Path(name)
    if p.stat().st_size>30_000_000 or p.name.startswith('~$'): continue
    count[p.suffix]+=1
    try:
        parts=[]
        if p.suffix in ('.docx','.pptx','.mlx'):
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    if re.search(r'(word/document|ppt/slides/slide\d+|ppt/notesSlides/notesSlide\d+|matlab/document)\.xml$',n):
                        text=' '.join(ET.fromstring(z.read(n)).itertext())
                        if pat.search(text): parts.append(dict(member=n,text=text))
        else:
            text=p.read_text(encoding='utf-8',errors='replace')
            if pat.search(text): parts.append(dict(member='text',text=text))
        if parts: hits.append(dict(path=p.as_posix(),matched_members=[v['member'] for v in parts]))
    except Exception as ex: errors.append(dict(path=p.as_posix(),error=str(ex)))
save('定向正文检索.json',dict(roots=search_roots,counts=count,hits=hits,errors=errors,stderr=r.stderr))
print('search',dict(count),'hits',[x['path'] for x in hits],'errors',len(errors))
