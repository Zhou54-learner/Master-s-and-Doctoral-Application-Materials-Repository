"""Assemble the selected OPC parts without redrawing or resaving any slide XML.

Only presentation ordering/relationships, document metadata and notes are edited.
The common masters/layouts/themes are reused only after byte equality checks.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from copy import deepcopy
import hashlib, json, posixpath, re, subprocess
from lxml import etree as E
from pptx import Presentation

OUT = Path(__file__).resolve().parents[1]
PI = OUT.parent
ROOT = next(p for p in PI.parents if (p / '申请路线总览.md').exists())
STEM = '刘癸庚交流_INTERNAL_FULL_DRAFT_v0.1_20261006'
FULL = PI / '完整讲稿_当前版本合并版_v2_20261006.md'
V4 = PI / 'S13_WhyWestlake-Liu_口述_v4_20261006.md'
NS = {'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'rel':'http://schemas.openxmlformats.org/package/2006/relationships',
      'ct':'http://schemas.openxmlformats.org/package/2006/content-types'}
COMMON = ('ppt/slideMasters/', 'ppt/slideLayouts/', 'ppt/theme/', 'ppt/notesMasters/')
SPECS = [
    ('S0','S0_封面_v1_20261005/S0_封面_v1.pptx',1),
    ('S1','S1_个人背景_v2_20261006/S1_个人背景_v2.pptx',1),
    *[(f'S{i}','本科毕设_S2-S5_v2.1_20261005/本科毕设_S2-S5_v2.1.pptx',i-1) for i in range(2,6)],
    ('S6','S6_尘埃等离子体_v1_20261005/S6_尘埃等离子体_v1.pptx',1),
    ('S7','S7_乐音研究_v1_20261005/S7_乐音研究_v1.pptx',1),
    ('S8','S8_项目级AI协作_v1_20261005/S8_项目级AI协作_v1.pptx',1),
    ('S9-A','S9_长期AI协作_v1_20261005/S9_长期AI协作_v1.pptx',1),
    ('S9-B','S9_长期AI协作_v1_20261005/S9_长期AI协作_v1.pptx',2),
    ('S10','S10_反思_v2_20261006/S10_反思_v2.pptx',1),
    ('S11','S11_表达_v2_20261006/S11_表达_v2.pptx',1),
    ('S12','S12_WhyPhD_v2.1_20261006/S12_WhyPhD_v2.1.pptx',1),
    ('S13','S13_WhyLiu_v2_20261006/S13_WhyLiu_v2.pptx',1),
]

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha(p): return sha_bytes(p.read_bytes())
def write_json(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def xml(b): return E.fromstring(b)
def dump(x): return E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
def relpath(part):
    return posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels')
def resolve(part,target):
    return posixpath.normpath(posixpath.join(posixpath.dirname(part),target)).lstrip('/')

def baseline():
    p=OUT/'制作前保全基线.json'
    if p.exists(): return
    protected=[f for f in PI.rglob('*') if f.is_file() and OUT not in f.parents
               and f!=PI/'README.md' and '__pycache__' not in f.parts and not f.name.startswith('~$')]
    unrelated=[ROOT/f for f in [
      '公共资料/面试与导师交流中心/公共主干/README.md',
      '公共资料/面试与导师交流中心/公共主干/项目重建/本科毕设/README.md',
      '公共资料/面试与导师交流中心/公共主干/项目重建/本科毕设/13_实际工作梳理与研究叙事底稿.md']]
    write_json(p,{'date':'2026-10-06','branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'protected':[{'path':f.relative_to(ROOT).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(protected+unrelated)],
        'allowed_existing_updates':['A线_西湖博士/工作台.md',(PI/'README.md').relative_to(ROOT).as_posix()]})

def sections():
    text=FULL.read_text(encoding='utf-8')
    starts=list(re.finditer(r'^# (S\d+)｜.*$',text,re.M))
    result={}
    for i,m in enumerate(starts):
        end=starts[i+1].start() if i+1<len(starts) else text.index('# 完整试讲时建议重点标记',m.end())
        result[m.group(1)]=text[m.start():end].strip().removesuffix('---').rstrip()
    assert set(result)=={f'S{i}' for i in range(1,14)}
    main_v4=V4.read_text(encoding='utf-8').split('## 主述\n\n',1)[1].split('\n\n## 与 S12',1)[0]
    assert main_v4 in result['S13']
    return result

def notes_for(key,old,secs):
    if key=='S0': return old, 'S0 v1 原备注，逐字保留'
    if key=='S13': return V4.read_text(encoding='utf-8').strip(), '独立 S13 口述 v4 全文（替换旧 v3）'
    logical=key.split('-')[0]
    note=secs[logical]
    extra=''
    if key in ['S2','S3','S4','S5']:
        extra=old[old.index('被打断时'):]
    elif key=='S6':
        # The current script already includes contribution boundaries.
        marker='来源'
        lines=old.splitlines()
        idx=next((i for i,l in enumerate(lines) if l.startswith(marker)),None)
        if idx is not None: extra='\n'.join(lines[idx:])
    elif key=='S7':
        extra=old[old.index('## 指图顺序与口述校正'):]
    elif key=='S8':
        extra=old[old.index('## 事实与 ownership 边界'):]
        extra+='\n\n过渡沿用原候选约定：S8 末尾与 S9 开头相同原句只说一次。'
    elif key.startswith('S9-'):
        # Preserve both frame instructions; the full shared script is not read twice.
        note=old.split('\n\n',1)[0]+'\n\n'+note
        extra=old[old.index('## 点击与时间分配'):]
    elif key in ['S10','S11']:
        # Keep source auxiliary notes after the two source narration paragraphs.
        m=re.search(r'^## (?!主述).*$',old[old.index('## 主述')+len('## 主述'):],re.M)
        if m:
            offset=old.index('## 主述')+len('## 主述')+m.start()
            extra=old[offset:]
    if extra:
        note+='\n\n## 原候选备查提示（非主述）\n\n'+extra
    # No paraphrase, shortening, or acceptance of optional wording suggestions.
    assert secs[logical] in note
    return note, '完整讲稿 v2 对应节原文'+('；保留原候选辅助备注' if extra else '')

def replace_note_text(blob,text):
    doc=xml(blob)
    body=doc.xpath('//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]/p:txBody',namespaces=NS)
    assert len(body)==1
    tx=body[0]
    for p in list(tx.findall('a:p',NS)):tx.remove(p)
    for line in text.split('\n'):
        p=E.SubElement(tx,'{'+NS['a']+'}p')
        if line:
            r=E.SubElement(p,'{'+NS['a']+'}r');t=E.SubElement(r,'{'+NS['a']+'}t');t.text=line
    return dump(doc)

def main():
    OUT.mkdir(exist_ok=True);(OUT/'逐页备注').mkdir(exist_ok=True)
    baseline();secs=sections()
    sources={s[1] for s in SPECS}
    archives={s:ZipFile(PI/s) for s in sources}
    base=archives[SPECS[0][1]]
    data={n:base.read(n) for n in base.namelist()}
    types=xml(data['[Content_Types].xml'])
    existing_types={x.get('PartName') for x in types if x.tag.endswith('Override')}
    mapping={};notes_map={};rows=[];visual=[]
    for n,(key,src,index) in enumerate(SPECS,1):
        mapping[(src,f'ppt/slides/slide{index}.xml')]=f'ppt/slides/slide{n}.xml'
        mapping[(src,f'ppt/notesSlides/notesSlide{index}.xml')]=f'ppt/notesSlides/notesSlide{n}.xml'
    # All template bytes and template relationship bytes must match, not merely names.
    for src,z in archives.items():
        for part in z.namelist():
            if part.startswith(COMMON):
                assert part in data and z.read(part)==data[part],(src,part,'template differs')
                mapping[(src,part)]=part
    src_ids={s:i+1 for i,s in enumerate(dict.fromkeys(s[1] for s in SPECS))}
    copied=set()
    def copy_part(src,part):
        z=archives[src]
        if part.startswith(COMMON):return part
        new=mapping.setdefault((src,part),f'ppt/imported/source{src_ids[src]:02d}/'+part)
        if (src,part) in copied:return new
        copied.add((src,part));data[new]=z.read(part)
        src_types=xml(z.read('[Content_Types].xml'))
        ctype=next((x.get('ContentType') for x in src_types if x.get('PartName')=='/'+part),None)
        if ctype is None:
            ctype=next(x.get('ContentType') for x in src_types if x.get('Extension')==part.rsplit('.',1)[1])
        if '/'+new not in existing_types:
            E.SubElement(types,'{'+NS['ct']+'}Override',PartName='/'+new,ContentType=ctype);existing_types.add('/'+new)
        rp=relpath(part)
        if rp in z.namelist():
            rels=xml(z.read(rp))
            for rel in rels:
                if rel.get('TargetMode')=='External':continue
                target=resolve(part,rel.get('Target'))
                dest=copy_part(src,target)
                rel.set('Target',posixpath.relpath(dest,posixpath.dirname(new)))
            data[relpath(new)]=dump(rels)
        return new
    for n,(key,src,index) in enumerate(SPECS,1):
        part=f'ppt/slides/slide{index}.xml'
        new=copy_part(src,part)
        assert data[new]==archives[src].read(part)
        original=Presentation(PI/src).slides[index-1]
        oldnotes=original.notes_slide.notes_text_frame.text
        note,rule=notes_for(key,oldnotes,secs)
        np=mapping[(src,f'ppt/notesSlides/notesSlide{index}.xml')]
        if note!=oldnotes:data[np]=replace_note_text(data[np],note)
        (OUT/'逐页备注'/f'{n:02d}_{key}.md').write_text(note+'\n',encoding='utf-8')
        notes_map[n]=note
        row={'page':n,'logical':key,'source':src,'source_page':index,'source_sha256':sha(PI/src),
             'source_slide_xml_sha256':sha_bytes(archives[src].read(part)),
             'output_slide_part':new,'shape_count':len(original.shapes),'notes_source':rule,
             'notes_sha256':sha_bytes(note.encode('utf-8')),'old_notes_changed':note!=oldnotes}
        rows.append(row)
        print(f'{n:02d} {key}: {len(original.shapes)} editable objects; notes {len(note)} chars',flush=True)
    pres=xml(data['ppt/presentation.xml']);lst=pres.find('p:sldIdLst',NS)
    for e in list(lst):lst.remove(e)
    rels=xml(data['ppt/_rels/presentation.xml.rels'])
    for e in list(rels):
        if e.get('Type').endswith('/slide'):rels.remove(e)
    ids={r.get('Id') for r in rels};nextid=1
    for n in range(1,len(SPECS)+1):
        while f'rId{nextid}' in ids:nextid+=1
        rid=f'rId{nextid}';ids.add(rid)
        E.SubElement(rels,'{'+NS['rel']+'}Relationship',Id=rid,Type=NS['r']+'/slide',Target=f'slides/slide{n}.xml')
        E.SubElement(lst,'{'+NS['p']+'}sldId',id=str(255+n),attrib={'{'+NS['r']+'}id':rid})
    data['ppt/presentation.xml']=dump(pres);data['ppt/_rels/presentation.xml.rels']=dump(rels)
    data['[Content_Types].xml']=dump(types)
    core=xml(data['docProps/core.xml'])
    cp='http://schemas.openxmlformats.org/package/2006/metadata/core-properties'
    dc='http://purl.org/dc/elements/1.1/'
    for tag,value in [(f'{{{dc}}}title','刘癸庚交流｜INTERNAL / FULL DRAFT v0.1'),
                      (f'{{{dc}}}subject','2026-10-06 完整可审阅初版'),
                      (f'{{{cp}}}contentStatus','INTERNAL / FULL DRAFT v0.1'),
                      (f'{{{cp}}}keywords','INTERNAL; FULL DRAFT v0.1; S13 notes v4'),
                      (f'{{{dc}}}description','15 physical slides / S0–S13; S9 A/B continuous; selected source slides retained without redraw.')]:
        node=core.find(tag)
        if node is None:node=E.SubElement(core,tag)
        node.text=value
    data['docProps/core.xml']=dump(core)
    app=xml(data['docProps/app.xml'])
    for name in ['Slides','Notes']:
        for node in app:
            if E.QName(node).localname==name:node.text=str(len(SPECS))
    data['docProps/app.xml']=dump(app)
    target=OUT/(STEM+'.pptx')
    assert not target.exists(),'Never overwrite an accepted build; use a new version.'
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for name,blob in data.items():z.writestr(name,blob)
    result=Presentation(target)
    assert len(result.slides)==15
    assert (result.slide_width,result.slide_height)==(12191999,6858000)
    for n,s in enumerate(result.slides,1):
        assert s.notes_slide.notes_text_frame.text==notes_map[n],n
        assert len(s.shapes)==rows[n-1]['shape_count']
    write_json(OUT/'页码与来源映射.json',rows)
    write_json(OUT/'合并结构检查.json',{'status':'PASS','slide_xml_byte_identical':15,'physical_slides':15,
       'logical_themes':14,'slide_size_emu':[12191999,6858000],'all_common_template_parts_byte_identical':True,
       'editable_objects':sum(r['shape_count'] for r in rows),'speaker_notes_exact_match':15,
       's13_v4_full_file_exact_match':result.slides[-1].notes_slide.notes_text_frame.text==V4.read_text(encoding='utf-8').strip(),
       'pptx_sha256':sha(target),'sources':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [FULL,V4]],
       'method':'OPC part copy; slide XML and visual asset bytes untouched; only relationships/order/metadata/notes updated.'})
    for z in archives.values():z.close()
    print(target,flush=True)

if __name__=='__main__':main()
