"""Prepare local Liu outreach v1. No mail, upload, simulation or source mutation."""
from pathlib import Path
import sys, shutil, hashlib, json, re
sys.path.insert(0,str(Path(__file__).parent/'a4_runtime'))
from docx import Document
from docx.shared import Pt
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
PACK=ROOT/'A线工作区/联系/刘癸庚'
for d in ['01_Email','02_CV','03_Project_Sheet/source','03_Project_Sheet/output','04_Background_Notes','05_Send_Readiness/附件备选','06_Response_Prep']:
 (PACK/d).mkdir(parents=True,exist_ok=True)
def write(rel,s):
 p=PACK/rel
 p.write_text(s.strip()+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=[]
def copy(src,rel):
 src=Path(src);dst=PACK/rel;shutil.copy2(src,dst)
 manifest.append({'source':str(src),'copy':str(dst.relative_to(PACK)),'source_sha256':sha(src),'copy_sha256':sha(dst)})
base=ROOT/'A线工作区/材料/对外PDF/周子靖_中文学术简历_Master_v1.1.docx'
basepdf=base.with_suffix('.pdf')
baseline={'docx':{'path':str(base),'sha256':sha(base)},'pdf':{'path':str(basepdf),'sha256':sha(basepdf)}}
stem='周子靖_中文学术简历_刘癸庚版_v1_INTERNAL'
copy(base,'02_CV/'+stem+'.docx')
doc=Document(PACK/'02_CV'/f'{stem}.docx')
changes={
 '计算物理 · 科学机器学习 · 物理驱动的逆向设计':'计算物理 · 电磁与光子学模拟 · 物理驱动的逆向设计',
 '使用并扩展 Python-CST 参数化电磁仿真与遗传算法优化流程':'使用并扩展 Python-CST 参数化电磁仿真与遗传算法结构优化流程',
 '电磁仿真、参数化建模与批量求解。':'频域电磁仿真、参数化建模与批量求解。',
}
found={k:0 for k in changes}
for p in doc.paragraphs:
 for run in p.runs:
  for old,new in changes.items():
   if old in run.text:found[old]+=1;run.text=run.text.replace(old,new)
assert all(found.values()),found
for sec in doc.sections:
 p=sec.footer.paragraphs[0];p.text='刘癸庚定制 v1 · INTERNAL · 人工审查稿，不外发'
 for r in p.runs:r.font.size=Pt(8)
doc.save(PACK/'02_CV'/f'{stem}.docx')
md=(ROOT/'A线工作区/材料/历史版本/周子靖_中文学术简历_v0.4_INTERNAL.md').read_text(encoding='utf-8')
for old,new in changes.items():md=md.replace(old,new)
write('02_CV/'+stem+'.md',md+'\n\n---\n刘癸庚定制 v1｜INTERNAL｜人工审查稿，不外发。')
write('02_CV/定制说明_v1.md','''# CV 定制说明

2026-09-26｜INTERNAL

事实与版式母版为冻结的 Master v1.1；v1.2 CANDIDATE 未经本人冻结，本轮未据此替换。只复制母版，未修改公共文件。晶格波 MATLAB 贡献沿用 v1.1 的论文条目位置，不重组科研经历；不新增均分、排名或其他候选版内容。

三处轻量调整：研究兴趣改为“计算物理 · 电磁与光子学模拟 · 物理驱动的逆向设计”；GA 明确为“结构优化流程”；CST 明确为“频域电磁仿真”。其余教育、第二学位、导师、论文贡献、Git、荣誉等事实不变。

“电磁与光子学模拟”为拟探索的兴趣方向；不表示已做拓扑光子学。熟练 FEM、独立软件开发、机器学习研究和拓扑物理成果均未加入。

文件名与页脚保持 INTERNAL。人工审查通过后另存清除内部页脚的 READY 发送版；不要仅重命名 PDF 冒充审查完成。英文旧版尚未按中文基线同步，首封推荐中文 PDF；官网博士段没有限定简历语言，学校英文 PS 要求不等于套磁 CV 要求。
''')
email='''刘老师您好：

我叫周子靖，2026年6月毕业于哈尔滨工业大学应用物理学专业，希望申请2027年入学博士。看到复杂波与场实验室的招生信息，想请您判断我的背景是否适合组内课题。

我的本科毕设研究电阻膜微波吸收结构。在导师和学长提供的初始结构与参考代码基础上，我使用并扩展Python-CST参数化仿真流程，调整遗传算法搜索、扩展几何与片阻变量，加入几何约束筛选，并处理反射响应、比较薄实体膜与Ohmic Sheet模型；编码和调试中使用了AI辅助。

您组利用损耗配置调控光子晶体手性边缘态局域化的研究，让我希望从“优化电磁性能”进一步学习拓扑与非厄米机制如何影响波传播，以及如何据此设计并验证器件。我也注意到当前招聘提及有限元仿真和AI辅助软件开发，希望将已有仿真自动化经验用于这些物理问题；AI对我主要是辅助工具。

请问您2027年目前是否仍有适合上述背景的博士名额，哪些具体课题更需要物理建模与计算研究，以及对应的招生学科是什么？附上中文简历、本科成绩单及两篇合作论文，个人贡献见简历；另备有毕设一页摘要，可进一步提供。感谢您的时间！

周子靖 | Zijing Zhou
哈尔滨工业大学 应用物理学（2026届）
zhouzijing54@gmail.com'''
write('01_Email/第一封套磁邮件_刘癸庚_v1_INTERNAL.md','''# 第一封套磁邮件 v1

2026-09-26｜INTERNAL／待人工审查｜未发送

收件人：liuguigeng@westlake.edu.cn  
发件邮箱：zhouzijing54@gmail.com  
发件显示名：周子靖 Zijing Zhou  
推荐主题：**博士生申请-周子靖**

以下为完整可复制正文。附件句按“简洁首封 + 官网要求的两篇论文”配置；不是已上传附件或已经发送的记录。

---

'''+email)
write('01_Email/邮件正文_v1.txt',email)
write('01_Email/非群发审查_v1.md','''# 非群发审查

结论：通过定制审查；仍需本人终读。对照本地旧《首轮联系包_v1.0》的刘仕、朱一舟、鲍芳琳段及旧刘癸庚长稿，没有仅替换姓名。

| 本版连接 | 可追溯来源 | 仅换导师姓名是否成立 |
|---|---|---|
| 损耗配置改变光子晶体手性边缘态局域化；由吸波结构性能优化转向拓扑与非厄米传播机制 | 实验室 research 页第2项；PRL 132, 113802 (2024) 在官方主页和发表列表均列出 | 不成立。刘仕旧稿围绕铁电/多尺度；朱一舟围绕 AutoMapper；鲍芳琳围绕光学信息反演 |
| 当前招聘明确提及有限元仿真与 AI 辅助软件开发，以 Python-CST 自动化作为进入具体物理问题的能力起点 | 本轮 job 页快照，急需方向段 | 不可随意移植，须有其他 PI 的独立招聘证据 |

身份与毕设段可以公共复用；这是事实一致性要求。真正定制集中在研究连接与当前需求，不堆论文题名，不声称本人已经精读或复现论文。第一封保留“希望进一步学习”，不把吸收损耗直接等同于非厄米拓扑能力。

相比旧长稿，删除“主要独立完成”“AI软件开发经历”的放大叙事、主动解释实验偏好和“已有名额可得”的暗示。未引用同学评价、未称有人推荐。没有把本轮联系顺序写成终身研究兴趣排序。
''')
snap=PACK/'04_Background_Notes/official_snapshots'
h=(snap/'faculty.html').read_text(encoding='utf-8'); segment=h.split('personObj:',1)[1]
parts=[]
for k in ['subject','lab','email','biographyStr','researchStr']:
 text=json.JSONDecoder().raw_decode(segment.split(k+':',1)[1].lstrip())[0]
 parts.append(k+'\n'+BeautifulSoup(text,'html.parser').get_text('\n',strip=True))
(snap/'faculty_extracted.txt').write_text('\n\n'.join(parts),encoding='utf-8')
write('04_Background_Notes/官网快速复核_20260926.md','''# 刘癸庚线：发送准备前有限更新

2026-09-26｜INTERNAL｜只核当前对象，不重做八位PI档案。来源网页均由本轮 HTTP 取得并存原始 HTML、正文与 SHA-256；官方主页正文从网页内嵌 JSON 字符串提取，不只看空壳标题。

| 来源 | 本轮核验与用途 |
|---|---|
| [学校教师主页](https://en.westlake.edu.cn/faculty/guigeng-liu.html) | 工学院；学科字段 Electronic Science and Technology, Physics；Laboratory of Complex Waves and Fields；邮箱 liuguigeng@westlake.edu.cn。双领域展示不代表每批都能任选招生学科 |
| [实验室主页](https://www.liuguigeng.com/) / [研究页](https://www.liuguigeng.com/research/) | 拓扑、非厄米、太赫兹、空间结构光、光子晶体与超材料；跨电路/微波/太赫兹/红外/可见光，强调机理、器件与应用 |
| [招聘页](https://www.liuguigeng.com/job/) | 仍公开写“2027年秋季入学博士生尚有名额……招满为止”，允许本科起点、gap申请。**这是网页当前自述，不是PI确认的即时剩余人数或个人接收承诺** |
| [2027第一批官方正文](https://www.westlake.edu.cn/admissions/graduate/brochure/general/202608/t20260813_68957.html) | 重新取得正文；2026-08-31 10:00截止。本科起点可申请；471只达到一般460分门槛，不到智能信息技术480；工学院英文PS及研究计划要求保留 |
| [普博招生列表](https://www.westlake.edu.cn/admissions/graduate/brochure/general/) | 当前列表仍见2027第一批，未见适用的后续批次；未登录系统，未查到不等于不存在。招聘名额与系统窗口分开问 |
| [发表列表](https://www.liuguigeng.com/publications/) | 已核2025–2026列表及题名；没有宣称本轮精读这些全文，也不能算申请人已读 |

## 关键词与目前缺人方向

有限元仿真（finite-element simulation）、AI辅助软件开发、太赫兹技术、无线通讯技术均仍在“急需”段；另列片上微纳加工、红外/可见光光路、低温量子理论与实验。此段面向实验室多类岗位，不等于每项都有独立2027博士题目。

topological / non-Hermitian photonics 和 complex waves 仍是官方研究内容；terahertz chips / 6G、空间结构光、光学AI计算/显示也仍列为方向。无线通信是应用线索，不能据此把申请人经历改成通信系统开发；光学AI计算与AI辅助写软件是不同概念。

## 2025–2026信息对套磁的影响

| 官网条目 | 对本轮的实际影响 |
|---|---|
| Photonic Axion Insulator，Science 387, 162 (2025) | 延续三维拓扑主线；不需要把申请人包装为已有轴子/拓扑经验 |
| Topological valley quasi-bound states in the continuum for radiatively accessible robust transport，Nature Communications（2026列表，DOI 10.1038/s41467-026-77201-z） | 说明辐射通道、开放系统和输运的连接仍活跃；仅核官网题名与链接，不写具体效率等未读结论 |
| Antichiral hinge states in a higher-order photonic nodal ring semimetal（2026列表，DOI 10.1038/s41467-026-77020-2） | 最新列表仍有高阶/反手性波态，不支持“已转向纯AI”的判断 |
| Local boundary modulation of photonic antichiral edge states，Photonics Research 14(8), 3368–3377 (2026) | 结构/边界调控如何改变传播，比罗列论文更接近申请人的建模入口 |
| Terahertz spin-selective dielectric metasurfaces from exceptional points，PhotoniX 7, 6 (2026) | 太赫兹、超表面和EP仍有研究联系；不能由微波仿真经历推定已掌握太赫兹实验 |

相比旧档案，没有发现足以推翻联系主线的变化。新增的精确2026条目只补充背景，不重写旧PI档案。邮件选用研究页清楚解释的“损耗配置—手性边缘态局域化”连接（2024 PRL），比暗示已读新论文更可辩护。材料中的本人成果数字与上述PI研究完全分开。

## 标题、附件与跟进原文

博士/科研助理段要求：“个人简历、成绩单、已发表文章（如有）等其他相关材料以PDF形式发送”；标题为“博士生/科研助理申请-本人姓名”。按博士岗位选择“博士生申请-周子靖”，不同时写两个岗位。语言未限定，采用已冻结中文母版派生稿。

博士段也写“一周后未收到回复无需再等待”，有条件可一周后重新发送。内部采用第7天一次礼貌跟进，再等3–5天评估下一位；这是一项沟通安排，不是校方规则。默认保留同一邮箱线程，不因官网建议可换邮箱就无证据跨邮箱重复投递。

招聘页“无需笔试”和英语可后补的概括不能覆盖学校/学院当批通知。正式申请仍按当批规则核验。

证据位置：[本轮网页快照](official_snapshots)。公开资料获取未传入任何个人附件、成绩单或私人组内反馈。
''')
write('04_Background_Notes/组内渠道与匹配判断_v1.md','''# 组内渠道与匹配判断

2026-09-26｜INTERNAL｜私人信息不外发。

本人本轮确认有同学在刘癸庚组；“所见即所得、比较push但真指导、工作制弹性、结果导向”是本人转述的单一组内样本。可辅助决策，不升级为独立核实的全组培养保证，也不出现在首封邮件或附件。

正式发出前值得由本人通过既有渠道做一次短核实：①2027当前剩余名额、PI是否仍看申请；②目前最缺人的具体博士课题；③有限元/AI软件需求是科研支撑还是博士主课题，现有CST-Python背景是否可进入。无需请求同学承诺录取，也无需等待完整导师评价问卷。无人回复不必阻止一封诚实咨询。此步骤可选，本轮未联系任何人。

默认正常、独立申请；若以后希望正式介绍，先由本人和同学明确同意，再修改邮件。当前不写其姓名、身份线索或“经推荐”。

匹配判断：电磁参数化建模、脚本自动化和受约束搜索有直接方法连续性；从低反射优化走向波传播机制是希望接受的训练，尚不是已掌握的理论能力。申请人此前优先计算材料/第一性原理/科学ML的偏好保持内部记录；本轮先联系刘癸庚不等于永久改变兴趣。是否值得继续，取决于具体问题中建模与计算能否构成主要科研贡献，以及指导、资源与实验合作方式。AI应服务物理问题。
''')
write('05_Send_Readiness/附件策略与投递节奏_v1.md','''# 附件策略与串行联系

2026-09-26｜INTERNAL

| 策略 | 优点 | 代价与条件 |
|---|---|---|
| A：中文CV + 官方本科成绩单 | 最短阅读路径，先判断背景和名额；本次推荐的核心组合 | 看不到毕设细节；而且官网另要求已发表文章（如有），两件本身不能声称完全符合官网 |
| B：CV + 成绩单 + 1页Project Sheet | 能较快看懂真实结构、计算流程与结果口径，适合主动评估计算能力 | 阅读负担更多；容易提前触发全端口/收敛及代码ownership追问；仍不能以项目页替代官网论文要求 |

**执行建议：以 A 为核心，另按官网补附 CV 所列两篇合作论文；Project Sheet 先备好，收到兴趣回复或本人决定增强技术展示时再附。** 邮件正文已按这一组合写好。两篇论文是遵循材料要求，不是把低署名论文当主成果；CV明确个人贡献，不加入基本未参与的第三篇或专利。若本人选择严格只发两件，须同时改邮件附件句，并知道这是对官网材料列表的精简。

中文CV与中文首封相配；当前英文旧稿未同步冻结中文母版，不临时生成英文替换。官方本科成绩单保留学校原始两页，不另造GPA或“美化”成绩。成绩单只用于本人向官方PI邮箱的直接投递，不上传外部处理网站。

## 拟附文件（均未发送）

1. 当前[CV审查PDF](../02_CV/周子靖_中文学术简历_刘癸庚版_v1_INTERNAL.pdf)：人工通过后另存READY版，清除内部页脚。
2. [周子靖_本科成绩单.pdf](附件备选/周子靖_本科成绩单.pdf)：原件逐字节复制；两页。
3. [合作论文_吸波材料_2025.pdf](附件备选/合作论文_吸波材料_2025.pdf)：9页，第四作者，数据/图件/稿件贡献。
4. [合作论文_晶格波_2025.pdf](附件备选/合作论文_晶格波_2025.pdf)：10页，第六作者，MATLAB处理/绘图贡献。

备用：[Project Sheet](../03_Project_Sheet/output/周子靖_毕设项目页_刘癸庚版_v1_INTERNAL.pdf)。本地复制与哈希见[manifest](../04_Background_Notes/本地复制与基线哈希_v1.json)。不附内部背景笔记、学信网截图、身份证号/准考证号证据、同学评价、完整工程或完整Research Proposal。

## 当前串行原则

西湖PI之间可能有日常交流，这是策略假设，不是已知具体沟通事件。第一批不同时群发多个PI。暂定刘癸庚 → 刘仕 → 朱一舟 → 鲍芳琳；是当前联系次序，不是永久排名。

以实际发送日D0为起点：5–7天无回复可跟进一次；结合刘组官网，默认D0+7天。同一线程简短跟进后，再等约3–5天仍无有效回复，可考虑下一位。当前没有D0，不预填任何日历日期，不设自动发送或提醒。

若要thesis/code、明确背景匹配、讨论具体题目、约线上/访问或提预留名额：暂停其他西湖PI主动联系，先澄清当前线。索要code先核课题组分享权限和文件内路径/私密信息，不默认发整个工程。

“欢迎申请/按系统申请”只是一般回应，不形成排他关系；合理间隔后可以继续下一位。明确不匹配/无名额则礼貌结束，不反复追问。正式名额及批次、第二学位手续由对应官方/PI书面回复落实。

当PI问实验时，可真实回答：“可以接受并愿意参与高质量的理论—仿真—实验闭环，希望主要贡献能够包含明确的物理建模和计算研究。”不在首封主动辩解偏好。
''')
copy(ROOT/'个人资料/成绩单.pdf','05_Send_Readiness/附件备选/周子靖_本科成绩单.pdf')
copy(ROOT/'个人资料/论文1.pdf','05_Send_Readiness/附件备选/合作论文_吸波材料_2025.pdf')
copy(ROOT/'个人资料/论文2.pdf','05_Send_Readiness/附件备选/合作论文_晶格波_2025.pdf')
copy(Path('E:/360MoveData/Users/zzj/OneDrive/桌面/毕业设计/结题/终稿/_ppt_assets_resistive_film/fig6_2_final_3d_model.png'),'03_Project_Sheet/source/structure_original.png')
copy(Path('F:/biyesheji/最终结果ohmic_sheet_12x12_multitemplate_topology_ga/best_s11_ohmic_sheet_12x12.txt'),'03_Project_Sheet/source/reflection_archived.tsv')
copy(Path('F:/biyesheji/最终结果ohmic_sheet_12x12_multitemplate_topology_ga/best_result_ohmic_sheet_12x12.txt'),'03_Project_Sheet/source/result_archived.txt')
write('03_Project_Sheet/source/figure-plan.md','''# Figure Plan — thesis one-pager

核心论点：从既有结构与参考代码出发，扩展参数化电磁仿真/优化流程；展示归档结果与可验证边界，不证明新算法或总吸收。

阅读顺序：研究问题 → 原结构与已保存曲线 → 工作流 → 个人贡献 → 结果/局限。

| 面板 | 内容类型 | 后端 | 保真要求 |
|---|---|---|---|
| 结构 | 原项目CST截图，真实栅格 | 原PNG，保留比例直接嵌入 | 不重画几何、不改像素或颜色；来源fig6_2，标签原样 |
| 反射曲线 | data-derived，已有201样本 | Matplotlib，SVG/PDF | 直接连线，不平滑、不重新仿真；GHz/dB，-10 dB参照；非总吸收 |
| 计算循环 | schematic，逻辑流程 | 紧凑原生SVG，生成源同时绘制PDF矢量 | 参数、候选、约束、CST、求解、S、fitness、GA及下一代；画反馈与终止出口，不暗示所有代码原创 |
| 整页 | 摘要排版 | ReportLab + PyMuPDF PDF矢量拼版 | A4；一页；中文10pt左右；Source Han Sans；灰黑+单一蓝；300dpi预览 |

最终结果只用归档的4.80–18.00 GHz同模反射采样区间，18 GHz为上限；不展示本轮后算的新性能。再绘图是呈现旧数据，不是新结果。全部像素材料之外的文字/曲线/箭头保持矢量。

输出：一页PDF、Markdown内容源、Python生成源、流程SVG、曲线SVG/PDF及PNG预览。说明含精确输入副本及哈希；不运行原优化器、CST或MATLAB。
''')
write('03_Project_Sheet/周子靖_毕设项目页_刘癸庚版_v1_INTERNAL.md','''# 电阻膜微波吸收结构的仿真与优化

周子靖｜哈尔滨工业大学应用物理学｜本科毕业设计，2026.05完成  
指导教师：李均教授｜zhouzijing54@gmail.com

## Research Question
如何在周期单元的几何约束下，通过电阻膜图案、尺寸与片阻的联合搜索拓宽低反射频带，并保持建模和评价条件一致？

## Physical / Structural Setup
金属背板上两块正交PET支撑电阻膜；周期单元、正入射。比较薄实体膜与Ohmic Sheet，后续分阶段搜索采用后者。结构图直接复用毕设图6.2原项目截图；旁图为保存的同模反射曲线，非实验测量。

## Computational Workflow
结构参数 → 候选生成 → 几何约束筛选 → CST参数化模型 → 频域求解 → S参数/同模反射 → 适应度评价 → GA选择/交叉/变异 → 下一代；不合格候选重新生成，达到终止条件后保存结果。流程图是计算逻辑摘要，不是新算法。

## My Contributions
- 基于课题组初始结构与学长参考代码，使用并扩展Python-CST自动建模、求解调用和响应提取；编码与调试使用AI辅助。
- 扩展图案、几何与双向片阻变量，调整6×6、9×9、12×12分阶段搜索及连通性等几何约束筛选。
- 处理与可视化仿真数据，对比薄实体膜和Ohmic Sheet的反射响应与优化结果。结构原型、遗传算法和电磁求解器均非本人发明。

## Archived Results
保存的201点曲线（2–18 GHz，间隔0.08 GHz）在4.80–18.00 GHz采样区间同模反射低于−10 dB，区间宽13.20 GHz；18 GHz为扫描上限。该结果不等同于已验证的总吸收带宽。

## Limitations / Next Step
已完成仿真流程修改与归档结果分析；全反射通道/功率平衡、网格与频率收敛、实验验证仍待完成。现阶段回看，可先完善这些验证，再评估代理模型辅助搜索；后者不是已完成工作。

---
v1 INTERNAL｜人工审查稿，不外发
''')
write('04_Background_Notes/本地复制与基线哈希_v1.json',json.dumps({'baseline':baseline,'copies':manifest},ensure_ascii=False,indent=2))
print('Prepared',PACK)
print('Email body Chinese count',len(re.findall(r'[\u4e00-\u9fff]',email.split('周子靖 |')[0])))
print('CV edits',found)
