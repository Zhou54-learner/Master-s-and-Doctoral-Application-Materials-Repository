"""Migrate the remote Liu v1.1 package; never modify source presentations."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image
import json, hashlib

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
SRC=ROOT/'A线_西湖博士/面试与导师交流/刘癸庚/完整PPT_v1.1_20261006/刘癸庚交流_完整PPT_v1.1_20261006.pptx'
AUD=ROOT/'公共资料/事实核验/本科毕设紧急审计_20261008'
prs=Presentation(SRC)
original=list(prs.slides)
NAVY='142C46';TEAL='098C8B';GRAY='637184';ORANGE='A44B2E';LIGHT='F2F6F8'

def text(sl,x,y,w,h,value,size=22,color=NAVY,bold=False):
    sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=sh.text_frame;tf.word_wrap=True
    tf.margin_left=tf.margin_right=Inches(.02);tf.margin_top=tf.margin_bottom=Inches(.015)
    for i,line in enumerate(value.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line
        p.font.name='Microsoft YaHei';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=RGBColor.from_string(color)
        p.space_after=Pt(7)
    return sh

def replace(sl,n,value,size=None):
    sh=sl.shapes[n];tf=sh.text_frame
    p=tf.paragraphs[0]
    old=p.runs[0] if p.runs else None
    fs=size or (old.font.size.pt if old and old.font.size else 22)
    bold=old.font.bold if old else False
    col=NAVY
    if old:
        try: col=str(old.font.color.rgb)
        except Exception: pass
    tf.clear();tf.word_wrap=True
    for i,line in enumerate(value.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line
        p.font.name='Microsoft YaHei';p.font.size=Pt(fs);p.font.bold=bold;p.font.color.rgb=RGBColor.from_string(col)
        p.space_after=Pt(3)
    return sh

def box(sl,x,y,w,h,title,body,size=21):
    sh=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string(LIGHT);sh.line.fill.background()
    text(sl,x+.18,y+.16,w-.36,.45,title,22,TEAL,True)
    text(sl,x+.18,y+.82,w-.36,h-.9,body,size)

def picture(sl,path,x,y,w,h):
    with Image.open(path) as im: iw,ih=im.size
    z=min(w/iw,h/ih);ww=iw*z;hh=ih*z
    sl.shapes.add_picture(str(path),Inches(x+(w-ww)/2),Inches(y+(h-hh)/2),width=Inches(ww),height=Inches(hh))

def blank(title,section):
    sl=prs.slides.add_slide(prs.slide_layouts[6])
    text(sl,.55,.24,10,.28,section,12,TEAL)
    text(sl,.55,.65,12.2,.72,title,30,NAVY,True)
    sh=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(.55),Inches(7.04),Inches(12.25),Inches(.012))
    sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string('D8E1E8');sh.line.fill.background()
    return sl

def remove_content(sl,keep):
    for sh in list(sl.shapes)[keep:]:
        el=sh._element;el.getparent().remove(el)

# Cover and education retain the actual remote layout.
s=original[0]
replace(s,4,'田静逸老师课题组交流 · 2026-10-09',12)
replace(s,6,'从数值建模，走向对物理机制的理解',32)
replace(s,10,'科研经历与研究兴趣  |  田静逸老师交流',20)
s=original[1]
replace(s,2,'已有建模与数据处理入口，希望接受系统科研训练',29)
replace(s,3,'2022.08—2026.06  哈尔滨工业大学 · 应用物理学',20)
replace(s,6,'三维周期电阻膜结构',23)
replace(s,7,'CST建模、自动仿真与结构搜索',18)
replace(s,17,'录音、频谱分析与实验记录',18)
replace(s,22,'工具协作与个人写作：帮助整理问题，不替代物理判断',17)

# Geometry page: original embedded figure and masks stay in place.
s=original[2]
replace(s,1,'本科毕设：在周期电阻膜结构中搜索低反射响应',29)
replace(s,22,'电阻面提供耗散；结构改变场与散射\n具体机制仍需受控验证',18)

# Material / parameter page keeps original geometry and masks.
s=original[3]
replace(s,1,'把几何、PET支撑和电阻层分开理解',30)
replace(s,4,'最终数值参数；不是材料实测或制造验证',16)
replace(s,10,'h = 10.0731 mm：竖直高度',21)
replace(s,11,'p = 13.1409 mm：横向周期',21)
replace(s,12,'12×12图案：保留 / 去除电阻层',21)
replace(s,17,'PET厚度0.188 mm，白区没有挖去PET',17)
replace(s,18,'Ohmic Sheet：直接输入等效片阻',20)
replace(s,19,'Rs,x = 140.79；Rs,y = 35.461 Ω/□\n不同片阻不等于已证明两层功能分工',18)
s.shapes[19].height=Inches(.78)
text(s,.65,6.48,11.7,.34,'PET：εr输入3.1；tanδ输入0.01，但保存介质损耗为0，有效损耗设置待核。',15,ORANGE)

port=blank('一个Floquet端口，包含不同反射通道','本科毕设 · 边界与观测量')
box(port,.65,1.68,5.45,3.55,'本工程边界','XY：周期单元 → 无限阵列\nZmax：沿−z入射，沿+z反射\nZmin：electric → 理想PEC\nmode1：E沿y；mode2：E沿x',22)
box(port,6.36,1.68,6.31,3.55,'先分清下标，再谈功率','rᵢⱼ = SZmax(i),Zmax(j)\nj为入射mode，i为反射mode\nr₂₁：交叉反射，不是透射\n原GA只评价r₁₁',22)
text(port,.8,5.66,11.8,.55,'R₁ = |r₁₁|² + |r₂₁|²；PEC模型 T = 0；A = 1 − R − T',25,TEAL,True)
text(port,.8,6.4,11.75,.42,'适用前提：功率归一化；本频段两种零级偏振传播。交叉项需核对，不能先验设零。',16,GRAY)

flow=blank('一次候选评价：模型和指标怎样连起来','本科毕设 · Python—CST—GA')
box(flow,.65,1.65,3.88,1.92,'1  候选与筛选','p / h / 双Rs / 两张mask\n修复、缓存、几何检查',20)
box(flow,4.73,1.65,3.88,1.92,'2  建模与求解','写CST History命令\n频域求解 → 保存工程',20)
box(flow,8.81,1.65,3.88,1.92,'3  读取与评分','复数r11 → 反射dB\n连续带宽＋边缘/裕量奖惩',20)
box(flow,.65,3.85,5.8,2.13,'4  选择与下一代','轮盘赌 → 交叉/变异 → 修复筛选\n精英与种子保留；16个体 × 8轮',21)
box(flow,6.67,3.85,6.02,2.13,'分数不是吸收率','RL = 20 log10|r11|\n−10 dB：仅该通道功率为10%',21)
text(flow,.8,6.43,11.8,.4,'已有GA / CST示例；本人＋AI完成具体结构、材料、自由度与流程扩展。',18,TEAL,True)

s=original[4]
replace(s,1,'搜索空间逐步变化，不能用30 bit概括所有阶段',28)
replace(s,4,'先做尺寸与\n图案探索',22)
replace(s,5,'已有CST / GA示例\n本人＋AI适配',18)
replace(s,6,'薄实体膜\n→ Ohmic Sheet\n随后细化图案',21)
replace(s,7,'保留较好结构作为种子，再开放局部自由度',21)
replace(s,8,'6×6：30 bit  |  9×9 fixed_ph：50 bit',18)
s.shapes[8].height=Inches(.4)
replace(s,23,'后期开放\nX/Y独立片阻',23)
s.shapes[23].height=Inches(.95)
replace(s,24,'最终：四连续量＋两张mask',14)
replace(s,29,'半约束多模板：\n保留Y骨架\n允许局部变化',19)
s.shapes[29].height=Inches(1.13)
replace(s,32,'最终获选mask与输入种子相同；不把13.12→13.20 GHz说成新拓扑发现。',15)

# Replace old single-curve conclusion with recovered two-project evidence.
s=original[5]
remove_content(s,4)
replace(s,1,'保存结果支持低反射，但可靠性仍需单独验证',29)
picture(s,AUD/'两工程同偏振对照.png',.58,1.5,8.15,4.65)
box(s,9.0,1.7,3.7,1.7,'GA保存结果','4.80–18.00 GHz\n跨度13.20 GHz',19)
box(s,9.0,3.52,3.7,1.7,'后期自适应结果','5.20–17.68 GHz\n跨度12.48 GHz',19)
text(s,.7,6.25,12,.55,'指定同模反射 ≤ −10 dB；两曲线不能混用，18 GHz只是扫描上限。',19,ORANGE,True)
text(s,9.06,5.53,3.56,1.08,'已核离散功率一致性\n未完成严格收敛与实测\n不具偏振鲁棒性',16,GRAY)

s=original[6]
replace(s,1,'团队研究：在粒子轨迹中理解不同振动响应',29)
replace(s,10,'论文解释为分量相位延迟；我的贡献主要在数据与图件',14)
s=original[7]
replace(s,10,'历史录音与频谱分析\n记录不同音调，再比较几何条件',18)
s.shapes[10].height=Inches(.71)
replace(s,12,'定性观察与验证边界',14)
s.shapes[12].height=Inches(.28)
replace(s,14,'图中横轴是记录序号，不是流量',17)
replace(s,15,'尚无定量流量控制与机制验证',18)
replace(s,16,'老师提出问题；本人推进分析，组员协助拍摄',13)
s=original[8]
replace(s,2,'AI帮助实现流程，研究判断仍要由自己负责',29)
replace(s,7,'AI协助实现与迭代',17)
replace(s,9,'分工、证据与人工核对',17)
s=original[9]
replace(s,2,'个人学习工具：减少整理负担，保留理解与判断',28)
replace(s,5,'希望组织哪些信息？',19)
replace(s,7,'阶段 · 进度 · 可用时间',15)
replace(s,9,'知识关系 · 当前学习位置',16)
replace(s,10,'个人探索的真实页面；不作为学习效果已验证或成熟AI研究成果',14)
s=original[13]
replace(s,1,'Why PhD：把“能做出结果”推进到“能判断结果”',29)
replace(s,4,'本科的建模、数据处理和个人探索，\n让我确认自己愿意持续追问一个问题。',25)
replace(s,5,'也让我看到：流程可以跑通，\n物理机制和结果可信度却未必已经理解。',27)
replace(s,6,'我希望系统补足理论、数值验证与实验训练，\n学会提出假设、检查证据、识别错误。',25)
replace(s,7,'在一个方向持续积累，\n逐步对自己的研究判断和结论负责。',25)
s.shapes[5].top=Inches(3.32);s.shapes[5].height=Inches(1.13)
s.shapes[6].top=Inches(4.7);s.shapes[6].height=Inches(1.03)
s.shapes[7].top=Inches(5.98);s.shapes[7].height=Inches(1.0)
s=original[14]
remove_content(s,4)
replace(s,1,'Why Tian：从结构—响应，继续追问共振与光场',29)
s.shapes[1].width=Inches(12.2);s.shapes[1].height=Inches(.72)
box(s,.72,1.68,5.79,3.98,'已有入口','周期电磁结构与数值建模\n参数搜索和数据分析\n开始重视通道与验证边界\n\n希望理解响应背后的物理',22)
box(s,6.75,1.68,5.85,3.98,'希望在田老师组继续学习','全介质纳米天线\n单粒子散射 → 阵列响应\n近场、远场与共振的联系\n从静态结构到主动调控',22)
text(s,.8,6.08,11.85,.65,'这是需要重新接受训练的迁移：材料色散、尺度、机制与实验条件都不同。',21,TEAL,True)

future=blank('Future：先建立可靠基线，再形成具体研究问题','下一阶段 · 拟议学习路径')
box(future,.7,1.75,3.81,3.72,'1–3个月：基础与基准','电磁 / 光学基础\n边界、偏振、色散与散射\n解析例子 ↔ 数值复现\n能解释假设与误差',21)
box(future,4.76,1.75,3.81,3.72,'3–6个月：一个闭环','在指导下复现简单体系\n学习加工或光谱测量\n仿真与测量相互核对\n记录与数据可追溯',21)
box(future,8.82,1.75,3.81,3.72,'6–12个月：一个小问题','控制变量与敏感性\n检验一个具体假设\n再讨论优化与机制\n与导师共同收束课题',21)
text(future,.83,5.91,11.7,.65,'不预设自己已经熟悉纳米光子学；以可复现、可解释、可检验为起点。',22,TEAL,True)
text(future,.83,6.62,11.7,.3,'时间与课题服从导师安排。谢谢老师，期待您的建议。',17,GRAY)

order=[original[0],original[1],original[2],original[3],port,flow,original[4],original[5],original[6],original[7],original[8],original[9],original[13],original[14],future]
ids=[(prs.part.related_slide(x.rId),x) for x in list(prs.slides._sldIdLst)]
for sl,el in ids:
    if sl not in order:
        prs.part.drop_rel(el.rId)
for el in list(prs.slides._sldIdLst): prs.slides._sldIdLst.remove(el)
for sl in order: prs.slides._sldIdLst.append(next(el for ss,el in ids if ss==sl))

# Single source for full spoken script and speaker notes.
data=[
('从数值建模，走向对物理机制的理解','建立真实起点，说明汇报重点。',
'田老师您好，我是周子靖，本科在哈尔滨工业大学学习应用物理。感谢您给我这次交流机会。今天我想重点介绍本科毕设里实际做过的建模、自动仿真和搜索，再简要介绍团队科研和个人探索。最后想说说，我为什么希望从工程优化继续走向更深入的物理理解。',
'主述建议10–12分钟，可随追问停页；会议安排两小时不代表连续报告两小时。',
'不预先道歉，不把自己包装成已有纳米光子学研究经验。',
'你的主要研究训练是什么？现在是什么学籍状态？','个人事实源；本次会议确认'),
('已有建模与数据处理入口，希望接受系统科研训练','在一页建立经历地图和本人定位。',
'我在2022年到2026年就读于哈工大应用物理学专业。主要训练来自本科毕设中的电磁结构建模和Python搜索，也参与过尘埃等离子体的数据处理。更早做过波纹管录音与频谱分析。后来我也尝试用AI做学习工具。这几段经历让我愿意把问题做成可操作的流程，但理论和实验判断还需要系统训练。',
'若问当前身份：2026年8月注册哈工大经济系第二学士项目，当前在读；正式专业名称不凭部门名扩写。课程包括电磁学、光学、傅里叶光学和计算物理，课程名称不代表已熟练掌握。',
'不主动讲成绩、排名或跨路线申请细节；不把项目数量当科研深度。',
'你独立做了哪一部分？课程基础如何？','个人事实源；刘v1.1原S1；当前学籍记录'),
('本科毕设：在周期电阻膜结构中搜索低反射响应','指着结构说清研究对象、目标和变量。',
'这是我本科毕设的周期单元。两块PET竖直正交，表面附着图案化电阻层，底部设理想PEC。目标是在2到18 GHz内，让指定偏振有更宽的低反射区间。右侧黑色表示保留电阻层，白色只去掉电阻层，没有把PET挖空。老师给课题、师兄建议立体方向，我在这个基础上与AI协作推进具体十字结构和建模。',
'p是横向周期，h是高度；X/Y是膜面几何名称。电阻面可以耗散，但这张结构图本身不证明宽带机制。',
'不说结构学术首创，不说两张膜对两个偏振天然等效，不把研究目标直接当已证吸收性能。',
'为什么这种结构？PEC、PET各做什么？初始方向是谁提出？','T第3/6章；C几何函数；U02'),
('把几何、PET支撑和电阻层分开理解','解释参数是模型输入，区分两种膜表示。',
'最终周期约13.14毫米、高度约10.07毫米，两块PET厚度都是0.188毫米。电阻层后来采用Ohmic Sheet，直接输入片阻；两面约140.79和35.461欧姆每方。早期用过等效薄实体，再转为片阻面。需要说明，PET脚本虽输入损耗角正切0.01，但保存结果中的介质损耗为零，有效损耗设置还要核实。我不会把这个输入当成已验证的PET耗散。',
'薄体绘制厚度0.02 mm，用σ=1/(Rs·t)换算，t取米；不是实际ITO纳米厚度。论文选择sheet的理由是片阻表征直接、避免假设厚度并便于像素迭代。',
'不把模型对比图说成严格单变量验证，不主张最终连续Rs可采购，不报每层损耗比例。',
'Ohmic Sheet是什么？PET是否耗散？为什么两片片阻不同？','C349–363及最终材料配置；G/H；U02/U03'),
('一个Floquet端口，包含不同反射通道','把今天最危险的端口、mode和功率关系讲清。',
'X和Y方向的周期边界代表无限阵列，上方Floquet端口从负z方向照入，底部PEC阻断透射。本工程端口场核对后，mode1电场沿y，mode2沿x。我用r的两个下标分别表示出射和入射mode。它们都在同一个上端口，所以r21是交叉偏振反射，不是透射。原GA只读r11；要谈总反射，还必须加上交叉通道的功率。',
'功率归一化后R1=|r11|²+|r21|²；本频段空气中只有两个零级传播偏振。首个非零级截止约22.81 GHz，倏逝模式仍可能影响数值精度。mode编号需按具体工程看场。',
'不说PEC使单个|r11|²自动等于总R；不把端口mode当结构共振模式。',
'S11是什么？mode1/2如何确认？有无交叉偏振？','F端口专项；C4711；native四项反射'),
('一次候选评价：模型和指标怎样连起来','给出从候选到下一代的可复述闭环。',
'每个候选包含尺寸、片阻和两张图案。Python先做修复、缓存检查和几何筛选，再写入CST的材料、结构与边界，调用频域求解并保存工程。之后通过results接口读复数r11，转成反射dB，找连续通过区间并算适应度。分数回到GA做选择、交叉和变异。参考里本来有GA与CST框架；我与AI做的是针对这项结构的适配和扩展。',
'实际函数：evaluate_individual→run_cst→configure_rs/decode→run_cst_for_params→run_solver→extract_metrics；select_parent/crossover/mutate/make_new_population。16×8是评价预算，128记录中113次新求解、15次缓存。',
'不说从零开发GA；不把所有设计量说成都在CST参数表；不背长权重表。',
'读哪个结果？fitness偏好什么？你具体改了什么？','C1747、4619–4803、5134–5464；D；U'),
('搜索空间逐步变化，不能用30 bit概括所有阶段','用原演化图说明编码与材料自由度分阶段。',
'早期6乘6阶段，用p和h各6位，加上两张3乘3种子各9位，总共30位，再镜像成6乘6。到9乘9，固定尺寸版本用两张5乘5种子，共50位。最终12乘12已经改成四个连续参数和两张mask的字典，并有骨架保护与修复。片阻也是后期才明确开放成两个连续量。因此不能拿早期30位解释最后的全部优化。',
'薄实体→Ohmic6×6→9×9→12×12模板/hybrid固定Rs→hf双Rs→multitemplate。最终保护Y骨架但不整张固定；获选mask与种子相同，末段0.08 GHz不构成新拓扑或显著提升证明。',
'不说每次加细必然提升；不把6×6像素与CST网格混淆，不把不可达桥接算子说成用过。',
'为什么30位？最后还是二进制吗？模板限制什么？','E阶段源码；C最后定义；U02/U03'),
('保存结果支持低反射，但可靠性仍需单独验证','明确报告两个结果和验证层次。',
'绿色是GA保存结果：指定同模反射不高于负10 dB的区间为4.80到18.00，端点跨度13.20 GHz。橙色是后来开启自适应的工程，区间变成5.20到17.68，跨度12.48。两套结果必须分别报告。近期回查已经恢复反射矩阵和离散功率，支持保存模型内的能量核对；但另一偏振接近全反射，材料和独立收敛仍待核，也没有吸波实测。',
'82.5%=13.20/16，是频带覆盖。局部场/损耗图只提供机制线索，未做模态/多极分解。后期有三轮内部网格自适应记录，不能给GA旧曲线背书。',
'不把13.20说成实测或严格收敛吸收带宽，不说交叉项先验为零，不把多个谷等同多模证明。',
'结果可靠吗？有没有收敛、实验、场图？为什么宽带？','G/H保存曲线；D；2026-10-08恢复/复算，非新仿真'),
('团队研究：在粒子轨迹中理解不同振动响应','讲清合作对象与本人贡献。',
'另一段团队科研是二维尘埃等离子体晶格波。这里的偏振指颗粒在平面内的振动方向，不是电磁偏振。我参与MATLAB相关数据处理、二维轨迹可视化和多位置图组整理。图中一些位置接近线状，另一些呈椭圆。论文讨论了不同振动分量的相位延迟，但核心模拟算法、全部运行和完整物理解释不能都归到我个人。',
'历史41位置轨迹图与论文Fig.12对应；可以用x/y分量相位关系解释轨迹概念，但不据署名认领全部研究。',
'不讲无法稳定解释的完整模拟方程或算法细节，不把2025模块倒写为2024贡献。',
'偏振是什么？MATLAB具体做什么？你做过核心模拟吗？','公共尘埃等离子体考古2026-10-05；刘原S6图'),
('同一根波纹管，为什么会出现几个稳定音调？','保留真实实验记录与数据分析训练。',
'更早我做过一个波纹管乐音小项目。老师提出最初问题，我推进录音和MATLAB频谱分析，提取主要频率，再比较不同几何条件。我们记录到同一根管可以出现不同的稳定音调。这里的历史图横轴是记录序号，不是标定的流量。我把它当成从现象走向可记录问题的训练，并没有完成定量气动声学机制验证。',
'演示拍摄有组员协助；近期对历史数据的统计属于2026复盘，不能说成当年已做完整统计。',
'不把音阶拼接当连续扫流，不宣称有精确流速控制或已验证无量纲机制。',
'控制了什么变量？怎样取频率？为什么不是流量横轴？','乐音2026-10-05/06事实核验；刘原S7历史图'),
('AI帮助实现流程，研究判断仍要由自己负责','把AI探索收束到工具使用与证据责任。',
'后来我也尝试用AI做物理学习工具。最初是把一个想法做成可以运行的Demo，复杂之后开始整理分工、流程和检查证据。AI确实降低了实现门槛，但这个经历没有让我觉得理解可以外包。相反，毕设里指标和通道的问题提醒我，工具能给出代码和图，是否回答了正确问题，仍然要由自己判断。',
'展示的是既有真实界面和协作方法探索。本人提出需求、组织迭代、检查结果；AI协作实现。',
'不说成熟ML研究、训练了模型、独立从零生产级开发或有已验证教学收益。',
'AI写了多少？怎样验证它？和申请物理有什么关系？','公共个人探索2026-10-06；刘原S8截图'),
('个人学习工具：减少整理负担，保留理解与判断','保留个人探索主线但控制篇幅。',
'我也尝试把学习进度、知识关系和后续任务组织成个人工具。希望减少的是整理、归档这类负担，真正推导、作答和判断仍需要我自己完成。写作和个人页面也是类似尝试，帮助我把模糊想法说清楚。它们不是科研成果，但让我更重视一件事：做出一个东西之后，要回头检查自己究竟理解了多少。',
'若老师感兴趣再简述个人写作与网页；本页是方法探索，不是常驻自主智能体或有效性研究。',
'不展开宏大AI外骨骼叙事，不暗示系统功能全部成熟，不让此页盖过毕设。',
'为什么保留自己推导？工具效果验证过吗？','公共个人探索事实；刘原S9A真实截图'),
('Why PhD：把“能做出结果”推进到“能判断结果”','自然说明长期训练动机。',
'这些经历让我确认，我愿意从一个没完全想清楚的问题出发，把它逐步变成可以研究的事情。但我也越来越清楚，流程跑通和理论理解是两回事。像毕设，我能推进自动搜索，却没有同时把通道、机制和可靠性理解到位。所以我希望在一个方向持续接受理论、数值和实验训练，学会提出假设、检查证据，逐步对自己的结论负责。',
'强调好奇心与具体薄弱环节；不是否定已有训练，而是形成下一阶段目标。',
'不说博士保证掌握AI永远不会的能力，也不把读博只讲成学更多工具。',
'为什么一定读博？最想补什么？能长期聚焦吗？','刘完整讲稿v5的动机主线；本次收束'),
('Why Tian：从结构—响应，继续追问共振与光场','建立具体但不夸大的研究连接。',
'看田老师组的研究介绍时，我比较关注全介质纳米天线这条线：从单粒子散射到阵列响应，再到主动调控。我想进一步理解几何和材料怎样影响共振，以及近场与远场之间的联系。我已有的是波动问题中的数值建模入口，但尺度、材料模型、具体机制和实验条件都不同。我把博士阶段看成需要重新接受系统训练的迁移，而不是把本科模型简单缩小。',
'2025高Q手性Janus论文可作摘要层兴趣入口，尚不说精读/复现；官网还涵盖有源微纳光学，不把全组压成单一主题。',
'不硬贴术语，不说微波与纳米光学完全相同，不许诺已有微纳加工/测量能力。',
'为什么田老师？能迁移什么？high-Q和宽带吸收有什么不同？','OMAL Research及2025 Janus摘要；2026-10-08核读'),
('Future：先建立可靠基线，再形成具体研究问题','提供现实的训练路径与开放结尾。',
'如果有机会入组，我希望先补电磁和光学基础，用简单可解析模型检查自己的数值结果。再在组里指导下复现一个小体系，学习相关加工或光谱测量，把仿真和测量连起来。之后才围绕一个明确问题做控制变量和机制分析。这个时间表是初步想法，具体服从老师和课题安排。我想先把每一步做得可靠，再逐步形成研究方向。谢谢老师。',
'反问：对以数值建模为起点、需要补实验训练的学生，组里通常选择什么入门问题？可将1–3、3–6、6–12个月作为讨论框架。',
'不承诺论文数量，不预设设备准入、招生承诺或已定博士题目。',
'怎么补光学基础？愿意做实验吗？前半年怎样验收学习？','本轮未来计划，非已完成能力')
]
assert len(data)==len(order)==15
notes=[];mapping=[]
for i,(sl,d) in enumerate(zip(order,data),1):
    title,goal,speech,expand,avoid,questions,source=d
    # Remove original numbering only, retain source footers.
    for sh in list(sl.shapes):
        if sh.has_text_frame and sh.text.strip() in ['S0','S1','S2','S3','S4','S5','S6','S7','S8','S9','S10','S11','S12','S13']:
            el=sh._element;el.getparent().remove(el)
    text(sl,12.12,7.1,.68,.29,f'{i:02d}/15',10,GRAY)
    note=f'第{i:02d}页｜{title}\n\n【这一页的目标】\n{goal}\n\n【推荐口述】\n{speech}\n\n【可以展开讲什么】\n{expand}\n\n【不要主动讲什么】\n{avoid}\n\n【最可能的追问】\n{questions}\n\n【证据/来源】\n{source}'
    sl.notes_slide.notes_text_frame.text=note
    notes.append(f'## 第{i:02d}页｜{title}\n\n**这一页的目标**：{goal}\n\n### 推荐口述\n\n{speech}\n\n**可以展开讲什么**：{expand}\n\n**不要主动讲什么**：{avoid}\n\n**最可能的追问**：{questions}\n\n**证据/来源**：{source}\n')
    mapping.append({'page':i,'title':title,'source_liu_page':original.index(sl)+1 if sl in original else None,'notes':note,'evidence':source})
    # Visible sources for the technical and PI slides.
    if 3<=i<=8:
        text(sl,.58,7.13,11.35,.23,'证据：本科论文/原始代码；2026-10-06端口核验、2026-10-08历史结果恢复（详见配套复习稿）',9,GRAY)
    if i==14:
        text(sl,.58,7.13,11.35,.23,'来源：OMAL · Research（omal.lab.westlake.edu.cn/Research.htm），2026-10-08核读',9,GRAY)

prs.core_properties.title='周子靖｜田静逸老师交流｜2026-10-09'
prs.core_properties.subject='从数值建模到物理理解：科研经历与研究兴趣'
prs.core_properties.author='Zijing Zhou'
prs.core_properties.comments='Derived from remote Liu v1.1; evidence-corrected Tian final preparation.'
ppt=OUT/'田静逸_最终面试PPT_20261009.pptx'
prs.save(ppt)
(OUT/'田静逸_完整讲稿_最终版_20261009.md').write_text('# 田静逸完整讲稿｜最终版\n\n与15页最终PPT逐页对应；PPT speaker notes与以下五部分正文同源生成。主述建议10–12分钟，展开内容只在追问时使用，不要求把整份文档读完。先讲真实工作，再讲判断边界。\n\n技术来源见[详细整理](本科毕设_详细思路与技术细节整理_20261009.md)；方向来源与备用回答见[针对性问答](田静逸_针对性提问与参考回答_20261009.md)。\n\n'+'\n'.join(notes),encoding='utf-8')
(OUT/'页面与备注源.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
check=Presentation(ppt)
assert len(check.slides)==15
assert all(s.notes_slide.notes_text_frame.text==m['notes'] for s,m in zip(check.slides,mapping))
print('15 slides created; 15 speaker notes matched. Source SHA256:',hashlib.sha256(SRC.read_bytes()).hexdigest())
