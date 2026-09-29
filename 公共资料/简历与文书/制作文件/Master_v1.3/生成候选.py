"""Derive v1.3 from the frozen v1.2 DOCX package without modifying the baseline.

Uses stdlib OpenXML editing and a separate Microsoft Word PDF export step.
Default refuses overwrite; --refresh is only for this unaccepted candidate.
"""
from pathlib import Path
from xml.dom import minidom as D
import argparse, re, zipfile, json

ROOT = Path(__file__).resolve().parents[4]
CV = ROOT / '公共资料/简历与文书'
BASE = CV / '对外PDF/周子靖_中文学术简历_Master_v1.2.docx'
SOURCE = CV / '周子靖_中文学术简历_v0.6_INTERNAL.md'
OUT = CV / '校对稿/周子靖_中文学术简历_Master_v1.3_CANDIDATE.docx'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--refresh',action='store_true')
    ap.add_argument('--leading',type=float,default=14)
    args=ap.parse_args()
    if OUT.exists() and not args.refresh: raise FileExistsError(OUT)
    with zipfile.ZipFile(BASE) as z: package={n:z.read(n) for n in z.namelist()}
    doc=D.parseString(package['word/document.xml'])
    rels=D.parseString(package['word/_rels/document.xml.rels'])
    body=doc.getElementsByTagName('w:body')[0]
    oldparas=[n for n in body.childNodes if n.nodeName=='w:p']
    def txt(n): return ''.join(x.firstChild.data if x.firstChild else '' for x in n.getElementsByTagName('w:t'))
    def sample(prefix): return next(p for p in oldparas if txt(p).startswith(prefix))
    templates={k:sample(v).getElementsByTagName('w:pPr')[0].cloneNode(True) for k,v in {
        'name':'周子靖','contact':'Zijing','heading':'教育背景','body':'应用物理学本科',
        'dated':'本科毕业设计','bullet':'• 仿真自动化','cite':'雨田','doi':'DOI'}.items()}
    for p in oldparas: body.removeChild(p)
    sect=doc.getElementsByTagName('w:sectPr')[0]
    def el(name,attrs=None):
        n=doc.createElementNS(W,'w:'+name)
        for k,v in (attrs or {}).items():n.setAttributeNS(W,'w:'+k,str(v))
        return n
    def setprop(parent,name,attrs):
        nodes=[n for n in parent.childNodes if n.nodeName=='w:'+name]
        n=nodes[0] if nodes else el(name)
        if not nodes:parent.appendChild(n)
        for k,v in attrs.items():n.setAttributeNS(W,'w:'+k,str(v))
    def para(kind,before=0,after=0,keep=False):
        p=el('p');pr=templates[kind].cloneNode(True);p.appendChild(pr)
        setprop(pr,'keepNext',{'val':1 if keep else 0})
        leading=28 if kind=='name' else 16 if kind=='heading' else args.leading
        setprop(pr,'spacing',{'before':round(before*20),'after':round(after*20),'line':round(leading*20),'lineRule':'exact'})
        body.insertBefore(p,sect)
        return p
    link_count=0
    def run(p,text,size=10.5,bold=False,color='222222',italic=False,uri=None,subscript=False):
        nonlocal link_count
        r=el('r');pr=el('rPr');r.appendChild(pr)
        face='Source Han Sans CN Bold' if bold else 'Source Han Sans CN Regular'
        pr.appendChild(el('rFonts',{k:face for k in ['ascii','hAnsi','eastAsia','cs']}))
        pr.appendChild(el('sz',{'val':round(size*2)}));pr.appendChild(el('color',{'val':color}))
        if bold:pr.appendChild(el('b'))
        if italic:pr.appendChild(el('i'))
        if subscript:pr.appendChild(el('vertAlign',{'val':'subscript'}))
        for i,part in enumerate(text.split('\t')):
            if i:r.appendChild(el('tab'))
            t=el('t');t.setAttribute('xml:space','preserve');t.appendChild(doc.createTextNode(part));r.appendChild(t)
        if uri:
            link_count+=1;rid='rIdCV13Link'+str(link_count)
            rel=rels.createElement('Relationship');rel.setAttribute('Id',rid);rel.setAttribute('Type',R+'/hyperlink');rel.setAttribute('Target',uri);rel.setAttribute('TargetMode','External');rels.documentElement.appendChild(rel)
            h=el('hyperlink');h.setAttributeNS(R,'r:id',rid);h.appendChild(r);p.appendChild(h)
        else:p.appendChild(r)
    def rich(p,text,size=10.5,color='222222'):
        for part in re.split(r'(\*\*.*?\*\*|\*[^*]+\*)',text):
            if not part:continue
            bold=part.startswith('**') and part.endswith('**');italic=not bold and part.startswith('*') and part.endswith('*')
            value=part[2:-2] if bold else part[1:-1] if italic else part
            value=value.replace('Zijing Zhou','Zijing\u00a0Zhou')
            for piece in re.split('(Nb₂CTₓ)',value):
                if piece=='Nb₂CTₓ':
                    run(p,'Nb',size,bold,color);run(p,'2',size,bold,color,subscript=True)
                    run(p,'CT',size,bold,color);run(p,'x',size,bold,color,italic=True,subscript=True)
                elif piece:run(p,piece,size,bold,color,italic)
    section='';footnote=''
    for raw in SOURCE.read_text(encoding='utf-8').splitlines():
        s=raw.strip()
        if not s:continue
        if s.startswith('*80.20'):
            footnote=s.strip('*');continue
        if s.startswith('# '):rich(para('name',after=2),'**'+s[2:]+'**',24)
        elif s.startswith('Zijing'):
            p=para('contact',after=1);name,email=s.split(' | ');run(p,name+'   |   ',10,color='555555');run(p,email,10,color='555555',uri='mailto:'+email)
        elif s.startswith('## '):
            section=s[3:];rich(para('heading',before=3,after=2,keep=True),'**'+section+'**',11.5)
        elif section=='论文发表（共同作者）' and re.match(r'^\d+\.',s):
            citation,doi=s.split(' DOI：');p=para('cite',before=2,keep=True);rich(p,citation)
            p=para('doi',keep=not s.startswith('3.'));run(p,'DOI：',9,color='555555');run(p,doi,9,color='555555',uri='https://doi.org/'+doi)
        elif ' | ' in s:
            label,date=s.rsplit(' | ',1);p=para('dated',before=2 if label.startswith('**合作') else 0,keep=section=='科研经历' or label.startswith('**哈尔'))
            rich(p,label);run(p,'\t'+date,9,color='555555')
        elif s.startswith('- '):
            content=s[2:]
            if section.startswith('论文发表'):rich(para('body'),content)
            else:rich(para('bullet',after=1),'• '+content)
        else:rich(para('body',keep=s.startswith(('**国家级','项目编号','指导教师'))),s,10 if s.startswith('算术均分') else 10.5)
    p=para('body',before=4);setprop(p.getElementsByTagName('w:pPr')[0],'spacing',{'line':'220'})
    run(p,'*'+footnote,9,color='555555')
    # Keep the existing A4 section/margins and footer relationships from v1.2.
    package['word/document.xml']=doc.toxml(encoding='UTF-8')
    package['word/_rels/document.xml.rels']=rels.toxml(encoding='UTF-8')
    # Status is in filename, document properties and review entry, not an external-looking claim in CV body.
    if 'docProps/core.xml' in package:
        core=D.parseString(package['docProps/core.xml'])
        for tag,value in [('dc:title','周子靖 | 中文学术简历 | Master v1.3 CANDIDATE'),('dc:description','Candidate for user review; not READY; not sent.')]:
            found=core.getElementsByTagName(tag)
            if found:
                n=found[0]
                for c in list(n.childNodes):n.removeChild(c)
                n.appendChild(core.createTextNode(value))
        package['docProps/core.xml']=core.toxml(encoding='UTF-8')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in package.items():z.writestr(n,b)
    print(json.dumps({'output':str(OUT),'body_pt':10.5,'leading_pt':args.leading,'doi_note_pt':9,'template':str(BASE)},ensure_ascii=False))

if __name__=='__main__':main()
