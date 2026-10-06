"""Read-only delivery checks plus JSON report. Does not rebuild or mutate presentations."""
from pathlib import Path
import hashlib,json,re,subprocess
from PIL import Image,ImageChops
from pptx import Presentation
OUT=Path(__file__).resolve().parents[1];PI=OUT.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
S8=PI/'S8_项目AI协作_v3_20261006'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return s.replace('\r\n','\n').replace('\r','\n').strip()
rows=[]
specs=[(S8,'S8_项目AI协作_v3',['S8'],['speaker_notes.md'],PI/'S8_项目AI协作_v2_20261006/S8_项目AI协作_v2.pptx'),
       (OUT,'S9_个人AI外骨骼_v3',['S9-A','S9-B'],['speaker_notes_A.md','speaker_notes_B.md'],PI/'S9_长期AI协作_v2_20261006/S9_长期AI协作_v2.pptx')]
for folder,stem,frames,notes,prior in specs:
    for name in ['README.md','来源与provenance.md','render_validation.md',stem+'.pptx',stem+'.pdf','派生素材说明.json']:
        assert (folder/name).is_file(),name
    p=Presentation(folder/(stem+'.pptx'));v2=Presentation(prior)
    assert len(p.slides)==len(frames) and abs(p.slide_width/p.slide_height-16/9)<1e-5
    report=json.loads((folder/'检查证据/PowerPoint实际渲染检查.json').read_text(encoding='utf8'))
    assert report['renderer']=='Microsoft PowerPoint 16.0'
    assert report['pptx_sha256']==sha(folder/(stem+'.pptx'))
    assert not report['text_overflow'] and not report['outside_canvas']
    assert all(n['exact_match'] for n in report['notes'])
    pdfinfo=subprocess.check_output(['pdfinfo',str(folder/(stem+'.pdf'))]).decode('utf8',errors='replace')
    assert 'Microsoft' in pdfinfo and 'PowerPoint' in pdfinfo
    producer=re.search(r'^Producer:\s+(.+)',pdfinfo,re.M)[1]
    assert int(re.search(r'^Pages:\s+(\d+)',pdfinfo,re.M)[1])==len(frames)
    for i,(slide,frame,note) in enumerate(zip(p.slides,frames,notes)):
        assert norm(slide.notes_slide.notes_text_frame.text)==norm((folder/note).read_text(encoding='utf8'))
        visible='\n'.join(sh.text for sh in slide.shapes if sh.has_text_frame)
        assert not any(t in visible for t in ['项目级协作','第一次比较系统地','PROJECT COLLABORATION','每次都从零开始'])
        assert 'v3 CANDIDATE' in visible
        textboxes=[sh for sh in slide.shapes if sh.has_text_frame]
        assert all(r.font.name=='Microsoft YaHei' for sh in textboxes for para in sh.text_frame.paragraphs for r in para.runs)
        imgs=[sh for sh in slide.shapes if sh.shape_type==13]
        oldimgs=[sh for sh in v2.slides[i].shapes if sh.shape_type==13]
        assert len(imgs)==len(oldimgs)==1
        image_match=imgs[0].image.blob==oldimgs[0].image.blob
        placement_match=all(getattr(imgs[0],a)==getattr(oldimgs[0],a) for a in ['left','top','width','height','crop_left','crop_right','crop_top','crop_bottom'])
        assert image_match and placement_match
        for w,h in [(3840,2160),(1920,1080)]:assert Image.open(folder/'预览'/f'{frame}_{w}x{h}.png').size==(w,h)
        assert Image.open(folder/'检查证据'/f'{frame}_PDF实际渲染.png').size==(1920,1080)
        rows.append(dict(frame=frame,native_textboxes=len(textboxes),images=1,font='Microsoft YaHei',
            notes_exact=True,original_v2_image_bytes_identical=image_match,original_v2_placement_identical=placement_match,
            preview_sizes=[[3840,2160],[1920,1080]],powerpoint_application_version='16.0',pdf_producer=producer,pptx_sha256=sha(folder/(stem+'.pptx'))))
records=json.loads((OUT/'检查证据/连续审阅来源.json').read_text(encoding='utf8'))
stem='S7A-S8v3-S9Av3-S9Bv3-S10_连续审阅'
vertical=Image.open(OUT/'预览'/f'{stem}_纵向.png').convert('RGB')
assert vertical.size==(1944,5674)
assert Image.open(OUT/'预览'/f'{stem}_横向.png').size==(4872,610)
for i,r in enumerate(records):
    original=ROOT/r['path'];assert sha(original)==r['sha256']
    cut=vertical.crop((12,50+i*1130,1932,1130+i*1130))
    assert ImageChops.difference(cut,Image.open(original).convert('RGB')).getbbox() is None
assert len(records)==5
broken=[];checked=0
fact=ROOT/'公共资料/事实核验/个人探索_20261006/S8S9_协作方法续核.md'
for path in list(S8.rglob('*.md'))+list(OUT.rglob('*.md'))+[fact]:
    for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf8')):
        target=target.strip('<>').split('#')[0]
        if not target or re.match(r'^[a-z]+:',target,re.I):continue
        checked+=1
        resolved=(path.parent/target).resolve()
        if not resolved.exists() and resolved!=(OUT/'检查证据/交付核验.json').resolve():broken.append({'file':str(path),'target':target})
assert not broken,broken
result={'status':'PASS','date':'2026-10-06','frames':rows,'sequence':{'frame_count':5,'vertical_original_pixels_identical':True,'sources_sha256_match':True},
        'markdown_links_checked':checked,'broken_links':broken,'limits':['No applicant rehearsal or live screen-share test.','Not an independent human UAT or product-efficacy validation.']}
(OUT/'检查证据/交付核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
