"""Build four independent v2 candidates, plus a second actual S10 crop option.
Only existing-image rectangular crops; all slide text/shapes remain editable.
"""
from pathlib import Path
import json,hashlib,shutil,argparse
_parser=argparse.ArgumentParser()
_parser.add_argument("--only",choices=["S10","S11","S12","S13"])
ONLY=_parser.parse_args().only
from PIL import Image
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.oxml.xmlchemy import OxmlElement

REVIEW=Path(__file__).resolve().parent.parent
PI=REVIEW.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
FACTS=ROOT/'公共资料/事实核验/个人探索_20261006'
NAMES=json.loads((REVIEW/'候选目录.json').read_text(encoding='utf8'))
INK,MUTED,TEAL,LINE='172B43','5C6D7E','007E86','D8E1E8'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')

def tx(s,name,x,y,w,h,content,size=20,color=INK,bold=False,align=PP_ALIGN.LEFT):
    sh=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));sh.name=name
    tf=sh.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    for i,l in enumerate(content.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=l
        p.alignment=align;p.space_before=p.space_after=Pt(0);p.line_spacing=1.18
        for r in p.runs:
            r.font.name='Microsoft YaHei';r.font.size=Pt(size);r.font.bold=bold
            r.font.color.rgb=RGBColor.from_string(color)
            ea=OxmlElement('a:ea');ea.set('typeface','Microsoft YaHei');r._r.get_or_add_rPr().append(ea)
    return sh

def base(key,title,subtitle='',section=''):
    p=Presentation();p.slide_width=Inches(13.333333);p.slide_height=Inches(7.5)
    p.core_properties.title=title;p.core_properties.author='Zijing Zhou'
    p.core_properties.subject=f'{key} | INTERNAL / v2 CANDIDATE | 2026-10-06'
    s=p.slides.add_slide(p.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=RGBColor(255,255,255)
    if section:tx(s,'section',.55,.24,10,.26,section,11,MUTED)
    tx(s,'title',.55,.65,12.25,.72,title,28,INK,True)
    if subtitle:tx(s,'subtitle',.58,1.43,12.1,.33,subtitle,13,MUTED)
    rule=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(.55),Inches(7.04),Inches(12.8),Inches(7.04))
    rule.name='footer_rule';rule.line.color.rgb=RGBColor.from_string(LINE);rule.line.width=Pt(.5)
    rule._element.spPr.append(OxmlElement('a:effectLst'))
    tx(s,'slide_number',12.16,7.09,.65,.36,key,15,TEAL,True,PP_ALIGN.RIGHT)
    return p,s

def pic(s,path,name,x,y,w,h):
    im=Image.open(path);k=min(w/im.width,h/im.height);iw,ih=im.width*k,im.height*k
    sh=s.shapes.add_picture(str(path),Inches(x+(w-iw)/2),Inches(y+(h-ih)/2),width=Inches(iw));sh.name=name
    return sh

def derive(out,source,box,name,reason):
    image=Image.open(source);target=out/'派生素材'/name
    image.crop(box).save(target)
    return target,dict(source=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),source_pixels=list(image.size),
                       crop_box=list(box),output=target.relative_to(out).as_posix(),pixels=list(Image.open(target).size),
                       sha256=sha(target),reason=reason,operation='Lossless rectangular crop of decoded source pixels; no redrawing, synthesis, retouching or sharpening.')

def save(p,s,out,stem,notes):
    s.notes_slide.notes_text_frame.text=notes
    p.save(out/(stem+'.pptx'))

instruction=(PI/'S10-S13_v2制作指令_20261006.md').read_text(encoding='utf8')
def quotes_between(start,end):
    part=instruction.split(start,1)[1].split(end,1)[0]
    return '\n'.join(l[2:] if l.startswith('> ') else '' for l in part.splitlines() if l.startswith('>')).strip()

notes10='''# S10｜本页备注

INTERNAL / v2 CANDIDATE｜2026-10-06。以下主述取本轮制作指令，两个裁切方案共用同一段话。

## 主述

'''+quotes_between('## 1.5 口述建议','---')+'''

## 接回与翻页

从S9直接接“做这些东西的时候”。若被打断：“这篇先把当时的问题留下来，我还没有一个成熟结论。”再转“有些想法不只会写下来，我也会试着做成页面”。不改S9原备注。

## 素材与边界

旧S03截图没有首篇完整条目。本轮使用本人2026-10-06新补图，包含公众号身份、完整文章标题及“和GPT聊了一个问题”。“第一篇”来自本人制作指令的确认；截图中的“80天前”保持历史画面，不反推具体日期或年份。公众号文章逐字的人/AI分工仍未核清；不声称完全独立创作或成熟理论。只讲为什么会记录这些问题，不展开文章观点或运营指标。
'''
notes11='''# S11｜本页备注

INTERNAL / v2 CANDIDATE｜2026-10-06。已恢复真实首页，未使用HUMAN+第三板块冒充封面。

## 主述

'''+quotes_between('## 2.5 口述建议','---')+'''

## 接回与翻页

如被追问：“这里是个人艺术网页的入口，我主要想展示的是整个页面空间；现有截图不能证明每一项交互或服务都已验证。”

接S12：“这些东西和前面的科研项目其实不太一样，但它们确实一直在帮我想一件事：我以后到底想把什么能力真正练出来。”

## 素材与边界

首页采用本人2026-10-06新补的1919×989真实截图，整张保留浏览器边界、站名、页面介绍、两个入口与空间关系。先前从2026-10-04素材包恢复的600×309副本继续保留为历史证据，本候选已使用新图；另提供的“知识与未来的对话.png”是公众号文章封面，不作为网页首页。不推定完整网站已全面测试或人/AI分工。画面里的链接/按钮不作为虚构交互演示。未把它提升为成熟产品或开发能力清单。
'''
original=(PI/'Why_PhD母稿_用户原文_20261005.md').read_text(encoding='utf8').strip()
notes12='''# S12｜本页备注

INTERNAL / v2 CANDIDATE｜2026-10-06。本人原始Why PhD母稿完整保留，未删节、未重写。三句页面只是提示，不要求按版面逐句读，也无硬时长。

## 本人原文

'''+original+'''

## 被打断后接回（辅助提示，不替代原文）

停在兴趣：“另一方面是基于我对AI时代的思考。”
停在AI时代能力：“我的毕业设计就是一个具体例子。”
停在毕设短板：接本人最后一段，保留不寻找“AI永远不会”的固定技能这一边界，落到长期深入、对结论负责及研究品味。

下一页从“如果把这个想法落到具体方向上”接起。不用框架词重新概括本人动机。
'''
notes13='''# S13｜本页备注

INTERNAL / v2 CANDIDATE｜2026-10-06。主述采用本轮制作指令4.4的v3，覆盖前一天口述和v1轻量节奏；不为20–30秒删稿。

## 主述 v3

'''+quotes_between('## 4.4 S13 口述建议 v3','## 4.5')+'''

## 被打断后接回

问工具或GA：“这些工具后面仍然会继续用。我现在更想追问的是为什么出现这个响应，以及应该怎么验证。”
问组内方向：“拓扑和非厄米目前是希望系统学习的问题，不是已有理论能力。”
问培养：“我看重的是围绕一个方向长期做深。定导培养来自西湖物理学科官方说明，个人具体招生学科和培养安排仍以学校及导师确认。”

## 来源与边界

西湖官方教师页支持组名；课题组首页支持拓扑/非厄米、光子晶体、超材料及重视机制与器件实现；西湖物理学科研究生培养页明确“定导招生培养模式”。已于2026-10-06重新核对，见README与官方来源记录。该培养事实只用于Westlake Physics，不外推所有学科，也不据此改变本人申请项目键或获得课题/指导承诺。

模式、边界、损耗、可靠性来自本人毕设复盘的问题组织；不把当前认识倒写为历史已完成的机理验证。不把工具与物理对立，不使用“高度匹配”“训练接口”“能力迁移”作为台前语言。
'''
allnotes={'S10':notes10,'S11':notes11,'S12':notes12,'S13':notes13}
for key,dirname in NAMES.items():
    if ONLY in (None,key):(PI/dirname/'本页备注.md').write_text(allnotes[key],encoding='utf8')

if ONLY in (None,'S10'):
    out=PI/NAMES['S10'];source=FACTS/'素材/公众号首篇文章_用户补图_20261006.jpg'
    first,f1=derive(out,source,(22,1396,1110,2228),'A_首篇完整条目.png','Keeps full first-article card: account identity, relative date, cover with GPT dialogue marker and complete title.')
    context,f2=derive(out,source,(22,598,1110,2228),'B_两条文章上下文.png','Keeps two adjacent real article cards and repeated account identity. Omits phone status bar and unrelated channels.')
    title,f3=derive(out,source,(45,2030,1075,2180),'B_首篇标题局部.png','Same screenshot first article title; real pixels only, no text re-layout.')
    for variant in ['A','B']:
        p,s=base('S10','我也会把这些问题写下来','“无用清静梦” · 个人公众号','个人探索')
        if variant=='A':
            pic(s,first,'first_article',2.86,1.97,7.60,4.85)
            assets=[dict(f1,shape_name='first_article')]
            stem='S10_反思_v2'
        else:
            pic(s,context,'article_list',1.25,1.93,3.20,4.93)
            tx(s,'detail_label',5.23,4.60,6.4,.29,'同一截图 · 首篇标题局部',11,MUTED)
            pic(s,title,'title_detail',5.20,5.08,6.83,1.28)
            assets=[dict(f2,shape_name='article_list'),dict(f3,shape_name='title_detail')]
            stem='S10_反思_v2_方案B'
        tx(s,'source_footer',.55,7.15,11.4,.23,'本人补充的历史截图 · 首篇文章条目',9,MUTED)
        save(p,s,out,stem,notes10)
        write(out/f'{stem}_图片索引.json',assets)
    write(out/'派生素材说明.json',[f1,f2,f3])

if ONLY in (None,'S11'):
    out=PI/NAMES['S11'];home=FACTS/'素材/个人艺术网页首页_用户补图_20261006.png'
    image,info=derive(out,home,(0,0,*Image.open(home).size),'无用清净梦_完整首页.png','Full user-supplied homepage screenshot, including browser, site identity, introduction and both entrances. No reconstruction.')
    p,s=base('S11','有些想法，我也会试着把它做成页面','个人艺术网页 · 无用清净梦','个人探索')
    pic(s,image,'homepage',.63,1.94,12.05,4.88)
    tx(s,'source_footer',.55,7.15,11.5,.23,'本人提供的网页截图 · 整站入口',9,MUTED)
    save(p,s,out,'S11_表达_v2',notes11)
    write(out/'派生素材说明.json',[info]);write(out/'S11_表达_v2_图片索引.json',[dict(info,shape_name='homepage')])

if ONLY in (None,'S12'):
    out=PI/NAMES['S12'];p,s=base('S12','为什么我还想继续深造',section='下一阶段')
    tx(s,'opening_sentence',.76,2.00,11.85,1.32,'我想继续深造，其实和我本科这几年\n做的一些事情是连在一起的。',27,INK,True)
    tx(s,'curiosity',.78,3.88,11.65,.99,'我喜欢从一个模糊的问题出发，\n慢慢把它变成可以研究、可以实现的东西。',20,MUTED)
    tx(s,'limits',.78,5.10,11.65,.99,'但做得越多，我越觉得自己真正缺的是\n理论深度和专业判断。',20,INK)
    tx(s,'long_term',.79,6.54,11.8,.35,'我想在一个领域里长期做深，最后能真正对自己的判断和结论负责。',14.5,TEAL)
    save(p,s,out,'S12_WhyPhD_v2',notes12);write(out/'派生素材说明.json',[]);write(out/'S12_WhyPhD_v2_图片索引.json',[])

if ONLY in (None,'S13'):
    out=PI/NAMES['S13'];p,s=base('S13','我接下来更想把物理问题做深',section='下一阶段')
    tx(s,'experience',.80,1.81,11.7,.48,'电磁仿真 / 周期结构 / 数值优化',19,MUTED)
    tx(s,'step1',.84,2.47,.50,.32,'↓',16,TEAL)
    tx(s,'question',.78,2.97,11.70,.75,'为什么会出现这样的响应？',30,INK,True)
    tx(s,'step2',.84,3.86,.50,.32,'↓',16,TEAL)
    tx(s,'physics_questions',.80,4.32,11.7,.54,'模式 · 边界 · 损耗 · 可靠性',23,INK)
    tx(s,'step3',.84,5.01,.50,.32,'↓',16,TEAL)
    tx(s,'lab',.80,5.46,11.7,.51,'Complex Waves and Fields',22,TEAL)
    tx(s,'learning_boundary',.82,6.19,11.5,.33,'topology / non-Hermitian：希望系统学习',14,MUTED)
    tx(s,'westlake',.57,7.15,11.5,.23,'Westlake Physics · 定导培养',9,MUTED)
    save(p,s,out,'S13_WhyLiu_v2',notes13);write(out/'派生素材说明.json',[]);write(out/'S13_WhyLiu_v2_图片索引.json',[])

for key,dirname in NAMES.items():
    target=PI/dirname/'制作源/build_slide.py'
    target.write_text(f'''"""Build this selected v2 slide only; archived v1 and S0-S9 are never executed or edited."""\nfrom pathlib import Path\nimport runpy,sys\nsource=Path(__file__).resolve().parents[2]/'S10-S13_联合审阅_v2_20261006/制作源/build_v2.py'\nsys.argv=[str(source),'--only','{key}']\nrunpy.run_path(str(source),run_name='__main__')\n''',encoding='utf8')
print('Built S10 A/B, S11 homepage, S12 quiet narrative, S13 question progression.')
