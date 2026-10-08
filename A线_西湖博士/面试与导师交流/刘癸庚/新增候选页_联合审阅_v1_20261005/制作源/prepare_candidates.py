"""Create NEW independent candidates only. Never edits prior slides or source evidence."""
from pathlib import Path
import hashlib, json, shutil, subprocess

HERE = Path(__file__).resolve().parent
REVIEW = HERE.parent
PI = REVIEW.parent
ROOT = next(p for p in PI.parents if (p/'申请路线总览.md').exists())
ASSETS = ROOT/'公共资料/事实核验/个人探索_20261004'
NAMES = {'S0':'S0_封面_v1_20261005','S1':'S1_个人背景_v1_20261005',
         'S10':'S10_反思_v1_20261005','S11':'S11_表达_v1_20261005',
         'S12':'S12_WhyPhD_v1_20261005','S13':'S13_WhyLiu_v1_20261005'}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p): return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def write(p,s): p.write_text(s,encoding='utf-8')

def main():
    assert all(not (PI/n).exists() for n in NAMES.values()), 'Candidate directory already exists; do not overwrite.'
    refs=[p for d in PI.iterdir() if d.is_dir() and
          (d.name.startswith('本科毕设_S2-S5_') or d.name.startswith(('S6_','S7_','S8_','S9_')))
          for p in sorted(d.rglob('*')) if p.is_file()]
    sources=[ASSETS/'核验记录.md',ASSETS/'来源清单.json',
             ASSETS/'素材/S03_无用清净梦.png',ASSETS/'素材/S08_个人艺术网页第三板块.png']
    sources += [PI/n for n in ['完整主线与明日问答训练框架_20261005.md','Personal_Explorations叙事与设计语言_20261005.md',
                'S10-S11_反思与表达双页设计_20261005.md','Why_PhD母稿_用户原文_20261005.md',
                'WhyPhD与WhyWestlake-Liu双页设计_20261005.md','完整讲稿_当前定稿内容合并版_v1_20261005.md',
                'PI与课题组研究地图.md','定制映射与PPT微调.md']]
    sources += [ROOT/n for n in ['公共资料/事实核验/材料审计与申请人事实.md',
                '公共资料/事实核验/毕设与新增个人证据核验_20260926.md',
                '公共资料/事实核验/本科毕设R1_20260930/核验记录.md',
                '公共资料/事实核验/尘埃等离子体_历史贡献与代码考古_20261005.md',
                '公共资料/事实核验/乐音研究_历史内容与独立贡献考古_20261005.md']]
    unrelated=[ROOT/'公共资料/面试与导师交流中心/公共主干'/n for n in
               ['README.md','项目重建/本科毕设/README.md','项目重建/本科毕设/13_实际工作梳理与研究叙事底稿.md']]
    baseline=dict(date='2026-10-05',base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  sources=[record(p) for p in sources],reference_files=[record(p) for p in refs],
                  unrelated_work=[record(p) for p in unrelated],
                  scope='Six independent single-page candidates. Read-only S2–S9 and all originals. No full deck.')
    write(REVIEW/'制作前保全基线.json',json.dumps(baseline,ensure_ascii=False,indent=2))
    archived=json.loads((ASSETS/'来源清单.json').read_text(encoding='utf-8'))
    for item in archived:
        if item['id'] in ('S03','S08'): assert sha(ROOT/item['copy'])==item['sha256']
    notes={
    'S0': '''# S0｜封面 · 本页备注

状态：INTERNAL / v1 CANDIDATE。可选封面，不占 S1–S13 内容页号。

## 开场

刘老师、各位老师好，我是周子靖。谢谢大家给我这次交流的机会。今天我想结合本科的研究经历和一些个人探索，介绍自己做过什么，以及这些经历带给我的一些思考。

## 使用与接回

封面只作开场停留，不重复讲教育和动机。若已口头寒暄，可直接翻到 S1。尚未填具体时刻、会议号、链接或平台。
''',
    'S1': '''# S1｜个人背景 / 起点 · 本页备注

状态：INTERNAL / v1 CANDIDATE。本轮新增讲稿候选，尚待本人审校，不回写完整讲稿母版。

## 主述

我的本科是在哈尔滨工业大学物理学院读应用物理学。今天想从几段实际经历来介绍自己，而不是逐项念简历。

本科毕设是电磁结构的仿真与优化，这里面我接触了 CST 参数化建模、Python 和数值工作流；合作科研里，我主要做过数值数据处理和轨迹可视化。后面也会讲一些由好奇心出发的小研究，以及我使用 AI 和表达想法的个人探索。

这些经历构成了我现在的起点。先从毕业设计讲起，它也是我这次重新复盘得最多的一个项目。

## 被打断后接回

若停在教育背景：“后面我会用几段实际工作说明这些经历，先讲本科毕设。”
若停在工具或贡献：“具体做到了哪一步，我会放在项目里讲清楚。先看毕设的问题和结构。”

## 事实边界

应用物理学采用最新学历登记口径；培养属性是中外合作，问及时如实说明。数值工作流是使用、修改和扩展已有流程，并有师兄与 AI 输入；不声称独立开发 GA 或熟练 FEM。合作科研限已核的数据处理、轨迹图件贡献。此页不增加 GPA、排名、论文主导性或新技能等级；不提前讲 Why PhD / Why Liu。自然讲清即可，未实测试讲时间。
''',
    'S10': '''# S10｜使用技术，也持续追问人的位置 · 本页备注

状态：INTERNAL / v1 CANDIDATE。沿用已处理口述，新增指图与接回提示；不按旧秒数删稿。

## 从 S9 接入

但我并不只关心怎样把 AI 用得更深。用得越多，我反而越会追问：人在这套协作里到底还应该保留什么。

## 主述

我也会把一些更长期的问题写下来。AI 越来越进入我的学习和工作以后，我会不断追问：效率提高之外，人自己的判断、价值和工作到底还意味着什么。“无用清净梦”就是我记录这些问题的地方。

〔指图，可自然补充〕这里放的是一篇真实文章条目，问题就是“当完成任务越来越不需要人，工作还意味着什么？”原封面里的 AI 对话标识也保留着。

## 转向 S11

这些问题除了写下来，我也会尝试用视觉和页面去表达。

## 被打断后接回

“这个问题我还在持续思考。这一页主要想说明，我会把这类问题留下来，继续追问。除了文字，我也尝试过另一种表达形式。”

## 证据与边界

只裁出 S03 的一个真实条目，保留截图中“8月4日”、文章封面、完整标题与 AI 对话标识；不据此补推年份。未展示阅读/粉丝数量。该页说明选题、组织与持续反思，不能推定每字每图独立创作、已建立社会理论或观点已经验证。原图内模型名称仅是历史画面，不是本轮对模型身份的认证。本人/AI逐项分工仍 UNKNOWN。
''',
    'S11': '''# S11｜把思考组织成可以被感知的表达 · 本页备注

状态：INTERNAL / v1 CANDIDATE。延续 S10 的问题意识，收束 Personal Explorations。

## 主述

文字之外，我也会用页面和视觉去组织想法。这是我个人艺术网页里的一个真实板块。对我来说，表达本身也是思考的一部分：一个想法不仅要想清楚，也要让别人能够感受到它。

## 接回与翻页

如果被问网页具体做了什么：“这里主要是我用文字、视觉和页面组织想法的一次尝试；它是个人艺术网页的第三个板块。”不展开技术栈或虚构上线服务。

接向 S12：“这些探索和前面的科研经历，也让我不断想清楚，自己为什么还想继续接受科研训练。”

## 事实边界

S08 真实截图的代表性主视觉局部，保留 HUMAN+、核心文案与圆形视觉；裁去顶部导航和底部栏，不通过重绘或生成式方法改界面。截图中按钮、服务文案只是历史页面内容，不证明商业服务、评估能力或交互已经验证。HUMAN+ 是第三个板块，不是整站首页。人/AI逐项创作分工仍 UNKNOWN。未因旧时间预算删掉推荐口述。
''',
    'S13': '''# S13｜下一步：更深入地理解波和场 · 本页备注

状态：INTERNAL / v1 CANDIDATE。轻量收束，Why Liu 优先。主述约20–30秒密度，仅供参考，尚未本人实测；可被随时打断。

## 主述候选

我之前更多从电磁结构和性能优化出发。复盘后，我更想深入理解波、模式、边界和损耗。刘老师组的 Complex Waves and Fields，以及拓扑、非厄米这些问题，让我很想继续学下去。我有一些仿真和数值工作的起点，理论还需要系统补足，也希望在西湖接受以科研为核心的训练。

## 被追问时展开：保留本人完整思想，不要求全部主讲

我之前的工作更多还是从结构设计和性能优化出发。重新复盘以后，我发现自己其实更希望往物理问题本身深入，而不只是继续做那些随着 AI 发展会越来越容易自动化的实现工作。

刘老师组的 Complex Waves and Fields，包括模式、边界、损耗以及拓扑、非厄米这些问题，对我来说正好是一个很有吸引力的下一步。我已经有一些电磁仿真和数值工作的基础，但理论上还有很多需要补，我反而很希望接受这种训练。

这延续前面的毕设复盘：能借 Python、CST、GA 和 AI 推进优化，并不等于已经充分理解理论、结果可信度和机制。下一步想加深的是物理问题本身，不是单纯让自动优化更复杂。

## 被打断后接回 / 收束

“所以我的已有起点是仿真和数值工作，但下一步想训练的是对波和场的理解，也希望听听老师对这一学习路径的建议。”

## 来源与边界

官网教师页确认 Laboratory of Complex Waves and Fields；课题组首页明确 topological photonics、non-Hermitian optics 等方向。波与模式、边界与损耗、物理机制，是本人希望深入的问题组织，不写成老师承诺的课题或培养安排。topology / non-Hermitian 是希望系统学习，不能声称已掌握、已精读全部论文。西湖部分只表达本人环境偏好，不推定具体制度、设备、资源和培养优势。来源见 README 和 官方来源记录.md。
'''}
    original=(PI/'Why_PhD母稿_用户原文_20261005.md').read_text(encoding='utf-8').strip()
    notes['S12']='''# S12｜为什么我想继续接受科研训练 · 本页备注

状态：INTERNAL / v1 CANDIDATE。下方本人原文完整写入 PPT speaker notes，未作删节或措辞替换。页面四段只是阅读索引，不替代完整思想链；无硬性时长。

## 本人原文（完整保留）

'''+original+'''

## 打断与接回提示（辅助，非替代稿）

1. 停在“好奇与探索”：从“另一方面是基于我对 AI 时代的思考”接起。
2. 停在“未来需要人的什么能力”：回到“我的毕业设计就是一个具体例子”。
3. 停在毕设短板：“所以我想训练的，不是某一种被认为永远不能替代的固定技能。”继续最后一段。
4. 停在训练目标：“这些能力需要在一个领域长期深入，也要接受导师和同行的挑战。”最后落在对结论负责、研究判断与研究品味。

## 转向 S13

“落实到下一阶段，我尤其希望在波和场的问题上继续深入。”

## 边界

AI时代的判断为本人动机与思考，不是关于未来技术能力的已验证预测。毕设复盘是当前认识，不倒写为历史已完成的机制分析。原文中的长期训练是目标，不是已经取得的能力。页面、备注均保留“不是寻找 AI 永远不会的固定技能”的边界。因完整原文较长，试讲可能明显超过旧50–70秒；本轮不凭估计删稿。
'''
    for key,dirname in NAMES.items():
        out=PI/dirname
        for sub in ['制作源','预览','派生素材']: (out/sub).mkdir(parents=True,exist_ok=False)
        write(out/'本页备注.md',notes[key])
        write(out/'来源与保全.json',json.dumps(baseline,ensure_ascii=False,indent=2))
        write(out/'制作源/config.json',json.dumps(dict(slide=key,stem=dirname.rsplit('_20261005',1)[0],date='2026-10-05'),ensure_ascii=False,indent=2))
        shutil.copyfile(HERE/'slide_builder.py',out/'制作源/build_slide.py')
    write(REVIEW/'候选目录.json',json.dumps(NAMES,ensure_ascii=False,indent=2))
    print(json.dumps(dict(created=NAMES,preserved_files=len(refs),base_commit=baseline['base_commit']),ensure_ascii=False))

if __name__=='__main__': main()
