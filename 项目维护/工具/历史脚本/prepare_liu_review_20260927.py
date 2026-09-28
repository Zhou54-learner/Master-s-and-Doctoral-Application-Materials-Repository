"""Create review candidates only; preserve existing material and research inputs."""
from pathlib import Path
import sys, json, hashlib, shutil

W = Path(__file__).resolve().parents[1]
ROOT = W.parent
P = W / '联系/刘癸庚'
sys.path.insert(0, str(W / '核验/a4_runtime'))
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def new(p, text):
    assert not p.exists(), p
    p.write_text(text, encoding='utf-8')

baseline_files = list((P/'02_CV').glob('*v2_INTERNAL.*')) + [
    P/'01_Email/第一封套磁邮件_刘癸庚_v3_CANDIDATE.md',
    P/'03_Project_Sheet/周子靖_毕设项目页_刘癸庚版_v2_CANDIDATE.md',
    W/'材料/对外PDF/周子靖_中文学术简历_Master_v1.2.pdf',
    W/'材料/对外PDF/周子靖_中文学术简历_Master_v1.2.docx',
    W/'材料/周子靖_中文学术简历_v0.5_INTERNAL.md',
    P/'03_Project_Sheet/source/build_project_sheet.py',
    P/'03_Project_Sheet/source/workflow.svg',
]
manifest = {'preserved': {p.relative_to(ROOT).as_posix():sha(p) for p in baseline_files}}

body = '''刘老师您好：

我叫周子靖，2026年6月毕业于哈尔滨工业大学应用物理学专业，希望申请您课题组2027年秋季入学的博士研究生。看到复杂波与场实验室的招生信息，想请您判断我的背景是否适合组内课题。

我的本科毕设研究电阻膜微波吸收结构。基于课题组已有结构与参考代码，我扩展了 Python-CST 参数化仿真与遗传算法搜索流程，增加几何与片阻变量、加入几何约束筛选，并完成反射响应处理及薄实体膜与 Ohmic Sheet 模型比较。此外，我在二维尘埃等离子体晶格波合作研究中使用 MATLAB 处理模拟数据、分析偏振特征并绘制粒子运动轨迹。

您课题组利用损耗配置调控光子晶体手性边缘态局域化的研究让我很感兴趣。我希望以物理建模与计算为主要切入点，将已有的仿真、自动化与参数搜索经验用于复杂波体系，进一步理解拓扑与非厄米机制对波传播的影响；也关注招聘信息中提及的有限元仿真与 AI 辅助软件开发方向。

请问您课题组2027年秋季是否仍有适合我背景的博士招生课题，以及对应的招生学科是什么？随信附上中文简历、本科成绩单及两篇合作论文，个人贡献见简历；另备有毕设一页摘要，可进一步提供。

感谢您阅读这封邮件，期待有机会进一步向您介绍我的研究经历。

周子靖 | Zijing Zhou
哈尔滨工业大学 应用物理学（2026届）
zhouzijing54@gmail.com
'''
new(P/'01_Email/第一封套磁邮件_刘癸庚_v4_CANDIDATE.md', '''# 第一封套磁邮件 v4 CANDIDATE

2026-09-27｜待本人审查｜未发送

收件人：liuguigeng@westlake.edu.cn  
发件邮箱：zhouzijing54@gmail.com  
发件显示名：周子靖 Zijing Zhou  
主题：**博士生申请-周子靖**

---

''' + body)
new(P/'01_Email/邮件正文_v4_CANDIDATE.txt', body)

stem = '周子靖_中文学术简历_刘癸庚版_v3_CANDIDATE'
oldstem = '周子靖_中文学术简历_刘癸庚版_v2_INTERNAL'
oldscore = '算术均分：80.20/100（成绩单自算）｜专业排名：21/46（2025.09推免口径）'
score = '算术均分：80.20/100*｜专业排名：21/46（前三年）*'
note = '*均分按本科成绩单中的百分制课程作算术平均；排名依据2025年9月推免排名名单，四年总排名证明办理中。'
md = (P/'02_CV'/f'{oldstem}.md').read_text(encoding='utf-8-sig')
assert oldscore in md
md = md.replace(oldscore, score).replace('---\n刘癸庚定制 v2｜INTERNAL｜人工审查稿，不外发。', note+'\n\n---\n刘癸庚定制 v3｜CANDIDATE｜待本人审查，未发送。')
new(P/'02_CV'/f'{stem}.md', md)
doc = Document(P/'02_CV'/f'{oldstem}.docx')
matched = 0
for p in doc.paragraphs:
    if p.text in ['教育背景', '研究兴趣', '科研经历', '代表论文', '技术与语言', '精选荣誉']:
        p.paragraph_format.space_before = Pt(4)
    if p.text.startswith('算术均分：'):
        p.clear()
        r = p.add_run(score)
        r.font.name = 'Source Han Sans CN Regular'
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor.from_string('222222')
        r._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), 'Source Han Sans CN Regular')
        matched += 1
assert matched == 1
for sec in doc.sections:
    footer = sec.footer
    fp = footer.paragraphs[0]
    fp.clear()
    fp.paragraph_format.space_before = Pt(0)
    fp.paragraph_format.space_after = Pt(2)
    fp.paragraph_format.line_spacing = Pt(11)
    r = fp.add_run(note)
    r.font.name = 'Source Han Sans CN Regular'
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor.from_string('444444')
    r._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), 'Source Han Sans CN Regular')
    p = footer.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = Pt(9)
    r = p.add_run('刘癸庚定制 v3 · CANDIDATE · 待本人审查，未发送')
    r.font.name = 'Source Han Sans CN Regular'
    r.font.size = Pt(7)
    r.font.color.rgb = RGBColor.from_string('777777')
    r._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), 'Source Han Sans CN Regular')
doc.core_properties.title = '周子靖 | 刘癸庚定制CV v3候选'
doc.core_properties.comments = 'Review only. Rank timeframe supplied by applicant; graduation rank certificate pending.'
assert not (P/'02_CV'/f'{stem}.docx').exists()
doc.save(P/'02_CV'/f'{stem}.docx')

sheet = (P/'03_Project_Sheet/周子靖_毕设项目页_刘癸庚版_v2_CANDIDATE.md').read_text(encoding='utf-8-sig')
sheet = sheet.replace('结构图复用毕设原项目截图；旁图为保存的同模反射曲线，非实验测量。', '图示：毕设 CST 模型与同模反射仿真曲线。')
sheet = sheet.replace('v2 CANDIDATE｜待人工审查，不外发', 'v3 CANDIDATE｜待本人审查，未发送')
new(P/'03_Project_Sheet/周子靖_毕设项目页_刘癸庚版_v3_CANDIDATE.md', sheet)

# Derive a new renderer without executing or changing the historical renderer.
src = (P/'03_Project_Sheet/source/build_project_sheet.py').read_text(encoding='utf-8')
changes = {
    "name='周子靖_毕设项目页_刘癸庚版_v1_INTERNAL'": "name='周子靖_毕设项目页_刘癸庚版_v3_CANDIDATE'",
    "OUT=args.output_dir or HERE.parent/'output'": "OUT=args.output_dir or HERE.parent/'output_v3_CANDIDATE'",
    "(HERE/'workflow.svg').write_text": "(OUT/'workflow.svg').write_text",
    '原项目CST结构截图（毕设图6.2）': '毕设CST模型（图6.2）',
    '归档曲线；非实验测量，非总吸收': '同模反射仿真曲线',
    '逻辑摘要：达到终止条件后保存结果；图示不代表提出新算法。': '达到终止条件后保存结果。',
    '基于课题组初始结构与学长参考代码，扩展Python-CST自动建模、求解调用与响应提取；编码和调试使用AI辅助。': '基于课题组初始结构与参考代码，扩展Python-CST自动建模、求解调用和响应提取流程。',
    '扩展图案、几何和双向片阻变量，调整6×6、9×9、12×12分阶段搜索及连通性等几何约束筛选。': '扩展图案、几何与双向片阻变量，调整6×6、9×9、12×12分阶段搜索，并加入连通性等几何约束筛选。',
    '处理和可视化数据，对比薄实体膜与Ohmic Sheet的反射响应及优化结果。结构原型、遗传算法和电磁求解器均非本人发明。': '处理与可视化仿真数据，对比薄实体膜和Ohmic Sheet的反射响应与优化结果。',
    '05  已归档结果': '05  主要仿真结果',
    '保存的201点曲线（2–18 GHz，间隔0.08 GHz）在<b>4.80–18.00 GHz</b>采样区间同模反射低于−10 dB，区间宽<b>13.20 GHz</b>；18 GHz为扫描上限。该结果不等同于已验证的总吸收带宽。': '保存的201点曲线（2–18 GHz，间隔0.08 GHz）显示，<b>4.80–18.00 GHz</b>采样区间内同模反射低于−10 dB，对应区间宽<b>13.20 GHz</b>；18 GHz为扫描上限。该区间为同模反射采样带宽，不等同于已验证的总吸收带宽。',
    '06  局限与后续改进': '06  后续验证与改进',
    '全反射通道/功率平衡、网格与频率收敛、实验验证仍待完成。现阶段回看，应先完善这些验证，再评估代理模型辅助搜索；后者不是已完成工作。': '下一步优先完善全端口功率平衡、网格与频率收敛等数值验证；实验验证视条件推进。在数值验证更充分后，可进一步评估代理模型辅助搜索，以减少高成本前向仿真的调用次数。',
    'v1 INTERNAL · 人工审查稿，不外发': 'v3 CANDIDATE · 待本人审查，未发送',
}
for before, after in changes.items():
    assert before in src, before
    src = src.replace(before, after)
src = src.replace("buffer=io.BytesIO()", "assert not (OUT/(name+'.pdf')).exists(), 'Preserve existing candidate'\nbuffer=io.BytesIO()")
new(P/'03_Project_Sheet/source/build_project_sheet_v3_candidate.py', src)
out = P/'03_Project_Sheet/output_v3_CANDIDATE'
out.mkdir(exist_ok=True)
shutil.copy2(P/'03_Project_Sheet/output/reflection.pdf', out/'reflection.pdf')
new(P/'05_Send_Readiness/审查候选_20260927_保全.json', json.dumps(manifest,ensure_ascii=False,indent=2))
print('Created email v4, CV v3, project sheet v3 review candidates.')
