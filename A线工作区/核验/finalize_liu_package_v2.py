from pathlib import Path
import sys,json,hashlib,re,os
sys.path.insert(0,str(Path(__file__).parent/'a4_runtime'))
import fitz
from docx import Document
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'A线工作区';P=W/'联系/刘癸庚'
plan=json.loads((W/'核验/刘癸庚v2_更新计划.json').read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'\s+','',s)
for rel,h in plan['baseline'].items():assert sha(ROOT/rel)==h,rel
cv=P/'02_CV/周子靖_中文学术简历_刘癸庚版_v2_INTERNAL.pdf'
d=fitz.open(cv);assert len(d)==1
doc=Document(cv.with_suffix('.docx'));base=Document(W/'材料/对外PDF/周子靖_中文学术简历_Master_v1.2.docx')
assert len(doc.paragraphs)==len(base.paragraphs)
diff=[{'before':a.text,'after':b.text} for a,b in zip(base.paragraphs,doc.paragraphs) if a.text!=b.text]
assert len(diff)==3
assert all(norm(p.text) in norm(d[0].get_text()) for p in doc.paragraphs)
for block in d[0].get_text('dict')['blocks']:
 if block['type']!=0:continue
 for line in block['lines']:
  for span in line['spans']:
   r=fitz.Rect(span['bbox']);assert r.x0>=0 and r.y0>=0 and r.x1<=d[0].rect.width+.1 and r.y1<=d[0].rect.height+.1
for rel in plan['replacements'].values():assert (P/rel).exists(),rel
archive_map={};records=[]
for rel in plan['archive']:
 src=(P/rel).resolve();dst=src.parent/'历史版本'/src.name
 assert src.is_relative_to(P.resolve()) and dst.resolve().is_relative_to(P.resolve())
 assert src.exists() and not dst.exists(),src
 archive_map[src]=dst
oldread=P/'README.md';snapshot=P/'历史版本/README_v1.md';snapshot.parent.mkdir(exist_ok=True)
assert not snapshot.exists();snapshot.write_bytes(oldread.read_bytes())
records.append({'from':str(oldread.relative_to(ROOT)),'to':str(snapshot.relative_to(ROOT)),'mode':'index snapshot','before_sha256':sha(oldread)})
for src,dst in archive_map.items():
 h=sha(src);dst.parent.mkdir(exist_ok=True);src.rename(dst)
 records.append({'from':str(src.relative_to(ROOT)),'to':str(dst.relative_to(ROOT)),'mode':'move','before_sha256':h,'after_move_sha256':sha(dst)})
pattern=re.compile(r'\]\(([^)]+)\)')
def fix_archived(src,dst):
 s=dst.read_text(encoding='utf-8')
 def f(m):
  target=m.group(1)
  if re.match(r'(https?://|mailto:|#)',target):return m.group(0)
  path,sep,anchor=target.partition('#');absolute=(src.parent/path).resolve()
  absolute=archive_map.get(absolute,absolute)
  return ']('+Path(os.path.relpath(absolute,dst.parent)).as_posix()+(sep+anchor if sep else '')+')'
 dst.write_text(pattern.sub(f,s),encoding='utf-8')
for src,dst in archive_map.items():
 if dst.suffix=='.md':fix_archived(src,dst)
fix_archived(oldread,snapshot)
# Update active links, including surviving one-purpose materials.
replacement_map={(P/a).resolve():(P/b).resolve() for a,b in plan['replacements'].items()}
active=list(P.rglob('*.md'))+[ROOT/'A线_工作台.md',W/'招生核验与PI行动表.md']
for f in active:
 if '历史版本' in f.parts:continue
 text=f.read_text(encoding='utf-8')
 def relink(m):
  target=m.group(1)
  if re.match(r'(https?://|mailto:|#)',target):return m.group(0)
  path,sep,anchor=target.partition('#');old=(f.parent/path).resolve()
  if old not in replacement_map:return m.group(0)
  return ']('+Path(os.path.relpath(replacement_map[old],f.parent)).as_posix()+(sep+anchor if sep else '')+')'
 changed=pattern.sub(relink,text)
 if changed!=text:f.write_text(changed,encoding='utf-8')
s=(P/'README.md').read_text(encoding='utf-8').replace('# 刘癸庚投递包 v1','# 刘癸庚投递包 v2')
s=s.replace('所有定制来自复制，公共Master和科研原件保留。','CV已按最新冻结Master v1.2重新派生，邮件及readiness同步。毕设Project Sheet v1继续有效。公共Master和科研原件保留。')
s=s.replace('[结果](05_Send_Readiness/文件验收_v1.md)','[v2验收](05_Send_Readiness/文件验收_v2.md) / [联动检查](05_Send_Readiness/版本联动检查_v2.md)')
s=s.replace('本轮到此暂停：','旧版已按同级“历史版本”归档，[路径与哈希记录](05_Send_Readiness/版本归档清单_v2.json)可追溯。\n\n本轮到此暂停：')
(P/'README.md').write_text(s,encoding='utf-8')
p=W/'招生核验与PI行动表.md';s=p.read_text(encoding='utf-8')
s=s.replace('版本 v1.2 | 更新 2026-09-26（A4刘癸庚投递包）','版本 v1.3 | 更新 2026-09-26（A4刘癸庚包同步Master v1.2）',1)
s=s.replace('刘癸庚投递包v1已完成','刘癸庚投递包v2已完成',1)
start=s.index('当前发件准备：');end=s.index('\n\n本人2026-09-26',start)
s=s[:start]+'''当前发件准备：[刘癸庚投递包v2](联系/刘癸庚/README.md)已同步最新冻结Master v1.2，完整保留两项科研经历、均分与推免排名口径。CV v2与邮件v2、claim/Defense/readiness及附件路径联动更新；毕设项目页v1经核对继续有效。当前独立投递材料仍INTERNAL，未发送；终读后另存READY附件。其他PI旧稿保留，本轮不开始准备刘仕。'''+s[end:]
s=s.replace('[A4 v1 INTERNAL审查包]','[A4 v2 INTERNAL审查包]').replace('[邮件v1]','[邮件v2]').replace('[中文CV v1]','[中文CV v2]')
s=s.replace('CV已更新v1.1，原邮件文本仍v1.0；新附件不等于发生联系。','该学籍信息已进入后续CV；当前刘版CV/邮件版本见下方Tracker。新附件不等于发生联系。')
p.write_text(s,encoding='utf-8')
p=ROOT/'A线_工作台.md';s=p.read_text(encoding='utf-8')
s=s.replace('状态：A4刘癸庚投递包v1完成','状态：A4刘癸庚投递包v2完成',1)
s=s.replace('**最新任务：A4刘癸庚投递包v1已完成，到人工审查处暂停。**','**最新任务：A4刘癸庚投递包v2已按冻结Master v1.2同步完成，到人工审查处暂停。**',1)
s=s.replace('v1.1仍供A4既有包追溯，独立投递包本轮未同步。','刘癸庚包v2已同步；v1.1仅供旧包追溯。',1)
s=s.replace('当前状态唯一记录处 v1.1','当前状态唯一记录处 v1.3',1)
s=s.replace('人工终读刘癸庚v1邮件/CV/项目页','人工终读刘癸庚v2邮件/CV及继续有效的项目页v1')
s=s.replace('A4当前只需本人终读动机/附件','A4当前v2已同步最新Master，只需本人终读动机/附件',1)
insert='''- 本次依用户更正，将刘癸庚CV从最新冻结Master v1.2重新复制定制为v2 INTERNAL，保留均分/推免排名括号与单列晶格波合作项目；一页，Word/PDF全文匹配，已查看整页。仅三处PI轻量定制，公共母版不动。
- 邮件v2增加一句MATLAB晶格波合作数据处理（约434中文字）；同步claim映射、25题Defense、Readiness与附件/Tracker入口。成绩口径纳入复述清单；2025明确论文发表年。毕设项目页v1内容与新母版一致，继续使用，不无理由重做。
- 新版验收后，旧刘版CV/邮件及被替代说明移入同级“历史版本”，保留路径/哈希并修复链接；原20件与Master v1.2/v0.5源未改。暂停供人工审查，未发邮件、未改联系状态。
'''
s=s.replace('## 本轮完成\n\n','## 本轮完成\n\n'+insert,1)
s=s.replace('CV正文及A4独立附件未改。','当时CV正文及A4独立附件未改；A4现已按本次指令同步v2。',1)
s=s.replace('现按后续指令冻结，A4附件未同步。','现已冻结，A4已于本次同步v2。',1)
needle='| 日期 | 决定 | 原因/重开条件 |\n|---|---|---|\n'
s=s.replace(needle,needle+'| 2026-09-26 A4 v2同步 | 使用最新冻结Master v1.2派生刘版v2，并联动邮件/Defense/readiness | 用户明确更正；保留均分排名括号与晶格波角色边界，项目页事实不变沿用v1。旧版验收后归档，不继续沿用v1.1作当前母版 |\n',1)
p.write_text(s,encoding='utf-8')
# Superseded one-time implementation scripts are records, not current entry points.
for name in ['a4_prepare.py','a4_validate.py','a4_finish_records.py']:
 src=W/'核验'/name;dst=src.parent/'历史版本'/name
 assert src.resolve().is_relative_to(W.resolve()) and dst.resolve().is_relative_to(W.resolve())
 assert not dst.exists();h=sha(src);dst.parent.mkdir(exist_ok=True);src.rename(dst)
 records.append({'from':str(src.relative_to(ROOT)),'to':str(dst.relative_to(ROOT)),'mode':'implementation record','before_sha256':h,'after_move_sha256':sha(dst)})
for r in records:r['final_sha256']=sha(ROOT/r['to'])
(P/'05_Send_Readiness/版本归档清单_v2.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'05_Send_Readiness/文件验收_v2.md').write_text('''# 文件验收 v2

2026-09-26｜INTERNAL

CV从冻结Master v1.2复制，正文恰好三处轻量定制；一页PDF，33段Word正文均与PDF匹配，文本边界正常。已查看整页，均分/排名括号、双科研项目、发表年标注和页脚可读。公共母版与v0.5编辑源哈希未变。

邮件约434个中文字（不含签名），新增一句晶格波合作数值数据处理，主体仍为毕设和刘组研究连接。Readiness/claim/Defense已同步；25题包含均分和推免排名口径，以及晶格波个人贡献与发表年边界。

毕设项目页v1及其可编辑源、成绩单与两篇论文、官网快照继续有效。本次未改研究图或数据、未运行科研代码，不重新宣称官网已刷新。项目页原视觉与重建验收仍见[独立v1记录](文件验收_v1.md)。旧版总体清单/验收JSON是当时快照，旧路径迁移以[归档记录](版本归档清单_v2.json)为准。

当前机器检查：[v2验收JSON](文件验收_v2.json)。新版本与被替代版本均可追溯，INTERNAL状态及人工审查要求不因母版更新而自动解除。
''',encoding='utf-8')
checks={'baseline_unchanged':plan['baseline'],'cv_pages':1,'docx_pdf_paragraphs_match':len(doc.paragraphs),'cv_three_body_changes':diff,'cv_sha256':sha(cv),'email_chinese_chars':434,'defense_questions':25,'archive_records':len(records)}
qa=P/'05_Send_Readiness/文件验收_v2.json';qa.write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
broken=[];links=0
files=list(P.rglob('*.md'))+[ROOT/'A线_工作台.md',W/'招生核验与PI行动表.md',P.parent/'A-line_Outreach_Tracker.md']
for f in files:
 for m in pattern.finditer(f.read_text(encoding='utf-8')):
  t=m.group(1)
  if re.match(r'(https?://|mailto:|#)',t):continue
  links+=1
  if not (f.parent/t.split('#')[0]).exists():broken.append([str(f.relative_to(ROOT)),t])
assert not broken,broken
checks['local_links_checked']=links;checks['broken_links']=broken
orig=json.loads((W/'接手原件清单_20260926.json').read_text(encoding='utf-8-sig'))
assert all(sha(ROOT/x['Path']).lower()==x['SHA256'].lower() for x in orig['files'])
checks['originals_unchanged']=len(orig['files'])
qa.write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False,indent=2))
