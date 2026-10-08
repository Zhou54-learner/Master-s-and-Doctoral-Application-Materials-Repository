"""Assemble selected slide OPC parts; retain source formatting and redact status only."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, json, posixpath, re, subprocess
from lxml import etree as E
from pptx import Presentation
OUT=Path(__file__).resolve().parents[1]
PI=OUT.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
STEM='刘癸庚交流_完整PPT_v1_20261006'
FULL=PI/'完整讲稿_最新合并版_v3_20261006.md'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','rel':'http://schemas.openxmlformats.org/package/2006/relationships','ct':'http://schemas.openxmlformats.org/package/2006/content-types'}
COMMON=('ppt/slideMasters/','ppt/slideLayouts/','ppt/theme/','ppt/notesMasters/')
SPECS=[
('S0','S0_封面_v1_20261005/S0_封面_v1.pptx',1),
('S1','S1_个人背景_v2_20261006/S1_个人背景_v2.pptx',1),
*[(f'S{i}','本科毕设_S2-S5_正式版_v0.1_20261006/本科毕设_S2-S5_正式版_v0.1.pptx',i-1) for i in range(2,6)],
('S6','S6_尘埃等离子体_v1_20261005/S6_尘埃等离子体_v1.pptx',1),
('S7','S7_乐音研究_v2_20261006/S7_乐音研究_v2_A_历史资产优先.pptx',1),
('S8','S8_项目AI协作_v3.1_20261006/S8_项目AI协作_v3.1.pptx',1),
('S9-A','S9_个人AI外骨骼_v3.1_20261006/S9_个人AI外骨骼_v3.1.pptx',1),
('S9-B','S9_个人AI外骨骼_v3.1_20261006/S9_个人AI外骨骼_v3.1.pptx',2),
('S10','S10_反思_v2_20261006/S10_反思_v2.pptx',1),
('S11','S11_表达_v2_20261006/S11_表达_v2.pptx',1),
('S12','S12_WhyPhD_v2.1_20261006/S12_WhyPhD_v2.1.pptx',1),
('S13','S13_WhyLiu_v2_20261006/S13_WhyLiu_v2.pptx',1)]

def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha(p):return sha_bytes(p.read_bytes())
def write_json(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def xml(b):return E.fromstring(b)
def dump(x):return E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
def relpath(part):return posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels')
def resolve(part,target):return posixpath.normpath(posixpath.join(posixpath.dirname(part),target)).lstrip('/')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)

def baseline():
    target=OUT/'制作前保全基线.json'
    if target.exists():return
    protected=[f for f in PI.rglob('*') if f.is_file() and OUT not in f.parents and f!=PI/'README.md' and '__pycache__' not in f.parts and not f.name.startswith('~$')]
    write_json(target,{'date':'2026-10-06','branch':git('branch','--show-current').decode().strip(),'head':git('rev-parse','HEAD').decode().strip(),'git_status':git('status','--short').decode('utf-8'),
    'protected':[{'path':f.relative_to(ROOT).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(protected)],
    'allowed_existing_updates':['A线_西湖博士/工作台.md',(PI/'README.md').relative_to(ROOT).as_posix()]})

def sections_with_lines():
    text=FULL.read_text(encoding='utf-8')
    starts=list(re.finditer(r'^# (S\d+)｜.*$',text,re.M))
    result={}; line_map={}
    def take(key,start,end):
        raw=text[start:end].rstrip()
        while raw.endswith('---'):raw=raw[:-3].rstrip()
        result[key]=raw
        line_map[key]=[text.count('\n',0,start)+1,text.count('\n',0,start+len(raw))+1]
    for i,m in enumerate(starts):
        end=starts[i+1].start() if i+1<len(starts) else text.index('# 完整试讲时建议重点标记',m.end())
        if m.group(1)=='S9':
            marker='〔切 S9-B〕'
            split=text.index(marker,m.end())+len(marker)
            take('S9-A',m.start(),split)
            bstart=split
            while text[bstart].isspace():bstart+=1
            take('S9-B',bstart,end)
        else:take(m.group(1),m.start(),end)
    assert set(result)=={s[0] for s in SPECS}
    assert not re.search(r'INTERNAL|CANDIDATE|FULL DRAFT|REVIEW DRAFT','\n'.join(result.values()),re.I)
    return result,line_map

def sections():return sections_with_lines()[0]

def clean_slide_xml(blob,key):
    doc=xml(blob); changes=[]
    for sh in doc.xpath('//p:sp',namespaces=NS):
        texts=sh.xpath('.//a:t',namespaces=NS)
        before=''.join(t.text or '' for t in texts)
        after=before
        if re.fullmatch(r'INTERNAL\s*/\s*v[\d.]+\s+CANDIDATE',before):after=''
        if key=='S0' and before=='刘癸庚老师课题组交流 · 独立封面候选':after='刘癸庚老师课题组交流'
        if after!=before:
            assert len(texts)==1,(key,before)
            texts[0].text=after
            pr=sh.find('p:nvSpPr/p:cNvPr',NS)
            if re.search(r'INTERNAL|CANDIDATE',pr.get('name',''),re.I):pr.set('name','TextBox '+pr.get('id'))
            off=sh.find('p:spPr/a:xfrm/a:off',NS); ext=sh.find('p:spPr/a:xfrm/a:ext',NS)
            rect=[int(off.get('x')),int(off.get('y')),int(ext.get('cx')),int(ext.get('cy'))]
            changes.append({'shape_id':int(pr.get('id')),'before':before,'after':after,'rect_emu':rect})
    return (dump(doc) if changes else blob),changes

def replace_note_text(blob,text):
    doc=xml(blob); bodies=doc.xpath('//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]/p:txBody',namespaces=NS)
    assert len(bodies)==1
    body=bodies[0]
    for p in list(body.findall('a:p',NS)):body.remove(p)
    for line in text.split('\n'):
        p=E.SubElement(body,'{'+NS['a']+'}p')
        if line:
            r=E.SubElement(p,'{'+NS['a']+'}r');t=E.SubElement(r,'{'+NS['a']+'}t');t.text=line
    return dump(doc)

def main():
    OUT.mkdir(exist_ok=True);(OUT/'逐页备注').mkdir(exist_ok=True)
    baseline();secs,line_map=sections_with_lines()
    sources=list(dict.fromkeys(s[1] for s in SPECS)); archives={s:ZipFile(PI/s) for s in sources}
    # Selected inputs must be the bytes stored in the latest current-branch HEAD.
    for p in [PI/s for s in sources]+[FULL]:
        assert p.read_bytes()==git('show','HEAD:'+p.relative_to(ROOT).as_posix()),str(p)
    base=archives[sources[0]];data={n:base.read(n) for n in base.namelist()}
    types=xml(data['[Content_Types].xml']);existing_types={x.get('PartName') for x in types if x.tag.endswith('Override')}
    mapping={};rows=[];shared=set()
    for n,(key,src,index) in enumerate(SPECS,1):
        mapping[src,f'ppt/slides/slide{index}.xml']=f'ppt/slides/slide{n}.xml'
        mapping[src,f'ppt/notesSlides/notesSlide{index}.xml']=f'ppt/notesSlides/notesSlide{n}.xml'
    for src,z in archives.items():
        parts=[n for n in z.namelist() if n.startswith(COMMON)]
        if all(n in data and z.read(n)==data[n] for n in parts):
            shared.add(src)
            for n in parts:mapping[src,n]=n
    source_ids={s:i+1 for i,s in enumerate(sources)};copied=set();part_audit=[]
    def copy_part(src,part):
        z=archives[src]
        # Normalize notes-page layout to the single deck notes master; speaker text is replaced.
        if part.startswith('ppt/notesMasters/'):
            mapping[src,part]=part
            return part
        if src in shared and part.startswith(COMMON):return part
        new=mapping.setdefault((src,part),f'ppt/imported/source{source_ids[src]:02d}/'+part)
        if (src,part) in copied:return new
        copied.add((src,part));data[new]=z.read(part)
        part_audit.append({'source':src,'source_part':part,'output_part':new,'sha256':sha_bytes(data[new])})
        st=xml(z.read('[Content_Types].xml'))
        ct=next((x.get('ContentType') for x in st if x.get('PartName')=='/'+part),None)
        if ct is None:ct=next(x.get('ContentType') for x in st if x.get('Extension')==part.rsplit('.',1)[1])
        if '/'+new not in existing_types:
            E.SubElement(types,'{'+NS['ct']+'}Override',PartName='/'+new,ContentType=ct);existing_types.add('/'+new)
        rp=relpath(part)
        if rp in z.namelist():
            rels=xml(z.read(rp))
            for rel in rels:
                if rel.get('TargetMode')=='External':continue
                target=resolve(part,rel.get('Target'));dest=copy_part(src,target)
                rel.set('Target',posixpath.relpath(dest,posixpath.dirname(new)))
            data[relpath(new)]=dump(rels)
        return new
    for n,(key,src,index) in enumerate(SPECS,1):
        sp=f'ppt/slides/slide{index}.xml';op=copy_part(src,sp)
        original=Presentation(PI/src).slides[index-1]
        data[op],changes=clean_slide_xml(data[op],key)
        np=mapping[src,f'ppt/notesSlides/notesSlide{index}.xml']
        data[np]=replace_note_text(data[np],secs[key])
        (OUT/'逐页备注'/f'{n:02d}_{key}.md').write_text(secs[key]+'\n',encoding='utf-8')
        rows.append({'page':n,'logical':key,'source':src,'source_page':index,'source_sha256':sha(PI/src),
            'source_slide_xml_sha256':sha_bytes(archives[src].read(sp)),'output_slide_xml_sha256':sha_bytes(data[op]),
            'output_slide_part':op,'shape_count':len(original.shapes),'status_changes':changes,
            'notes_source':FULL.name,'notes_source_lines':line_map[key],'notes_source_sha256':sha(FULL),'notes_sha256':sha_bytes(secs[key].encode())})
        print(f'{n:02d} {key}: {len(original.shapes)} objects, {len(changes)} status edits, {len(secs[key])} note characters',flush=True)
    pres=xml(data['ppt/presentation.xml']);lst=pres.find('p:sldIdLst',NS)
    for e in list(lst):lst.remove(e)
    rels=xml(data['ppt/_rels/presentation.xml.rels'])
    for e in list(rels):
        if e.get('Type').endswith('/slide'):rels.remove(e)
    ids={r.get('Id') for r in rels};serial=1
    def add_rel(typ,target):
        nonlocal serial
        while f'rId{serial}' in ids:serial+=1
        rid=f'rId{serial}';ids.add(rid)
        E.SubElement(rels,'{'+NS['rel']+'}Relationship',Id=rid,Type=NS['r']+'/'+typ,Target=posixpath.relpath(target,'ppt'))
        return rid
    for n in range(1,len(SPECS)+1):
        rid=add_rel('slide',f'ppt/slides/slide{n}.xml')
        E.SubElement(lst,'{'+NS['p']+'}sldId',id=str(255+n),attrib={'{'+NS['r']+'}id':rid})
    masters=pres.find('p:sldMasterIdLst',NS)
    # PowerPoint requires unique IDs across masters and their layouts.
    existing_ids=[int(e.get('id')) for e in masters]
    for name,blob in data.items():
        if name.startswith('ppt/slideMasters/') and name.endswith('.xml'):
            existing_ids.extend(int(e.get('id')) for e in xml(blob).findall('p:sldLayoutIdLst/p:sldLayoutId',NS))
    mid=max(existing_ids)+1
    for src,part in sorted(copied):
        if part.startswith('ppt/slideMasters/') and part.endswith('.xml'):
            rid=add_rel('slideMaster',mapping[src,part])
            E.SubElement(masters,'{'+NS['p']+'}sldMasterId',id=str(mid),attrib={'{'+NS['r']+'}id':rid});mid+=1
            name=mapping[src,part];master=xml(data[name])
            for layout in master.findall('p:sldLayoutIdLst/p:sldLayoutId',NS):
                layout.set('id',str(mid));mid+=1
            data[name]=dump(master)
    if pres.find('p:notesMasterIdLst',NS) is None:
        notes_rel=next(r.get('Id') for r in rels if r.get('Type').endswith('/notesMaster'))
        nl=E.Element('{'+NS['p']+'}notesMasterIdLst')
        E.SubElement(nl,'{'+NS['p']+'}notesMasterId',attrib={'{'+NS['r']+'}id':notes_rel})
        pres.insert(1,nl)
    data['ppt/presentation.xml']=dump(pres);data['ppt/_rels/presentation.xml.rels']=dump(rels)
    # No stale cover thumbnail or author/session metadata from a source package.
    rootrels=xml(data['_rels/.rels'])
    for r in list(rootrels):
        if r.get('Type').endswith('/thumbnail'):
            data.pop(resolve('',r.get('Target')),None);rootrels.remove(r)
    data['_rels/.rels']=dump(rootrels)
    cp='http://schemas.openxmlformats.org/package/2006/metadata/core-properties';dc='http://purl.org/dc/elements/1.1/'
    core=E.Element('{'+cp+'}coreProperties',nsmap={'cp':cp,'dc':dc})
    for tag,value in [(f'{{{dc}}}title','科研经历与个人探索'),(f'{{{dc}}}subject','刘癸庚老师课题组交流'),(f'{{{dc}}}creator','周子靖'),(f'{{{dc}}}description','科研经历与个人探索；15页演示文稿及逐页演讲者备注')]:E.SubElement(core,tag).text=value
    data['docProps/core.xml']=dump(core)
    app=xml(data['docProps/app.xml'])
    for node in list(app):
        local=E.QName(node).localname
        if local in ('Slides','Notes'):node.text=str(len(SPECS))
        elif local in ('HeadingPairs','TitlesOfParts','Company','Manager','Template'):app.remove(node)
    data['docProps/app.xml']=dump(app)
    # Remove any unused base content-type overrides.
    for node in list(types):
        if node.tag.endswith('Override') and node.get('PartName').lstrip('/') not in data:types.remove(node)
    data['[Content_Types].xml']=dump(types)
    status_hits=[n for n,b in data.items() if n.endswith('.xml') and re.search(rb'INTERNAL|CANDIDATE|FULL DRAFT|REVIEW DRAFT',b,re.I)]
    assert not status_hits,status_hits
    target=OUT/(STEM+'.pptx');assert not target.exists(),'Use a new version for a previously delivered deck.'
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for name,b in data.items():z.writestr(name,b)
    result=Presentation(target);assert len(result.slides)==15
    for row,s in zip(rows,result.slides):
        assert s.notes_slide.notes_text_frame.text==secs[row['logical']]
        assert len(s.shapes)==row['shape_count']
    write_json(OUT/'页码与来源映射.json',rows)
    write_json(OUT/'部件复制映射.json',part_audit)
    write_json(OUT/'合并结构检查.json',{'status':'PASS','source_head':git('rev-parse','HEAD').decode().strip(),'source_files_match_HEAD':True,'physical_slides':15,'logical_themes':14,'slide_size_emu':[result.slide_width,result.slide_height],'objects':sum(r['shape_count'] for r in rows),'slides_without_visible_edits':sum(not r['status_changes'] for r in rows),'status_edit_count':sum(len(r['status_changes']) for r in rows),'speaker_notes_exact_matches':15,'script':FULL.name,'script_sha256':sha(FULL),'shared_template_sources':len(shared),'independently_preserved_template_sources':len(archives)-len(shared),'pptx_sha256':sha(target),'package_status_marker_hits':status_hits})
    for z in archives.values():z.close()
    print(target)
if __name__=='__main__':main()
