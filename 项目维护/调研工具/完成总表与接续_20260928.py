"""本轮一次性整理记录。不得重跑覆盖后续人工维护的总表或档案。"""
from pathlib import Path
import json
from urllib.parse import quote

root = Path(__file__).resolve().parents[2]
base = root / 'A线_西湖博士/导师资料'
data_path = root / '项目维护/调研工具/本轮档案结构记录_20260928.json'
data = json.loads(data_path.read_text(encoding='utf-8'))
liu = next(d for d in data if d['name'] == '刘癸庚')
changes = {
 'students': 'S01列6博士、5博后及3访问学者。S02–S07分别列赵博（山西本科2023及RA）、魏帅阳（湖南本科/华南师大硕士2024）、张心怡（浙江师大本科2024）、程敏奇（南昌本科/南科大硕士2025）、李梓晨（哈工大本科2026）、岳明阳（武汉本科/阿姆斯特丹硕士2026）',
 'intake': '6位当前博士的前置学位年份可见，但博士入学日期不完整，不能把毕业年当入组年；年度实际招生仍UNKNOWN',
 'pre': 'S06列李梓晨本科2026及2025年Chemical Physics Letters第一顺位署名，支持本科期间有一作的个体样本，申请/接收时间及独立ownership未核。S04张心怡明确本科电子设计省赛一等奖、智能车省赛三等奖及省/校研究项目，未列论文不等于无论文。S02赵博有本科后RA及2024/2025一作列表，入组时间未知；硕士样本另列，不能混推本科直博普遍标准',
 'bar_reason': '用户转述博后意见提示较高竞争；新增S02–S07确有本科期间一作、竞赛/项目及本科后RA等不同准备路径，但只有小样本且申请时间、ownership和完整录取结果缺失，仍Low confidence，不认定必须一作或已核剩余名额。',
 'refs': 'O01/P01/S01–S07/内部分析',
}
dp=base/'刘癸庚/档案/PI档案_20260928.md'
s=dp.read_text(encoding='utf-8')
for key,value in changes.items():
 s=s.replace(liu[key],value);liu[key]=value
dp.write_text(s,encoding='utf-8')
data_path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
idx=base/'刘癸庚/来源索引.md'
s=idx.read_text(encoding='utf-8'); rows=[]
for p in sorted((base/'刘癸庚/公开证据/2026-09-28').glob('S*.json')):
 m=json.loads(p.read_text(encoding='utf-8')); key=p.stem
 rows.append(f'| {key} | 成员S | [原网址]({m["source_url"]}) | 200；已核角色/前置学位/个人列示成果；不是完整录取档案 | [正文](公开证据/2026-09-28/{key}.txt) / [原始响应](公开证据/2026-09-28/{key}.html) / [元数据/哈希](公开证据/2026-09-28/{key}.json) |')
s=s.replace('\nHTTP 200', '\n'+'\n'.join(rows)+'\n\nHTTP 200').replace('|\n\n| S01','|\n| S01')
idx.write_text(s,encoding='utf-8')

def pi(d): return f'[{d["name"]}]({quote(d["name"])}/README.md)'
def table(head,rows):
 return '| '+' | '.join(head)+' |\n|'+ '|'.join(['---']*len(head))+'|\n'+''.join('| '+' | '.join(str(c).replace('|',' / ').replace('\n',' ') for c in row)+' |\n' for row in rows)

out='''# 西湖大学 PI 申请池总表

2026-09-28｜INTERNAL｜唯一横向导师池；不是已通过资格审核或最终投递顺序

30位已建独立档案：P1 8、P2 9、P3 6、Reach 4、Hold 3、Drop 0。P1+P2共17位未联系候选，另刘癸庚已发。**值得联系不等于实际bar已证实可达**；除吴泰霖有明确条件风险，其余Admission Feasibility保留UNKNOWN或谨慎/UNKNOWN。

[执行报告](全池核验/执行报告_20260928.md) · [筛选与核验口径](全池核验/筛选与核验口径.md) · [唯一联系记录](../联系记录.md) · [历史原始导师总表](原始导师总表.md)

以下分表共同构成同一总表，以PI为键。事实细节和证据ID见逐人档案/来源索引；证据日期统一为2026-09-28，不冒充页面发布日期。联系列仅引用唯一记录的当轮快照，后续真实事件只更新联系记录。

## 1. 分层、五维评价与竞争门槛

Research / Training Fit、Admission Feasibility、Communication / Onboarding Fit、Transferable Skill Value、Evidence Confidence分别判断，不合成总分。High潜在训练价值是条件分析，不是培养保证。Competitive Bar与证据置信度单列：28位Uncertain/Low，2位Probably High/Low，尚无可可靠标为Plausibly Moderate的组。

'''
out+=table(['PI','层级','Research / Training Fit','Admission Feasibility','Communication / Onboarding Fit','Transferable Skill Value','Evidence Confidence','Competitive Bar / Bar Confidence','联系状态（引用）'],[
 [pi(d),d['tier'],d['fit'],d['admit'],d['language'],'High（潜在；具体见第3表）',d['confidence'],d['bar']+' / '+d['bar_confidence'],'[SENT / AWAITING RESPONSE；2026-09-28](../联系记录.md#a4-outreach-tracker)' if d['name']=='刘癸庚' else '[本轮未联系；档案INTERNAL](../联系记录.md)'] for d in data])
out+='\n## 2. 身份、入组接口与公开招生信号\n\n学院/学科来自官网目录，不保证2027系统可选；组龄主要以入职近似。Public Eligibility / Recruiting Signal不能单独降低实际bar。相关学历背景被欢迎，只证明公开路径；学校批次、第二学位学籍及学科英语门槛另核。\n\n'
out+=table(['PI','学院 / 可能学科','组龄','核心研究','Entry Bridge','Trainability / 重训','Public Eligibility / Recruiting Signal（含2027）','成果 / 方法门槛：required或preferred'],[
 [pi(d),d['school']+'；'+d['subject'],d['year'],d['core'],d['bridge'],d['train']+'；需学：'+d['retrain'],d['signal'],d['gate']] for d in data])
out+='\n## 3. 学生、实际研究方式和训练资产\n\n学生学历多样性不等于bar低；当前论文不倒推申请时成果。所有个人理论/计算/实验工时比例未核，保留定性描述。博士计数是页面列示，不保证完整名册；RA/访问/联合培养不得冒充普通通道录取。\n\n'
out+=table(['PI','博士 / 学生背景证据','近2–4年入组信号','入组前成果 / ownership','理论 / 计算 / 实验','Training Asset'],[
 [pi(d),d['students'],d['intake'],d['pre'],d['mode'],d['training']] for d in data])
out+='\n## 4. 实际bar依据、决策风险与下一证据\n\n所有行证据日期：2026-09-28。P1是优先取得反馈的研究候选，不能当“容易录取”；Reach也不是已经证明每组竞争都高。下阶段可设计随反馈调整的批次，本轮不规定发送顺序。\n\n'
out+=table(['PI','Bar Confidence的依据','主要风险','未决问题','证据入口 / 日期'],[
 [pi(d),d['bar_reason'],d['risk'],d['question'],f'[来源]({quote(d["name"])}/来源索引.md)；{d["refs"]}；2026-09-28'] for d in data])
(base/'导师池总表.md').write_text(out,encoding='utf-8')

p=root/'A线_西湖博士/联系材料/刘癸庚/当前材料/说明.md';s=p.read_text(encoding='utf-8')
s=s.replace('# 刘癸庚首封联系：发送入口','# 刘癸庚首封联系：材料留档入口')
s=s.replace('2026-09-28｜最终审稿已完成，材料 READY；实际联系 NOT SENT。','2026-09-28｜本人确认首封已发送；真实状态以[唯一联系记录](../../../联系记录.md#a4-outreach-tracker)为准。以下保留发送前核定的邮件v9、CV v4及四附件清单，实发正文/收件地址/附件仍待发送原件核对，不能把准备清单当回执。已发后不重复发送，原文件不覆盖。')
s=s.replace('直接复制[邮件纯正文 v9]','发送前准备的[邮件纯正文 v9]').replace('## 本次只附四个 PDF','## 发送前核定的四个 PDF（实际随信内容待核）')
start=s.index('发送时只需核对实际发件账户')
s=s[:start]+'后续仅按真实回复更新[唯一联系记录](../../../联系记录.md#a4-outreach-tracker)。具体课题、学科、剩余名额由PI答复；正式申请批次和学籍手续并行核实。该目录现用于追溯准备版本，不作为再次发送指令。\n'
p.write_text(s,encoding='utf-8')

p=root/'申请路线总览.md';s=p.read_text(encoding='utf-8');s=s.replace('- [A线 PI 历史总表]', '- [A线唯一导师池总表](A线_西湖博士/导师资料/导师池总表.md)（30位证据型候选；分层不是最终发送顺序）\n- [A线 PI 历史总表]',1);p.write_text(s,encoding='utf-8')

p=root/'AGENTS.md';s=p.read_text(encoding='utf-8');needle='## 文件与行动';s=s.replace(needle,'- 2026-09-28扩池接续：本人已确认刘癸庚首封于2026-09-28实际发送，无精确时刻；唯一联系记录为准，原先等待本人发送的文字仅属历史。当前30位PI池入口为`A线_西湖博士/导师资料/导师池总表.md`；不再执行旧八人上限或固定四人顺序。公开招生信号与Estimated Competitive Bar / Bar Confidence分开；友好招聘措辞和组龄不得上调可达性，组内转述独立标记anecdote。本轮仅独立PR审查，不代发、不自动合并。\n\n'+needle);p.write_text(s,encoding='utf-8')

print('已生成30位唯一总表并更新接续入口；未运行旧生成器。')
