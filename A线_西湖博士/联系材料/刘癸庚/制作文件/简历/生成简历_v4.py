from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'A线工作区/核验/a4_runtime'))
from docx import Document
from docx.shared import Pt,RGBColor
from docx.oxml.ns import qn
B=ROOT/'A线工作区/联系/刘癸庚'
old=B/'02_CV/周子靖_中文学术简历_刘癸庚版_v3_CANDIDATE.docx'
if not old.exists():old=old.parent/'历史版本'/old.name
stem='周子靖_中文学术简历_刘癸庚版_v4'
target=B/'02_CV'/f'{stem}.docx'
assert not target.exists()
doc=Document(old)
score='算术均分：80.20/100*｜专业排名：21/46'
note='*均分按本科成绩单中的百分制课程作算术平均。'
for p in doc.paragraphs:
    if p.text.startswith('算术均分：'):
        p.clear();r=p.add_run(score);r.font.name='Source Han Sans CN Regular';r.font.size=Pt(10);r.font.color.rgb=RGBColor.from_string('222222');r._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Source Han Sans CN Regular')
    for r in p.runs:
        if '构建分阶段搜索流程' in r.text:r.text=r.text.replace('构建分阶段搜索流程','调整分阶段搜索流程')
for sec in doc.sections:
    footer=sec.footer
    for p in list(footer.paragraphs)[1:]:p._element.getparent().remove(p._element)
    fp=footer.paragraphs[0];fp.clear();r=fp.add_run(note);r.font.name='Source Han Sans CN Regular';r.font.size=Pt(8.5);r.font.color.rgb=RGBColor.from_string('444444');r._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Source Han Sans CN Regular')
doc.core_properties.title='周子靖｜中文学术简历'
doc.core_properties.subject=''
doc.core_properties.author='Zijing Zhou'
doc.core_properties.last_modified_by='Zijing Zhou'
doc.core_properties.comments=''
doc.core_properties.keywords=''
doc.core_properties.category=''
doc.save(target)
md=old.with_suffix('.md').read_text(encoding='utf-8').replace('算术均分：80.20/100*｜专业排名：21/46（前三年）*',score).replace('构建分阶段搜索流程','调整分阶段搜索流程')
md=md.replace('*均分按本科成绩单中的百分制课程作算术平均；排名依据2025年9月推免排名名单，四年总排名证明办理中。',note).replace('\n---\n刘癸庚定制 v3｜CANDIDATE｜待本人审查，未发送。','')
(B/'02_CV'/f'{stem}.md').write_text(md.rstrip()+'\n',encoding='utf-8')
print(target)
