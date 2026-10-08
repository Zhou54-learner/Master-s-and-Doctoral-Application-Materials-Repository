"""Two standalone editable S7 candidates; never opens or edits another slide."""
from pathlib import Path
import csv, json, hashlib, shutil, statistics
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.oxml.xmlchemy import OxmlElement

OUT=Path(__file__).resolve().parent.parent
ROOT=next(p for p in OUT.parents if (p/'申请路线总览.md').exists())
DATA=ROOT/'公共资料/事实核验/乐音研究_深挖证据_20261006/历史表对应42组统计.csv'
INK,MUTED,TEAL,LINE='172B43','5C6D7E','007E86','D8E1E8'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
rows=list(csv.DictReader(DATA.open(encoding='utf-8-sig')))
assert len(rows)==42 and sum(float(r['cv_pct'])<1 for r in rows)==40
lengths=[]
for length in [40,60,100]:
    group=sorted([r for r in rows if float(r['R'])==7.5 and int(r['L'])==length],key=lambda r:r['group'])
    f=[float(r['mean_hz']) for r in group]
    df=[b-a for a,b in zip(f,f[1:])]
    lengths.append(dict(length_cm=length,groups=[r['group'] for r in group],mean_frequencies_hz=f,direct_gaps_hz=df,mean_gap_hz=statistics.mean(df),L_deltaf_hz_m=length/100*statistics.mean(df)))
dump(OUT/'检查证据/页面数值复核.json',dict(source=DATA.as_posix(),source_sha256=sha(DATA),groups=42,cv_lt_1=40,valid_records=sum(int(r['n']) for r in rows),lengths=lengths))

original=Path('E:/2023/traindata/数据处理/长度关系比较/数据图表1.jpg')
copy=OUT/'派生素材/历史长度比较_完整原图.jpg'
if original.exists():shutil.copyfile(original,copy)
else:original=copy
# Only the redundant original title area is removed. All samples/axes/legends remain.
cropbox=(0,100,1200,1020)
crop=OUT/'派生素材/历史长度比较_仅裁顶端图题.png'
Image.open(original).convert('RGB').crop(cropbox).save(crop)
fig=OUT/'历史资产核查/历史FIG_80cm_原标签.png'
dump(OUT/'派生素材说明.json',[
 dict(id='A_main',source=original.as_posix(),sha256=sha(original),original_copy=copy.relative_to(OUT).as_posix(),output=crop.relative_to(OUT).as_posix(),output_sha256=sha(crop),crop_box=list(cropbox),operation='Crop duplicate historical title only; retain every plotted point, axes, units, legend and mean-summary segment. No redraw, recolor, sharpening or selective removal.'),
 dict(id='B_main',source='E:/2023/traindata/R11.6mm_r8.0mm/80cm/R11.6mmr8mm_80mm_scale.fig',sha256=sha(Path('E:/2023/traindata/R11.6mm_r8.0mm/80cm/R11.6mmr8mm_80mm_scale.fig')),output=fig.relative_to(OUT).as_posix(),output_sha256=sha(fig),operation='Native MATLAB render of saved FIG objects. No new data analysis, no labels changed, no crop, no removed anomalies. Incorrect historical Time(s) label explained on slide.' )])

def text(s,name,x,y,w,h,content,size=20,color=INK,bold=False,align=PP_ALIGN.LEFT):
    shape=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));shape.name=name
    tf=shape.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    for i,line in enumerate(content.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.alignment=align
        p.space_before=p.space_after=Pt(0);p.line_spacing=1.13
        for r in p.runs:
            r.font.name='Microsoft YaHei';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
            ea=OxmlElement('a:ea');ea.set('typeface','Microsoft YaHei');r._r.get_or_add_rPr().append(ea)
    return shape
def line(s,name,x,y,w):
    sh=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x),Inches(y),Inches(x+w),Inches(y));sh.name=name
    sh.line.color.rgb=RGBColor.from_string(LINE);sh.line.width=Pt(.7)
def picture(s,name,path,x,y,w):
    sh=s.shapes.add_picture(str(path),Inches(x),Inches(y),width=Inches(w));sh.name=name
    return sh
def base(variant,subtitle):
    prs=Presentation();prs.slide_width=Inches(13.333333);prs.slide_height=Inches(7.5)
    prs.core_properties.title='同一根波纹管，为什么会出现几个稳定音调？'
    prs.core_properties.author='Zijing Zhou';prs.core_properties.subject=f'INTERNAL / S7 v2 CANDIDATE {variant}'
    prs.core_properties.comments='Historical assets and 2026 retrospective analysis explicitly separated. Standalone candidate only.'
    s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=RGBColor(255,255,255)
    text(s,'section',.55,.24,10,.25,'个人探索 · 波纹管乐音研究',11,MUTED)
    text(s,'title',.55,.65,12.25,.65,prs.core_properties.title,28,INK,True)
    text(s,'subtitle',.58,1.36,12,.32,subtitle,13,MUTED)
    line(s,'footer_rule',.55,7.04,12.25)
    text(s,'slide_number',12.16,7.09,.65,.34,'S7',15,TEAL,True,PP_ALIGN.RIGHT)
    return prs,s

prs,s=base('A','大二 · 从“听起来稳定”，到可以记录和比较的频率问题')
text(s,'historical_label',.6,1.85,6.5,.28,'历史图件 · 五种管长的频率记录',13,MUTED)
picture(s,'historical_length_comparison',crop,.6,2.16,6.15)
text(s,'observation',7.35,1.98,5.25,.84,'同一根管，\n多个彼此分离的稳定音调',22,INK,True)
text(s,'within_vs_between',7.35,3.0,5.25,.38,'同组频率集中，组间出现台阶',18,TEAL,True)
text(s,'method',7.35,3.57,5.25,.35,'录音 → MATLAB 频谱 → 提取主要频率',14,MUTED)
text(s,'statistics',7.35,4.05,5.25,.56,'2026复盘：9个几何条件，42组历史音调\n其中40组的组内相对波动 < 1%（s / 均值）',12,MUTED)
line(s,'evidence_time_separator',7.35,4.8,5.25)
text(s,'retrospective_label',7.35,4.98,5.25,.28,'历史数据 · 2026 复盘重分析',12,TEAL)
text(s,'length_claim',7.35,5.4,5.25,.38,'管越长，台阶间距总体越小',19,INK,True)
text(s,'lengths',7.35,5.97,5.25,.33,'40 / 60 / 100 cm',16,INK)
text(s,'gaps',7.35,6.33,5.25,.43,'平均约 378 / 262 / 151 Hz',20,TEAL,True)
text(s,'geometry',7.35,6.79,5.3,.22,'R/r = 7.5/5.5 mm · 近似与 1/L 尺度相容',10.5,MUTED)
text(s,'source_footer',.55,7.16,11.5,.2,'历史图横轴为实验序号；图末 Δ 为组均值，并非台阶间距；同序号不代表同流量或同模态。',9,MUTED)
s.notes_slide.notes_text_frame.text=(OUT/'speaker_notes_A.md').read_text(encoding='utf8')
prs.save(OUT/'S7_乐音研究_v2_A_历史资产优先.pptx')

prs,s=base('B','大二 · 录音 → MATLAB 频谱分析 → 提取主要频率；另尝试时变音高分析')
text(s,'historical_label',.6,1.85,6.5,.28,'历史音高图 · 同一根管的多个音调',14,INK,True)
text(s,'historical_condition',.6,2.2,6.55,.25,'80 cm · R/r = 11.6/8.0 mm · 拼接展示，非连续扫流',12,MUTED)
picture(s,'historical_pitch_fig',fig,.6,2.53,5.62)
text(s,'axis_caveat',.6,6.83,6.45,.22,'原图 Time (s) 误标：横轴实为采样点序号。',10.5,MUTED)
text(s,'retrospective_label',7.35,1.85,5.25,.28,'历史数据 · 2026 复盘重分析',12,TEAL)
text(s,'length_claim',7.35,2.24,5.25,.83,'管越长，\n音调台阶间距总体越小',22,INK,True)
text(s,'geometry',7.35,3.24,5.25,.28,'R/r = 7.5/5.5 mm',13,MUTED)
text(s,'table_head_length',7.35,3.72,1.5,.26,'管长',12,MUTED)
text(s,'table_head_gap',9.33,3.72,3.3,.26,'平均台阶间距',12,MUTED)
for i,r in enumerate(lengths):
    y=4.10+i*.65
    text(s,f'length_{i}',7.35,y,1.65,.48,f"{r['length_cm']} cm",22,INK)
    text(s,f'arrow_{i}',9.0,y,.4,.48,'→',22,MUTED)
    text(s,f'gap_{i}',9.6,y,2.7,.48,f"≈ {round(r['mean_gap_hz'])} Hz",24,TEAL,True)
text(s,'scale_interpretation',7.35,6.14,5.25,.33,'近似与 1/L 尺度相容',17,INK)
text(s,'statistics',7.35,6.62,5.3,.43,'全量复盘：42组历史音调，40组 s / 均值 < 1%\n统计来自成组短录音，不将左图另计为实验。',10.5,MUTED)
text(s,'source_footer',.55,7.16,11.5,.2,'左：历史音阶整理与音高分析；右：历史短录音复盘。两部分截面条件不同，均不代表机制已验证。',9,MUTED)
s.notes_slide.notes_text_frame.text=(OUT/'speaker_notes_B.md').read_text(encoding='utf8')
prs.save(OUT/'S7_乐音研究_v2_B_历史与复盘并置.pptx')
print('Built two standalone S7 v2 candidates, 1 slide each.')
