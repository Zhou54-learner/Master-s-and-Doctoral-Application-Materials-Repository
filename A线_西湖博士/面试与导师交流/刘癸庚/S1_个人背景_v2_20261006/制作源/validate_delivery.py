"""Check user-specified content, single-string S12 delta, and preservation."""
from pathlib import Path
import hashlib,json,re,zipfile
from pptx import Presentation
from PIL import Image,ImageChops

OUT=Path(__file__).resolve().parents[1]
PI=OUT.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
S12=PI/'S12_WhyPhD_v2.1_20261006'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    s1=Presentation(OUT/'S1_个人背景_v2.pptx')
    shapes={s.name:s for s in s1.slides[0].shapes}
    expected={
        'title':'本科这几年，我主要做过这些事情',
        'education':'哈尔滨工业大学 · 物理学院 · 应用物理学',
        'section_01':'本科毕业设计','project_01':'三维周期电阻膜吸波结构','detail_01':'结构设计、仿真与优化',
        'section_02':'合作科研','project_02':'二维尘埃等离子体晶格波','detail_02':'偏振数据处理与粒子轨迹可视化',
        'section_03':'一次较早的自主探索','project_03':'波纹管乐音研究','detail_03':'实验、录音与频谱分析',
        'section_04':'后来的一些个人探索','project_04a':'物理学习 Agent / 长期学习系统','project_04b':'写作 / 个人网页'}
    assert all(shapes[k].text==v for k,v in expected.items())
    texts='\n'.join(s.text for s in shapes.values() if s.has_text_frame)
    banned=['CST','Python','MATLAB','GPA','排名','四六级','topology','non-Hermitian','探究','协作','整合','反思','表达',
            'research judgment','capability','workflow','Why PhD','Why Liu','数值工作流','Physics background','research map',
            'Zijing Zhou','周子靖','我的起点']
    found=[word for word in banned if word.lower() in texts.lower()]
    assert not found and not re.search(r'\bGA\b',texts)
    notes=(OUT/'本页备注.md').read_text(encoding='utf-8').strip()
    assert s1.slides[0].notes_slide.notes_text_frame.text==notes
    assert [shapes[f'number_0{i}'].text for i in range(1,5)]==['01','02','03','04']
    ys=[shapes[f'number_0{i}'].top for i in range(1,5)]
    assert ys==sorted(ys)
    sizes=[shapes[k].text_frame.paragraphs[0].runs[0].font.size.pt for k in ['project_01','project_02','project_03','project_04a']]
    assert all(a>b for a,b in zip(sizes,sizes[1:]))
    original=PI/'S12_WhyPhD_v2_20261006'
    old='但做得越多，我越觉得自己真正缺的是';new='但做得越多，我越觉得自己还需要补的是'
    with zipfile.ZipFile(original/'S12_WhyPhD_v2.pptx') as a,zipfile.ZipFile(S12/'S12_WhyPhD_v2.1.pptx') as b:
        assert a.namelist()==b.namelist()
        changed=[name for name in a.namelist() if a.read(name)!=b.read(name)]
        assert changed==['ppt/slides/slide1.xml']
        assert b.read(changed[0])==a.read(changed[0]).replace(old.encode(),new.encode())
    assert sha(original/'本页备注.md')==sha(S12/'本页备注.md')
    diff_records=[]
    for w,h in [(1920,1080),(3840,2160)]:
        a=Image.open(original/f'预览/S12_{w}x{h}.png').convert('RGB')
        b=Image.open(S12/f'预览/S12_{w}x{h}.png').convert('RGB')
        assert a.size==b.size==(w,h)
        bbox=ImageChops.difference(a,b).getbbox()
        sx=w/(13.333333*72);sy=h/(7.5*72)
        allowed=[int(.78*72*sx)-2,int(5.10*72*sy)-2,int((.78+11.65)*72*sx)+2,int((5.10+.99)*72*sy)+2]
        assert bbox and bbox[0]>=allowed[0] and bbox[1]>=allowed[1] and bbox[2]<=allowed[2] and bbox[3]<=allowed[3]
        diff_records.append(dict(pixels=[w,h],actual_changed_bbox=list(bbox),allowed_textbox_bbox=allowed,all_pixels_outside_textbox_identical=True))
    write(S12/'图片差异检查.json',dict(comparison='PowerPoint 16.0 PNGs: v2 vs one-string v2.1',records=diff_records))
    base=json.loads((OUT/'制作前保全基线.json').read_text(encoding='utf-8'))
    preserved=[x for group in ['protected_candidates','unrelated'] for x in base[group]]
    assert all((ROOT/x['path']).stat().st_size==x['bytes'] and sha(ROOT/x['path'])==x['sha256'] for x in preserved)
    # These three reports are generated below; other README targets must already exist.
    generated={OUT/'交付检查.json',OUT/'交付文件清单.json',S12/'交付文件清单.json'}
    broken=[]
    for folder in [OUT,S12]:
        for md in folder.rglob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)',md.read_text(encoding='utf-8')):
                if re.match(r'[a-zA-Z]+:',link) or link.startswith('#'):continue
                target=(md.parent/link.split('#')[0]).resolve()
                if not target.exists() and target not in generated:broken.append(dict(file=str(md),link=link))
    assert not broken,broken
    for folder in [OUT,S12]:
        report=json.loads((folder/'PowerPoint排版检查.json').read_text(encoding='utf-8'))
        assert report['renderer']=='Microsoft PowerPoint 16.0' and report['slides']==report['pdf_pages']==1
        assert not report['text_overflow'] and not report['shapes_outside_canvas'] and report['notes_exact_match']
    summary=dict(status='PASS',date='2026-10-06',s1_required_texts_match=True,s1_banned_labels_found=found,
                 s1_sequence_correct=True,s1_project_font_sizes_pt=sizes,s1_notes_verbatim=True,
                 s12_changed_parts=changed,s12_exactly_one_string=True,s12_original_notes_unchanged=True,
                 s12_pixels_outside_target_unchanged=True,preserved_files=len(preserved),broken_local_links=broken,
                 boundary='Candidate only; no merged deck; no main merge; no sending. Existing slides and unrelated work unchanged.')
    write(OUT/'交付检查.json',summary)
    for folder in [OUT,S12]:
        files=[p for p in folder.rglob('*') if p.is_file() and p.name!='交付文件清单.json' and '__pycache__' not in p.parts]
        write(folder/'交付文件清单.json',[dict(path=p.relative_to(folder).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)])
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':main()
