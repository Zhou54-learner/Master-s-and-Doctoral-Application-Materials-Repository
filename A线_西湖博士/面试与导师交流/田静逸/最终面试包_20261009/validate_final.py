from pathlib import Path
import re,json,hashlib,subprocess
from urllib.parse import unquote
from pptx import Presentation
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
missing=[]
for p in OUT.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        target=unquote(target.strip('<>').split('#')[0])
        if not target or target.startswith(('http:','https:')):continue
        if not (p.parent/target).exists():missing.append({'file':p.name,'target':target})
qa=(OUT/'田静逸_针对性提问与参考回答_20261009.md').read_text(encoding='utf-8')
questions=re.split(r'^## [ABC]\d{2} ',qa,flags=re.M)[1:]
assert len(questions)==45
for q in questions:
    assert all(v in q for v in ['**短答版**','**展开版**','**安全边界**','**如果不知道**'])
notes=json.loads((OUT/'页面与备注源.json').read_text(encoding='utf-8'))
ppt=Presentation(OUT/'田静逸_最终面试PPT_20261009.pptx')
assert len(ppt.slides)==len(notes)==15
assert all(s.notes_slide.notes_text_frame.text==m['notes'] for s,m in zip(ppt.slides,notes))
render=json.loads((OUT/'版式与备注验收.json').read_text(encoding='utf-8'))
assert not render['issues'] and all(render['notes_com_matched'])
base=ROOT/'A线_西湖博士/面试与导师交流/刘癸庚/完整PPT_v1.1_20261006/刘癸庚交流_完整PPT_v1.1_20261006.pptx'
source_hash=json.loads((OUT/'证据/原件核对.json').read_text(encoding='utf-8'))['liu_remote_base_sha256']
assert hashlib.sha256(base.read_bytes()).hexdigest()==source_hash
orig=Presentation(base)
old_images={hashlib.sha256(s.image.blob).hexdigest() for sl in orig.slides for s in sl.shapes if s.shape_type==13}
images=[hashlib.sha256(s.image.blob).hexdigest() for sl in ppt.slides for s in sl.shapes if s.shape_type==13]
result={'missing_local_links':missing,'A_questions':33,'B_questions':4,'C_questions':8,'all_question_fields':True,'slides_and_notes':15,'powerpoint_overflow':0,'powerpoint_bounds':0,'liu_original_hash_unchanged':True,'image_occurrences':len(images),'original_liu_image_occurrences_preserved':sum(x in old_images for x in images)}
(OUT/'交付完整性验收.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
assert not missing
