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

BG='FFFFFF'; INK='172B43'; MUTED='5C6D7E'; TEAL='007E86'; PALE='E8F4F3'; LINE='D8E1E8'; BLUE='2859A0'; AMBER='9B682D'
prs=Presentation(); prs.slide_width=Inches(13.333333); prs.slide_height=Inches(7.5)
prs.core_properties.title='本科毕设 S2–S5｜刘癸庚交流中文 PPT v2'
prs.core_properties.author='Zijing Zhou'
prs.core_properties.subject='三维周期电阻膜：结构设计、设计空间演化与研究判断'
prs.core_properties.comments='INTERNAL v2; sources and boundaries in accompanying README and notes.'
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

# Existing C07 drawing was already audited in the visual selection record.
# It is a preparation-stage schematic, never a CST export or an experimental image.
source_map['C07']=ROOT/'A线_西湖博士/联系材料/刘癸庚/制作文件/项目页/第四版/图件/geometry.png'
manifest['sources']['C07']={'path':source_map['C07'].relative_to(ROOT).as_posix(),'sha256':sha(source_map['C07'])}
schematic=crop('C07','C07_既有结构示意',(60,100,545,493),False)
V1=OUT.parent/'本科毕设_S2-S5_v1_20261005'
old=Presentation(V1/'本科毕设_S2-S5_v1.pptx')
boundaries=[s.notes_slide.notes_text_frame.text.split('来源与边界（不逐条朗读）\n')[1] for s in old.slides]
def base(no,title,source):
    s=prs.slides.add_slide(prs.slide_layouts[6]); s.background.fill.solid(); s.background.fill.fore_color.rgb=RGBColor.from_string(BG)
    txt(s,.55,.24,10,.20,'本科毕设',11,MUTED)
    txt(s,.55,.65,12.23,.70,title,30,INK,True)
    line(s,.55,7.04,12.80,7.04,LINE,.7)
    txt(s,.55,7.15,11.54,.21,source,9,MUTED)
    txt(s,12.16,7.09,.65,.33,f'S{no}',15,TEAL,True,PP_ALIGN.RIGHT)
    return s
notes=[]
def note(s,no,script,pause,extra=''):
    evidence=boundaries[no-2]+('\n'+extra if extra else '')
    t=f'S{no}\n\n口述稿\n{script}\n\n被打断时\n{pause}\n\n来源与边界（不逐条朗读）\n{evidence}'
    s.notes_slide.notes_text_frame.text=t;notes.append(t)

# S2: retain the real CST image as the dominant visual, remove banner/slogan.
s=base(2,'我的毕业设计：三维周期电阻膜吸波结构','C01 原始CST图裁切；C18 最终图案。边界设置沿用R1；截图不能独立锁定最终参数。')
txt(s,.58,1.48,11.8,.4,'想在 2–18 GHz 内，让反射尽量低',22,TEAL)
pic(s,cst,1.68,2.04,5.96,4.72)
txt(s,.58,2.27,1.29,.74,'两组膜\n竖直正交',18,INK,True)
line(s,1.91,2.92,3.46,3.40,TEAL,1.3)
txt(s,.58,4.03,1.46,.74,'PET 支撑\n表面为电阻层',16,INK)
line(s,2.05,4.57,3.46,4.72,TEAL,1.3)
txt(s,.58,5.73,1.5,.4,'XY 周期',18,INK)
line(s,1.93,5.97,2.57,5.77,TEAL,1.3)
txt(s,6.42,2.08,1.49,.68,'正入射\n沿 −z',16,TEAL)
line(s,6.20,2.13,6.20,2.95,TEAL,2,True)
pic(s,axis,7.07,5.89,.59,.57)
txt(s,2.15,6.66,5.80,.28,'底部设为 PEC 理想电边界',15,MUTED)
txt(s,8.78,2.34,3.97,.35,'两张膜的图案',19,INK)
for i in range(2):
    x=8.87+i*2.0
    txt(s,x,2.89,1.46,.29,['X','Y'][i],16,MUTED,False,PP_ALIGN.CENTER)
    pic(s,pair['C18'][i],x,3.26,1.46,1.46)
txt(s,8.86,4.91,3.88,.50,'黑：保留电阻层　白：去除电阻层\n原矩阵行序；PET没有随白区挖空',12,MUTED)
txt(s,8.79,5.96,4.01,.92,'反射要少，能量也要\n真正耗散在电阻膜中。',21,INK)
note(s,2,'我的毕业设计做的是这个三维电阻膜结构，想在2到18 GHz这段范围里，把反射降下来。师兄建议考虑立体结构以后，我想到把膜竖起来，用两组互相垂直的膜组成周期单元。\n\n左边是当时的CST图。膜由PET支撑，XY方向周期排列，底部设成理想PEC电边界，波从上面正入射。三维图里有遮挡，所以右边单独放了最终的两张膜图案。\n\n吸收要做得好，光让反射少还不够，能量也得真正耗散在里面。后面我会再说，这个项目当时的结果验证到了哪一步。','介绍完目标、结构组成或图案，任一处都可停下来指图回答；不必急着转入下一页。','标题的“吸波结构”指研究对象和目标，不是宣称总吸收已验证。S2末句仍是目标解释，不是项目功率闭合结论。')

# S3: two physical views, dimension annotations, and conversational explanations.
s=base(3,'这些参数分别在改变什么？','C07：2026-09据保存图案绘制的结构示意；C18原矩阵图案。此页是当前物理理解，不是已验证机理。')
txt(s,.59,1.48,11.9,.31,'这是我现在对这些参数的理解。',17,MUTED)
# The C07 crop excludes its old literal "metal backplate" caption.
pic(s,schematic,1.33,2.67,4.20,3.4033)
# h annotation follows a single vertical film edge at x=407 in the source.
# Its upper/lower endpoints are (407,126)/(407,309), not two different depths.
sx,sy,sw,sh=1.33,2.67,4.20,3.4033
gx=lambda v:sx+(v-60)/485*sw
gy=lambda v:sy+(v-100)/393*sh
line(s,gx(433),gy(126),gx(433),gy(309),TEAL,1.3)
line(s,gx(420),gy(126),gx(441),gy(126),TEAL,1.3)
line(s,gx(420),gy(309),gx(441),gy(309),TEAL,1.3)
txt(s,gx(441)+.04,gy(198),.30,.35,'h',21,TEAL,True)
txt(s,.60,2.13,5.92,.35,'高度 h：PEC 返回场的相位会变',21,TEAL,True)
# p is labelled at a unit-cell span; leader is explanatory, not a scale bar.
txt(s,.59,6.22,6.2,.35,'周期 p：横向尺度、单元之间的相互作用',19,TEAL,True)
txt(s,.62,6.65,6.05,.25,'周期也影响 Floquet 通道条件；灰底表示理想 PEC 边界。',12,MUTED)
txt(s,7.20,2.15,5.43,.40,'图案：电流从哪里走？',23,INK,True)
for i in range(2):
    x=7.35+i*2.02
    txt(s,x,2.73,1.56,.27,['X','Y'][i],15,MUTED,False,PP_ALIGN.CENTER)
    pic(s,pair['C18'][i],x,3.07,1.56,1.56)
txt(s,7.22,4.81,5.42,.35,'哪里积累电荷，局部场也会跟着变。',17,INK)
txt(s,7.21,5.48,5.45,.40,'片阻：同样的局部电场，电流有多大？',20,TEAL,True)
txt(s,7.23,6.03,5.43,.65,'Rₛ,ₓ、Rₛ,ᵧ 改变局部 Eₜ 与 K 的关系\n电流变了，散射和耗散也会变。',17,INK)
note(s,3,'我现在重新理解这个项目时，会先问：这些参数到底在改什么？\n\n像周期，改的是横向的大小、周期条件，以及相邻单元怎样相互影响，也会影响Floquet通道的条件。高度改了，结构相对于波长的大小会变，PEC返回场的相位也会变，所以膜所在位置的场会跟着变。\n\n图案就比较直观：哪些地方有电阻层，电流就能从哪些地方走；边缘哪里容易积累电荷、局部场怎么分布，也会受影响。片阻则是在改变同样的局部切向电场下，会有多大的表面电流。这里的“同样电场”只是用来说明局部关系，实际求解时，电场和电流会一起变。\n\n所以这些参数最后都会影响内部的场和膜上的电流，再改变散射和耗散。我当时主要是看响应、继续调结构；这里讲的是我现在的理解，还不能说已经解释清楚了这个结构的具体宽带机制。','可依次停在尺寸、图案、片阻任一处；被追问时围绕图上的具体位置展开。不需要背一条完整理论链。','C07是已有复盘示意，非历史CST或样件；本轮只裁切，不重画像素。h辅助线限定膜高，不跨空气区。C07按物理z向上，右侧C18按原矩阵行序，两者上下方向不同；不得用此视觉差异推导另一版本。高度的“返回相位”指PEC返回场，不等于认定Salisbury screen。正文“同样的局部电场”用于说明局部本构，不是把场固定的独立优化假设。')

# S4: the real image sequence takes the space previously occupied by boxes.
s=base(4,'后来，我怎么决定下一步改什么？','C12 → C15 → C16 → C17/C18。图案与继承沿用已核素材；判断按本人回顾，不补精确历史断点。')
txt(s,.58,1.55,2.46,.8,'先调周期、高度，\n把仿真跑通',21,INK,True)
txt(s,.58,2.62,2.21,.86,'那时也在学\nCST / Python，\n算力得省着用。',17,MUTED)
txt(s,.58,4.07,2.24,1.35,'再调尺寸，\n提升开始变慢。\n\n我开始加图案。',18,INK)
txt(s,.59,6.01,2.25,.52,'早期用少量固定材料组合\n独立结构图尚未唯一定位',11,MUTED)
txt(s,3.24,1.55,6.23,.43,'这组图案不错，保留下来再做细一点',21,TEAL,True)
txt(s,3.25,2.14,5.99,.35,'X 中央条带 + Y「纺锤形」阶梯镂空',15,MUTED)
for j,key in enumerate(['C12','C15','C16']):
    x=3.47+j*2.01
    txt(s,x,2.73,1.35,.33,['6×6','9×9','12×12'][j],20,INK,True,PP_ALIGN.CENTER)
    pic(s,pair[key][0],x,3.22,1.35,1.35)
    pic(s,pair[key][1],x,4.83,1.35,1.35)
    if j<2:line(s,x+1.48,4.69,x+1.83,4.69,TEAL,1.6,True)
txt(s,3.01,3.76,.31,.3,'X',16,MUTED);txt(s,3.01,5.37,.31,.3,'Y',16,MUTED)
txt(s,3.48,6.34,5.76,.28,'蓝/黑：保留电阻层；灰/白：去除。均为原矩阵行序。',11,MUTED)
txt(s,10.04,1.55,2.76,.88,'再加细，\n还是试试片阻？',21,TEAL,True)
txt(s,10.06,2.66,2.76,.50,'细化更费算力，\n提升也慢了。',15,MUTED)
txt(s,10.50,3.29,2.16,.39,'Rₛ,ₓ、Rₛ,ᵧ',23,INK,True)
pic(s,pair['C18'][0],10.22,4.12,1.08,1.08);pic(s,pair['C18'][1],11.59,4.12,1.08,1.08)
txt(s,10.22,3.82,1.08,.25,'X',14,MUTED,False,PP_ALIGN.CENTER);txt(s,11.59,3.82,1.08,.25,'Y',14,MUTED,False,PP_ALIGN.CENTER)
txt(s,10.04,5.49,2.78,.73,'从固定商品参数，\n转向连续数值片阻。',17,INK)
txt(s,10.04,6.34,2.78,.29,'hf与最终同图案；尺寸、片阻不同',10,MUTED)
line(s,2.56,5.12,3.14,4.66,TEAL,1.4,True)
line(s,8.99,4.68,9.77,4.68,TEAL,1.4,True)
txt(s,.59,6.75,12.08,.29,'工具帮我试这些选择：GA 提候选 → Python 组织仿真 → CST 求解',14,MUTED)
note(s,4,'这些参数不是一开始就全部放开的。最早主要调周期和高度，材料也只有少量固定组合。那时我也在学CST和Python，先得把参数化仿真跑通，再在有限算力下找一个有效范围。后来只继续调尺寸，提升开始变慢，我就开始往膜上加图案。\n\n我印象比较深的是这组6×6：X膜中间有一条完整条带，Y膜里是有点像纺锤形的阶梯镂空。它表现还不错，所以后面没有每次都从头随机来，而是保留这个母型，继续试9×9、12×12，让图案更细。\n\n再往下做，图案越细，搜索就越费计算，提升也开始慢下来。这时候面临的选择是：继续加细，还是换一种参数来调？后面的版本把两张膜的片阻也放开了，从固定商品参数转向连续数值。\n\n当时我也考虑过实际装配：细长的膜不容易摆整齐，位置和形状误差不好控制，后来确实更偏向仿真。不过，这个考虑和放开片阻究竟怎么衔接，现有记录还不能完整还原，不能把它讲成一个已经查清的直接原因。\n\n师兄给了参考和建议，我也用了很多AI辅助。我的工作是结合已经跑出来的结果，接着判断该保留什么、下一步允许哪些量变化。','每段都是一个可独立停下的意思。若老师指着图问，先说明相应X/Y膜、当时保留了什么。工具链不必逐项复述；“装配考虑”的段落可在被问现实约束时展开。','v2把决策写成自然回顾，不新增独立算法设计或全部决策由本人首倡的结论。具体GA参数/优化路径也有大量AI建议；不把图案细化当作求解网格加密。装配误差属于当时考虑，没有新增样件或公差试验。没有使用同学转述推定老师必然打断或实际考核方式。')

# S5: retain positive results and original samples, simplify all surrounding prose.
s=base(5,'最终结果：做到了什么，还缺什么？','C22最终201点逐点连线；C18最终图案；C01结构回忆。没有新增求解或总吸收验证。')
txt(s,.58,1.48,7.7,.65,'4.80–18.00 GHz',36,TEAL,True)
txt(s,.60,2.17,7.90,.35,'指定同模反射 ≤ −10 dB 的连续采样区间',20,INK)
txt(s,9.03,1.53,3.79,.60,'13.20 GHz',31,TEAL,True)
txt(s,9.06,2.17,3.73,.34,'端点跨度',18,INK)
px,py,pw,ph=1.03,3.03,7.15,2.77
X=lambda v:px+(v-2)/16*pw
Y=lambda v:py+(0-v)/25*ph
for db in [0,-5,-10,-15,-20,-25]:
    line(s,px,Y(db),px+pw,Y(db),LINE,.65)
    txt(s,.52,Y(db)-.12,.40,.23,str(db).replace('-','−'),12,MUTED,False,PP_ALIGN.RIGHT)
for f in [2,6,10,14,18]:
    txt(s,X(f)-.22,py+ph+.11,.44,.25,str(f),12,MUTED,False,PP_ALIGN.CENTER)
line(s,px,Y(-10),px+pw,Y(-10),AMBER,1.05,False,True)
txt(s,1.09,Y(-10)-.33,1.32,.28,'−10 dB',13,AMBER)
fb=s.shapes.build_freeform(round(Inches(X(data[0][0]))),round(Inches(Y(data[0][1]))))
fb.add_line_segments([(round(Inches(X(f))),round(Inches(Y(db)))) for f,db in data[1:]],close=False)
curve=fb.convert_to_shape();curve.name='C22_original_201_samples';curve.fill.background();curve.line.color.rgb=RGBColor.from_string(TEAL);curve.line.width=Pt(2.6)
line(s,X(4.8),py,X(4.8),py+ph,TEAL,1,False,True)
for f,db in [data[35],data[-1]]:
    q=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(X(f)-.044),Inches(Y(db)-.044),Inches(.088),Inches(.088));q.fill.solid();q.fill.fore_color.rgb=RGBColor.from_string(TEAL);q.line.fill.background()
txt(s,1.03,2.67,5.61,.27,'指定同模反射 / dB',14,MUTED)
txt(s,6.47,2.67,1.74,.27,'18.00：扫描上限',12,TEAL,False,PP_ALIGN.RIGHT)
txt(s,1.82,6.18,2.44,.27,'4.80：首个连续通过点',12,TEAL)
txt(s,6.52,6.18,1.7,.27,'频率 / GHz',13,MUTED,False,PP_ALIGN.RIGHT)
txt(s,.60,6.50,7.93,.31,'保存扫描 2–18 GHz · 201点 · 间隔0.08 GHz',15,INK)
for i in range(2):
    x=9.06+i*1.19;txt(s,x,2.85,.91,.25,['X','Y'][i],13,MUTED,False,PP_ALIGN.CENTER);pic(s,pair['C18'][i],x,3.19,.91,.91)
pic(s,cst,11.48,2.99,1.28,1.18)
txt(s,9.03,4.47,3.79,.40,'如果现在继续，我会先做：',18,INK,True)
txt(s,9.07,5.07,3.67,.67,'把开放传播通道的功率\n算清楚',17,INK)
txt(s,9.07,5.91,3.67,.37,'检查网格和数值收敛',17,INK)
txt(s,9.07,6.45,3.67,.52,'结果可靠后，再解释\n为什么会有宽带响应',16,INK)
txt(s,.60,6.83,7.80,.21,'这里统计的是同模反射，尚不能认定为总吸收带宽。',11,MUTED)
note(s,5,'这是最后保存下来的反射曲线。4.80到18.00 GHz这段，指定同模反射都不高于负10 dB，端点相减是13.20 GHz。这是这个项目当时得到的主要结果。\n\n这里的4.80，是保存数据里第一个连续通过的采样点；18则已经到扫描上限了，不是说我找到了它真正的高频截止。扫描是2到18 GHz，共201个输出点，间隔0.08 GHz。\n\n现在回头看，当时做到了结构优化，但还没有把总吸收算清楚。如果继续，我会先把所有开放传播通道的功率算一遍，看能量到底去了哪里；再检查网格和数值结果是否稳定。结果可靠以后，再去解释为什么能在这么宽的一段频率里保持低反射。我不会先想着把GA做得更大。至于怎么做成样件、实验能不能对上，也需要往后接着做。','数字介绍完成即可接受追问。若老师问“吸收多少”，直接区分保存的同模反射与尚未核算的总吸收。后续工作按功率、数值、机制逐项展开，不需要一口气念完。','18.00同时是末端通过点和扫描上限；13.20仅端点跨度。图像图案原矩阵方向、CST捕获参数等边界与v1相同。')

for slide in prs.slides:
    for shape in slide.shapes:
        for effect in shape._element.xpath('.//a:effectRef'):effect.set('idx','0')
        sp=shape._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}spPr')
        if sp is not None:sp.append(OxmlElement('a:effectLst'))
prs.save(OUT/'本科毕设_S2-S5_v2.pptx')
(OUT/'口述稿与备注.md').write_text('# 本科毕设 S2–S5 v2｜逐页口述稿\n\nINTERNAL，未发送。约4分钟只作完整讲述参考，不设逐页硬秒数；每段可独立停下回答追问。正文是拟议口述，不是已发生的发言或新增事实确认。装配等补充可以随追问展开，无需为了4分05秒抢讲。\n\n'+'\n\n---\n\n'.join(notes)+'\n',encoding='utf-8')
assert all(sha(source_map[k])==v['sha256'] for k,v in manifest['sources'].items())
baseline=json.loads((OUT/'v1保全基线.json').read_text(encoding='utf-8'))
assert all(sha(V1/k)==v for k,v in baseline.items())
manifest.update({'originals_unchanged_after_build':True,'v1_unchanged_after_build':True,'nature':'v2 presentation revision; sources/boundaries inherited, no new research audit or simulation'})
(OUT/'素材来源与派生记录.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(OUT/'本科毕设_S2-S5_v2.pptx')
