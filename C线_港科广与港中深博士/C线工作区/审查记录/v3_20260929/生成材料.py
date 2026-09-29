from pathlib import Path
import re, json, html, hashlib
import fitz

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'C线_港科广与港中深博士/C线工作区'
REC = Path(__file__).resolve().parent
PUB = BASE / '公共联系材料'
def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s.strip()+'\n', encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

xu = '''Dear Prof. Xu,

I graduated from Harbin Institute of Technology with a B.S. in Applied Physics in June 2026. I am interested in joining your group as a PhD student in Fall 2027, building on my experience in electromagnetic simulation and design optimization.

For my undergraduate thesis on resistive-film microwave absorbers, I used and extended an existing Python–CST simulation and genetic-algorithm-based optimization workflow in our group. My work included adding geometry and sheet-resistance variables, implementing geometric constraint checks, and automating simulation runs and reflection-data processing. I also compared thin-film and Ohmic Sheet models to examine how modelling choices affected the simulated responses.

Your group's research on metamaterials and integrated photonic devices interests me. I would like to extend my experience in electromagnetic modelling, automation, and design search to photonic-device problems, while developing my understanding of the relevant photonics.

Would you consider an applicant entering with a bachelor's degree and my simulation background for a Fall 2027 PhD project involving electromagnetic modelling and device design? I have attached my CV and undergraduate transcript and would welcome an opportunity to discuss my previous work.

Thank you for your time.

Best regards,
Zijing Zhou
Harbin Institute of Technology | B.S. Applied Physics, 2026
zhouzijing54@gmail.com'''
xuzh = '''许老师您好：

我于2026年6月毕业于哈尔滨工业大学，获得应用物理学学士学位。希望在已有电磁仿真和设计优化经历的基础上，申请您课题组2027年秋季入学的博士研究生。

我的本科毕设研究电阻膜微波吸收结构。我使用并扩展了课题组已有的 Python–CST 仿真与基于遗传算法的优化流程，具体工作包括增加几何与片阻变量、加入几何约束检查，以及自动化执行仿真和处理反射数据。我还比较了薄膜与 Ohmic Sheet 模型，考察建模选择对模拟响应的影响。

我对您组的超材料和集成光子器件研究感兴趣，希望将电磁建模、自动化和设计搜索经验进一步延伸到光子器件问题，同时加深对相关光子学知识的理解。

请问您是否会考虑我这样以本科学历申请、具有上述仿真背景的申请者，参与2027年秋季与电磁建模和器件设计相关的博士项目？随信附上简历和本科成绩单，期待有机会进一步介绍我之前的工作。

感谢您阅读这封邮件。

祝好！
周子靖 / Zijing Zhou
哈尔滨工业大学｜应用物理学学士，2026届
zhouzijing54@gmail.com'''
gong = '''Dear Prof. Gong,

I graduated from Harbin Institute of Technology with a B.S. in Applied Physics in June 2026. I am interested in PhD study in scientific computing at CUHK-Shenzhen for Fall 2027, particularly numerical methods for wave problems.

For my undergraduate thesis on resistive-film microwave absorbers, I used and extended an existing Python–CST simulation and genetic-algorithm-based optimization workflow. My contributions included additional design variables, geometric constraint checks, automated simulation runs, and reflection-data processing. Comparing thin-film and Ohmic Sheet models also gave me experience examining how modelling choices affect simulation results.

Your work on numerical methods for frequency-domain wave problems, including Helmholtz and Maxwell equations, interests me. My experience so far centres on application-level electromagnetic modelling and workflow automation. I would like to build on it through training in numerical analysis and finite-element methods, with the aim of contributing to reliable and efficient wave simulation.

Would you consider an applicant entering with an Applied Physics bachelor's degree and this simulation background for a Fall 2027 PhD project in your group? I have attached my CV, undergraduate transcript, and a short research statement, and would welcome the opportunity to discuss my work and research interests.

Thank you for your time.

Best regards,
Zijing Zhou
Harbin Institute of Technology | B.S. Applied Physics, 2026
zhouzijing54@gmail.com'''
gongzh = '''龚老师您好：

我于2026年6月毕业于哈尔滨工业大学，获得应用物理学学士学位。希望申请香港中文大学（深圳）2027年秋季入学的科学计算方向博士研究生，尤其对波动问题的数值方法感兴趣。

我的本科毕设研究电阻膜微波吸收结构。我使用并扩展了已有的 Python–CST 仿真与基于遗传算法的优化流程，具体贡献包括增加设计变量、加入几何约束检查、自动化执行仿真，以及处理反射数据。通过比较薄膜与 Ohmic Sheet 模型，我也积累了考察建模选择如何影响模拟结果的经验。

我对您关于频域波动问题数值方法的研究感兴趣，包括 Helmholtz 和 Maxwell 方程相关工作。我目前的经验主要集中在应用层面的电磁建模和工作流程自动化，希望在此基础上接受数值分析与有限元方法训练，逐步参与可靠、高效的波动仿真研究。

请问您是否会考虑我这样以应用物理学本科学历申请、具有上述仿真背景的申请者，参与您组2027年秋季的博士项目？随信附上简历、本科成绩单和一份简短研究陈述，期待有机会进一步介绍我的工作和研究兴趣。

感谢您阅读这封邮件。

祝好！
周子靖 / Zijing Zhou
哈尔滨工业大学｜应用物理学学士，2026届
zhouzijing54@gmail.com'''
rs = '''# Short Research Statement — Zijing Zhou

I am interested in reliable and efficient numerical simulation of wave phenomena. My undergraduate thesis concerned resistive-film microwave absorbers. Using and extending an existing Python–CST workflow, I expanded design variables, added geometric screening, and automated simulation runs and reflection-data processing. Comparing thin-film and Ohmic Sheet representations drew my attention to how modelling assumptions affect computed responses.

I would like to develop from application-level electromagnetic simulation towards numerical methods for frequency-domain wave problems. I hope to begin with finite-element methods and standard frequency-domain wave problems, gradually understanding how discretization, error, and solver choices affect simulation reliability and computational efficiency.

I would bring experience in organizing parameterized simulation workflows and analysing their outputs, while developing the mathematical and programming foundations needed for numerical-method research. These are areas in which I hope to receive training; the specific research topic would be shaped through discussion with the supervisor.'''
rszh = '''# 简短研究陈述——周子靖

我对可靠、高效的波动现象数值仿真感兴趣。我的本科毕设研究电阻膜微波吸收结构。在使用并扩展已有 Python–CST 流程的过程中，我扩展了设计变量、加入几何筛选，并自动化执行仿真和处理反射数据。薄膜与 Ohmic Sheet 表示方式的比较，使我开始关注建模假设如何影响计算响应。

我希望从应用层面的电磁仿真进一步深入频域波动问题的数值方法，希望从有限元方法和标准频域波问题入手，逐步理解离散、误差和求解器选择如何影响仿真可靠性与计算效率。

我能够带来组织参数化仿真流程与分析输出的经验，同时继续发展数值方法研究所需的数学与编程基础。以上是我希望接受训练的方向；具体研究课题将通过与导师讨论确定。'''

cv = (PUB/'周子靖_英文AcademicCV_v2.md').read_text(encoding='utf-8')
for old,new in [
('Computational Physics · Electromagnetic / Photonic Simulation · Physics-Driven Inverse Design','Computational Physics · Electromagnetic and Photonic Modelling · Scientific Computing'),
("**Harbin Institute of Technology, Second Bachelor's Program in Economics**  \nAug. 2026 – Present",'**Harbin Institute of Technology, Department of Economics**  \nSecond bachelor’s degree programme, currently enrolled | Aug. 2026–Present'),
('### Collaborative Research — Numerical Analysis of 2D Dusty-Plasma Lattice Waves\n2025','### Collaborative Research — Numerical Analysis of 2D Dusty-Plasma Lattice Waves'),
('bidirectional sheet resistance','sheet-resistance parameters'),
('version control and research-project management','Version control for research projects'),
("Single-item People's Scholarship","People’s Scholarship (single-category award)")]:
    assert old in cv, old
    cv=cv.replace(old,new)
write(PUB/'周子靖_英文AcademicCV_v3.md',cv)
cvzh=(PUB/'周子靖_中文审查CV_v2.md').read_text(encoding='utf-8').split('\n---\n')[0]
for old,new in [
('计算物理 · 电磁/光子学仿真 · 物理驱动的逆向设计','计算物理 · 电磁与光子学建模 · 科学计算'),
('**哈尔滨工业大学，经济学第二学士学位项目**  \n2026年8月 – 至今','**哈尔滨工业大学经济系**  \n第二学士学位项目，目前在读｜2026年8月–至今'),
('### 合作研究——二维尘埃等离子体晶格波的数值分析\n2025','### 合作研究——二维尘埃等离子体晶格波的数值分析'),
('双向片阻','片阻参数'),('版本控制与科研项目管理','科研项目的版本控制')]:
    assert old in cvzh, old
    cvzh=cvzh.replace(old,new)
# Bibliographic entries remain identical to the English source; translate their titles for Chinese review.
cvzh=cvzh.replace('“Design of Magnetic Nanoalloy/Graphene Composite Absorbing Materials for Wireless Communication.” *Flight Control & Detection*','“用于无线通信的磁纳米合金/石墨烯复合吸波材料设计。” *飞控与探测*')
cvzh=cvzh.replace('“Research of the Lattice Wave Properties of Two-Dimensional Dusty Plasma.” *Scientia Sinica Physica, Mechanica & Astronomica*','“二维尘埃等离子体晶格波特性研究。” *中国科学：物理学 力学 天文学*')
write(PUB/'周子靖_中文审查CV_v3.md',cvzh+'\n\n---\n\n中文审查镜像，不外发。逐项对应 [英文CV v3](周子靖_英文AcademicCV_v3.md)。论文题名与期刊名使用对应中文名称，作者顺序、年份、卷期、页码和 DOI 不变。')

subject='Fall 2027 PhD inquiry — Zijing Zhou, HIT Applied Physics'
for school,name,email,en,zh in [('HKUST_GZ','许泽锋','zefengxu@hkust-gz.edu.cn',xu,xuzh),('CUHK_Shenzhen','龚世华','gongshihua@cuhk.edu.cn',gong,gongzh)]:
    pack=BASE/school/'联系包'/name
    write(pack/'当前材料'/f'第一封套磁邮件_{name}_v3_READY_REVIEW.md',f'# {name}首封联系 v3\n\n2026-09-29｜READY_REVIEW / NOT SENT｜等待用户终读，未获发送批准\n\n收件人：{email}\n\n## Subject\n\n{subject}\n\n## Email\n\n{en}\n\n## 内部说明\n\n中文仅供审阅；英文为外发源。附件以本目录说明及哈希清单为准。本人逐封批准后手动发送；不得代发或创建 Gmail 草稿。')
    write(pack/'当前材料'/'邮件正文_v3.txt',en)
    write(pack/'中文审查镜像'/f'第一封套磁邮件_{name}_v3_中文审查.md',f'# {name}首封邮件 v3｜中文审查镜像\n\nREVIEW MIRROR / NOT FOR SENDING\n\n对应英文：[邮件 v3](../当前材料/第一封套磁邮件_{name}_v3_READY_REVIEW.md)\n\n收件人：{email}\n\n主题中文释义：2027年秋季博士申请咨询——周子靖，哈工大应用物理学\n\n---\n\n{zh}')
gpack=BASE/'CUHK_Shenzhen/联系包/龚世华'
write(gpack/'当前材料/Short_Research_Statement_龚世华_v1.md',rs)
write(gpack/'中文审查镜像/简短研究陈述_龚世华_v1_中文审查.md',rszh+'\n\n---\n\n中文审查镜像，不外发。对应 [英文研究陈述 v1](../当前材料/Short_Research_Statement_龚世华_v1.md)。')

def inline(s):
    s=html.escape(s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'\*(.+?)\*',r'<i>\1</i>',s)
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',s)
    return s
def mdhtml(md):
    out=[]; para=[]; ul=False
    def flush():
        if para: out.append('<p>'+ '<br>'.join(inline(x.strip()) for x in para)+'</p>');para.clear()
    for line in md.splitlines()+['']:
        if line.startswith('- '):
            flush()
            if not ul: out.append('<ul>');ul=True
            out.append('<li>'+inline(line[2:])+'</li>');continue
        if ul: out.append('</ul>');ul=False
        if not line.strip(): flush()
        elif line.startswith('#'):
            flush(); level=len(line)-len(line.lstrip('#'));out.append(f'<h{level}>'+inline(line[level:].strip())+f'</h{level}>')
        elif line=='---': flush();out.append('<hr>')
        else: para.append(line)
    return ''.join(out)

def single_pdf(path, md, css, rect):
    doc=fitz.open();pg=doc.new_page(width=595.28,height=841.89)
    spare,scale=pg.insert_htmlbox(rect,mdhtml(md),css=css,scale_low=1)
    assert spare>=0 and scale==1,(path,spare,scale)
    doc.set_metadata({'title':path.stem,'author':'Zijing Zhou'})
    doc.save(path,deflate=True,garbage=4);doc.close()
    return {'path':str(path.relative_to(ROOT)), 'sha256':sha(path),'pages':1,'spare_height':spare,'scale':scale}
cv_css='''body{font-family:Arial,sans-serif;font-size:9.6pt;line-height:1.18;color:#17202a;margin:0} h1{font-size:22pt;margin:0 0 5pt} h2{font-size:10.8pt;color:#183d57;border-bottom:0.5pt solid #aab8c3;margin:8pt 0 3pt} h3{font-size:9.8pt;margin:5pt 0 2pt} p{margin:2pt 0} ul{margin:3pt 0;padding-left:13pt} li{margin:2pt 0}'''
rs_css='''body{font-family:Arial,sans-serif;font-size:11pt;line-height:1.45;color:#17202a;margin:0} h1{font-size:17pt;margin:0 0 18pt} p{margin:0 0 13pt}'''
(PUB/'对外PDF').mkdir(exist_ok=True)
cvpdf=PUB/'对外PDF/Zijing_Zhou_Academic_CV_2027_PhD_v3.pdf'
rspdf=gpack/'当前材料/Zijing_Zhou_Short_Research_Statement_Gong_v1.pdf'
pdfmeta=[single_pdf(cvpdf,cv,cv_css,fitz.Rect(34,27,561,816)),single_pdf(rspdf,rs,rs_css,fitz.Rect(51,48,544,795))]

intro='''# C线 v3 中文人工审查包

2026-09-29｜英文包 READY_REVIEW / NOT SENT｜中文仅供本人审阅，不外发

本轮只落实 Chat 与 Work 共同确认的有限修订，不调整 PI 顺序。两封英文邮件与公共英文 CV 为 v3；龚世华研究陈述为 v1。

请按顺序审阅：许泽锋邮件 → 龚世华邮件 → 龚世华研究陈述 → 公共 CV。所有中文内容逐项对应英文版本；修改意见将先落到英文，再同步中文。

主要变化：邮件删除重复提问与晶格波旁支；龚世华只保留频域波研究连接，改用正向能力边界；CV 删除晶格波经历的未核年份、保留经济系在读身份，修正研究兴趣与三处英语表达；补齐实际 PDF 与版本清单。
'''
review=intro+'\n## 1. 许泽锋｜邮件 v3\n\n收件人：zefengxu@hkust-gz.edu.cn\n\n主题：2027年秋季博士申请咨询——周子靖，哈工大应用物理学\n\n'+xuzh+'\n\n## 2. 龚世华｜邮件 v3\n\n收件人：gongshihua@cuhk.edu.cn\n\n主题：2027年秋季博士申请咨询——周子靖，哈工大应用物理学\n\n'+gongzh+'\n\n## 3. 龚世华｜研究陈述 v1\n\n'+rszh.split('\n',1)[1]+'\n\n## 4. 公共 CV v3\n\n'+cvzh+'\n\n## 5. 附件与人工审阅边界\n\n许泽锋：英文 CV v3 PDF + 本科成绩单 PDF。龚世华：相同 CV 与成绩单 + 英文 short research statement v1 PDF。不附论文全文。\n\n第二学位专业正式名称、2027具体名额、本人录取资格和资金组合仍未确认；本包不把这些写成事实。英语成绩仍需按正式项目要求准备。\n\n同校两封首封至少间隔3个自然日，每3个自然日最多新增1封首封；旧未回复联系继续保留等待状态。下一封最早日期按上一封实际发送日加3个自然日滚动。用户逐封明确批准后本人手动发送，不代发、不创建草稿。\n\n[英文CV PDF](公共联系材料/对外PDF/Zijing_Zhou_Academic_CV_2027_PhD_v3.pdf) · [许泽锋发送入口](HKUST_GZ/联系包/许泽锋/当前材料/说明.md) · [龚世华发送入口](CUHK_Shenzhen/联系包/龚世华/当前材料/说明.md)\n'
write(BASE/'第一批中文审查包_v3_20260929.md',review)
cvparts=cvzh.split('## 论文发表')
pages=[
    '# 01 / 05 · 许泽锋邮件 v3\n\n中文审查镜像｜未发送｜对应英文邮件 v3\n\n**本轮修改：** 压缩经历、删除重复问题；保留已有流程上的使用与扩展。\n\n**主题：** 2027年秋季博士申请咨询——周子靖，哈工大应用物理学\n\n'+xuzh+'\n\n**拟附：** 英文 CV v3、本科成绩单。',
    '# 02 / 05 · 龚世华邮件 v3\n\n中文审查镜像｜未发送｜对应英文邮件 v3\n\n**本轮修改：** 只保留频域波连接；明确应用层经验与未来方法训练。\n\n**主题：** 2027年秋季博士申请咨询——周子靖，哈工大应用物理学\n\n'+gongzh+'\n\n**拟附：** 英文 CV v3、本科成绩单、英文研究陈述 v1。',
    '# 03 / 05 · 龚世华研究陈述 v1\n\n中文审查镜像｜对应英文 Short Research Statement v1\n\n'+rszh+'\n\n---\n\n**审阅提示（不在英文陈述中）：** 这里表达的是未来训练兴趣，不是已经掌握有限元或自行制定博士研究计划。具体课题留待与导师讨论。',
    '# 04 / 05 · 公共 CV v3（上）\n\n中文审查镜像｜对应英文 CV v3\n\n'+cvparts[0],
    '# 05 / 05 · 公共 CV v3（下）\n\n中文审查镜像｜对应英文 CV v3；论文使用对应中文题名\n\n## 论文发表'+cvparts[1]+'\n\n---\n\n**审阅状态：** 两份联系包均等待本人审查；尚未批准、未发送。第二学位在读身份保留，联系版不主动列均分或排名，正式成绩单照常附。中文包不外发。'
]
reviewpdf=BASE/'第一批中文审查包_v3_20260929.pdf'
doc=fitz.open()
zhcss='''body{font-family:sans-serif;font-size:10.5pt;line-height:1.5;color:#17202a;margin:0}h1{font-size:19pt;color:#193e58;margin:0 0 12pt}h2{font-size:12pt;margin:12pt 0 5pt}h3{font-size:11pt;margin:9pt 0 4pt}p{margin:0 0 10pt}ul{padding-left:16pt;margin:4pt 0}li{margin:5pt 0}'''
for i,md in enumerate(pages):
    pg=doc.new_page(width=595.28,height=841.89)
    spare,scale=pg.insert_htmlbox(fitz.Rect(43,38,552,798),mdhtml(md),css=zhcss,scale_low=1)
    assert spare>=0 and scale==1,('Chinese page',i+1,spare,scale)
doc.set_metadata({'title':'C线 v3 中文人工审查包','author':'Zijing Zhou'})
doc.save(reviewpdf,deflate=True,garbage=4);doc.close()
htmlpages=''.join('<section>'+mdhtml(p)+'</section>' for p in pages)
write(BASE/'第一批中文审查包_v3_20260929.html','<!doctype html><html lang="zh-CN"><meta charset="UTF-8"><title>C线 v3 中文审查包</title><style>body{background:#eef1f4;color:#17202a;font:16px/1.8 "Microsoft YaHei",sans-serif;margin:0}section{max-width:820px;margin:24px auto;padding:40px 48px;background:white;border:1px solid #dce2e7}h1{color:#193e58;font-size:26px}h2{font-size:21px}h3{font-size:18px}a{color:#1a5c8c}@media(max-width:650px){section{margin:0;padding:24px}}</style>'+htmlpages+'</html>')

transcript=ROOT/'A线_西湖博士/联系材料/田静逸/当前材料/首封附件/周子靖_本科成绩单.pdf'
counts={name:len(en.split()) for name,en in [('许泽锋',xu),('龚世华',gong)]}
assert 200<=counts['许泽锋']<=230,counts
meta={'base_commit':'31a4908134cb1c18f4bfb7b9d4225789c5ee81cb','email_word_counts_including_signature':counts,'statement_words':len(rs.split())-7,'pdfs':pdfmeta,'transcript':{'path':str(transcript.relative_to(ROOT)),'pages':len(fitz.open(transcript)),'sha256':sha(transcript)},'visual_review':'PENDING','state':'CANDIDATE / NOT SENT'}
write(REC/'生成检查.json',json.dumps(meta,ensure_ascii=False,indent=2))
previews=REC/'预览'
previews.mkdir(exist_ok=True)
for p in [cvpdf,rspdf,reviewpdf]:
    d=fitz.open(p)
    for i,pg in enumerate(d): pg.get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(previews/f'{p.stem}_{i+1}.png')
print(json.dumps(meta,ensure_ascii=False,indent=2))
