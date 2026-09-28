from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
W=ROOT/'A线工作区';PACK=W/'联系/刘癸庚'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
def save(p,s):
 records.append({'path':str(p.relative_to(ROOT)),'before_sha256':sha(p)})
 p.write_text(s,encoding='utf-8')
 records[-1]['after_sha256']=sha(p)
p=W/'招生核验与PI行动表.md';s=p.read_text(encoding='utf-8')
s=s.replace('版本 v1.1 | 更新 2026-09-26','版本 v1.2 | 更新 2026-09-26（A4刘癸庚投递包）',1)
start=s.index('本轮后续澄清：');end=s.index('\n\n最新学籍补充',start)
s=s[:start]+'''当前A4行动：用户指定刘癸庚为第一顺位，暂定串行顺序为刘癸庚→刘仕→朱一舟→鲍芳琳；替代旧“并行联系”执行建议，不是永久研究兴趣排名。刘癸庚投递包v1已完成，INTERNAL人工审查中，未发送。当前新联系主邮箱zhouzijing54@gmail.com，QQ备用；系统是否已有提交仍待单独确认。'''+s[end:]
start=s.index('当前发件准备：');end=s.index('\n\n本人2026-09-26',start)
s=s[:start]+'''当前发件准备：[刘癸庚投递包v1](联系/刘癸庚/README.md)已建立。定制CV按本轮明确要求复制冻结Master v1.1，Master v1.2仍为候选，不擅自冻结或取代母版。新CV、邮件、项目页统一Gmail；中文CV/项目页均为INTERNAL审查稿，终读后另存READY发送版并清除内部页脚。其他PI旧草稿保留，本轮不开始准备刘仕。'''+s[end:]
s=s.replace('| 刘癸庚 | liuguigeng@westlake.edu.cn，P01 | READY v1.0 | 未联系，本人确认 | 主题按组要求：博士生申请-周子靖 |','| 刘癸庚 | liuguigeng@westlake.edu.cn，P01已于本轮刷新 | [A4 v1 INTERNAL审查包](联系/刘癸庚/README.md) | READYING / NOT SENT；未联系，本人确认 | 本人审查，关闭最低readiness项后决定发送；主题：博士生申请-周子靖 |')
s=s.replace('这是有限时间下的行动队列，不是导师质量、录取概率或最终去向排名。','下表保留八人分层与研究连接，当前实际执行顺序以本页A4 Tracker及置顶决定为准。这是有限时间下的行动队列，不是导师质量、录取概率或最终去向排名。',1)
s=s.replace('先问在组同学，再定制首封','已定制首封；同学核实可选，不擅自联系')
old='跟进规则：按实际发送日起算，一般7–10天无回复可考虑一次简短跟进；以PI页说明优先。明确拒绝即停止追问。刘癸庚页提示超过一周无回复可另寻导师，因此不应等待其回复才联系其他人。更新材料后再次接触需有实质新信息。'
new='跟进规则（A4最新）：串行联系，不同时群发西湖PI。发出后5–7天无回复可一次跟进；结合刘组官网默认第7天，再等3–5天仍无有效回复可考虑下一位。强正面信号暂停其他西湖PI主动联系；一般“欢迎申请/按系统申请”不形成排他关系。明确拒绝停止追问。当前未发送，不填任何跟进日历日期。旧并行建议由本次策略覆盖。'
assert old in s;s=s.replace(old,new)
tracker='''## A4 Outreach Tracker

这是A线Outreach唯一可编辑联系状态表；[Outreach目录入口](联系/A-line_Outreach_Tracker.md)只链接此处。准备文件状态不等同联系事件。名额/邮箱等来源见[2026-09-26有限官网刷新](联系/刘癸庚/04_Background_Notes/官网快速复核_20260926.md)。

| PI | priority | current status | email file | CV file | Project Sheet | planned send date | actual send date | follow-up date | reply level | next action | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 刘癸庚（Gui-Geng Liu） | 1（当前串行首位，非永久排名） | READYING / NOT SENT | [邮件v1](联系/刘癸庚/01_Email/第一封套磁邮件_刘癸庚_v1_INTERNAL.md) | [中文CV v1](联系/刘癸庚/02_CV/周子靖_中文学术简历_刘癸庚版_v1_INTERNAL.pdf) | [项目页v1](联系/刘癸庚/03_Project_Sheet/output/周子靖_毕设项目页_刘癸庚版_v1_INTERNAL.pdf) | 未定，待本人审查 | — | —，由实际发送日起算 | 无（尚未发送） | 人工审查；Gmail测试；最低Defense复核；另存READY附件后由本人决定发出 | 官网仍写2027尚有名额，具体余量/题目/招生学科待PI；下一系统批次待官方；未代发 |

当前后续顺序：刘仕→朱一舟→鲍芳琳；尚未为这些PI创建本轮正式投递包。发送、回复、面试、系统提交分别记录；不将草稿/附件生成写入下方实际事件日志。

'''
assert '## A4 Outreach Tracker' not in s
s=s.replace('### 实际事件日志',tracker+'### 实际事件日志')
save(p,s)
p=ROOT/'A线_工作台.md';s=p.read_text(encoding='utf-8')
s=s.replace('状态：原资产审计完成，已形成首轮联系包，尚未发送','状态：A4刘癸庚投递包v1完成，待人工审查，尚未发送',1)
start=s.index('**最新任务：');end=s.index('\n\n原有工作',start)
s=s[:start]+'''**最新任务：A4刘癸庚投递包v1已完成，到人工审查处暂停。** 入口：[投递包](A线工作区/联系/刘癸庚/README.md)、[Readiness Report](A线工作区/联系/刘癸庚/05_Send_Readiness/Readiness_Report_v1.md)、[唯一Outreach Tracker](A线工作区/招生核验与PI行动表.md#a4-outreach-tracker)。本轮只推进刘癸庚；用户最新暂定串行顺序为刘癸庚→刘仕→朱一舟→鲍芳琳，覆盖旧并行执行建议，不代表永久兴趣排序。未发送、未联系同学、未登录系统，不自动开始下一位或完整proposal。

Research Defense工作区已建好，维持原快照与训练边界：[地图](07_Research_Defense/00_Defense_Index.md)。本轮仅把对外claim映射至现有材料并列25题最低复核清单，没有教学、试讲测试、运行优化器或CST。'''+s[end:]
needle='## 本轮完成\n\n'
add='''- A4刘癸庚：重读冻结中文Master v1.1、Applicant Profile/Contribution Record对应事实源、毕设及Research Defense；有限刷新官方主页、组主页/研究/招聘/发表列表及2027第一批通知。官网仍写2027尚有名额及有限元/AI软件急需；具体余量、博士题目和学科仍问PI，下一系统窗口未确认。
- 独立建立六分区投递目录：中文CV v1（Word/Markdown/PDF）、首封邮件（约391中文字）、真实结构/归档曲线/矢量流程的一页项目页、官网更新、claim映射、25题Defense、Readiness、附件/串行策略。CV与项目页各一页且已看整页；公共Master、原科研源和原20件不动。
- 依据本轮“以冻结Master为母版”要求，从v1.1复制，仅三处轻量调整；v1.2候选仍待原有终读，不擅自升级正式版。中文附件优先；首封推荐CV+成绩单为核心，按刘组官网补两篇合作论文，项目页暂作备用。不把低署名成果改成核心贡献。
- Tracker正式建立在行动表中，Outreach目录只设入口；唯一联系状态READYING / NOT SENT，实际发送/跟进日期未填。初稿审查完成后才另存READY附件，保留INTERNAL审查版。无自动监控。
'''
assert needle in s;s=s.replace(needle,needle+add,1)
start=s.index('以下为内部工作目标');end=s.index('\n推荐人候选：',start)
s=s[:start]+'''当前暂停在用户人工审查，不自动继续下表。时间由实际行动确定，旧内部目标日不当作招生截止。

| 顺序 | 下一动作 | 完成标准 |
|---|---|---|
| 1 | 人工终读刘癸庚v1邮件/CV/项目页 | 确认动机与贡献范围；已有事实无需重述 |
| 2 | 最低Defense及Gmail测试 | 能解释一个真实代码改动、两篇论文有限贡献、同模反射边界；收发可用 |
| 3 | 形成READY附件并由本人决定发送 | 审查后另存，清除内部页脚；当天重核招聘；真实发送才记SENT和D0 |
| 4 | 按实际回复串行推进 | D0+7天一次跟进，再等3–5天评估；强正面暂停其他西湖PI |
| 5 | 具体学科/可报批次与第二学位手续 | PI及招生办/当批官方确认；不由2026规则推算；未代发招生办咨询 |
| 6 | 有真实研究方向后再做PS/Proposal与正式面试包 | 推荐人意愿、英文PS与当批模板要求分别落实；不在本轮生成长proposal |
'''+s[end:]
needle='| 日期 | 决定 | 原因/重开条件 |\n|---|---|---|\n'
decision='| 2026-09-26 A4 | 刘癸庚首位，按冻结v1.1轻量定制；完成审查包后暂停，串行不群发 | 用户本轮明确指定；不替用户冻结v1.2，不重做PI池。官网仍需已发表文章，首封核心A策略加两篇有实际贡献合作论文；名额/课题/系统批次分开核 |\n'
assert needle in s;s=s.replace(needle,needle+decision,1)
needle='## 待补与接续重点\n\n'
add='''A4当前只需本人终读动机/附件、圈定真实代码和论文贡献例子、完成最低Defense复核及Gmail收发测试。具体2027剩余名额、博士课题/学科与后续批次由PI/官方答复；不将这些待答咨询写成已知事实。材料质量已经达到可审查v1，不继续无限润色、不准备刘仕。当前CV和项目页仍带INTERNAL页脚，不直接作为发送终稿。

'''
s=s.replace(needle,needle+add,1)
save(p,s)
(PACK/'05_Send_Readiness/工作台与行动表更新哈希_v1.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print('Updated workbench and authoritative tracker; no send events entered.')
