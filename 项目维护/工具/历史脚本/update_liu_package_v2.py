"""One-time v2 preparation. No outreach or research-code execution."""
from pathlib import Path
import sys,json,hashlib,re
sys.path.insert(0,str(Path(__file__).parent/'a4_runtime'))
from docx import Document
from docx.shared import Pt
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'A线工作区';P=W/'联系/刘癸庚'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(rel):return (P/rel).read_text(encoding='utf-8')
def write(rel,s):
 p=P/rel;assert not p.exists(),p;p.write_text(s,encoding='utf-8')
base=W/'材料/对外PDF/周子靖_中文学术简历_Master_v1.2.docx'
cvstem='周子靖_中文学术简历_刘癸庚版_v2_INTERNAL'
cvold=cvstem.replace('_v2_','_v1_')
plan={'baseline':{str(x.relative_to(ROOT)):sha(x) for x in [base,base.with_suffix('.pdf'),W/'材料/周子靖_中文学术简历_v0.5_INTERNAL.md']},'replacements':{},'archive':[]}
def pair(old,new):
 plan['replacements'][old]=new;plan['archive'].append(old)
for ext in ['.docx','.pdf','.md','.png']:pair('02_CV/'+cvold+ext,'02_CV/'+cvstem+ext)
changes={
 '计算物理 · 科学机器学习 · 物理驱动的逆向设计':'计算物理 · 电磁与光子学模拟 · 物理驱动的逆向设计',
 '使用并扩展 Python-CST 参数化电磁仿真与遗传算法优化流程':'使用并扩展 Python-CST 参数化电磁仿真与遗传算法结构优化流程',
 '电磁仿真、参数化建模与批量求解。':'频域电磁仿真、参数化建模与批量求解。'}
doc=Document(base);counts={k:0 for k in changes}
for p in doc.paragraphs:
 for r in p.runs:
  for old,new in changes.items():
   if old in r.text:r.text=r.text.replace(old,new);counts[old]+=1
assert all(v==1 for v in counts.values()),counts
for sec in doc.sections:
 p=sec.footer.paragraphs[0];p.text='刘癸庚定制 v2 · INTERNAL · 人工审查稿，不外发'
 for r in p.runs:r.font.size=Pt(8)
assert not (P/'02_CV'/f'{cvstem}.docx').exists()
doc.save(P/'02_CV'/f'{cvstem}.docx')
md=(W/'材料/周子靖_中文学术简历_v0.5_INTERNAL.md').read_text(encoding='utf-8')
for old,new in changes.items():md=md.replace(old,new)
write('02_CV/'+cvstem+'.md',md.rstrip()+'\n\n---\n刘癸庚定制 v2｜INTERNAL｜人工审查稿，不外发。\n')
updates={}
updates['02_CV/定制说明_v1.md']='''# CV 定制说明 v2

2026-09-26｜INTERNAL｜最新事实与版式母版：已冻结中文Master v1.2。

本次从Master v1.2 DOCX复制，完整继承一页双科研项目、80.20/100（成绩单自算）、21/46（2025.09推免口径）、晶格波合作研究及“2025年论文发表”标签、论文区去重复、Python技能表述和荣誉次序。只进行三处PI轻量定制：研究兴趣改为“计算物理 · 电磁与光子学模拟 · 物理驱动的逆向设计”；GA明确为“结构优化流程”；CST明确为“频域电磁仿真”。公共Master及v0.5编辑源不改。

均分不是GPA；推免排名不是毕业总排名。两处括号按最新要求保留；未来是否删除需另立公共v1.3并核适用口径，本轮不先行删。晶格波是合作数值数据分析，不写完整求解器或独立模型开发，不由论文发表年倒推参与起止时间。论文贡献沿用Master，不重复添加回晶格波论文条目。

依赖同步：首封邮件v2增加一句MATLAB合作数据处理经历；claim映射增加成绩口径和晶格波项目条目；25题Defense更新成绩与晶格波边界；发送清单、Readiness、附件路径和Tracker同步。毕设Project Sheet v1经核对与新母版一致，继续作为当前备用材料，不因CV版本升级而无理由重做。

CV文件为v2 INTERNAL，正文可审但未发送；审查后另存无内部页脚的READY附件。中文优先，旧英文CV不自动视为已同步。被替代的刘版v1在新版PDF验收后移入同目录“历史版本”，留路径/哈希及修复链接。
'''
sentence='此外，我在二维尘埃等离子体晶格波合作研究中使用MATLAB处理模拟数据、分析偏振特征并绘制粒子运动轨迹。'
for rel in ['01_Email/第一封套磁邮件_刘癸庚_v1_INTERNAL.md','01_Email/邮件正文_v1.txt']:
 s=read(rel).replace('第一封套磁邮件 v1','第一封套磁邮件 v2')
 anchor='编码和调试中使用了AI辅助。'
 assert anchor in s;s=s.replace(anchor,anchor+sentence)
 updates[rel]=s
updates['01_Email/非群发审查_v1.md']=read('01_Email/非群发审查_v1.md').replace('# 非群发审查','# 非群发审查 v2',1)+'\n本次随Master v1.2同步：在科研段加入一句晶格波MATLAB数据处理经历，与CV新单列的合作项目一致；未将团队模型/理论认领为本人。刘组专属的两条研究连接保持不变，未在短邮件重复均分/排名。\n'
updates['05_Send_Readiness/Readiness_Report_v1.md']=read('05_Send_Readiness/Readiness_Report_v1.md').replace('Report v1','Report v2').replace('第一版人工审查包已完成','v2人工审查包已按最新冻结Master v1.2同步').replace('本轮依明确要求使用冻结Master v1.1，未擅自冻结v1.2候选。','本轮使用已冻结Master v1.2；均分与排名括号保留，晶格波单列合作研究，2025只表示论文发表年。均分算法和推免口径已有本地证据，不要求本人重复回忆数字。').replace('25题具体清单已链接Research Defense','另需能解释80.20是成绩单百分制课程的算术均分、21/46是2025.09推免口径，以及晶格波数据/图件的个人角色；25题具体清单已链接Research Defense').replace('官网仍公开写2027秋季','沿用2026-09-26上轮官方快照（本次材料同步未重查网页），官网公开写2027秋季')
updates['05_Send_Readiness/Send_Readiness_Checklist_v1.md']=read('05_Send_Readiness/Send_Readiness_Checklist_v1.md').replace('# Send Readiness Checklist','# Send Readiness Checklist v2',1).replace('本轮核读学校主页','上轮已核读学校主页').replace('从冻结Master v1.1复制','从最新冻结Master v1.2复制').replace('邮件约391个中文字（不含签名）','邮件新增一句晶格波合作数据处理经历，保持约350–550个中文字（不含签名）').replace('两篇论文书目/有限贡献延续事实记录；','CV保留均分/推免排名口径及独立晶格波合作条目；2025为论文发表年。两篇论文书目/有限贡献延续事实记录；').replace('- [ ] 完成最低Defense清单','- [ ] 能解释均分自算方式、推免排名的时点与口径，以及晶格波项目不代表独立开发团队求解器。\n- [ ] 完成最低Defense清单')
updates['05_Send_Readiness/附件策略与投递节奏_v1.md']=read('05_Send_Readiness/附件策略与投递节奏_v1.md').replace('# 附件策略与串行联系','# 附件策略与串行联系 v2',1).replace('中文CV与中文首封相配','中文CV v2从最新冻结Master v1.2派生，含两项科研经历；成绩及排名限定括号保留。中文CV与中文首封相配')
s=read('04_Background_Notes/对外Claim到Defense映射_v1.md').replace('# 对外 Claim → 证据 → Defense','# 对外 Claim → 证据 → Defense v2',1)
line='| 指导教师李均；CV、项目页'
addition='''| 80.20/100（成绩单自算）及21/46（2025.09推免口径）；CV | 本地成绩单转录复算7298.6/91、排名原图，已冻结Master v1.2 | 算术均分非GPA，2025.09推免口径非毕业总排名；两处括号保留；Defense 8 |
| 晶格波合作数值数据分析：MATLAB、偏振特征与轨迹图；CV科研区、邮件 | 本人已确认分工＋本地论文/代码/输出，见晶格波贡献底稿 | 只认数据处理与部分图件，不认完整理论/求解器；2025是论文发表年，非项目起止；Defense 23 |
'''
s=s.replace(line,addition+line).replace('本轮未增加技能、成果或个人项目起止日期','本轮继承Master v1.2的既有晶格波合作研究呈现与成绩，不增加未经证实的技能、成果或个人项目起止日期')
updates['04_Background_Notes/对外Claim到Defense映射_v1.md']=s
s=read('06_Response_Prep/最低Research_Defense_Checklist_v1.md').replace('2026-09-26｜INTERNAL｜25题','2026-09-26｜v2 INTERNAL｜25题')
s=s.replace('用一张图解释电阻膜、PET和金属背板各起什么作用，基本损耗/耦合图像是什么？','用一张图解释电阻膜、PET和金属背板各起什么作用，基本损耗/耦合图像是什么；有背板是否能免除反射通道检查？')
old=next(x for x in s.splitlines() if x.startswith('| 8 |'))
s=s.replace(old,'| 8 | CV的80.20/100和21/46各怎样得来？为何前者不是GPA、后者不是毕业总排名？ | NEEDS REVIEW | E及CV增密事实记录；7298.6/91算术均分、2025.09推免名单；括号保留，不混入学分加权或官方GPA |')
old=next(x for x in s.splitlines() if x.startswith('| 23 |'))
s=s.replace(old,'| 23 | 晶格波模拟数据的MATLAB输入、偏振分析和轨迹输出中哪些由你处理，哪些是团队模型？2025表示什么？吸波论文你贡献了哪些图件/文字？ | HIGH-RISK | T，晶格波及材料项目入口；2025为论文发表年而非参与起止。第四/第六作者不等于主导；个人具体模块/图号仍需圈定 |')
updates['06_Response_Prep/最低Research_Defense_Checklist_v1.md']=s
for old in updates:
 new=old.replace('_v1','_v2');pair(old,new)
# Relink only superseded material; Project Sheet v1 and source snapshots remain current.
for old,s in updates.items():
 for a,b in plan['replacements'].items():s=s.replace(Path(a).name,Path(b).name)
 write(plan['replacements'][old],s)
write('05_Send_Readiness/版本联动检查_v2.md','''# v2版本联动检查

本次触发：用户明确要求刘癸庚投递包使用最新冻结Master v1.2。

| 材料 | 处理与理由 |
|---|---|
| 中文CV | v2，完整继承最新母版：成绩口径、晶格波合作科研条目、Python表述、论文去重复及荣誉排序；保留三处PI轻量定制 |
| 首封邮件 | v2，补一句MATLAB晶格波数值数据处理，毕设仍为主体；不在首封重复成绩或加长为SOP |
| claim映射 | v2，补成绩来源与口径、晶格波项目范围及发表年边界 |
| Defense | v2，仍25题；合并背板问题，加入成绩口径题并加强晶格波个人贡献/年份问题 |
| 发送清单、Readiness、附件策略 | v2，使用最新母版及附件路径，删除“v1.2尚未冻结”的过时判断 |
| Thesis Project Sheet | v1继续有效。新母版的毕设三条贡献和事实没有改变，不加入成绩或晶格波内容，也不为了整包编号相同而重生成 |
| 官网复核、组内渠道、回复动作卡、成绩单/论文附件 | 继续沿用独立用途文件；本次未重新调研，不冒充新核验日期或新名额确认 |
| Tracker、README、工作台 | 更新当前入口与版本，联系状态仍READYING / NOT SENT；旧决定作为历史记录保留 |

原公共Master v1.2和v0.5 INTERNAL编辑源保持原样。被替代文件在PDF验收后移入各自同级“历史版本”，旧稿内容保留，必要时只修相对链接；归档清单记录移动前后哈希。科研源与Research Defense快照不变，学习任务未启动。
''')
(W/'核验/刘癸庚v2_更新计划.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('CV v2 and dependent drafts prepared. Body Chinese count:',len(re.findall(r'[\u4e00-\u9fff]',updates['01_Email/邮件正文_v1.txt'].split('周子靖 |')[0])))
