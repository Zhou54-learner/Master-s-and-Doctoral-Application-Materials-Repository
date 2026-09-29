"""Verify the actual DOCX/PDF export, factual guardrails and baseline preservation."""
from pathlib import Path
import sys, json, hashlib, re, zipfile, csv, unicodedata
from xml.etree import ElementTree as E
from decimal import Decimal

ROOT=Path(__file__).resolve().parents[4]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'项目维护/工具/运行依赖'))
import pymupdf

HERE=Path(__file__).parent
CV=ROOT/'公共资料/简历与文书'
stem=CV/'校对稿/周子靖_中文学术简历_Master_v1.3_CANDIDATE'
docx=Path(str(stem)+'.docx');pdf=Path(str(stem)+'.pdf')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def normalize(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s))
with zipfile.ZipFile(docx) as z:
    xml=E.fromstring(z.read('word/document.xml'))
    rels=E.fromstring(z.read('word/_rels/document.xml.rels'))
paras=[''.join(p.itertext()) for p in xml.findall('.//w:body/w:p',ns)]
texts=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in xml.findall('.//w:body/w:p',ns)]
source_lines=[]
for s in (CV/'周子靖_中文学术简历_v0.6_INTERNAL.md').read_text(encoding='utf-8').splitlines():
    s=s.strip()
    if not s:continue
    s=re.sub(r'^#+\s*','',s)
    s=re.sub(r'^-\s*','',s).replace('*','')
    if not s.startswith('Zijing'):s=s.replace(' | ','')
    source_lines.append(s)
normdoc=normalize(''.join(texts)).replace('*','')
source_missing=[s for s in source_lines if normalize(s) not in normdoc]
assert not source_missing,source_missing
doc=pymupdf.open(pdf);assert len(doc)==1
page=doc[0];pdftext=page.get_text();normpdf=normalize(pdftext)
missing=[s for s in texts if normalize(s) not in normpdf]
assert not missing,missing
assert pdftext.count('个人贡献：')==2
third=pdftext.split('3. Zeyang')[1].split('技术与语言')[0]
assert '个人贡献' not in third
for s in ['202410213227','项目成员','调整分阶段搜索流程','21/46','80.20/100','64(19): 9435-9446','10.1021/acs.inorgchem.4c05411']:
    assert normalize(s) in normpdf,s
for s in ['国家级已结题','负责人','主导实验','共同一作','开发遗传算法','构建分阶段搜索流程','2025.09推免口径']:
    assert s not in pdftext,s
urls=[l.get('uri') for l in page.get_links() if l.get('uri')]
for u in ['mailto:zhouzijing54@gmail.com','https://doi.org/10.20249/j.cnki.2096-5974.2025.01.011','https://doi.org/10.1360/SSPMA-2024-0393','https://doi.org/10.1021/acs.inorgchem.4c05411']:
    assert u in urls,u
baseline=json.loads((HERE/'基线保全_20260928.json').read_text(encoding='utf-8'))
for r in baseline:
    p=ROOT/r['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['path']
rows=list(csv.DictReader((ROOT/'公共资料/事实核验/成绩单转录_20260926.csv').open(encoding='utf-8-sig')))
scores=[]
for r in rows:
    try:scores.append(Decimal(r['score']))
    except:pass
assert len(scores)==91 and sum(scores)==Decimal('7298.6')
cross=json.loads((ROOT/'公共资料/事实核验/PR8审查_20260928/公开证据/Crossref.json').read_text(encoding='utf-8'))['message']
authors=[a['given']+' '+a['family'] for a in cross['author']]
assert authors==['Zeyang Zhang','Jun Li','Juan Cui','Zegeng Chen','Zhengyu Zhang','Nandong Deng','Yulin Zeng','Zijing Zhou','Zhongxiang Zhou']
assert (cross['volume'],cross['issue'],cross['page'],cross['DOI'])==('64','19','9435-9446','10.1021/acs.inorgchem.4c05411')
spans=[s for b in page.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans'] if s['text'].strip()]
bounds=[min(s['bbox'][0] for s in spans),min(s['bbox'][1] for s in spans),max(s['bbox'][2] for s in spans),max(s['bbox'][3] for s in spans)]
assert bounds[0]>35 and bounds[2]<page.rect.width-35 and bounds[1]>30 and bounds[3]<page.rect.height-35
bold_names=[s['text'] for s in spans if 'Bold' in s['font'] and ('周子靖' in s['text'] or 'Zijing' in s['text'])]
assert len(bold_names)>=4,bold_names
page.get_pixmap(matrix=pymupdf.Matrix(1.65,1.65)).save(str(HERE/'候选整页预览.png'))
report={
 'status':'Master v1.3 CANDIDATE; not READY; not sent',
 'word_export_pages':1,'pdf_pages':len(doc),'page_pt':list(page.rect),
 'template':'Master v1.2 Word; A4, original margins, Source Han Sans CN',
 'body_font_pt':10.5,'body_leading_pt':14,'heading_pt':11.5,'doi_note_pt':9,
 'chemical_formula':'actual Word subscripts; smaller subscript glyphs are not body-size compression',
 'docx_paragraphs_verified_in_pdf':len(texts),'missing_paragraphs':missing,
 'source_lines_verified_in_docx':len(source_lines),'missing_source_lines':source_missing,
 'clickable_links':urls,'nonempty_text_bounds_pt':bounds,'author_bold_spans':bold_names,
 'baseline_files_unchanged':len(baseline),'score_sum':str(sum(scores)),'numeric_courses':len(scores),'arithmetic_mean':str(sum(scores)/len(scores)),
 'third_paper_authors':authors,'third_paper_author_position':8,'personal_contribution_lines':2,
 'artifacts':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [docx,pdf]],
 'limitations':['local factual originals not independently verified online','ACS HTTP 403; bibliography checked with publisher-deposited Crossref metadata','original source code not rerun','candidate must be approved by user before READY']}
(HERE/'验收记录_20260928.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
