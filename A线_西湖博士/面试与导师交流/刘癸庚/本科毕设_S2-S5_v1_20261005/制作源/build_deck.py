"""Build only this presentation; historical research sources are read-only.
Python 3.11 + python-pptx 1.0.2 + Pillow. Run from any working directory.
Derived crops retain original orientation and colours. No simulation is run.
"""
from pathlib import Path
import csv, json, hashlib, math
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.xmlchemy import OxmlElement

OUT = Path(__file__).resolve().parent.parent
ROOT = next(p for p in OUT.parents if (p/'申请路线总览.md').exists())
ASSET = OUT/'派生素材'
ASSET.mkdir(exist_ok=True)
G = ROOT/'科研准备/本科毕设/图件/原始工程'
D = ROOT/'科研准备/本科毕设/仿真结果/原始工程/最终结果ohmic_sheet_12x12_multitemplate_topology_ga'
source_map = {
 'C01': G/'report_figures/results/最终版素材/3D.png',
 'C12': G/'数据存档/14基本-60-拓扑1.2/电阻膜图案.png',
 'C15x': G/'report_figures/results/9×9ph/final_9x9_x_pattern_paper.png',
 'C15y': G/'report_figures/results/9×9ph/final_9x9_y_pattern_paper.png',
 'C16': G/'ohmic_sheet_12x12_hybrid_coverage85_ga/best_mask_xy_12x12.png',
 'C17': G/'ohmic_sheet_12x12_hf_compensation_ga/best_mask_xy_12x12.png',
 'C18': G/'最终结果ohmic_sheet_12x12_multitemplate_topology_ga/best_mask_xy_12x12.png',
 'C22': D/'best_s11_ohmic_sheet_12x12.txt',
 'final_parameters': D/'best_result_ohmic_sheet_12x12.txt',
 'mask_x': D/'best_mask_x_12x12.txt', 'mask_y': D/'best_mask_y_12x12.txt',
}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = {'sources':{k:{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for k,p in source_map.items()}, 'derived':{}}
def crop(key, name, box, norm=True):
    im=Image.open(source_map[key]); w,h=im.size
    b=tuple(round(v*(w if i%2==0 else h)) for i,v in enumerate(box)) if norm else box
    target=ASSET/(name+'.png'); im.crop(b).save(target)
    manifest['derived'][target.name]={'source':key,'crop_px':b,'source_size':[w,h], 'operation':'crop only; original colours/orientation; no geometric reconstruction','sha256':sha(target)}
    return target
cst=crop('C01','C01_结构裁切',(480,330,1320,1010),False)
axis=crop('C01','C01_原坐标轴',(1810,950,1915,1050),False)
pair={}
pair['C12']=[crop('C12','C12_X',(.009,.147,.453,.939)),crop('C12','C12_Y',(.548,.147,.991,.939))]
pair['C15']=[crop('C15x','C15_X',(.103,.122,.975,.9)),crop('C15y','C15_Y',(.103,.122,.975,.9))]
pair['C16']=[crop('C16','C16_X',(.065,.133,.468,.887)),crop('C16','C16_Y',(.585,.133,.989,.887))]
pair['C18']=[crop('C18','C18_X',(.062,.133,.454,.887)),crop('C18','C18_Y',(.567,.133,.958,.887))]

rows=list(csv.DictReader(source_map['C22'].open(encoding='utf-8-sig'),delimiter='\t'))
data=[(float(r['freq_GHz']),float(r['rl_dB'])) for r in rows]
assert len(data)==201 and math.isclose(data[0][0],2) and math.isclose(data[-1][0],18)
assert all(math.isclose(b[0]-a[0],.08,abs_tol=1e-10) for a,b in zip(data,data[1:]))
passed=[i for i,(f,db) in enumerate(data) if db<=-10]
assert passed==list(range(35,201)) and math.isclose(data[35][0],4.8)
manifest['curve_validation']={'points':201,'step_GHz':.08,'first_continuous_pass_GHz':data[35][0], 'previous_dB':data[34][1], 'first_pass_dB':data[35][1], 'scan_limit_GHz':18,'last_dB':data[-1][1],'span_GHz':18-data[35][0],'rendering':'all 201 original samples joined by straight segments; no smoothing, interpolation of threshold, or new solver run'}

BG='FAFBFD'; INK='172B43'; MUTED='5C6D7E'; TEAL='007E86'; PALE='E8F4F3'; LINE='D8E1E8'; BLUE='2859A0'; AMBER='9B682D'
prs=Presentation(); prs.slide_width=Inches(13.333333); prs.slide_height=Inches(7.5)
prs.core_properties.title='本科毕设 S2–S5｜刘癸庚交流中文 PPT v1'
prs.core_properties.author='Zijing Zhou'
prs.core_properties.subject='三维周期电阻膜：结构设计、设计空间演化与研究判断'
prs.core_properties.comments='INTERNAL v1; sources and boundaries in accompanying README and notes.'
def rect(s,x,y,w,h,fill=BG,line=None,radius=False):
    z=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x),Inches(y),Inches(w),Inches(h))
    z.fill.solid(); z.fill.fore_color.rgb=RGBColor.from_string(fill)
    if line: z.line.color.rgb=RGBColor.from_string(line); z.line.width=Pt(.8)
    else: z.line.fill.background()
    if radius: z.adjustments[0]=.08
    return z
def txt(s,x,y,w,h,text,size=20,color=INK,bold=False,align=PP_ALIGN.LEFT):
    h=max(h, len(text.split('\n'))*size*1.34/72)
    z=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    f=z.text_frame; f.clear(); f.word_wrap=True
    f.margin_left=f.margin_right=0; f.margin_top=f.margin_bottom=0
    for i,t in enumerate(text.split('\n')):
        p=f.paragraphs[0] if i==0 else f.add_paragraph(); p.text=t; p.alignment=align
        p.space_before=Pt(0); p.space_after=Pt(0); p.line_spacing=1.12
        for r in p.runs:
            r.font.name='Microsoft YaHei'; r.font.size=Pt(size); r.font.bold=bold; r.font.color.rgb=RGBColor.from_string(color)
            ea=OxmlElement('a:ea'); ea.set('typeface','Microsoft YaHei'); r._r.get_or_add_rPr().append(ea)
    return z
def line(s,x1,y1,x2,y2,color=LINE,width=1.2,arrow=False,dash=False):
    z=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1),Inches(y1),Inches(x2),Inches(y2))
    z.line.color.rgb=RGBColor.from_string(color); z.line.width=Pt(width)
    if arrow:
        el=OxmlElement('a:tailEnd'); el.set('type','triangle'); z.line._get_or_add_ln().append(el)
    if dash:
        from pptx.enum.dml import MSO_LINE_DASH_STYLE
        z.line.dash_style=MSO_LINE_DASH_STYLE.DASH
    return z
def pic(s,path,x,y,w,h=None):
    im=Image.open(path); iw,ih=im.size
    if h is None: h=w*ih/iw
    else:
        scale=min(w/iw,h/ih); nw,nh=iw*scale,ih*scale; x+=(w-nw)/2; y+=(h-nh)/2; w,h=nw,nh
    return s.shapes.add_picture(str(path), Inches(x),Inches(y),Inches(w),Inches(h))
def base(no,kicker,title,source):
    s=prs.slides.add_slide(prs.slide_layouts[6]); s.background.fill.solid(); s.background.fill.fore_color.rgb=RGBColor.from_string(BG)
    txt(s,.52,.25,11,.25,'本科毕设  /  '+kicker,12,TEAL,True)
    txt(s,.52,.68,12.25,.61,title,29,INK,True)
    line(s,.52,7.04,12.82,7.04,LINE,.8)
    txt(s,.52,7.13,11.8,.2,source,10,MUTED)
    txt(s,12.16,7.09,.65,.3,f'S{no}',16,TEAL,True,PP_ALIGN.RIGHT)
    return s
notes=[]
def note(s,no,sec,script,evidence):
    text=f'S{no}｜目标 {sec} 秒（设计预算，尚未本人实测）\n\n口述稿\n{script}\n\n来源与边界（不逐条朗读）\n{evidence}'
    s.notes_slide.notes_text_frame.text=text; notes.append(text)

# S2: one physical object, not the tool chain.
s=base(2,'研究对象','面向宽带低反射，构建三维周期电阻膜单元','来源：C01 原始 CST 图（裁切）；C18 最终掩码；模型边界据 R1 / 最终 History。')
rect(s,.52,1.48,12.3,.57,PALE)
txt(s,.73,1.58,11.8,.35,'研究目标   在 2–18 GHz 内探索宽带低反射电阻膜结构',22,TEAL,True)
pic(s,cst,1.64,2.30,5.26,4.26)
txt(s,.62,2.39,1.18,.66,'两组竖直\n正交膜',19,INK,True)
line(s,1.78,2.98,3.15,3.48,TEAL,1.5)
txt(s,.62,4.0,1.23,.75,'PET 支撑\n+ 电阻层',17,INK,True)
line(s,1.8,4.54,3.37,4.7,TEAL,1.5)
txt(s,5.83,2.31,1.60,.7,'正入射\n沿 −z 传播',16,TEAL,True)
line(s,5.59,2.40,5.59,3.22,TEAL,2.5,True)
txt(s,.63,5.53,1.20,.5,'XY 周期',18,TEAL,True)
line(s,1.8,5.75,2.39,5.63,TEAL,1.3)
pic(s,axis,6.32,5.77,.63,.6)
rect(s,2.15,6.40,4.83,.40,'EEF1F5')
txt(s,2.29,6.46,4.60,.27,'底部：PEC 理想电边界（非实体背板图）',14,MUTED)
line(s,7.45,2.3,7.45,6.75,LINE)
txt(s,7.89,2.35,4.7,.43,'最终双膜图案：补足三维遮挡',19,INK,True)
for i,key in enumerate(['X','Y']):
    x=8.00+i*2.33
    txt(s,x,2.95,2.1,.3,f'{key} 膜',17,TEAL,True,PP_ALIGN.CENTER)
    pic(s,pair['C18'][i],x,3.34,2.06,2.06)
txt(s,7.99,5.54,4.65,.52,'黑：保留电阻层　白：去除电阻层\n原矩阵行序；白区不代表 PET 被挖空',13,MUTED)
rect(s,7.88,6.15,4.92,.66,PALE)
txt(s,8.04,6.27,4.63,.40,'整体散射 / 匹配状态 + 阻性耗散',19,TEAL,True)
note(s,2,50,'我的本科毕设，是在2到18 GHz范围内探索宽带低反射的电阻膜结构。在师兄建议考虑三维结构的基础上，我把两组电阻膜竖直、正交排列，落实成这里的周期单元。膜由PET支撑，横向采用XY周期边界，底部设置理想PEC电边界，微波从上方正入射。左边是历史CST图，右边的最终双膜图案补充了被遮挡的部分。物理上，我关心的是整体散射、匹配状态与阻性耗散的共同作用。那么，要改变这个系统的响应，可以设计哪些量？','C01截图为最终结构族，不能独立认证捕获参数或对应13.20 GHz那次运行；坐标轴来自同图独立裁切。C18按原矩阵方向展示，没有翻转，不是物理z向上的展开。理想PEC由边界实现；没有增加实体金属几何。R1第0/3/7节、素材筛选第3.1节。')

# S3: compact conceptual explanation, explicitly current general physics.
s=base(3,'设计自由度','四类自由度，在不同层级塑造同一电磁响应','依据：吸波物理图像与设计自由度 §10；R1 / U02 / U03。概念图为本轮整理，非仿真场图。')
txt(s,.56,1.48,12,.35,'一般电磁学解释 · 当前复盘理解；不代表本项目已验证的具体机理',16,AMBER)
cards=[('p','周期','横向电尺寸 / 周期尺度','单元耦合\nFloquet 通道开启条件'),('h','高度','纵向电尺寸','PEC 返回场相位\n内部场分布'),('图案','膜面图案','电流路径 / 边缘电荷','局部场\n分布式反应性'),('Rₛ,ₓ / Rₛ,ᵧ','双膜片阻','局部 Eₜ–K 关系','表面电流\n阻性耗散与散射')]
for i,(v,title,a,b) in enumerate(cards):
    x=.53+i*3.13; rect(s,x,2.09,2.9,2.69,'FFFFFF',LINE,True)
    rect(s,x,2.09,2.9,.06,TEAL)
    txt(s,x+.19,2.31,2.55,.60,v,30 if i<3 else 24,TEAL,True)
    txt(s,x+.19,3.02,2.55,.35,title,21,INK,True)
    txt(s,x+.19,3.56,2.60,.36,a,16,INK)
    txt(s,x+.19,4.01,2.58,.62,b,16,MUTED)
txt(s,.61,5.14,12,.36,'共同落点：同一个 Maxwell 自洽系统',22,INK,True)
nodes=[(.62,4.55,'局部 E / H / K 与极化'),(5.74,2.82,'散射 + 耗散'),(9.15,3.62,'频率响应')]
for x,w,t in nodes:
    rect(s,x,5.77,w,.67,PALE)
    txt(s,x+.12,5.95,w-.24,.34,t,21,TEAL,True,PP_ALIGN.CENTER)
line(s,5.28,6.10,5.61,6.10,TEAL,2,True);line(s,8.68,6.10,9.02,6.10,TEAL,2,True)
txt(s,.63,6.62,12,.29,'E：电场　H：磁场　K：表面电流；场与感应响应相互反馈，箭头表示解释关系。',14,MUTED)
note(s,3,55,'我优化的参数都有物理含义。周期改变横向电尺寸、单元耦合和Floquet通道的条件；高度改变纵向电尺寸、PEC返回场的相位和内部场分布。膜面图案改变电流能走的路径、边缘电荷与局部场，也改变分布式的反应性。两张膜的片阻则直接影响局部切向电场与表面电流的关系，同时影响散射和耗散。这些不是彼此独立的旋钮，最后都汇入同一个Maxwell自洽系统，表现为频率响应的变化。这是我现在复盘时使用的一般电磁解释，当时没有完成特定模态或等效电路的验证。接下来，我想重点讲这些自由度是怎样逐步形成的。','不主张项目已做输入阻抗反演、等效电路拟合或模态验证。Floquet仅列通道条件，不声称2–18 GHz已经开启高阶空间衍射。图案“分布式反应性”属一般物理解释，不给某个图案指定LC机理。主链是解释关系，不是单向求解流程。')

# S4: image-led ownership, three stages, no fabricated early visual.
s=base(4,'研究推进','我逐步扩展的是物理设计空间', '来源：C12 → C15 → C16 → C17/C18；R1 / U02 / U03。阶段判断按本人回顾整理，不是单因素因果证明。')
cols=[(.54,2.46,'01','全局几何'),(3.25,5.33,'02','局部拓扑'),(8.83,3.98,'03','材料阻性响应')]
for x,w,n,t in cols:
    rect(s,x,1.52,w,4.32,'FFFFFF',LINE,True)
    txt(s,x+.16,1.71,.47,.4,n,21,TEAL,True)
    txt(s,x+.70,1.70,w-.83,.42,t,22,INK,True)
txt(s,.73,2.44,2.1,.56,'p  /  h',34,TEAL,True)
txt(s,.73,3.14,2.10,.69,'少量固定材料组合\n先找有效参数区间',17,INK)
txt(s,.73,4.18,2.10,1.05,'建立全局电尺寸\n跑通参数化仿真\n控制初期计算规模',16,MUTED)
txt(s,.73,5.33,2.11,.33,'早期独立图：未唯一定位',11,MUTED)
txt(s,3.44,2.22,4.96,.37,'保留较优母型，提高图案分辨率',19,TEAL,True)
txt(s,3.44,2.67,4.96,.27,'母型：X 中央条带 + Y 纺锤形阶梯镂空',13,MUTED)
for j,key in enumerate(['C12','C15','C16']):
    x=3.92+j*1.54
    txt(s,x,3.03,1.21,.3,['6×6','9×9','12×12'][j],18,INK,True,PP_ALIGN.CENTER)
    pic(s,pair[key][0],x,3.39,1.02,1.02); pic(s,pair[key][1],x,4.52,1.02,1.02)
    if j<2: txt(s,x+1.14,3.86,.36,.35,'→',19,TEAL,True)
txt(s,3.46,3.75,.35,.3,'X',16,MUTED,True); txt(s,3.46,4.95,.35,.3,'Y',16,MUTED,True)
txt(s,9.01,2.34,3.66,.39,'开放 Rₛ,ₓ 与 Rₛ,ᵧ',23,TEAL,True)
txt(s,9.02,2.94,3.57,.70,'固定材料配置 → 连续数值变量\n同时调空间边界与局部材料响应',15,INK)
for i in range(2):
    x=9.37+i*1.62; txt(s,x,3.79,1.2,.27,['X','Y'][i],15,MUTED,True,PP_ALIGN.CENTER);pic(s,pair['C18'][i],x,4.12,1.18,1.18)
txt(s,9.03,5.44,3.61,.27,'hf → 最终：获选图案相同，尺寸 / 片阻不同',11,MUTED)
txt(s,3.46,5.61,5.02,.20,'蓝/黑：保留；灰/白：去除。原矩阵行序。',10,MUTED)
rect(s,.54,5.99,5.58,.48,PALE);rect(s,6.33,5.99,6.48,.48,PALE)
txt(s,.69,6.08,5.29,.29,'收益递减 / 表达受限 → 加入局部图案',17,TEAL,True)
txt(s,6.49,6.08,6.17,.29,'细化成本上升 / 性能趋缓 → 放开材料响应',17,TEAL,True)
txt(s,.58,6.66,12.25,.27,'支撑：GA 提候选 → Python 管实验 → CST 解 Maxwell → 结果反馈到下一阶段设计决策',15,MUTED)
note(s,4,85,'推进这个课题时，我没有一开始同时开放所有变量。第一阶段主要调周期和高度，配合少量固定材料组合；一边跑通参数化与自动仿真，一边在有限计算资源下找有效区间。只调全局尺寸的收益趋缓后，我加入膜面图案，从简单形态走向更高自由度搜索。中间这条链里，6×6阶段留下了我当时印象较好的母型：X膜的中央条带，以及Y膜类似纺锤形的阶梯镂空。后续保留较优母型，推进到9×9、12×12，让局部拓扑更细。继续细化的成本上升、提升趋缓后，后期版本进一步开放两张膜的连续片阻，把设计空间从空间边界扩展到材料阻性响应。右侧hf到最终的获选图案其实相同，变化的是尺寸和片阻，不能把最后增量归因于新拓扑。这个过程是在师兄参考和AI辅助下推进的；GA提出候选，Python组织评估，CST解物理，我持续参与的是结构、自由度和阶段结果的判断。','C12蓝色保留/灰色去除，C15/C16/C18黑色保留/白色去除，均为原矩阵行序。C12的“纺锤形”是回忆描述，图面保留真实阶梯像素；X中央条带与Y镂空分属不同膜。6→9严格像素映射UNKNOWN，9→12有继承实现。hybrid仍固定60 Ω/□；hf才有已核连续双片阻。C17与C18共用mask但参数不同，本页共用一次C18图。具体放宽建议者、准确决定时间、制造判断与放宽的因果仍UNKNOWN；不宣称每个更新由本人独立提出。代码参考来自师兄，AI广泛辅助。阶段叙事按本轮用户冻结指令，不补写精确历史断点。')

# S5: positive quantitative result first, future questions second.
s=base(5,'结果与判断','得到宽频段同模低反射；继续研究先补齐验证','来源：C22 最终原始201点（本轮逐点连线）；C18 最终图案；C01 原始CST结构族回忆图。')
txt(s,.57,1.48,7.04,.59,'4.80–18.00 GHz',36,TEAL,True)
txt(s,.60,2.14,7.3,.36,'指定同模反射 ≤ −10 dB 的连续采样区间',20,INK,True)
txt(s,8.70,1.48,4.08,.59,'13.20 GHz',36,TEAL,True)
txt(s,8.73,2.14,3.92,.33,'端点跨度  =  18.00 − 4.80',18,INK)
# Plot uses original values directly; a native editable PowerPoint polyline.
px,py,pw,ph=1.12,2.97,6.74,2.48
X=lambda v:px+(v-2)/16*pw
Y=lambda v:py+(0-v)/25*ph
rect(s,X(4.8),py,X(18)-X(4.8),ph,PALE)
for db in [0,-5,-10,-15,-20,-25]:
    line(s,px,Y(db),px+pw,Y(db),LINE,.7)
    txt(s,.55,Y(db)-.10,.45,.24,str(db).replace('-','−'),12,MUTED,False,PP_ALIGN.RIGHT)
for f in [2,6,10,14,18]:
    line(s,X(f),py,X(f),py+ph,LINE,.7)
    txt(s,X(f)-.22,py+ph+.10,.44,.25,str(f),12,MUTED,False,PP_ALIGN.CENTER)
line(s,px,Y(-10),px+pw,Y(-10),AMBER,1.2,False,True)
txt(s,1.15,Y(-10)-.30,1.27,.26,'−10 dB 阈值',12,AMBER)
fb=s.shapes.build_freeform(round(Inches(X(data[0][0]))),round(Inches(Y(data[0][1]))))
fb.add_line_segments([(round(Inches(X(f))),round(Inches(Y(db)))) for f,db in data[1:]],close=False)
curve=fb.convert_to_shape(); curve.fill.background();curve.line.color.rgb=RGBColor.from_string(TEAL);curve.line.width=Pt(2.5)
line(s,X(4.8),py,X(4.8),py+ph,TEAL,1,False,True)
for f,db in [data[35],data[-1]]:
    q=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(X(f)-.045),Inches(Y(db)-.045),Inches(.09),Inches(.09));q.fill.solid();q.fill.fore_color.rgb=RGBColor.from_string(TEAL);q.line.fill.background()
txt(s,1.12,2.66,5.5,.23,'指定同模反射 / dB',13,MUTED)
txt(s,3.90,5.84,2.57,.28,'频率 / GHz',13,MUTED,False,PP_ALIGN.CENTER)
txt(s,1.81,5.86,2.40,.27,'4.80：首个连续通过点',12,TEAL)
txt(s,6.29,2.67,1.58,.23,'18.00：扫描上限',12,TEAL,True,PP_ALIGN.RIGHT)
txt(s,.63,6.19,7.76,.32,'保存扫描：2–18 GHz · 201 点 · 间隔 0.08 GHz',16,INK)
txt(s,.63,6.64,7.84,.28,'该采样跨度尚不能认定为总吸收带宽。',16,AMBER,True)
# Structural reminder and three short questions, kept subordinate to chart.
for i in range(2):
    x=8.83+i*1.23;txt(s,x,2.82,1.0,.26,['X','Y'][i],13,MUTED,True,PP_ALIGN.CENTER);pic(s,pair['C18'][i],x,3.14,1.0,1.0)
pic(s,cst,11.35,2.95,1.38,1.23)
txt(s,11.35,4.20,1.40,.22,'CST 结构回忆',10,MUTED,False,PP_ALIGN.CENTER)
txt(s,8.77,4.53,4.03,.36,'现在继续：优先闭合三个问题',19,INK,True)
for i,t in enumerate(['全通道功率闭合','数值稳定性 / 收敛','宽带物理机理解释']):
    txt(s,8.83,5.10+i*.43,3.94,.32,f'{i+1:02d}   '+t,19,TEAL if i==0 else INK,i==0)
rect(s,8.70,6.48,4.09,.41,PALE)
txt(s,8.86,6.55,3.77,.29,'先闭合能量账与可靠性，再解释机制',14,TEAL,True)
note(s,5,55,'最后保存的结果是：2到18 GHz扫描中，指定同模反射不高于负10 dB的连续采样区间为4.80到18.00 GHz，端点跨度13.20 GHz。这里共有201个输出点，间隔0.08 GHz；4.80是首个连续通过点，18是扫描上限，也是末端通过点，所以不能把它当作已经找到的物理高频截止，更不能直接叫作总吸收带宽。当年完成的是性能驱动的结构优化。如果现在继续，我不会优先扩大GA，而会先核全通道功率，把能量账闭合，再检查数值稳定性和收敛，之后解释宽带机制，并逐步考虑制造和实验闭环。','C22输入201点原样读取并作折线，没有平滑或阈值插值。4.72 GHz = −9.733259 dB；4.80 GHz = −10.042591 dB；18 GHz = −10.268263 dB。最终p=13.1409 mm，h=10.0731 mm，PET=0.188 mm；Rs,x=140.79、Rs,y=35.461 Ω/□。C18黑保留/白去除、原矩阵行序，不是按物理z向上排列。201输出点不等于201次独立频率求解。已有后期软件自适应记录但未与GA曲线逐项绑定；全功率、独立收敛、机理、制造实测仍未完成。本页小CST图不能独立认证最终参数。')

target=OUT/'本科毕设_S2-S5_v1.pptx'
for slide in prs.slides:
    for shape in slide.shapes:
        for effect in shape._element.xpath('.//a:effectRef'):
            effect.set('idx','0')
        sp=shape._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}spPr')
        if sp is not None:
            sp.append(OxmlElement('a:effectLst'))
prs.save(target)
(OUT/'口述稿与备注.md').write_text('# 本科毕设 S2–S5 v1｜口述稿与备注\n\nINTERNAL；预算50 + 55 + 85 + 55 = 245秒（约4分05秒），尚未本人计时试讲。备注不是新增个人事实或已掌握能力证明。\n\n'+'\n\n---\n\n'.join(notes)+'\n',encoding='utf-8')
assert all(sha(source_map[k])==v['sha256'] for k,v in manifest['sources'].items())
manifest['originals_unchanged_after_build']=True
(OUT/'素材来源与派生记录.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(target)
