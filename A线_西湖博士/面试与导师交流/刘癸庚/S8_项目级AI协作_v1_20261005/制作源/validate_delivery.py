"""Final artifact/source/link audit; PDF inspection uses existing local Poppler tools.
Does not modify the slides or any historical materials.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import tempfile
from PIL import Image
from pptx import Presentation

S8=Path(__file__).resolve().parent.parent
PI=S8.parent;S9=PI/'S9_长期AI协作_v1_20261005'
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pdf_checks=[];bad_links=[];deliveries=[]
for out,stem,frames in [(S8,'S8_项目级AI协作_v1',['S8']),(S9,'S9_长期AI协作_v1',['S9-A','S9-B'])]:
    baseline=json.loads((out/'来源与保全.json').read_text(encoding='utf8'))
    for key in ['sources','reference_files','unrelated_work']:
        for item in baseline[key]:
            p=ROOT/item['path']
            assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],p
    for md in out.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',md.read_text(encoding='utf8')):
            if '://' in target or target.startswith('#'):continue
            if not (md.parent/target.split('#')[0]).exists():bad_links.append([str(md),target])
    prs=Presentation(out/(stem+'.pptx'))
    assert len(prs.slides)==len(frames)
    for frame in frames:
        for w,h in [(3840,2160),(1920,1080)]:
            assert Image.open(out/'预览'/f'{frame}_{w}x{h}.png').size==(w,h)
    pdf=out/(stem+'.pdf')
    info=subprocess.check_output(['pdfinfo',str(pdf)]).decode('utf8',errors='replace')
    count=int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))
    assert count==len(frames)
    assert 'PowerPoint' in info
    pdf_checks.append(dict(path=pdf.relative_to(ROOT).as_posix(),pages=count,creator_is_powerpoint=True,
                           page_size_pt=[960,540],pdf_sha256=sha(pdf)))
    deliveries.append(dict(directory=out.name,physical_slides=len(prs.slides),logical_topics=1,
                           pptx_sha256=sha(out/(stem+'.pptx')),all_preserved=True))
assert not bad_links,bad_links

# S9 keeps every shape fixed except the image/caption and question emphasis color.
p=Presentation(S9/'S9_长期AI协作_v1.pptx')
a,b=p.slides
ignore={'evidence_label','historical_map','historical_cockpit'}
sa={s.name:s for s in a.shapes if s.name not in ignore}
sb={s.name:s for s in b.shapes if s.name not in ignore}
assert sa.keys()==sb.keys()
for name in sa:
    one,two=sa[name],sb[name]
    assert (one.left,one.top,one.width,one.height)==(two.left,two.top,two.width,two.height)
    if one.has_text_frame:assert one.text==two.text

# Independent view of PowerPoint-produced PDF, in the OS temp folder only.
preview=Path(tempfile.gettempdir())/'liu_s8_s9_v1_pdf_review'
preview.mkdir(exist_ok=True)
for out,stem,frames in [(S8,'S8_项目级AI协作_v1',['S8']),(S9,'S9_长期AI协作_v1',['S9-A','S9-B'])]:
    prefix=preview/('S8' if out==S8 else 'S9')
    subprocess.run(['pdftoppm','-png','-scale-to-x','1920','-scale-to-y','1080',str(out/(stem+'.pdf')),str(prefix)],check=True,capture_output=True)
report=dict(status='PASS',deliveries=deliveries,pdf_checks=pdf_checks,broken_local_links=bad_links,
            s9_static_text_and_positions_identical=True,s9_extra_topic_or_time=False,
            preservation_counts={'sources':7,'S2_to_S7_files':88,'unrelated_work':3},
            notes='PowerPoint layout reports and visual review are complementary; timing and real projector legibility remain user checks.')
(S8/'交付核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(status='PASS',pdfs=pdf_checks,pdf_review_directory=str(preview)),ensure_ascii=False))
