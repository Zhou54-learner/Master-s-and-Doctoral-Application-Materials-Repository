"""Prepare and verify Tian v2 from frozen Master v1.4; retain all v1 assets."""
from pathlib import Path
from xml.etree import ElementTree as E
import sys,zipfile,json,hashlib,shutil,re,unicodedata,os

ROOT=Path(__file__).resolve().parents[4]
PACK=ROOT/'A线_西湖博士/联系材料/田静逸'
OUT=PACK/'当前材料'
HERE=Path(__file__).parent
BASE=ROOT/'公共资料/简历与文书'
ATT=OUT/'首封附件_待审阅'
STEM=OUT/'周子靖_中文学术简历_田静逸版_v2_CANDIDATE'
OLD='计算物理 · 科学机器学习 · 物理驱动的逆向设计'
NEW='计算物理 · 电磁/光子学仿真 · 物理驱动的逆向设计'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def ext(p,s):return Path(str(p)+s)
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s))
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:f.write(s)
src=BASE/'对外PDF/周子靖_中文学术简历_Master_v1.4.docx'

if len(sys.argv)==1:
    assert not ext(STEM,'.docx').exists()
    baseline=[src,src.with_suffix('.pdf'),BASE/'周子靖_中文学术简历_v0.7_INTERNAL.md']
    baseline+=list((ROOT/'A线_西湖博士/联系材料/刘癸庚/当前材料').rglob('*'))
    baseline+=list((ROOT/'A线_西湖博士/联系材料/刘仕').rglob('*'))
    frozen=[{'path':rel(p),'sha256':sha(p)} for p in baseline if p.is_file()]
    previous=[p for p in OUT.rglob('*') if p.is_file() and 'v2_' not in p.name]
    write(PACK/'准备记录/v2_修改前基线.json',json.dumps({'protected':frozen,'old_files':[{'path':rel(p),'sha256':sha(p)} for p in previous]},ensure_ascii=False,indent=2))
    with zipfile.ZipFile(src) as z:data={n:z.read(n) for n in z.namelist()}
    assert data['word/document.xml'].count(OLD.encode())==1
    data['word/document.xml']=data['word/document.xml'].replace(OLD.encode(),NEW.encode())
    with zipfile.ZipFile(ext(STEM,'.docx'),'x',zipfile.ZIP_DEFLATED) as z:
        for k,v in data.items():z.writestr(k,v)
    source=(BASE/'周子靖_中文学术简历_v0.7_INTERNAL.md').read_text(encoding='utf-8-sig')
    assert source.count(OLD)==1
    write(ext(STEM,'.md'),source.replace(OLD,NEW))
    ATT.mkdir(exist_ok=True)
    for name in ['周子靖_本科成绩单.pdf','磁纳米合金与石墨烯复合吸波材料_2025.pdf','二维尘埃等离子体晶格波特性研究_2025.pdf']:
        target=ATT/name
        assert not target.exists()
        shutil.copyfile(OUT/'首封附件_待终读'/name,target)
    mail=(OUT/'第一封套磁邮件_田静逸_v2_CANDIDATE.md').read_text(encoding='utf-8')
    write(OUT/'邮件正文_v2.txt',mail.split('\n---\n',1)[1].strip()+'\n')
    print('v2 Word, Markdown, email body and three supporting PDFs prepared.')
    sys.exit()

sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'项目维护/工具/运行依赖'))
import pymupdf
with zipfile.ZipFile(src) as a,zipfile.ZipFile(ext(STEM,'.docx')) as b:
    assert set(a.namelist())==set(b.namelist())
    changed=[n for n in a.namelist() if a.read(n)!=b.read(n)]
    assert changed==['word/document.xml']
    assert a.read(changed[0]).replace(OLD.encode(),NEW.encode())==b.read(changed[0])
    xml=E.fromstring(b.read(changed[0]))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
paras=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in xml.findall('.//w:body/w:p',ns)]
pdf=ATT/'周子靖_学术简历.pdf'
with pymupdf.open(src.with_suffix('.pdf')) as previous,pymupdf.open(pdf) as current:
    assert len(previous)==len(current)==1
    page=current[0];text=page.get_text()
    assert norm(previous[0].get_text().replace(OLD,NEW))==norm(text)
    assert all(norm(p) in norm(text) for p in paras)
    links=lambda d:sorted(l['uri'] for l in d[0].get_links() if 'uri' in l)
    assert links(previous)==links(current)
    assert text.count('个人贡献：')==2
    assert '论文发表（共同作者）' not in text
    assert 'CANDIDATE' not in text and 'INTERNAL' not in text
    spans=[s for b in page.get_text('dict')['blocks'] if 'lines' in b for line in b['lines'] for s in line['spans'] if s['text'].strip()]
    assert all(s['bbox'][0]>35 and s['bbox'][2]<page.rect.width-35 and s['bbox'][3]<page.rect.height-35 for s in spans)
    preview=HERE/'田静逸CV_v2_整页预览.png'
    if not preview.exists():page.get_pixmap(matrix=pymupdf.Matrix(1.65,1.65)).save(str(preview))
expected={'周子靖_学术简历.pdf':1,'周子靖_本科成绩单.pdf':2,'磁纳米合金与石墨烯复合吸波材料_2025.pdf':9,'二维尘埃等离子体晶格波特性研究_2025.pdf':10}
assert {p.name for p in ATT.iterdir()}==set(expected)
for name,pages in expected.items():
    with pymupdf.open(ATT/name) as p:assert len(p)==pages,(name,len(p))
    if name!='周子靖_学术简历.pdf':
        original=OUT/'首封附件_待终读'/name
        if not original.exists():original=OUT/'历史版本/v1/首封附件_待终读'/name
        assert sha(ATT/name)==sha(original)
mail=(OUT/'第一封套磁邮件_田静逸_v2_CANDIDATE.md').read_text(encoding='utf-8')
body=(OUT/'邮件正文_v2.txt').read_text(encoding='utf-8')
assert body==mail.split('\n---\n',1)[1].strip()+'\n'
assert '收件人：tianjingyi@westlake.edu.cn' in mail and '主题：博士生申请+周子靖' in mail
assert body.startswith('田老师您好：') and body.endswith('zhouzijing54@gmail.com\n')
baseline=json.loads((PACK/'准备记录/v2_修改前基线.json').read_text(encoding='utf-8'))
for r in baseline['protected']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
print('Validated four PDFs, one-page CV, interest-only change, email/body agreement and protected assets.')
if sys.argv[1]!='--archive':sys.exit()

# Archive superseded v1 only after v2 passed content and visual review.
mapping={ROOT/r['path']:OUT/'历史版本/v1'/Path(r['path']).relative_to(OUT.relative_to(ROOT)) for r in baseline['old_files']}
records=[]
for r in baseline['old_files']:
    source=ROOT/r['path'];target=mapping[source]
    assert source.resolve().is_relative_to(OUT.resolve()) and target.resolve().is_relative_to(OUT.resolve())
    assert sha(source)==r['sha256'] and not target.exists()
    target.parent.mkdir(parents=True,exist_ok=True)
    old_text=source.read_text(encoding='utf-8') if source.suffix=='.md' else None
    size=source.stat().st_size
    source.rename(target)
    assert sha(target)==r['sha256']
    if old_text is not None:
        def rebase(m):
            dest=m.group(1)
            if '://' in dest or dest.startswith('#'):return m.group(0)
            parts=dest.split('#',1)
            old_dest=(source.parent/parts[0]).resolve()
            new_dest=mapping.get(old_dest,old_dest)
            link=os.path.relpath(new_dest,target.parent).replace('\\','/')
            if len(parts)==2:link+='#'+parts[1]
            return ']('+link+')'
        fixed=re.sub(r'\]\(([^)]+)\)',rebase,old_text)
        if fixed!=old_text:
            with target.open('w',encoding='utf-8',newline='\n') as f:f.write(fixed)
    records.append({'source':rel(source),'target':rel(target),'bytes_before':size,'sha256_before':r['sha256'],'sha256_after':sha(target),'index_links_rebased':sha(target)!=r['sha256']})
report={'date':'2026-09-29','status':'v2 CANDIDATE; verified; pending Chat review, merge and user final inspection; not sent','base':'Master v1.4 READY','cv_change':{'old':OLD,'new':NEW},'pdf_pages':1,'paragraphs_matched':len(paras),'body_font_pt':10.5,'interest_only_change':True,'protected_files_unchanged':len(baseline['protected']),'email_body_characters':len(body),'attachments':[{'path':rel(ATT/name),'pages':pages,'bytes':(ATT/name).stat().st_size,'sha256':sha(ATT/name)} for name,pages in expected.items()],'attachment_bytes_total':sum((ATT/n).stat().st_size for n in expected),'archive':records}
write(PACK/'准备记录/邮件包_v2_验收与归档_20260929.json',json.dumps(report,ensure_ascii=False,indent=2))
print('v1 archived; final v2 verification record created.')
