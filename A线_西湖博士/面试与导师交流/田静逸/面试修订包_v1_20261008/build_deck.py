from pathlib import Path
import json,io,hashlib
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
AUD=ROOT/'公共资料/事实核验/本科毕设紧急审计_20261008'
SRC=ROOT/'A线_西湖博士/面试与导师交流/刘癸庚/完整PPT_v1.1_20261006/刘癸庚交流_完整PPT_v1.1_20261006.pptx'
ASSET=Path('E:/360MoveData/Users/zzj/OneDrive/桌面/毕业设计/结题/终稿/_ppt_assets_resistive_film')
(OUT/'assets').mkdir(exist_ok=True)
old=Presentation(SRC)
for no,tag in [(6,'晶格波'),(7,'乐音')]:
    pics=[s for s in old.slides[no].shapes if s.shape_type==13]
    if pics:
        pic=max(pics,key=lambda s:s.width*s.height)
        (OUT/'assets'/f'{tag}.{pic.image.ext}').write_bytes(pic.image.blob)

prs=Presentation();prs.slide_width=Inches(13.3333);prs.slide_height=Inches(7.5)
NAVY='142C46';TEAL='098C8B';GRAY='637184';BG='F2F6F8';ORANGE='A44B2E'
def text(sl,x,y,w,h,value,size=21,color=NAVY,bold=False,font='Microsoft YaHei'):
    sh=sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf=sh.text_frame;tf.word_wrap=True
    tf.margin_left=tf.margin_right=Inches(.025);tf.margin_top=tf.margin_bottom=Inches(.02)
    for i,line in enumerate(value.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name=font;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=RGBColor.from_string(color);p.space_after=Pt(7)
    return sh
def rect(sl,x,y,w,h,color=BG):
    sh=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string(color);sh.line.fill.background();return sh
def pic(sl,p,x,y,w,h):
    with Image.open(p) as im: iw,ih=im.size
    ratio=min(w/iw,h/ih);ww,hh=iw*ratio,ih*ratio
    return sl.shapes.add_picture(str(p), Inches(x+(w-ww)/2),Inches(y+(h-hh)/2),width=Inches(ww),height=Inches(hh))
notes=[];sources=[]
def slide(title,section,source,note):
    sl=prs.slides.add_slide(prs.slide_layouts[6]);n=len(prs.slides)
    rect(sl,.45,.45,.08,.31,TEAL);text(sl,.65,.39,11,.35,section,12,TEAL,True)
    text(sl,.62,.96,12.1,.75,title,29,NAVY,True)
    rect(sl,.65,6.99,12.0,.015,'D8E1E8')
    text(sl,.65,7.08,11.25,.24,source,9,GRAY)
    text(sl,12.0,7.06,.65,.29,f'{n:02d} / 12',10,GRAY)
    sl.notes_slide.notes_text_frame.text=note+'\n\n【证据】'+source
    notes.append(f'## 第{n}页｜{title}\n\n{note}\n\n证据：{source}\n')
    sources.append({'page':n,'title':title,'source':source})
    return sl
def panel(sl,x,y,w,h,title,body,size=20):
    rect(sl,x,y,w,h);text(sl,x+.18,y+.13,w-.36,.44,title,21,TEAL,True);text(sl,x+.18,y+.76,w-.36,h-.88,body,size)

s=slide('科研经历与研究兴趣','周子靖  /  Zijing Zhou','本科教育与身份：现行个人事实记录；会议：田静逸老师已确认邀请',
'田老师您好，我是周子靖，本科在哈尔滨工业大学学习应用物理。感谢您给我这次交流机会。今天我想用大约八到十分钟，重点介绍本科毕设中结构建模、自动仿真和参数搜索的实际过程，再简要介绍两项其他经历，以及希望进一步学习的方向。')
text(s,.75,2.13,11.8,1.3,'从周期电阻膜结构的仿真设计\n谈实际工作、验证边界与下一步问题',33,NAVY,True)
text(s,.8,4.18,10,.65,'哈尔滨工业大学 · 应用物理学本科',24)
text(s,.8,5.0,10,.55,'田静逸老师课题组交流  |  2026年10月9日',20,GRAY)
rect(s,.8,6.12,10.8,.07,TEAL)

s=slide('以物理学习为基础，逐步接触建模与数据分析','教育经历与研究轨迹','教育事实源；刘老师版本第2、7、8页；各项目专题核验',
'我在2022年8月至2026年6月就读于哈工大应用物理学专业，本科课程包括电磁学、光学、傅里叶光学和计算物理。我的主要研究训练来自本科毕设中的CST仿真和Python搜索流程；合作科研中参与了MATLAB数据处理；更早也做过波纹管录音和频谱分析。今天以毕设为主，重点说明每一步实际操作和目前结果的边界。\n\n【追问备用】当前另有哈工大经济系第二学士项目在读（2026年8月注册，本人确认）；如问当前学籍如实说明。课程名称不表示已熟练掌握全部理论。')
text(s,.78,1.93,11.7,.58,'2022.08—2026.06  哈尔滨工业大学 · 物理学院 · 应用物理学',23,NAVY,True)
panel(s,.78,2.91,3.78,2.68,'本科毕业设计','周期电阻膜结构\nCST建模与仿真\nPython参数搜索',21)
panel(s,4.77,2.91,3.78,2.68,'合作研究','二维尘埃等离子体\nMATLAB数据处理\n粒子轨迹可视化',21)
panel(s,8.76,2.91,3.78,2.68,'较早的个人探索','波纹管乐音\n录音与频谱分析\n不同几何条件比较',21)
text(s,.82,6.12,11.6,.48,'本次主线：研究问题 → 模型设置 → 仿真数据 → 搜索实现 → 结果核验',20,TEAL,True)

s=slide('目标是在2–18 GHz内拓宽指定偏振的低反射频段','本科毕设｜结构与设计目标','T：图3-2/3-3、第5章；H：History块3/4/352；D：最终图案与参数',
'这是本科毕设的周期单元：两块PET竖直正交，电阻层附在表面，底部用理想PEC边界。目标是在2到18 GHz范围内拓宽低反射频段。右边两张图是电阻层的保留区域，白色区域只去掉电阻层，PET没有跟着挖空。设计中先探索尺寸，随后加入图案和更细分辨率，再开放两片的片阻。这个次序有历史文件支持，但不是每一步都有严格单变量对照。具体十字构思由我在师兄立体结构建议基础上与AI协作推进，不主张结构学术首创。')
pic(s,ASSET/'fig6_2_final_3d_model.png',.72,1.93,6.28,3.73)
pic(s,AUD/'最终图案.png',7.18,1.94,5.3,2.9)
text(s,7.3,4.91,5.05,1.04,'p = 13.1409 mm   h = 10.0731 mm\n黑：保留电阻层；白：去除电阻层',18)
text(s,.8,5.91,11.8,.68,'尺寸探索 → 条带 / 像素图案 → 6×6 / 9×9 / 12×12 → 双片阻',22,TEAL,True)
text(s,.8,6.55,11.8,.29,'图案分辨率是设计变量；CST四面体网格是另一层数值离散。',14,GRAY)

s=slide('PET支撑与电阻层需要分开建模','本科毕设｜材料参数','C：58–66、349–363、4669–4679；H：History块1/3–6；N：介质损耗结果',
'我把支撑材料和耗散电阻层分别定义。两块PET厚度都是0.188毫米，脚本输入相对介电常数3.1、相对磁导率1和损耗角正切0.01。需要特别说明，这些是输入值，原始物性来源尚未核清，而且保存结果中的介质损耗为零，损耗是否真正启用仍待核。电阻层则用Ohmic Sheet直接输入面阻抗，最终双片阻约140.79和35.461欧姆每方。这些是连续搜索得到的模型参数，不代表已采购或测量的材料。')
panel(s,.75,1.95,5.8,3.56,'PET：几何支撑与介电环境','厚度：0.188 mm\n脚本输入：εr = 3.1，μr = 1\nσ = 0；tanδ输入值 = 0.01\n物性来源、损耗启用仍待核',21)
panel(s,6.78,1.95,5.8,3.56,'电阻层：二维Ohmic Sheet','Rs,x = 140.79 Ω/□\nRs,y = 35.461 Ω/□\n面阻抗虚部输入为0\n连续参数；未验证可采购性',21)
rect(s,.75,5.77,11.83,.81,'FBF0E9');text(s,.95,5.9,11.43,.56,'保存的介质损耗为0：不能把输入tanδ当成已验证的PET耗散。',20,ORANGE,True)

s=slide('周期边界定义阵列，Floquet模式定义入射与反射','本科毕设｜边界、激励与观测量','C：269–326、738–819；F：端口场与模式映射；N：四项反射矩阵',
'X和Y方向用unit cell表示无限周期，Zmin最终设electric作为PEC，Zmax为开放Floquet端口，入射沿负z。频域求解使用四面体网格。本工程模式场核对显示，mode 1电场沿y，mode 2沿x；两个模式分别激励。为了避免S21记法造成混淆，我这里写成反射矩阵r：右边下标是入射，左边是反射，全部属于同一个上方端口。因此r21是交叉偏振反射，并不是透射。原来的优化仅取r11。')
panel(s,.75,1.93,5.27,3.87,'最终工程设置','XY：unit cell无限周期\nZmin：PEC理想电边界\nZmax：Floquet开放端口\nθ = φ = 0；入射沿 −z\n频域求解 · 二阶四面体',21)
panel(s,6.26,1.93,6.32,3.87,'两个偏振，四项反射','mode 1：E沿y；mode 2：E沿x\nrᵢⱼ = SZmax(i),Zmax(j)\nj：入射mode；i：反射mode\nr₂₁是交叉反射，不是透射\n原优化指标只读取r₁₁',21)
text(s,.84,6.14,11.7,.47,'两mode分别求响应 ≠ 已优化双偏振；有限样品、斜入射另需验证。',20,TEAL,True)

s=slide('每个候选都经过建模、求解、读数和记录','本科毕设｜实际自动化过程','C：1747–1814、4669–4693、5134–5172；D：individual_trace；U：本人确认',
'具体到一次求解，Python先接收候选的尺寸、片阻和图案，检查是否已有缓存及是否通过几何筛选。随后新建CST，把材料和结构展开成History命令，设置边界并调用频域求解器。完成后保存临时工程，读取复数S参数，转换成dB并计算适应度。参数、分数与工程路径进入日志，当前最好的工程和曲线另外导出。师兄参考本来就有CST调用和GA框架；我与AI协作做的是针对PET电阻膜的建模和流程扩展，包括按History排查材料命令错误。')
items=[('1  候选与检查','p、h、双Rs、两张mask\n缓存检查＋硬筛选'),('2  Python → CST','写材料、几何与最终边界\n参数数值写入History'),('3  求解与保存','调用频域求解器\n保存独立临时工程'),('4  读数与后处理','复数r11 → dB\n连续区间 → fitness'),('5  留档与更新','参数 / 分数 / 路径入日志\n保留最好个体，更新种群')]
for k,(t,b) in enumerate(items):
    x=.75+(k%3)*4.01;y=1.94+(k//3)*2.14
    panel(s,x,y,3.8,1.91,t,b,19)
panel(s,8.77,4.08,3.8,1.91,'实际记录','128条评估\n113次求解＋15次缓存',19)
text(s,.84,6.32,11.65,.45,'继承：CST / GA示例；本人＋AI：具体结构、材料建模、自由度与筛选更新。',18,TEAL,True)

s=slide('最终GA围绕历史种子搜索，固定预算迭代','本科毕设｜算法的实际实现','C：4537–4568、4958–4990、5187–5464；D：8轮日志；N：mask核对',
'最后生效版本用字典保存四个连续参数和两张12乘12图案，不是文件开头仍保留的旧36位编码。初始化包含历史最好结构和参考参数。选择用非负分数轮盘赌；交叉交换局部图案块，连续参数用均值加扰动；变异包括参数高斯扰动和局部图案修改，之后做修复与筛选。每代保留精英并注入新候选，固定16个体、8轮。这不是达到全局最优的证明。最终获选图案与历史种子相同，因此末段改进不能解释为新拓扑发现。\n\n【追问备用】p_m=max(0.07,0.23−0.014·it)。桥接/开槽函数虽定义，但最终调度累计阈值超过1而不可达，不列为实际使用。')
rect(s,.75,1.94,11.83,.82);text(s,.95,2.1,11.43,.5,'个体 = {p, h, Rs,x, Rs,y, mask_x[12×12], mask_y[12×12]}',23,TEAL,True)
panel(s,.75,3.0,3.78,2.58,'初始化与选择','历史种子＋参考参数\n模板 / 局部扰动补充\n非负权重轮盘赌',20)
panel(s,4.77,3.0,3.78,2.58,'交叉与变异','二维块 / 软区域交叉\n连续参数均值＋扰动\n局部像素 / 块 / 边缘修改',20)
panel(s,8.79,3.0,3.78,2.58,'约束与终止','修复、密度 / 连通分量筛选\n保留精英与历史种子\n16个体 × 8轮预算',19)
text(s,.85,6.06,11.55,.56,'末段获选mask与种子相同；不声称全局最优、全图案自由搜索或独立开发GA。',19,ORANGE,True)

s=slide('从复数反射到带宽，再到启发式适应度','本科毕设｜原始数据如何变成指标','C：4711–4803；D：best_s11 / best_result；N：score复算',
'这里是原代码读取数据后转成dB的真实片段。目标路径是SZmax(1),Zmax(1)，计算的是20倍以10为底的幅值对数。随后找不高于负10 dB的最长连续采样段，用高低端点相减。82.5%是这一宽度除以16 GHz。适应度还叠加了频带边缘、目标宽度和裕量等奖惩，所以分数不是吸收率，也不只是带宽。权重属于启发式配置，没有系统消融。\n\n【追问备用】原f_low=4.800000000000001没有触发≤4.80的7分奖励；按原浮点值复算为89.63868，不先舍入。')
code=(Path('F:/biyesheji/code/ohmic_sheet_12x12_multitemplate_topology_ga_code.py').read_text(encoding='utf-8-sig').splitlines())
rect(s,.75,1.94,6.27,3.77,'EEF3F6')
text(s,.95,2.08,5.87,.56,'真实代码：extract_metrics，4716–4723行',16,TEAL,True)
snippet=text(s,.95,2.91,5.87,2.39,'\n'.join(line[4:] if line.startswith('    ') else line for line in code[4715:4723]),16,NAVY,False,'Consolas')
for paragraph in snippet.text_frame.paragraphs:
    paragraph.space_after=Pt(0)
panel(s,7.27,1.94,5.3,3.77,'后处理定义','RL = 20 log10|r11|\nB = f_high − f_low\n覆盖比例 = B / 16 GHz\nfitness：带宽主项＋边缘/裕量奖惩',21)
text(s,.83,6.0,11.72,.64,'−10 dB只表示该反射通道功率为10%；总吸收需核对全部传播通道。',20,ORANGE,True)

s=slide('13.20 GHz与后期12.48 GHz必须分别报告','本科毕设｜保存结果的可靠性边界','G/H：原始CST保存结果；N：2026-10-08只读复算与重绘（非新仿真）',
'左图把两份原始工程的保存结果放在一起。绿色是GA获选结果，最长通过区间4.80到18.00，宽度13.20 GHz；橙色是后来开启网格自适应的工程，区间5.20到17.68，宽度12.48。后期日志有软件内部自适应停止证据，但这不能给绿色曲线背书。两套保存结果有差异，我现在不把13.20作为独立收敛后的器件性能。另一个边界是18 GHz只是GA扫描上限。下一步必须固定结构材料，分别验证网格、频扫和端口设置。')
pic(s,AUD/'两工程同偏振对照.png',.72,1.94,8.3,4.4)
panel(s,9.25,2.05,3.29,1.71,'GA保存结果','4.80–18.00 GHz\n跨度13.20 GHz',19)
panel(s,9.25,3.99,3.29,1.71,'后期保存结果','5.20–17.68 GHz\n跨度12.48 GHz',19)
text(s,.86,6.42,11.5,.34,'只读恢复历史结果；尚未完成独立网格、端口、材料与频率敏感性验证。',17,ORANGE,True)

s=slide('功率核对支持模型内耗散，但结果不具偏振鲁棒性','本科毕设｜物理解释与未完成验证','N：两偏振S矩阵及功率；F：传播通道；T第6章的场图只作定性线索',
'左图显示同一GA工程的两种入射：y偏振有低反射区间，x偏振接近全反射，不能称偏振不敏感。对于功率归一化的两个传播通道，总反射要把两项模平方相加；PEC下透射为零。保存的功率结果与S矩阵功率和可以对应，但这仅证明保存模型的内部一致性。物理上，电阻面上的电流能够耗散能量，图案和片阻改变场、散射与损耗；局部场图不足以单独证明多模耦合或每层独立作用。没有实测和制造验证，下一步应先核可靠性，再做受控机理分析。')
pic(s,AUD/'两偏振对照.png',.72,2.05,7.32,3.7)
panel(s,8.3,1.95,4.26,3.83,'可说与待验证','PEC模型：T = 0\n总R = 两反射通道功率和\nA = 1 − R − T\n场图：定性机制线索\n实测、容差、严格收敛：待做',19)
text(s,.84,6.09,11.7,.55,'当前贡献是具体建模与搜索实践；保存样点能量核对相符，独立验证仍待完成。',19,TEAL,True)

s=slide('其他经历补充了数据处理和实验记录训练','合作研究与个人探索','原15页稿第7/8页实际图件；公共事实核验：晶格波、乐音专题（2026-10-05/06）',
'另外两段经历我简要说明。晶格波合作中，我参与MATLAB偏振相关处理、二维粒子轨迹可视化和多位置图组整理；这里的偏振是颗粒振动方向，不是电磁偏振，核心模拟算法和全部运行不能归为我的贡献。波纹管项目中，我推进录音和MATLAB频谱分析，比较不同管长的频率记录；老师提出初始问题，演示拍摄有组员协助。这个项目有实际声音记录，但没有定量流量控制或已经完成的气动声学机制验证。')
text(s,.8,1.9,5.7,.53,'二维尘埃等离子体晶格波',23,TEAL,True)
text(s,6.91,1.9,5.6,.53,'波纹管乐音研究',23,TEAL,True)
for tag,x in [('晶格波',.78),('乐音',6.9)]:
    paths=list((OUT/'assets').glob(tag+'.*'))
    if paths: pic(s,paths[0],x,2.6,5.64,2.35)
text(s,.82,5.23,5.62,1.35,'MATLAB数据处理与二维轨迹整理\n不认领核心模拟算法\n图组与论文Fig.12对应',19)
text(s,6.94,5.23,5.55,1.35,'录音 → 频谱 → 主要频率比较\n历史图横轴为记录序号，非流量\n未完成定量气动声学验证',19)

s=slide('希望从结构—响应问题，走向微纳光学研究','未来兴趣｜田静逸老师课题组','OMAL Research：https://omal.lab.westlake.edu.cn/Research.htm（2026-10-08核读）',
'这次毕设让我接触到一个长期感兴趣的问题：几何、材料和边界怎样共同决定电磁响应。田老师组的全介质纳米天线方向从单粒子散射到阵列响应，也探索静态到主动调控，我希望理解其中共振、近场与远场之间的关系。我目前的起点是电磁结构建模和数据处理；光频材料色散、Mie共振以及微纳加工与光谱测量都需要系统学习。我希望从一个能复现、能与测量对照的小问题开始，在研究中逐步确定更具体的方向。感谢老师。\n\n【反问备用】组里对以建模为起点、需要补实验训练的学生，通常会选择什么入门问题？\n【阅读边界】本轮核读官网研究介绍，不声称本人精读了未读论文。')
panel(s,.75,1.98,3.78,3.73,'已有起点','周期电磁结构建模\n参数化仿真与数据处理\n参考代码＋AI协作实践\n开始关注验证与可解释性',20)
panel(s,4.77,1.98,3.78,3.73,'希望进一步理解','全介质纳米天线\n单粒子散射 → 阵列响应\n几何 / 材料如何调控光\n从静态设计到主动调控',20)
panel(s,8.79,1.98,3.78,3.73,'需要补充的训练','光频材料色散与共振\n近场与远场的定量联系\n微纳加工与光谱测量\n可复现的仿真—实验对照',20)
text(s,.84,6.08,11.7,.58,'从一个可复现、可检验的小问题开始，在具体课题中逐步形成研究方向。',21,TEAL,True)

prs.core_properties.title='周子靖｜田静逸老师课题组交流｜2026-10-09'
prs.core_properties.subject='科研经历、实际工作过程与验证边界'
prs.core_properties.author='Zijing Zhou'
prs.save(OUT/'周子靖_田静逸交流_12页修订版_v1_20261008.pptx')
(OUT/'逐页讲稿.md').write_text('# 田静逸交流｜12页逐页讲稿\n\n建议主述8–10分钟；不是本人已掌握的证明。遇追问可以停页。来源简称见科研审计。\n\n'+'\n'.join(notes),encoding='utf-8')
(OUT/'页面证据映射.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
check=Presentation(OUT/'周子靖_田静逸交流_12页修订版_v1_20261008.pptx')
assert len(check.slides)==12
assert all(s.notes_slide.notes_text_frame.text for s in check.slides)
print('Created 12 slides with editable text/shapes and complete notes.')
