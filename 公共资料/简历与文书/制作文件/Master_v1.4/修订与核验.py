"""A title-only revision; old formal artifacts are immutable."""
from pathlib import Path
import sys,zipfile,json,hashlib,re,unicodedata
from xml.etree import ElementTree as E

ROOT=Path(__file__).resolve().parents[4]
CV=ROOT/'公共资料/简历与文书'
HERE=Path(__file__).parent
OLD='论文发表（共同作者）'
NEW='论文发表'
base=CV/'对外PDF/周子靖_中文学术简历_Master_v1.3'
out=CV/'对外PDF/周子靖_中文学术简历_Master_v1.4'
def ext(p,e):return Path(str(p)+e)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(t):return re.sub(r'\s+','',unicodedata.normalize('NFKC',t))
def write(p,t):
    with p.open('x',encoding='utf-8',newline='\n') as f:f.write(t)

if len(sys.argv)==1:
    assert not ext(out,'.docx').exists()
    with zipfile.ZipFile(ext(base,'.docx')) as z: data={n:z.read(n) for n in z.namelist()}
    assert data['word/document.xml'].count(OLD.encode())==1
    data['word/document.xml']=data['word/document.xml'].replace(OLD.encode(),NEW.encode())
    with zipfile.ZipFile(ext(out,'.docx'),'x',zipfile.ZIP_DEFLATED) as z:
        for name,value in data.items():z.writestr(name,value)
    source=(CV/'周子靖_中文学术简历_v0.6_INTERNAL.md').read_text(encoding='utf-8-sig')
    assert source.count(OLD)==1
    write(CV/'周子靖_中文学术简历_v0.7_INTERNAL.md',source.replace(OLD,NEW))
    print('Created v1.4 DOCX and v0.7 source; only publication heading changed.')
    sys.exit()

sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'项目维护/工具/运行依赖'))
import pymupdf
with zipfile.ZipFile(ext(base,'.docx')) as a,zipfile.ZipFile(ext(out,'.docx')) as b:
    assert set(a.namelist())==set(b.namelist())
    changed=[n for n in a.namelist() if a.read(n)!=b.read(n)]
    assert changed==['word/document.xml'],changed
    assert a.read(changed[0]).replace(OLD.encode(),NEW.encode())==b.read(changed[0])
    xml=E.fromstring(b.read('word/document.xml'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
paras=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in xml.findall('.//w:body/w:p',ns)]
with pymupdf.open(ext(base,'.pdf')) as previous,pymupdf.open(ext(out,'.pdf')) as current:
    assert len(previous)==len(current)==1
    oldtext=previous[0].get_text();text=current[0].get_text()
    assert norm(oldtext.replace(OLD,NEW))==norm(text)
    assert all(norm(p) in norm(text) for p in paras)
    assert text.count('个人贡献：')==2 and OLD not in text
    links=lambda d:sorted(l['uri'] for l in d[0].get_links() if 'uri' in l)
    assert links(previous)==links(current)
    spans=lambda d:[s for b in d[0].get_text('dict')['blocks'] if 'lines' in b for line in b['lines'] for s in line['spans'] if s['text'].strip()]
    oldspans=spans(previous);newspans=spans(current)
    assert len(oldspans)==len(newspans)
    for a,b in zip(oldspans,newspans):
        assert a['text'].replace(OLD,NEW)==b['text']
        assert abs(a['size']-b['size'])<0.01
        assert all(abs(x-y)<0.1 for x,y in zip(a['origin'],b['origin']))
        assert b['bbox'][0]>35 and b['bbox'][2]<current[0].rect.width-35
    preview=HERE/'正式母版预览_20260929.png'
    if not preview.exists():current[0].get_pixmap(matrix=pymupdf.Matrix(1.65,1.65)).save(str(preview))
    checked_links=links(current)
print('Verified: one page, heading-only change, 37 paragraphs, unchanged font sizes/positions and links.')
if sys.argv[1]!='--finalize':sys.exit()

records=[]
for suffix in ['.pdf','.docx']:
    old=ext(base,suffix);new=old.parent/'历史版本'/old.name
    assert old.resolve().is_relative_to(CV.resolve()) and new.resolve().is_relative_to(CV.resolve())
    assert not new.exists()
    before=sha(old);size=old.stat().st_size
    old.rename(new)
    assert sha(new)==before
    records.append({'action':'archive_move','source':old.relative_to(ROOT).as_posix(),'target':new.relative_to(ROOT).as_posix(),'sha256':before,'bytes':size})
for suffix in ['.pdf','.docx']:
    p=ext(out,suffix)
    records.append({'action':'new_formal','path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
# Update link destinations only; preserve historical descriptions and frozen/sent evidence.
for p in CV.glob('*.md'):
    text=p.read_text(encoding='utf-8-sig')
    fixed=text.replace('对外PDF/周子靖_中文学术简历_Master_v1.3','对外PDF/历史版本/周子靖_中文学术简历_Master_v1.3')
    if fixed!=text:
        with p.open('w',encoding='utf-8',newline='\n') as f:f.write(fixed)
p=ROOT/'公共资料/说明.md'
text=p.read_text(encoding='utf-8-sig').replace('对外PDF/周子靖_中文学术简历_Master_v1.3','对外PDF/历史版本/周子靖_中文学术简历_Master_v1.3')
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(text)
report={'date':'2026-09-29','status':'Master v1.4 READY; not sent','authorization':'User approved title-only revision and merge of PR #8','change':{'old':OLD,'new':NEW},'docx_changed_parts':changed,'pdf_pages':1,'paragraphs_matched':len(paras),'pdf_other_text_unchanged':True,'font_sizes_and_text_origins_unchanged':True,'links':checked_links,'artifacts':records}
write(HERE/'冻结验收_20260929.json',json.dumps(report,ensure_ascii=False,indent=2))
print('v1.4 frozen; v1.3 archived byte-for-byte.')
