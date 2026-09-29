"""Derive the Tian candidate without modifying the shared or sent baseline."""
from pathlib import Path
from xml.dom import minidom
import zipfile, hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[4]
PACK=ROOT/'A线_西湖博士/联系材料/田静逸'
BASE=ROOT/'公共资料/简历与文书'
OUT=PACK/'当前材料'
ATT=OUT/'首封附件_待终读'
OLD='计算物理 · 科学机器学习 · 物理驱动的逆向设计'
NEW='计算物理 · 电磁与光学结构设计 · 科学机器学习'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

ATT.mkdir(parents=True,exist_ok=True)
(PACK/'准备记录').mkdir(exist_ok=True)
src=BASE/'校对稿/周子靖_中文学术简历_Master_v1.3_CANDIDATE.docx'
dst=OUT/'周子靖_中文学术简历_田静逸版_v1_CANDIDATE.docx'
if dst.exists(): raise FileExistsError(dst)
with zipfile.ZipFile(src) as z: data={n:z.read(n) for n in z.namelist()}
doc=minidom.parseString(data['word/document.xml'])
nodes=[n for n in doc.getElementsByTagName('w:t') if n.firstChild and n.firstChild.data==OLD]
assert len(nodes)==1
nodes[0].firstChild.data=NEW
data['word/document.xml']=doc.toxml(encoding='utf-8')
with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
    for name,value in data.items(): z.writestr(name,value)
text=(BASE/'周子靖_中文学术简历_v0.6_INTERNAL.md').read_text(encoding='utf-8-sig')
assert text.count(OLD)==1
(OUT/'周子靖_中文学术简历_田静逸版_v1_CANDIDATE.md').write_text(text.replace(OLD,NEW),encoding='utf-8')
records=[{'source':str(src.relative_to(ROOT)),'source_sha256':sha(src),'output':str(dst.relative_to(ROOT)),'output_sha256':sha(dst),'change':'Only research interests; remains CANDIDATE.'}]
sent=ROOT/'A线_西湖博士/联系材料/刘癸庚/当前材料/首封附件'
for name in ['周子靖_本科成绩单.pdf','磁纳米合金与石墨烯复合吸波材料_2025.pdf','二维尘埃等离子体晶格波特性研究_2025.pdf']:
    source=sent/name
    target=ATT/name
    if target.exists(): raise FileExistsError(target)
    shutil.copyfile(source,target)
    assert sha(source)==sha(target)
    records.append({'source':str(source.relative_to(ROOT)),'output':str(target.relative_to(ROOT)),'sha256':sha(target),'size':target.stat().st_size})
(PACK/'准备记录/来源与基线哈希_v1.json').write_text(json.dumps({'date':'2026-09-29','artifacts':records},ensure_ascii=False,indent=2),encoding='utf-8')
print('Tian candidate and three supporting PDFs created.')
