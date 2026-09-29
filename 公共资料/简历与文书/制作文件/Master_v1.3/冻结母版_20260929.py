"""Validate and freeze the reviewed candidate; never overwrite any artifact."""
from pathlib import Path
from xml.etree import ElementTree as ET
from decimal import Decimal
import sys, re, unicodedata, zipfile, json, hashlib, csv, shutil

ROOT=Path(__file__).resolve().parents[4]
CV=ROOT/'公共资料/简历与文书'
HERE=Path(__file__).parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'项目维护/工具/运行依赖'))
import pymupdf

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s): return re.sub(r'\s+','',unicodedata.normalize('NFKC',s))
def rel(p): return p.relative_to(ROOT).as_posix()

candidate=CV/'校对稿/周子靖_中文学术简历_Master_v1.3_CANDIDATE'
formal=CV/'对外PDF/周子靖_中文学术简历_Master_v1.3'
copies=[(Path(str(candidate)+ext),Path(str(formal)+ext)) for ext in ['.pdf','.docx']]
moves=[(CV/f'对外PDF/周子靖_中文学术简历_Master_v1.2{ext}',CV/f'对外PDF/历史版本/周子靖_中文学术简历_Master_v1.2{ext}') for ext in ['.pdf','.docx']]
report_path=HERE/'冻结验收_20260929.json'
assert not report_path.exists()
for source,target in copies+moves:
    assert source.is_file(),source
    assert not target.exists(),target
baseline=json.loads((HERE/'基线保全_20260928.json').read_text(encoding='utf-8'))
for item in baseline: assert sha(ROOT/item['path'])==item['sha256'],item['path']
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(copies[1][0]) as z:
    xml=ET.fromstring(z.read('word/document.xml'))
paragraphs=[''.join(n.text or '' for n in p.findall('.//w:t',ns)) for p in xml.findall('.//w:body/w:p',ns)]
doc=pymupdf.open(copies[0][0])
assert len(doc)==1
page=doc[0]
text=page.get_text()
assert all(norm(p) in norm(text) for p in paragraphs)
for line in (CV/'周子靖_中文学术简历_v0.6_INTERNAL.md').read_text(encoding='utf-8').splitlines():
    line=re.sub(r'^#+\s*|^-\s*','',line.strip()).replace('*','')
    if not line: continue
    if not line.startswith('Zijing'): line=line.replace(' | ','')
    assert norm(line) in norm(''.join(paragraphs)).replace('*',''),line
for value in ['202410213227','项目成员','调整分阶段搜索流程','21/46','80.20/100','2026.08','64(19): 9435-9446']:
    assert norm(value) in norm(text),value
for value in ['国家级已结题','负责人','主导实验','共同一作','开发遗传算法','CANDIDATE','INTERNAL','2025.09推免口径']:
    assert value not in text,value
assert text.count('个人贡献：')==2
assert '个人贡献' not in text.split('3. Zeyang')[1].split('技术与语言')[0]
urls=[l.get('uri') for l in page.get_links() if l.get('uri')]
for uri in ['mailto:zhouzijing54@gmail.com','https://doi.org/10.20249/j.cnki.2096-5974.2025.01.011','https://doi.org/10.1360/SSPMA-2024-0393','https://doi.org/10.1021/acs.inorgchem.4c05411']:
    assert uri in urls,uri
scores=[]
with (ROOT/'公共资料/事实核验/成绩单转录_20260926.csv').open(encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        try:scores.append(Decimal(row['score']))
        except Exception:pass
assert len(scores)==91 and sum(scores)==Decimal('7298.6')
spans=[s for b in page.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans'] if s['text'].strip()]
assert all(s['bbox'][0]>35 and s['bbox'][2]<page.rect.width-35 and s['bbox'][1]>30 and s['bbox'][3]<page.rect.height-35 for s in spans)
page.get_pixmap(matrix=pymupdf.Matrix(1.65,1.65)).save(str(HERE/'正式母版预览_20260929.png'))
records=[]
for source,target in copies:
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)
    assert sha(source)==sha(target)
    records.append({'action':'freeze_copy','source':rel(source),'target':rel(target),'sha256':sha(target),'bytes':target.stat().st_size})
for source,target in moves:
    assert source.resolve().is_relative_to(CV.resolve()) and target.resolve().is_relative_to(CV.resolve())
    target.parent.mkdir(parents=True,exist_ok=True)
    before=sha(source)
    source.rename(target)
    assert sha(target)==before
    records.append({'action':'archive_move','source':rel(source),'target':rel(target),'sha256':before,'bytes':target.stat().st_size})
# Repair paths only in live Markdown; never touch sent material or historical snapshot bytes.
link_repairs=[]
for file in [ROOT/'A线_西湖博士/工作台.md',ROOT/'公共资料/说明.md',CV/'中文CV_Master_v1.2_候选版_changelog.md',CV/'材料版本与发送说明.md',CV/'中文CV_Master_v1.3_审查结论与验收.md']:
    old=file.read_text(encoding='utf-8-sig')
    new=old.replace('对外PDF/周子靖_中文学术简历_Master_v1.2','对外PDF/历史版本/周子靖_中文学术简历_Master_v1.2')
    if new!=old:
        before=sha(file)
        file.write_text(new,encoding='utf-8')
        link_repairs.append({'path':rel(file),'before_sha256':before,'after_sha256':sha(file)})
for item in baseline:
    p=ROOT/item['path']
    if not p.exists(): p=next(target for source,target in moves if source==p)
    assert sha(p)==item['sha256'],str(p)
report={'date':'2026-09-29','status':'Master v1.3 READY; not sent','authorization':'User instruction: 先把母版cv敲定吧; assistant final review and freeze, not a claim of user line-by-line approval.','pdf_pages':1,'docx_paragraphs_matched':len(paragraphs),'body_font_pt':10.5,'body_leading_pt':14,'all_required_links':urls,'numeric_courses':91,'score_sum':str(sum(scores)),'arithmetic_mean':str(sum(scores)/91),'personal_contribution_lines':2,'baseline_files_preserved':len(baseline),'artifacts':records,'link_repairs':link_repairs,'limitations':['No external submission or email sent','No new independent online validation of private certificates','Third paper remains bibliography only; no added personal contribution']}
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','pdf_pages','docx_paragraphs_matched','baseline_files_preserved']},ensure_ascii=False))
