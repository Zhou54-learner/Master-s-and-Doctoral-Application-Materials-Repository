"""Create a separate Liu Shi candidate; preserve all source and sent files."""
from pathlib import Path
from xml.dom import minidom
import zipfile, hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '公共资料/简历与文书'
PACK = ROOT / 'A线_西湖博士/联系材料/刘仕'
OUT = PACK / '当前材料'
OLD = '计算物理 · 科学机器学习 · 物理驱动的逆向设计'
NEW = '计算材料物理 · 第一性原理与多尺度模拟 · 科学机器学习'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    records=[]
    for folder in ['当前材料/首封附件_待终读', '当前材料/备用论文', '准备记录']:
        (PACK/folder).mkdir(parents=True, exist_ok=True)
    src=BASE/'校对稿/周子靖_中文学术简历_Master_v1.3_CANDIDATE.docx'
    dst=OUT/'周子靖_中文学术简历_刘仕版_v1_CANDIDATE.docx'
    if dst.exists(): raise FileExistsError(dst)
    with zipfile.ZipFile(src) as z:
        content={n:z.read(n) for n in z.namelist()}
    doc=minidom.parseString(content['word/document.xml'])
    count=0
    for n in doc.getElementsByTagName('w:t'):
        if n.firstChild and n.firstChild.data==OLD:
            n.firstChild.data=NEW
            count+=1
    assert count==1, count
    content['word/document.xml']=doc.toxml(encoding='utf-8')
    with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in content.items(): z.writestr(name,data)
    text=(BASE/'周子靖_中文学术简历_v0.6_INTERNAL.md').read_text(encoding='utf-8-sig')
    assert text.count(OLD)==1
    (OUT/'周子靖_中文学术简历_刘仕版_v1_CANDIDATE.md').write_text(text.replace(OLD,NEW),encoding='utf-8')
    records.append({'source':str(src.relative_to(ROOT)),'source_sha256':digest(src),'output':str(dst.relative_to(ROOT)),'output_sha256':digest(dst),'change':'Only research-interest paragraph; remains CANDIDATE.'})
    sent=ROOT/'A线_西湖博士/联系材料/刘癸庚/当前材料/首封附件'
    copies=[(sent/'周子靖_本科成绩单.pdf',OUT/'首封附件_待终读/周子靖_本科成绩单.pdf')]
    for name in ['磁纳米合金与石墨烯复合吸波材料_2025.pdf','二维尘埃等离子体晶格波特性研究_2025.pdf']:
        copies.append((sent/name,OUT/'备用论文'/name))
    for source,target in copies:
        if target.exists(): raise FileExistsError(target)
        shutil.copyfile(source,target)
        assert digest(source)==digest(target)
        records.append({'source':str(source.relative_to(ROOT)),'output':str(target.relative_to(ROOT)),'sha256':digest(target),'size':target.stat().st_size})
    frozen=list((BASE/'对外PDF').glob('*v1.2*'))+list((ROOT/'A线_西湖博士/联系材料/刘癸庚/当前材料').rglob('*'))
    preserved=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in frozen if p.is_file()]
    (PACK/'准备记录/来源与基线哈希_v1.json').write_text(json.dumps({'date':'2026-09-29','artifacts':records,'preserved_baselines':preserved},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Candidate DOCX and three unchanged supporting PDFs created.')

if __name__=='__main__': main()
