"""Final targeted validation of delivered files, links, notes, and preserved inputs."""
from pathlib import Path
import hashlib,json,re,zipfile
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from PIL import Image

REVIEW=Path(__file__).resolve().parent.parent
PI=REVIEW.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
NAMES=json.loads((REVIEW/'候选目录.json').read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

baseline=json.loads((REVIEW/'制作前保全基线.json').read_text(encoding='utf8'))
entries=[x for cat in ['sources','reference_files','unrelated_work'] for x in baseline[cat]]
assert len(entries)==140
for x in entries:
    p=ROOT/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],x['path']
summaries=[];links=[]
for key,dirname in NAMES.items():
    out=PI/dirname;stem=dirname.rsplit('_20261005',1)[0]
    expected=[f'{stem}.pptx',f'{stem}.pdf','README.md','本页备注.md','来源与保全.json','派生素材说明.json',
              '排版与保全检查.json','制作源/build_slide.py','制作源/config.json',
              f'预览/{key}_3840x2160.png',f'预览/{key}_1920x1080.png']
    assert all((out/p).is_file() and (out/p).stat().st_size>0 for p in expected)
    with zipfile.ZipFile(out/(stem+'.pptx')) as z:
        assert len([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)])==1
        tree=ET.fromstring(z.read('ppt/notesSlides/notesSlide1.xml'))
        ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
        note='\n'.join(''.join(p.itertext()) for p in tree.findall('.//a:p',ns))
        md=(out/'本页备注.md').read_text(encoding='utf8').strip()
        assert md in note,key
        if key=='S12':assert (PI/'Why_PhD母稿_用户原文_20261005.md').read_text(encoding='utf8').strip() in note
    pdf=(out/(stem+'.pdf')).read_bytes()
    assert pdf.startswith(b'%PDF-') and b'%%EOF' in pdf[-100:]
    pdf_page_objects=len(re.findall(rb'/Type\s*/Page\b',pdf))
    assert pdf_page_objects==1,(key,pdf_page_objects)
    report=json.loads((out/'排版与保全检查.json').read_text(encoding='utf8'))
    assert report['renderer']=='Microsoft PowerPoint 16.0' and report['notes_complete']
    assert not report['text_overflow'] and not report['shapes_outside_canvas']
    for w,h in [(3840,2160),(1920,1080)]:assert Image.open(out/'预览'/f'{key}_{w}x{h}.png').size==(w,h)
    summaries.append(dict(slide=key,one_page_pptx=True,one_page_pdf=True,complete_notes_exact_match=True,
                          editable_text_objects=sum('text' in s for s in report['shapes']),
                          sha256_pptx=sha(out/(stem+'.pptx')),sha256_pdf=sha(out/(stem+'.pdf'))))
    files=[p for p in sorted(out.rglob('*')) if p.is_file() and p.name!='交付文件清单.json']
    manifest=[dict(path=p.relative_to(out).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
    (out/'交付文件清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
for folder in [REVIEW]+[PI/n for n in NAMES.values()]:
    for md in folder.rglob('*.md'):
        for dest in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',md.read_text(encoding='utf8')):
            if dest.startswith(('http:','https:','#')):continue
            dest=unquote(dest.split('#')[0]);target=(md.parent/dest).resolve()
            assert target.exists(),(md,dest)
            links.append(dict(from_file=md.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()))
summary=dict(status='PASS',date='2026-10-05',candidates=summaries,preserved_files=len(entries),
             prior_candidate_files=len(baseline['reference_files']),local_links_checked=len(links),
             old_candidate_files_changed=0,full_deck_created=False,scope='INTERNAL / v1 CANDIDATE')
(REVIEW/'最终交付核验.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(summary,ensure_ascii=False))
