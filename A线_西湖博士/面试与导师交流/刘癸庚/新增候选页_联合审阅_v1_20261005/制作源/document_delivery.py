"""Document reviewed candidate outputs. Does not rebuild or change slide content."""
from pathlib import Path
import json, os, re, hashlib

REVIEW=Path(__file__).resolve().parent.parent
PI=REVIEW.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
NAMES=json.loads((REVIEW/'候选目录.json').read_text(encoding='utf8'))
def rel(target,start):return Path(os.path.relpath(target,start)).as_posix()
def link(label,target,start):return f'[{label}]({rel(target,start)})'
def write(p,s):p.write_text(s,encoding='utf8')

designs={
'S0':('极简封面','只放交流主题、姓名和本科背景。无校徽、虚构日期时刻或设备图；不抢先讲动机。S0 是可选封面，不改变 S1–S13 编号。',
      '是否保留独立封面，或现场寒暄后直接从 S1 开始。'),
'S1':('个人背景 / 起点','左侧身份与应用物理学本科背景；右侧三段开放排版：本科毕设、合作科研、个人探索。用实际经历承接 CST / Python 数值工作流与数据分析，不做技能评级、CV清单或工具logo墙。',
      '新增自我介绍是否像本人说话；三类经历的强调顺序是否自然接向 S2。'),
'S10':('反思','放大真实文章条目，保留“8月4日”、原封面、标题和 AI 对话标识；右侧复述原问题便于投影。公众号名放副标题，不展示粉丝或阅读数。',
       '原条目与右侧可读问题的双重呈现是否合适；是否接受当前裁切与图文比例。'),
'S11':('表达','真实 HUMAN+ 第三个板块的主视觉占主体，保留文字与圆形视觉的组织关系；只有一句表达说明。裁去导航和底部三栏，未重绘、补造界面或增加产品能力。',
       '主视觉局部是否足以体现“表达”；是否希望下一版扩大到更多原网页留白。'),
'S12':('Why PhD','一条细线串起好奇与探索、AI时代、毕设复盘、长期科研训练；下方列训练目标、对结论负责和研究品味。页面是原文索引，speaker notes 完整逐段保留本人原文，另加打断接回提示。',
       '四段排版是否准确提示本人原始思想链；实际试讲时哪里适合停顿与接回。不能仅凭估计时长删原文。'),
'S13':('Why Liu / Westlake','左右对照已有电磁/数值起点与希望深入的波、模式、边界、损耗、机制；中间一条 performance → physics。topology / non-Hermitian 降权并明示希望系统学习。西湖仅一句个人训练偏好。',
       '轻量主述是否自然，约20–30秒密度是否合适；对“希望深入”的表述是否与本人当前理解一致。')}

common_sources=[PI/'完整主线与明日问答训练框架_20261005.md',PI/'完整讲稿_当前定稿内容合并版_v1_20261005.md']
specific={
'S0':[ROOT/'公共资料/事实核验/毕设与新增个人证据核验_20260926.md'],
'S1':[ROOT/'公共资料/事实核验/材料审计与申请人事实.md',ROOT/'公共资料/事实核验/毕设与新增个人证据核验_20260926.md',ROOT/'公共资料/事实核验/本科毕设R1_20260930/核验记录.md',ROOT/'公共资料/事实核验/尘埃等离子体_历史贡献与代码考古_20261005.md'],
'S10':[PI/'Personal_Explorations叙事与设计语言_20261005.md',PI/'S10-S11_反思与表达双页设计_20261005.md',ROOT/'公共资料/事实核验/个人探索_20261004/核验记录.md',ROOT/'公共资料/事实核验/个人探索_20261004/素材/S03_无用清净梦.png'],
'S11':[PI/'Personal_Explorations叙事与设计语言_20261005.md',PI/'S10-S11_反思与表达双页设计_20261005.md',ROOT/'公共资料/事实核验/个人探索_20261004/核验记录.md',ROOT/'公共资料/事实核验/个人探索_20261004/素材/S08_个人艺术网页第三板块.png'],
'S12':[PI/'Why_PhD母稿_用户原文_20261005.md',PI/'WhyPhD与WhyWestlake-Liu双页设计_20261005.md'],
'S13':[PI/'WhyPhD与WhyWestlake-Liu双页设计_20261005.md',PI/'PI与课题组研究地图.md',PI/'定制映射与PPT微调.md']}

for key,dirname in NAMES.items():
    out=PI/dirname;stem=dirname.rsplit('_20261005',1)[0]
    title,design,questions=designs[key]
    report=json.loads((out/'排版与保全检查.json').read_text(encoding='utf8'))
    assert not report['text_overflow'] and not report['shapes_outside_canvas'] and report['notes_complete']
    assert len(report['source_and_reference_preservation'])==140
    source_md='\n'.join('- '+link(p.name,p,out) for p in common_sources+specific[key])
    extra=('\n- [官方及课题组来源记录](官方来源记录.md)：2026-10-05公开核对及原始响应。\n' if key=='S13' else '')
    note='S12 原始母稿逐行完整存在于实际 PPT 备注中，核验为 true。' if key=='S12' else '实际 PPT 内的备注与本页备注 Markdown 内容一致。'
    write(out/'README.md',f'''# {key}｜{title} · v1 CANDIDATE

2026-10-05｜**INTERNAL / v1 CANDIDATE**｜供本人和 Chat 审阅，未升为 READY / final。

## 直接审阅

- [可编辑单页 PPTX]({stem}.pptx)
- [Microsoft PowerPoint 实际导出 PDF]({stem}.pdf)
- [1920×1080 PNG](预览/{key}_1920x1080.png) / [3840×2160 PNG](预览/{key}_3840x2160.png)
- [本页备注 / speaker notes](本页备注.md)（已写入 PPT）
- {link('本轮联合审阅入口',REVIEW/'README.md',out)}

## 设计与叙事职责

{design}

统一 16:9、白底、Microsoft YaHei、深蓝 `#172B43`、青色 `#007E86`；标题/页脚位置与 S2–S9 连续。均为可编辑文字和图形；真实截图作为单独图像对象，未将整页压成图片。

{note} 讲稿可停顿、被打断后接回；不受旧8–9分钟或个人探索80–90秒预算硬性约束。S13只有轻量主述，其完整思想保留为可展开内容。

## 来源与保全

{source_md}
{extra}
最新本人指令覆盖旧设计中要求合并整套PPT和按秒数删稿的部分；其他原稿保留原样。来源类型区分本人确认、历史截图、本地核验与本轮设计判断。

- [制作前来源与保全基线](来源与保全.json)：140份文件（120份已有S2–S9候选文件、17份源材料、3份既有未提交资料）。
- [派生素材与精确裁切说明](派生素材说明.json)：无图片的页面为空表；有图片的页面记录源尺寸、裁切框与SHA-256。
- [排版及保全检查](排版与保全检查.json)：全部140份基线文件内容保持；没有改科研原件或运行科研程序。

## 实际渲染与检查

Microsoft PowerPoint **16.0** 实际只读打开该单页，导出PDF和两档PNG。文字溢出 **0**，对象越界 **0**，备注完整；导出过程未改变PPTX字节。截图原比例、嵌入字节与确定性裁切像素检查通过（适用时）。

已逐页人工查看1080p实际导出：标题、主体与强调语层次清楚，没有截断；并以联合审阅图核看视觉连续性。截图细字仅作历史语境，投影时不要求全文阅读。现场房间、亮度、投影设备与本人实际试讲尚未测试，不以桌面预览冒充现场验收。

## 本人和 Chat 待仲裁

{questions}

## 制作源与复现

- [独立页面制作源](制作源/build_slide.py) / [配置](制作源/config.json)。依赖 Python、python-pptx、Pillow；从本目录的制作源运行只重建本候选，不调用旧页脚本。
- {link('PowerPoint 导出与检查源',REVIEW/'制作源/render_candidates.py',out)}：pywin32 + Microsoft PowerPoint 16.0，逐个打开本轮六份独立PPT，生成预览拼图，不生成合并PPT。
- 本轮验收完成后视为冻结候选；后续实质修改另建v2目录，不能用制作源覆盖审阅基线。

分支 `chatgpt/liu-interview-plan-20261004`，PR #15 保持 OPEN / no auto-merge；未合并main、未合并S1–S13、未发送材料。
''')

s13=PI/NAMES['S13']
raw=(s13/'公开来源/O01.html').read_text(encoding='utf8')
lab=re.search(r'lab:\s*"([^"]+)"',raw)
assert lab and lab.group(1)=='Laboratory of Complex Waves and Fields'
records=json.loads((s13/'公开来源/来源记录.json').read_text(encoding='utf8'))
records[0]['static_script_field']={'field':'personObj.lab','value':lab.group(1),'method':'Read literal data only; no JavaScript execution.'}
for entry in records:
    for ex in entry.get('excerpts',[]): ex['excerpt']=ex['term']
write(s13/'公开来源/来源记录.json',json.dumps(records,ensure_ascii=False,indent=2))
write(s13/'官方来源记录.md','''# S13｜官方与课题组来源记录

核对日期：2026-10-05。范围仅限组名和公开研究方向，不核招生承诺或具体培养保障。

| 类型 | 来源 | 支持的本页信息 | 保留边界 |
|---|---|---|---|
| O 官方教师页 | [西湖大学 Gui-Geng Liu](https://en.westlake.edu.cn/faculty/guigeng-liu.html) | `Laboratory of Complex Waves and Fields`；本地响应脚本的 personObj.lab 字段与网页检索结果相符 | 只读数据字段，未执行网页脚本；不由头衔推定招生或资源 |
| P 课题组自述 | [Liu Gui-Geng Research Group 首页](https://www.liuguigeng.com/) | 明确列出拓扑光子学、非厄米光学等；支持将二者作为希望进一步学习的方向 | 自述研究范围不是本人的已有技能，也不是导师承诺的新生课题 |

本轮网页工具首次直开教师页超时，随后检索取得组名；本地只读请求最终成功返回200并保存。教师页主要内容位于脚本配置，普通去脚本正文提取为空不代表该字段不存在；本轮静态读取 personObj.lab 原文，未执行。课题组页200，方向词在正文可核。

本地原始响应：[O01.html](公开来源/O01.html)、[P01.html](公开来源/P01.html)；HTTP状态、字节、哈希与字段见[来源记录.json](公开来源/来源记录.json)。旧仓库来源继续保留，不覆盖。

“波与模式、边界与损耗、物理机制”是结合本人毕设复盘组织的学习问题，不声称是课题组官方课程目录。西湖大学部分只写本人“希望进入以科研训练为核心的环境”的偏好，未增加未经核验的制度、师生比、设备、跨学科机制或培养优势。没有宣称申请人精读了组内论文。
''')

rows='\n'.join(f'| {k} | {designs[k][0]} | {link("PPTX",PI/n/(n.rsplit("_20261005",1)[0]+".pptx"),REVIEW)} / {link("PDF",PI/n/(n.rsplit("_20261005",1)[0]+".pdf"),REVIEW)} | {link("说明与备注",PI/n/"README.md",REVIEW)} |' for k,n in NAMES.items())
write(REVIEW/'README.md',f'''# 刘癸庚交流｜新增候选页联合审阅

2026-10-05｜**INTERNAL / v1 CANDIDATE**｜本轮只补页，等待本人和 Chat 审阅。

## 本轮实际交付

| 页 | 用途 | 实际文件 | 备注与来源 |
|---|---|---|---|
{rows}

每份均为独立一页：可编辑PPTX、PowerPoint 16.0实际导出PDF、3840×2160及1920×1080 PNG、README、已嵌入备注、来源与保全、制作源。**没有S1–S13合并PPT**，也没有把旧S2–S9重新制作。

## 联合预览

- [S10–S13 联合审阅](预览/S10-S13_联合审阅.png)
- [S10–S11 双页审阅](预览/S10-S11_双页审阅.png)
- [S12–S13 双页审阅](预览/S12-S13_双页审阅.png)
- [S1 与既有 S2 衔接审阅](预览/S1-S2_衔接审阅.png)
- [拼图来源与哈希](预览来源.json)

![S10–S13联合审阅](预览/S10-S13_联合审阅.png)

![S1与S2衔接](预览/S1-S2_衔接审阅.png)

预览是实际PowerPoint导出PNG的等比例拼接，供看叙事与视觉连续性，不是新的合并演示文件。S2直接引用既有v2.1预览字节，没有打开或改写旧PPT。

## 开始时的实际文件与版本状态

1. 本地起点 `9211a3f`，正确分支；PR #15 是 OPEN，autoMergeRequest 为 null。
2. 核对远端后发现三条仅新增主线/讲稿的提交；不与既有未提交资料冲突，已快进当前分支至 `2cff85ef2f2e7551d8e245a0b014fdeefcb41658`，再以新版完整主线和合并讲稿制作。
3. PPTX及文件检索确认：S2–S5 v2.1、S6、S7、S8、S9 A/B已有实际候选；S1/S10–S13没有实际候选。新版完整讲稿也明确S1尚待制作。
4. 未发现本次刘老师交流可复用正式封面。仓库中历史本科答辩PPT属于其他用途，不能当作本次交流封面。因此补一个可选、独立S0，不改内容页编号。
5. 三份既有未提交公共毕设资料不属于本轮，原样保留，不纳入提交。

## 叙事与原稿优先级

以本人本轮指令优先：不合整套、不改S2–S9、不按旧8–9分钟删稿。旧设计文件中相冲突的合并步骤和秒数预算仅保留为历史记录。

新增页围绕“实际问题与工具起点 → 反思与表达 → 为什么长期训练 → 为什么向波动物理深入”接续。S12页面四段仅作路标，其本人原文在speaker notes逐行完整保留；S13主讲保持轻量，完整逻辑置于可展开备注。未改任何已有口述母稿或完整讲稿。

## 验收

- [PowerPoint渲染汇总](PowerPoint渲染汇总.json)：六份独立PPT均由Microsoft PowerPoint **16.0**实际打开，导出PDF/4K/1080p；文字溢出0、对象越界0。
- [人工视觉检查记录](人工视觉检查.md)：逐页查看实际1080p输出；页面比例、核心可辨性与连续性通过桌面预览检查。现场投影和本人试讲未实测。
- [制作前保全基线](制作前保全基线.json)：120份已有S2–S9文件、17份来源及3份无关未提交资料共140份，哈希保持。
- S10/S11裁切像素逐一与原图对比，PPT嵌入字节一致，图片比例无拉伸。
- 每页实际备注与本页Markdown一致；S12原文完整性检查为true。

## 本人与 Chat 的主要仲裁点

1. **S1** 的新口述是否像本人；三段入口是否自然引出S2。
2. **S10/S11** 的裁切、图文占比与两页“反思 → 表达”是否成立，避免被误听成运营/产品成果。
3. **S12** 四段索引能否支撑原文完整表达、被打断后接回；先标真实表达问题，不以估计时长删思想。
4. **S13** 轻量主述是否自然、理论学习边界是否明确；可选S0是否保留。

下一步由本人和Chat审完新增页，再决定新版本修订及整套合并。本轮候选不升级为final，不更改联系事件，不发送申请材料。PR #15继续OPEN / no auto-merge，不合并main。
''')
write(REVIEW/'人工视觉检查.md','''# 实际输出人工视觉检查

2026-10-05｜INTERNAL / v1 CANDIDATE

检查对象：Microsoft PowerPoint 16.0 导出的六张1920×1080图；并对照既有S2 v2.1、S8与本轮联合图。几何/字形边界通过COM读取实际文字边界，未用仅源代码尺寸替代。

| 页 | 视觉检查 | 剩余实际条件 |
|---|---|---|
| S0 | 白底、姓名与标题明确；无多余研究承诺或日期；留白符合封面用途 | 是否现场使用由本人审阅决定 |
| S1 | 左侧身份与右侧经历分工清楚；没有等级/工具logo堆叠；可直接接S2 | 新口述须本人确认自然程度 |
| S10 | 原问题醒目；文章日期、完整标题和AI对话痕迹保留；没有粉丝/阅读量；右侧可编辑大字保证核心问题可读 | 原封面的小模型名只是历史语境，不要求会场全文读出；年月不补推 |
| S11 | HUMAN+、原核心文案与圆形视觉占主体；没有新增功能介绍；原图比例正常 | 历史页面中服务词/按钮保留为证据，不能口述成上线能力；细字不是投影重点 |
| S12 | 四段逻辑线与下方训练目标分层；“AI永远不会”的边界可见；没有四象限/卡片墙 | 备注完整原文较长，真实时长及停顿位置待试讲 |
| S13 | 起点→物理问题方向清楚；学习标签降权但可见；学校句是个人偏好 | 轻量主述仅约20–30秒内容密度估计，尚未实测 |

连续性：与S2–S9共用16:9、Microsoft YaHei、深蓝/青色、白底、左上分区与页底细线、右下S页号。S1–S2预览使用现有S2 PNG，本轮没有改旧页。

限制：桌面1080p视觉检查支持当前审阅；没有使用真实会议室投影、远程会议压缩链或现场距离做实测。不把4K导出解释为原始历史截图细节增加。
''')
print('Readmes, source records and review entry written.')
