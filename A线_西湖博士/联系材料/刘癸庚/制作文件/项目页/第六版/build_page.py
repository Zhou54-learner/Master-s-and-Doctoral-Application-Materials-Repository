"""Compose an A4 research-experience sheet from vector panels."""
from pathlib import Path
import sys, io, argparse, re, json
HERE=Path(__file__).resolve().parent
W=next(p for p in HERE.parents if (p/'申请路线总览.md').exists())
sys.path.insert(0,str(W/'项目维护/工具/运行依赖'))
import pymupdf as fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.colors import HexColor

parser=argparse.ArgumentParser()
parser.add_argument('--output-dir',type=Path,default=HERE)
OUT=parser.parse_args().output_dir
OUT.mkdir(exist_ok=True,parents=True)
WID,HEI=595.276,841.89
NAME='周子靖_毕设项目页_刘癸庚版_v6'
PANELS=HERE.parent/'第四版/图件'
assert not (OUT/(NAME+'.pdf')).exists(), 'Preserve saved versions'
pdfmetrics.registerFont(TTFont('Han','C:/Windows/Fonts/SourceHanSansCNRegular.ttf'))
pdfmetrics.registerFont(TTFont('HanBold','C:/Windows/Fonts/SourceHanSansCNBold.ttf'))
pdfmetrics.registerFontFamily('Han',normal='Han',bold='HanBold')
buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(WID,HEI))
c.setTitle('周子靖｜电阻膜微波吸收结构的仿真与优化｜研究经历补充')
c.setAuthor('Zijing Zhou')
text_bounds=[]
def line(s,x,t,size=9,color='#555555',font='Han'):
    c.setFont(font,size);c.setFillColor(HexColor(color));c.drawString(x,HEI-t,s)
def para(s,t,x=40,width=515.3,size=10,leading=14.5,color='#252525'):
    st=ParagraphStyle('body',fontName='Han',fontSize=size,leading=leading,textColor=HexColor(color),wordWrap='CJK')
    q=Paragraph(s,st);_,hh=q.wrap(width,1000);q.drawOn(c,x,HEI-t-hh)
    text_bounds.append([t,t+hh,s]);return t+hh
def head(s,t):line(s,40,t,11,'#246889','HanBold')
line('电阻膜微波吸收结构的仿真与优化',40,47,20,'#171717','HanBold')
line('周子靖｜哈尔滨工业大学应用物理学｜本科毕业设计，2026.05完成',40,68,9.4)
line('指导教师：李均教授｜zhouzijing54@gmail.com',40,84,9.4)
c.setStrokeColor(HexColor('#C6CDD1'));c.setLineWidth(.6);c.line(40,HEI-97,WID-40,HEI-97)
head('研究目标',117)
end=para('围绕宽带微波吸收结构设计，研究电阻膜图案、几何尺寸与片阻的联合优化，以同模反射响应为评价量开展参数化仿真与结构搜索。',130)
assert end<166
head('结构与设计变量',177)
end=para('两片正交PET基底支撑图案化电阻膜，底部为金属背板；采用周期单元、正入射设置。设计变量包括图案、周期、高度及两片电阻膜各自的片阻。',189,size=9.5,leading=13.3)
assert end<218
geometry_rect=fitz.Rect(40,224,555.3,394)
para('依据最终参数与12×12图案数据绘制；着色区域为电阻膜。结构示意，非CST截图。',402,size=8.1,leading=11,color='#666666')
head('我的工作',434)
yy=447
items=[
 '<b>仿真流程：</b>基于课题组初始结构与参考代码，扩展Python–CST参数化建模、求解调用及响应提取流程。',
 '<b>搜索与筛选：</b>扩展图案、几何与两片电阻膜各自的片阻变量，调整6×6、9×9、12×12图案离散规模的分阶段搜索，并加入连通性等几何约束筛选。',
 '<b>模型与结果分析：</b>对比薄实体膜与Ohmic Sheet模型的反射响应和优化结果，完成批量数据处理与可视化。',
]
for s in items:yy=para(s,yy,size=9.8,leading=13.7)+5
assert yy<550,yy
head('主要仿真结果',530)
curve_rect=fitz.Rect(37,543,351,708)
line('同模反射低于 −10 dB',373,566,10,'#246889','HanBold')
line('4.80–18.00 GHz',373,592,17,'#252525','HanBold')
line('采样频率区间',373,609,8.8,'#666666')
line('13.20 GHz',373,654,19,'#246889','HanBold')
line('研究频窗内的采样带宽',373,671,8.8,'#666666')
para('正入射仿真；频窗2–18 GHz，步长0.08 GHz；18 GHz为扫描上限。<br/>评价量为同模反射，总吸收需另核全通道功率。',719,size=8.1,leading=11.3,color='#666666')
end=741.6
assert yy<525,yy
c.save()
d=fitz.open(stream=buf.getvalue(),filetype='pdf')
for rect,name in [(geometry_rect,'geometry.pdf'),(curve_rect,'reflection.pdf')]:
    panel=fitz.open(PANELS/name);d[0].show_pdf_page(rect,panel,0,keep_proportion=True)
d.save(OUT/(NAME+'.pdf'),garbage=4,deflate=True)
d[0].get_pixmap(dpi=300).save(OUT/(NAME+'.png'))
assert len(d)==1
for b in d[0].get_text('dict')['blocks']:
    if b['type']!=0:continue
    for ln in b['lines']:
        for span in ln['spans']:
            x0,y0,x1,y1=span['bbox'];assert x0>=0 and y0>=0 and x1<=WID+.1 and y1<=HEI+.1
assert not d[0].get_images(), 'This composition is vector only'
(OUT/'page_checks.json').write_text(json.dumps({'pages':1,'raster_images':0,'text_bounds':'PASS','contribution_end':yy,'page_text_end':end,'visual_review':'PENDING'},ensure_ascii=False,indent=2),encoding='utf-8')
print('A4 vector PDF exported; no research software invoked.')
