from pathlib import Path
import sys,json,hashlib,re,importlib.metadata,csv
sys.path.insert(0,str(Path(__file__).parent/'a4_runtime'))
import fitz
from docx import Document
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'A线工作区/联系/刘癸庚'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'\s+','',s)
fail=[];checks={}
mfile=P/'04_Background_Notes/本地复制与基线哈希_v1.json'
m=json.loads(mfile.read_text(encoding='utf-8'))
for item in m['copies']:
 cp=P/item['copy']
 if cp.suffix=='.docx':
  item['after_copy_customized']=True
  item['initial_copy_sha256']=item['copy_sha256']
  item['current_customized_sha256']=sha(cp)
 else:
  assert sha(cp)==item['copy_sha256']==sha(Path(item['source'])),item
checks['copies_and_original_sources_match']=True
assert all(sha(Path(x['path']))==x['sha256'] for x in m['baseline'].values())
checks['frozen_master_unchanged']=True
mfile.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
orig=json.loads((ROOT/'A线工作区/接手原件清单_20260926.json').read_text(encoding='utf-8-sig'))
assert all(sha(ROOT/x['Path']).lower()==x['SHA256'].lower() for x in orig['files'])
checks['original_files_unchanged']=len(orig['files'])
cv=P/'02_CV/周子靖_中文学术简历_刘癸庚版_v1_INTERNAL.pdf'
ps=P/'03_Project_Sheet/output/周子靖_毕设项目页_刘癸庚版_v1_INTERNAL.pdf'
pdfs=[]
for f,expected in [(cv,1),(ps,1),*[(x,n) for x,n in zip(sorted((P/'05_Send_Readiness/附件备选').glob('*.pdf')), [9,10,2])]]:
 d=fitz.open(f)
 # Attachment expected pages mapped by name, independent of locale sorting.
 if '本科成绩单' in f.name:expected=2
 elif '吸波材料' in f.name:expected=9
 elif '晶格波' in f.name:expected=10
 assert len(d)==expected,(str(f),len(d))
 if f in (cv,ps):
  for page in d:
   for block in page.get_text('dict')['blocks']:
    if block['type']!=0:continue
    for ln in block['lines']:
     for span in ln['spans']:
      r=fitz.Rect(span['bbox']);assert r.x0>=0 and r.y0>=0 and r.x1<=page.rect.width+.1 and r.y1<=page.rect.height+.1,(f,span)
  assert 'INTERNAL' in d[0].get_text()
 pdfs.append({'file':str(f.relative_to(P)),'pages':len(d),'bytes':f.stat().st_size,'sha256':sha(f)})
checks['pdfs']=pdfs
doc=Document(cv.with_suffix('.docx'));pdf=fitz.open(cv);text=norm(pdf[0].get_text())
for para in doc.paragraphs:
 assert norm(para.text) in text,para.text
checks['cv_docx_pdf_paragraphs_match']=len(doc.paragraphs)
baseline=Document(Path(m['baseline']['docx']['path']));differences=[{'before':a.text,'after':b.text} for a,b in zip(baseline.paragraphs,doc.paragraphs) if a.text!=b.text]
assert len(differences)==3 and len(baseline.paragraphs)==len(doc.paragraphs),differences
checks['cv_only_three_body_edits']=differences
d1=fitz.open(ps);d2=fitz.open(P/'03_Project_Sheet/qa_regenerated'/ps.name)
assert d1[0].get_pixmap(dpi=120).samples==d2[0].get_pixmap(dpi=120).samples
checks['project_independent_rebuild_pixels_equal']=True
df=list(csv.DictReader((P/'03_Project_Sheet/source/reflection_archived.tsv').open(encoding='utf-8'),delimiter='\t'))
assert len(df)==201
low=[float(x['freq_GHz']) for x in df if float(x['rl_dB'])<-10]
assert abs(min(low)-4.8)<1e-8 and max(low)==18
checks['archived_data_points']=201
checks['archived_reflection_interval']=[min(low),max(low)]
checks['email_chinese_characters_excluding_signature']=len(re.findall(r'[\u4e00-\u9fff]',(P/'01_Email/邮件正文_v1.txt').read_text(encoding='utf-8').split('周子靖 |')[0]))
# All package/index links; no requests to remote URLs.
files=list(P.rglob('*.md'))+[ROOT/'A线_工作台.md',ROOT/'A线工作区/招生核验与PI行动表.md',P.parent/'A-line_Outreach_Tracker.md']
links=0
for f in files:
 for target in re.findall(r'\]\(([^)]+)\)',f.read_text(encoding='utf-8')):
  if re.match(r'(https?://|mailto:|#)',target):continue
  path=target.split('#',1)[0]
  if not path:continue
  links+=1
  if not (f.parent/path).exists():fail.append((str(f.relative_to(ROOT)),target))
checks['local_links_checked']=links
checks['broken_links']=fail
checks['dependencies']={x:importlib.metadata.version(x) for x in ['PyMuPDF','python-docx','reportlab','beautifulsoup4']}
(P/'05_Send_Readiness/文件验收_v1.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False,indent=2))
if fail:raise RuntimeError('Broken local links')
