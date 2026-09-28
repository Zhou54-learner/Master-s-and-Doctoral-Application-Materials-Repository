"""Render one-page local review PDF; only reads copied source inputs."""
from pathlib import Path
import sys, re, math, io, argparse
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'核验/a4_runtime'))
import fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from xml.sax.saxutils import escape
parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path);args=parser.parse_args()
OUT=args.output_dir or HERE.parent/'output';OUT.mkdir(parents=True,exist_ok=True)
W,H=595.276,841.89
pdfmetrics.registerFont(TTFont('Han','C:/Windows/Fonts/SourceHanSansCNRegular.ttf'))
pdfmetrics.registerFont(TTFont('HanBold','C:/Windows/Fonts/SourceHanSansCNBold.ttf'))
pdfmetrics.registerFontFamily('Han',normal='Han',bold='HanBold')
name='周子靖_毕设项目页_刘癸庚版_v1_INTERNAL'
buffer=io.BytesIO()
c=canvas.Canvas(buffer,pagesize=(W,H))
c.setTitle('电阻膜微波吸收结构的仿真与优化 — 周子靖');c.setAuthor('Zijing Zhou')
STYLE=ParagraphStyle('body',fontName='Han',fontSize=9.4,leading=13.4,textColor=HexColor('#252525'),wordWrap='CJK')
def para(text,y,width=515.3,x=40,size=None):
 st=STYLE if size is None else ParagraphStyle('s',parent=STYLE,fontSize=size,leading=size*1.4)
 p=Paragraph(text,st);pw,ph=p.wrap(width,1000);p.drawOn(c,x,y-ph);return y-ph
def head(label,y):
 c.setFillColor(HexColor('#226287'));c.setFont('HanBold',10.2);c.drawString(40,y,label);return y-9
def line_text(text,x,y,size=8.3):
 c.setFillColor(HexColor('#555555'));c.setFont('Han',size);c.drawString(x,y,text)
c.setFont('HanBold',19);c.setFillColor(HexColor('#161616'));c.drawString(40,799,'电阻膜微波吸收结构的仿真与优化')
line_text('周子靖｜哈尔滨工业大学应用物理学｜本科毕业设计，2026.05完成',40,779,9)
line_text('指导教师：李均教授｜zhouzijing54@gmail.com',40,764,9)
c.setStrokeColor(HexColor('#BBBBBB'));c.setLineWidth(.6);c.line(40,751,W-40,751)
y=head('01  研究问题',731)
y=para('如何在周期单元的几何约束下，通过电阻膜图案、尺寸与片阻的联合搜索拓宽低反射频带，并保持建模和评价条件一致？',y)
y=head('02  物理结构与仿真设置',y-23)
y=para('金属背板上两块正交PET支撑电阻膜；周期单元、正入射。比较薄实体膜与Ohmic Sheet，后续分阶段搜索采用后者。',y)
top=y-7; panel_h=140;left_w=245
im=ImageReader(str(HERE/'structure_original.png'));iw,ih=im.getSize();ratio=min(left_w/iw,panel_h/ih)
c.drawImage(im,40+(left_w-iw*ratio)/2,top-panel_h+(panel_h-ih*ratio)/2,width=iw*ratio,height=ih*ratio)
plot_rect=fitz.Rect(302,H-top,W-36,H-(top-panel_h))
y=top-panel_h-13
line_text('原项目CST结构截图（毕设图6.2）',40,y,8)
line_text('归档曲线；非实验测量，非总吸收',307,y,8)
y=head('03  计算工作流',y-25)
# A compact, schematic SVG and matching native PDF vector drawing.
scale=1;fx=40;fy=y-104
nodes=[(0,20,78,27,['结构参数','图案 / 尺寸 / 片阻']),
       (107,20,70,27,['候选生成']), (207,20,77,27,['几何约束筛选']),
       (318,20,80,27,['CST模型']), (429,20,86,27,['频域求解']),
       (429,72,86,27,['S参数 / 同模反射']), (315,72,90,27,['适应度评价']),
       (159,72,127,27,['GA选择 / 交叉 / 变异']), (22,72,103,27,['下一代'])]
sv=['<svg xmlns="http://www.w3.org/2000/svg" width="182mm" height="44mm" viewBox="-5 -12 525 127">','<rect x="-5" y="-12" width="525" height="127" fill="white"/>','<g font-family="Source Han Sans CN, sans-serif" font-size="8.2" fill="#252525">']
def sy(v):return fy+104-v
for x,yy,w,hh,labels in nodes:
 c.setStrokeColor(HexColor('#9AA3AA'));c.setFillColor(HexColor('#FFFFFF'));c.setLineWidth(.65);c.rect(fx+x,sy(yy+hh),w,hh,stroke=1,fill=1)
 sv.append(f'<rect x="{x}" y="{yy}" width="{w}" height="{hh}" stroke="#9AA3AA" fill="white" stroke-width=".65"/>')
 for j,label in enumerate(labels):
  yytext=yy+(12 if len(labels)>1 else 16)+j*10
  size=7.1 if j else 8.2
  c.setFont('Han',size);c.setFillColor(HexColor('#252525'));c.drawCentredString(fx+x+w/2,sy(yytext),label)
  sv.append(f'<text x="{x+w/2}" y="{yytext}" text-anchor="middle" font-size="{size}">{escape(label)}</text>')
def arr(points):
 c.setStrokeColor(HexColor('#5D6871'));c.setLineWidth(.7)
 path=c.beginPath();path.moveTo(fx+points[0][0],sy(points[0][1]))
 for px,py in points[1:]:path.lineTo(fx+px,sy(py))
 c.drawPath(path)
 x1,y1=points[-2];x2,y2=points[-1];a=math.atan2(y2-y1,x2-x1)
 tri=[(x2,y2),(x2-4*math.cos(a)+1.8*math.sin(a),y2-4*math.sin(a)-1.8*math.cos(a)),(x2-4*math.cos(a)-1.8*math.sin(a),y2-4*math.sin(a)+1.8*math.cos(a))]
 p=c.beginPath();p.moveTo(fx+tri[0][0],sy(tri[0][1]));[p.lineTo(fx+x,sy(z)) for x,z in tri[1:]];p.close();c.setFillColor(HexColor('#5D6871'));c.drawPath(p,stroke=0,fill=1)
 sv.append('<polyline points="'+' '.join(f'{x},{z}' for x,z in points)+'" fill="none" stroke="#5D6871" stroke-width=".7"/>')
 sv.append('<polygon points="'+' '.join(f'{x},{z}' for x,z in tri)+'" fill="#5D6871"/>')
for p in [[(78,33.5),(107,33.5)],[(177,33.5),(207,33.5)],[(284,33.5),(318,33.5)],[(398,33.5),(429,33.5)],[(472,47),(472,72)],[(429,85.5),(405,85.5)],[(315,85.5),(286,85.5)],[(159,85.5),(125,85.5)],[(22,85.5),(8,85.5),(8,59),(142,59),(142,47)],[(245,20),(245,6),(142,6),(142,20)]]:arr(p)
line_text('不合格：重新生成',fx+156,sy(1),7)
sv.append('<text x="156" y="1" font-size="7" fill="#555555">不合格：重新生成</text></g></svg>')
(HERE/'workflow.svg').write_text('\n'.join(sv),encoding='utf-8')
y=fy-9
y=para('逻辑摘要：达到终止条件后保存结果；图示不代表提出新算法。',y,size=8)
y=head('04  我的贡献',y-22)
for s in ['<b>自动化：</b>基于课题组初始结构与学长参考代码，扩展Python-CST自动建模、求解调用与响应提取；编码和调试使用AI辅助。',
 '<b>搜索与筛选：</b>扩展图案、几何和双向片阻变量，调整6×6、9×9、12×12分阶段搜索及连通性等几何约束筛选。',
 '<b>建模分析：</b>处理和可视化数据，对比薄实体膜与Ohmic Sheet的反射响应及优化结果。结构原型、遗传算法和电磁求解器均非本人发明。']:
 y=para(s,y)-4
y=head('05  已归档结果',y-18)
y=para('保存的201点曲线（2–18 GHz，间隔0.08 GHz）在<b>4.80–18.00 GHz</b>采样区间同模反射低于−10 dB，区间宽<b>13.20 GHz</b>；18 GHz为扫描上限。该结果不等同于已验证的总吸收带宽。',y)
y=head('06  局限与后续改进',y-23)
y=para('全反射通道/功率平衡、网格与频率收敛、实验验证仍待完成。现阶段回看，应先完善这些验证，再评估代理模型辅助搜索；后者不是已完成工作。',y)
assert y>45,('overflow',y)
c.setStrokeColor(HexColor('#CCCCCC'));c.line(40,36,W-40,36)
line_text('v1 INTERNAL · 人工审查稿，不外发',40,23,7.5)
c.save()
pdf=fitz.open(stream=buffer.getvalue(),filetype='pdf');plot=fitz.open(OUT/'reflection.pdf');pdf[0].show_pdf_page(plot_rect,plot,0)
pdf.save(OUT/(name+'.pdf'),garbage=4,deflate=True)
pdf[0].get_pixmap(dpi=300).save(OUT/(name+'.png'))
print('one-page PDF, bottom text y=',y)
