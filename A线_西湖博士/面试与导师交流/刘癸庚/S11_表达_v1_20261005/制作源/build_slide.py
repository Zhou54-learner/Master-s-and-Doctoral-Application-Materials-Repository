"""Independent editable slide builder. Run a candidate's build_slide.py.
python-pptx + Pillow; source evidence stays read only. MS PowerPoint handles rendering.
"""
from pathlib import Path
import hashlib, json
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_CONNECTOR, MSO_AUTO_SHAPE_TYPE
from pptx.oxml.xmlchemy import OxmlElement

OUT=Path(__file__).resolve().parent.parent
PI=OUT.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
CFG=json.loads((OUT/'制作源/config.json').read_text(encoding='utf-8'))
KEY=CFG['slide']
INK,MUTED,TEAL,LINE='172B43','5C6D7E','007E86','D8E1E8'
ASSETS=ROOT/'公共资料/事实核验/个人探索_20261004/素材'
DERIVED=[]

def tx(s,name,x,y,w,h,content,size=20,color=INK,bold=False,align=PP_ALIGN.LEFT):
    shape=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));shape.name=name
    tf=shape.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    for i,line in enumerate(content.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.text=line;p.alignment=align;p.space_before=p.space_after=Pt(0);p.line_spacing=1.15
        for r in p.runs:
            r.font.name='Microsoft YaHei';r.font.size=Pt(size);r.font.bold=bold
            r.font.color.rgb=RGBColor.from_string(color)
            ea=OxmlElement('a:ea');ea.set('typeface','Microsoft YaHei');r._r.get_or_add_rPr().append(ea)
    return shape

def line(s,name,x1,y1,x2,y2,color=LINE,width=1):
    sh=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1),Inches(y1),Inches(x2),Inches(y2))
    sh.name=name;sh.line.color.rgb=RGBColor.from_string(color);sh.line.width=Pt(width)
    return sh

def base(title,subtitle,section,stage,footer):
    p=Presentation();p.slide_width=Inches(13.333333);p.slide_height=Inches(7.5)
    p.core_properties.title=title;p.core_properties.author='Zijing Zhou'
    p.core_properties.subject=f'{KEY} | INTERNAL / v1 CANDIDATE | 2026-10-05'
    s=p.slides.add_slide(p.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=RGBColor(255,255,255)
    tx(s,'section',.55,.24,5,.25,section,11,MUTED)
    tx(s,'stage',7.1,.27,5.7,.24,stage,9.5,MUTED,False,PP_ALIGN.RIGHT)
    tx(s,'title',.55,.65,12.25,.70,title,28,INK,True)
    if subtitle:tx(s,'subtitle',.58,1.40,12,.36,subtitle,13,MUTED)
    line(s,'footer_rule',.55,7.04,12.8,7.04,width=.7)
    tx(s,'source_footer',.55,7.15,11.55,.23,footer,9,MUTED)
    tx(s,'slide_number',12.16,7.09,.65,.35,KEY,15,TEAL,True,PP_ALIGN.RIGHT)
    return p,s

def crop(name,box,target,reason):
    src=ASSETS/name;img=Image.open(src);dest=OUT/'派生素材'/target
    img.crop(box).save(dest)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    DERIVED.append(dict(source=src.relative_to(ROOT).as_posix(),source_sha256=digest(src),source_pixels=list(img.size),
                        crop_box=list(box),output=dest.relative_to(OUT).as_posix(),pixels=list(Image.open(dest).size),
                        sha256=digest(dest),reason=reason,operation='Lossless rectangular crop only; no synthesis, redrawing, inpainting or pixel editing.'))
    return dest

def image_fit(s,path,name,x,y,w,h):
    im=Image.open(path);k=min(w/im.width,h/im.height)
    iw,ih=im.width*k,im.height*k
    sh=s.shapes.add_picture(str(path),Inches(x+(w-iw)/2),Inches(y+(h-ih)/2),width=Inches(iw));sh.name=name
    return sh

def build():
    if KEY=='S0':
        p,s=base('', '', '科研交流', 'INTERNAL / v1 CANDIDATE', '刘癸庚老师课题组交流 · 独立封面候选')
        tx(s,'cover_title',.80,2.00,11.7,.85,'科研经历与个人探索',38,INK,True)
        line(s,'accent',.82,3.22,2.1,3.22,TEAL,3)
        tx(s,'name',.82,3.67,6,.62,'周子靖  /  Zijing Zhou',24,INK)
        tx(s,'education',.84,4.50,10,.44,'哈尔滨工业大学 · 应用物理学本科',20,MUTED)
        tx(s,'occasion',.84,5.45,11,.36,'与刘癸庚老师课题组的科研交流',15,MUTED)
    elif KEY=='S1':
        p,s=base('我的起点：物理背景与实际问题','用几段研究和探索经历，介绍我怎样接触并推进问题',
                 '个人背景','BACKGROUND','教育与经历口径见公共事实核验 · INTERNAL / v1 CANDIDATE')
        tx(s,'name',.65,2.18,4.4,.66,'周子靖',30,INK,True)
        tx(s,'english_name',.68,2.95,4.3,.35,'Zijing Zhou',16,MUTED)
        tx(s,'education',.65,3.66,4.5,1.16,'哈尔滨工业大学 · 物理学院\n应用物理学本科',19,INK)
        tx(s,'start_label',.67,5.30,4.3,.38,'Physics background',16,TEAL)
        line(s,'division',5.37,2.20,5.37,6.52,width=1)
        for i,(y,t,d) in enumerate([(2.20,'本科毕设','电磁结构 · 参数化仿真\nPython–CST 数值工作流'),
                                    (3.84,'合作科研','数值数据处理 · 轨迹可视化'),
                                    (5.25,'个人探索','从现象到数据\n也尝试新的工具与表达')]):
            tx(s,f'number_{i}',5.82,y,.47,.38,f'0{i+1}',15,TEAL,True)
            tx(s,f'experience_{i}',6.51,y,6.0,.45,t,22,INK,True)
            tx(s,f'experience_detail_{i}',6.52,y+.58,6.0,.86,d,18,MUTED)
    elif KEY=='S10':
        p,s=base('使用技术，也持续追问人的位置','“无用清净梦” · 关于 AI、学习、工作与个体的长期记录',
                 '个人探索','反思  /  REFLECTION','本人历史截图 S03 · 真实文章条目局部，保留 AI 对话标识')
        pic=crop('S03_无用清净梦.png',(20,856,962,1518),'S03_真实文章条目局部.png',
                 'Keeps original date, full article cover including AI dialogue markers, and title; omits account metrics and readership counts.')
        image_fit(s,pic,'historical_article',.60,1.94,6.62,4.74)
        tx(s,'question_label',7.64,2.38,4.94,.35,'一篇真实记录里的问题',14,MUTED)
        tx(s,'question',7.62,3.10,5.15,2.08,'当完成任务\n越来越不需要人，\n工作还意味着什么？',24,INK,True)
        line(s,'question_accent',7.66,5.67,8.44,5.67,TEAL,2.4)
        tx(s,'evidence_caption',.63,6.74,11.8,.25,'原条目保留日期、标题与 AI 对话语境',11,MUTED)
    elif KEY=='S11':
        p,s=base('把思考组织成可以被感知的表达','个人艺术网页 · HUMAN+ 第三个板块',
                 '个人探索','表达  /  EXPRESSION','本人历史截图 S08 · 第三个板块主视觉局部 · 页面文案不代表服务已验证')
        pic=crop('S08_个人艺术网页第三板块.png',(178,139,1730,748),'S08_第三板块主视觉局部.png',
                 'Keeps HUMAN+ identity, main verbal composition, original buttons and circular visual; removes top navigation, lower column and browser scrollbar without changing the remaining pixels.')
        image_fit(s,pic,'historical_webpage',.59,1.97,12.14,4.77)
        tx(s,'expression_sentence',.65,6.75,11.9,.26,'把抽象想法同时组织成文字、视觉与页面。',12,TEAL)
    elif KEY=='S12':
        p,s=base('为什么我想继续接受科研训练','从自己真实做过的事情出发，也从重新看见的短板出发',
                 '下一阶段','WHY PhD','本人原始 Why PhD 母稿完整写入 speaker notes · INTERNAL / v1 CANDIDATE')
        xs=[.70,3.78,6.86,9.94]
        line(s,'story_line',.82,2.70,12.26,2.70,LINE,1.2)
        entries=[('好奇与探索','从模糊问题走向\n可研究的问题'),('AI 时代','未来真正需要人的\n什么能力？'),
                 ('毕设复盘','实现能力 ≠ 理论理解\n与结果可信度'),('长期科研训练','在一个领域深入\n接受导师与同行的挑战')]
        for i,(x,(t,d)) in enumerate(zip(xs,entries)):
            dot=s.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL,Inches(x),Inches(2.63),Inches(.14),Inches(.14))
            dot.name=f'story_dot_{i}';dot.fill.solid();dot.fill.fore_color.rgb=RGBColor.from_string(TEAL);dot.line.fill.background()
            tx(s,f'story_title_{i}',x,2.02,2.75,.52,t,21,INK,True)
            tx(s,f'story_detail_{i}',x,3.13,2.83,1.11,d,16.5,MUTED)
        tx(s,'training_label',.72,4.76,2.8,.33,'我希望训练',14,TEAL)
        tx(s,'training_goals',.70,5.26,12.0,.55,'提出问题 · 定义问题 · 判断结果 · 识别错误 · 决定下一步',22,INK,True)
        tx(s,'research_taste',.72,5.99,11.6,.43,'对结论负责，在长期深入中形成研究判断与研究品味',19,TEAL)
        tx(s,'ai_boundary',.74,6.61,11.5,.30,'这不是去寻找一组“AI 永远不会”的固定技能。',12.5,MUTED)
    elif KEY=='S13':
        p,s=base('下一步：更深入地理解波和场','Westlake University · Laboratory of Complex Waves and Fields',
                 '下一阶段','WHY LIU / WESTLAKE','组名与研究方向：西湖官方教师页 / 课题组主页 · 2026-10-05 核对')
        tx(s,'start',.74,2.27,3.95,.40,'已有起点',17,MUTED)
        tx(s,'experience',.72,3.04,4.24,2.80,'电磁结构\n参数化仿真\nPython–CST 自动化\n参数搜索 / 数值分析',21,INK)
        tx(s,'performance_physics',5.07,3.44,2.6,.43,'performance → physics',12.6,TEAL,True,PP_ALIGN.CENTER)
        line(s,'bridge',5.38,4.21,7.30,4.21,TEAL,1.5)
        tx(s,'bridge_arrow',7.20,3.98,.38,.43,'›',22,TEAL)
        tx(s,'future',8.00,2.27,4.78,.40,'希望深入',17,TEAL)
        tx(s,'physics',7.98,3.03,4.78,1.67,'波与模式\n边界与损耗\n物理机制',23,INK,True)
        tx(s,'complex_waves',8.00,5.04,4.82,.42,'Complex Waves and Fields',16,TEAL)
        tx(s,'learning_boundary',8.00,5.59,4.82,.70,'希望系统学习：topology / non-Hermitian\n这些理论还需要补足',12,MUTED)
        tx(s,'westlake_preference',.73,6.57,11.9,.34,'在西湖：希望进入以科研训练为核心的环境',14,MUTED)
    else: raise ValueError(KEY)
    s.notes_slide.notes_text_frame.text=(OUT/'本页备注.md').read_text(encoding='utf-8')
    p.save(OUT/(CFG['stem']+'.pptx'))
    (OUT/'派生素材说明.json').write_text(json.dumps(DERIVED,ensure_ascii=False,indent=2),encoding='utf-8')
    print(KEY,'built',len(s.shapes),'editable objects')

if __name__=='__main__':build()
