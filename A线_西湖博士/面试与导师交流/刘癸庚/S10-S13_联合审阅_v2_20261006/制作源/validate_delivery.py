"""Final artifact/provenance/link checks; does not rebuild or rerender slides."""
from pathlib import Path
import json,re,hashlib,zipfile,xml.etree.ElementTree as ET
from PIL import Image
REVIEW=Path(__file__).resolve().parent.parent;PI=REVIEW.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
NAMES=json.loads((REVIEW/'候选目录.json').read_text(encoding='utf8'))
FACTS=ROOT/'公共资料/事实核验/个人探索_20261006'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((REVIEW/'制作前保全基线.json').read_text(encoding='utf8'))
old=[r for k in ['protected_candidates','sources','unrelated'] for r in baseline[k]]
assert len(old)==242
for r in old:assert (ROOT/r['path']).stat().st_size==r['bytes'] and sha(ROOT/r['path'])==r['sha256'],r['path']
for r in json.loads((FACTS/'本人补充素材核验.json').read_text(encoding='utf8'))['files']:
    assert sha(Path(r['source']))==sha(ROOT/r['copy'])==r['sha256']
initial=json.loads((FACTS/'来源与恢复核验.json').read_text(encoding='utf8'))
assert sha(Path(initial['attachment']['source']))==sha(ROOT/initial['attachment']['copy'])==initial['attachment']['sha256']
assert sha(ROOT/initial['homepage']['output'])==initial['homepage']['output_sha256']

instruction=(PI/'S10-S13_v2制作指令_20261006.md').read_text(encoding='utf8')
def quoted(start,end):
    section=instruction.split(start,1)[1].split(end,1)[0]
    return '\n'.join(l[2:] if l.startswith('> ') else '' for l in section.splitlines() if l.startswith('>')).strip()
expected={'S10':quoted('## 1.5 口述建议','---'),'S11':quoted('## 2.5 口述建议','---'),
          'S12':(PI/'Why_PhD母稿_用户原文_20261005.md').read_text(encoding='utf8').strip(),
          'S13':quoted('## 4.4 S13 口述建议 v3','## 4.5')}
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
decks=[]
for key,dirname in NAMES.items():
    out=PI/dirname
    for ppt in sorted(out.glob('*.pptx')):
        with zipfile.ZipFile(ppt) as z:
            assert len([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)])==1
            paragraphs=[p for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n) for p in ET.fromstring(z.read(n)).findall('.//a:p',ns)]
            notes='\n'.join(''.join(p.itertext()) for p in paragraphs)
            assert expected[key] in notes
            assert (out/'本页备注.md').read_text(encoding='utf8').strip() in notes
        report=json.loads((out/(ppt.stem+'_排版检查.json')).read_text(encoding='utf8'))
        assert not report['text_overflow'] and not report['shapes_outside_canvas'] and report['renderer']=='Microsoft PowerPoint 16.0'
        assert report['pdf_pages']==1 and report['notes_complete']
        variant=report['variant']
        for size in [(3840,2160),(1920,1080)]:assert Image.open(out/'预览'/f'{variant}_{size[0]}x{size[1]}.png').size==size
        assert (out/(ppt.stem+'.pdf')).read_bytes().startswith(b'%PDF')
        decks.append(dict(slide=key,variant=variant,pptx=ppt.relative_to(ROOT).as_posix(),notes_exact=True))
assert len(decks)==5

dirs=[FACTS,REVIEW,*(PI/n for n in NAMES.values())]
links=0;manifest_files=0
for d in dirs:
    for md in d.rglob('*.md'):
        for target in re.findall(r'\[[^\]]*\]\(([^\n\)]+)\)',md.read_text(encoding='utf8')):
            if target.startswith(('https:','http:','#')):continue
            target=target.split('#',1)[0]
            assert (md.parent/target).resolve().exists(),(str(md),target)
            links+=1
    manifest=json.loads((d/'交付文件清单.json').read_text(encoding='utf8'))
    for r in manifest['files']:
        p=d/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],str(p)
        manifest_files+=1
    actual={p.relative_to(d).as_posix() for p in d.rglob('*') if p.is_file() and p.name not in ['交付文件清单.json','交付验收.json'] and '__pycache__' not in p.parts}
    recorded={r['path'] for r in manifest['files']}
    assert actual<=recorded,(str(d),actual-recorded)
    assert not list(d.rglob('*.zip'))
report=dict(status='INTERNAL / v2 CANDIDATE',presentations=decks,unchanged_existing_files=len(old),relative_links_checked=links,
    manifest_files_checked=manifest_files,all_checks_passed=True,actual_projection_tested=False,no_full_deck_created=True)
(REVIEW/'交付验收.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
