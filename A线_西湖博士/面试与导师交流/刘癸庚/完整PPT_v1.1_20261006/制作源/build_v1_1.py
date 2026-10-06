"""Edit only S12/S13 slide and notes XML in the user's saved v1 package."""
from pathlib import Path
from copy import deepcopy
import hashlib, json, posixpath, re, subprocess, zipfile
from lxml import etree as E
from pptx import Presentation

OUT = Path(__file__).resolve().parents[1]
PI = OUT.parent
ROOT = PI.parents[2]
SOURCE = PI / '完整PPT_v1_20261006/刘癸庚交流_完整PPT_v1_20261006.pptx'
SCRIPT = PI / '完整讲稿_完整母稿_v5_20261006.md'
STEM = '刘癸庚交流_完整PPT_v1.1_20261006'
DECK = OUT / (STEM + '.pptx')
KEYS = ['S0','S1','S2','S3','S4','S5','S6','S7','S8','S9-A','S9-B','S10','S11','S12','S13']
NS = {'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
NAVY, CYAN, GRAY = '172B43', '007E86', '5C6D7E'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def jwrite(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def xml(b): return E.fromstring(b)
def dump(r): return E.tostring(r,encoding='UTF-8',xml_declaration=True,standalone=True)
def q(prefix,tag): return '{'+NS[prefix]+'}'+tag
def shape(root,name):
    found=root.xpath('.//p:sp[p:nvSpPr/p:cNvPr[@name=$name]]',namespaces=NS,name=name)
    assert len(found)==1, name
    return found[0]
def rect(sh,x,y,w,h):
    xf=sh.find('p:spPr/a:xfrm',NS)
    for tag,attrs in [('off',{'x':x,'y':y}),('ext',{'cx':w,'cy':h})]:
        el=xf.find('a:'+tag,NS)
        for key,val in attrs.items():el.set(key,str(round(val*914400)))
def text(sh,lines):
    """Each line: text, point size, color, bold. Retain original shape styling."""
    tb=sh.find('p:txBody',NS)
    bp=tb.find('a:bodyPr',NS)
    for key,val in {'wrap':'square','lIns':'0','rIns':'0','tIns':'0','bIns':'0','anchor':'t'}.items():bp.set(key,val)
    for e in list(bp):
        if E.QName(e).localname in ['spAutoFit','normAutofit','noAutofit']:bp.remove(e)
    E.SubElement(bp,q('a','noAutofit'))
    for p in tb.findall('a:p',NS):tb.remove(p)
    for words,size,color,bold in lines:
        p=E.SubElement(tb,q('a','p'))
        pp=E.SubElement(p,q('a','pPr'),{'algn':'l','marL':'0','indent':'0'})
        line=E.SubElement(pp,q('a','lnSpc'));E.SubElement(line,q('a','spcPct'),{'val':'118000'})
        after=E.SubElement(pp,q('a','spcAft'));E.SubElement(after,q('a','spcPts'),{'val':'0'})
        r=E.SubElement(p,q('a','r'))
        rp=E.SubElement(r,q('a','rPr'),{'lang':'zh-CN','altLang':'en-US','sz':str(round(size*100)),'b':'1' if bold else '0','dirty':'0'})
        fill=E.SubElement(rp,q('a','solidFill'));E.SubElement(fill,q('a','srgbClr'),{'val':color})
        for tag in ['latin','ea','cs']:E.SubElement(rp,q('a',tag),{'typeface':'Microsoft YaHei'})
        E.SubElement(r,q('a','t')).text=words
        E.SubElement(p,q('a','endParaRPr'),{'lang':'zh-CN','sz':str(round(size*100))})

def section(n):
    source=SCRIPT.read_text(encoding='utf-8-sig').replace('\r\n','\n')
    s=re.search(rf'(?ms)^# S{n}｜.*?(?=^# |\Z)',source).group(0).rstrip()
    return re.sub(r'\n---\s*$','',s).rstrip()

def notes_target(z,slide_part):
    folder,name=posixpath.split(slide_part)
    rels=xml(z.read(folder+'/_rels/'+name+'.rels'))
    targets=[r.get('Target') for r in rels if r.get('Type','').endswith('/notesSlide')]
    assert len(targets)==1
    return posixpath.normpath(posixpath.join(folder,targets[0])) if not targets[0].startswith('/') else targets[0][1:]

def update_notes(b,content):
    r=xml(b)
    found=r.xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]',namespaces=NS)
    assert len(found)==1
    tb=found[0].find('p:txBody',NS)
    for p in tb.findall('a:p',NS):tb.remove(p)
    for line in content.split('\n'):
        p=E.SubElement(tb,q('a','p'))
        if line:
            run=E.SubElement(p,q('a','r'))
            E.SubElement(run,q('a','rPr'),{'lang':'zh-CN','sz':'1100'})
            E.SubElement(run,q('a','t')).text=line
        else:E.SubElement(p,q('a','endParaRPr'),{'lang':'zh-CN','sz':'1100'})
    return dump(r)

def build():
    assert not DECK.exists(), 'Use a new delivery version; do not overwrite a delivered deck.'
    assert sha(SOURCE)=='f09effacea63224484c9e8cf41747a6d59dde3669906b3d2a0bd2ff388339514'
    with zipfile.ZipFile(SOURCE) as z:
        assert z.testzip() is None
        replacements={}
        r=xml(z.read('ppt/slides/slide14.xml'))
        edits={
          'opening_sentence':(.76,1.844,11.8,1.10,[('本科这几年做过的事情虽然比较散，',27,NAVY,True),('但我慢慢确认了一件事。',27,NAVY,True)]),
          'curiosity':(.76,3.492,11.8,.85,[('我很喜欢从一个还没想清楚的问题出发，',20,GRAY,False),('再一点点把它变成可以研究、可以验证的东西。',20,GRAY,False)]),
          'limits':(.76,4.874,11.8,.86,[('做得越多，我也越能看到自己的不足：',20,NAVY,False),('比起把事情“做出来”，我更需要补的是理论理解和对结果的判断。',20,NAVY,False)]),
          'long_term':(.76,6.08,11.8,.81,[('所以我想找一个方向真正沉下去做几年，',20,CYAN,False),('直到能够对自己的判断和结论负责。',20,CYAN,False)]),
        }
        for name,(x,y,w,h,lines) in edits.items():sh=shape(r,name);rect(sh,x,y,w,h);text(sh,lines)
        replacements['ppt/slides/slide14.xml']=dump(r)
        r=xml(z.read('ppt/slides/slide15.xml'))
        edits={
          'experience':(.8,1.52,11.8,.72,[('我已经做过一些：',16,GRAY,False),('电磁仿真 · 周期结构 · 数值优化',19,GRAY,False)]),
          'question':(.78,2.61,11.8,.94,[('但我现在更想继续往下问：',17,GRAY,False),('为什么会有这样的响应？',28,NAVY,True)]),
          'physics_questions':(.8,3.87,11.8,.83,[('模式 · 边界 · 损耗 · 可靠性',23,NAVY,False),('背后到底是哪一部分物理在起作用？',19,GRAY,False)]),
          'lab':(.8,5.04,11.8,.43,[('Complex Waves and Fields',22,CYAN,False)]),
          'learning_boundary':(.8,5.54,11.8,.39,[('topology / non-Hermitian：这些是我接下来很想系统学习的方向',18,GRAY,False)]),
        }
        for name,(x,y,w,h,lines) in edits.items():sh=shape(r,name);rect(sh,x,y,w,h);text(sh,lines)
        for name,y in [('step1',2.27),('step2',3.57),('step3',4.73)]:rect(shape(r,name),.84,y,.5,.29)
        ending=deepcopy(shape(r,'experience'))
        ids=[int(v) for v in r.xpath('.//p:cNvPr/@id',namespaces=NS)]
        props=ending.find('p:nvSpPr/p:cNvPr',NS);props.set('id',str(max(ids)+1));props.set('name','long_term_direction')
        rect(ending,.8,6.14,11.8,.75)
        text(ending,[('我希望接下来能围绕一个方向连续做深',20,NAVY,False),('Westlake Physics · 定导培养',16,CYAN,False)])
        tree=r.find('p:cSld/p:spTree',NS)
        ext=tree.find('p:extLst',NS)
        if ext is None:tree.append(ending)
        else:tree.insert(list(tree).index(ext),ending)
        replacements['ppt/slides/slide15.xml']=dump(r)
        for n,page in [(12,14),(13,15)]:
            target=notes_target(z,f'ppt/slides/slide{page}.xml')
            replacements[target]=update_notes(z.read(target),section(n))
        with zipfile.ZipFile(DECK,'w',compression=zipfile.ZIP_DEFLATED) as dst:
            for item in z.infolist():dst.writestr(item,replacements.get(item.filename,z.read(item.filename)))
    with zipfile.ZipFile(SOURCE) as a,zipfile.ZipFile(DECK) as b:
        assert set(a.namelist())==set(b.namelist())
        changed=[n for n in a.namelist() if a.read(n)!=b.read(n)]
        assert set(changed)==set(replacements)
        media=[n for n in a.namelist() if n.startswith('ppt/media/')]
        assert all(a.read(n)==b.read(n) for n in media)
    src=Presentation(SOURCE);dst=Presentation(DECK)
    assert len(src.slides)==len(dst.slides)==15
    for i in range(13):
        assert src.slides[i].part.blob==dst.slides[i].part.blob
        assert src.slides[i].notes_slide.part.blob==dst.slides[i].notes_slide.part.blob
    (OUT/'逐页备注').mkdir(exist_ok=True)
    rows=[]
    for i,key in enumerate(KEYS):
        note=dst.slides[i].notes_slide.notes_text_frame.text
        if i>=13:assert note==section(i-1)
        (OUT/'逐页备注'/f'{i+1:02d}_{key}.md').write_text(note,encoding='utf-8')
        rows.append({'page':i+1,'logical':key,'page_source':'本人微调后的完整 PPT v1' if i<13 else '本轮用户指定文案',
          'notes_source':'本人微调后的完整 PPT v1，原样保留' if i<13 else SCRIPT.name+f'，S{i-1}章节全文',
          'notes_sha256':hashlib.sha256(note.encode()).hexdigest(),
          'slide_xml_unchanged':src.slides[i].part.blob==dst.slides[i].part.blob,
          'notes_xml_unchanged':src.slides[i].notes_slide.part.blob==dst.slides[i].notes_slide.part.blob})
    jwrite(OUT/'页码与来源映射.json',rows)
    jwrite(OUT/'局部修改检查.json',{'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=PI,text=True).strip(),
      'source_pptx':str(SOURCE),'source_sha256':sha(SOURCE),'v5_script_sha256':sha(SCRIPT),
      'output_sha256':sha(DECK),'changed_package_parts':changed,'unchanged_media_count':len(media),
      'S0_S11_slide_and_notes_xml_unchanged':True,'S12_S13_notes_exact_v5':True,
      'package_parts_added':0,'package_parts_removed':0,'images_added':0})
    print(json.dumps({'output':str(DECK),'changed_parts':changed,'slides':15,'S0_S11_exact':True},ensure_ascii=False),flush=True)

if __name__=='__main__':build()
