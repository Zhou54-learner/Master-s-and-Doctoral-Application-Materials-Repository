"""Capture primary public sources for the limited S13 statements."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json,hashlib,re,requests
PI=Path(__file__).resolve().parents[2]
OUT=PI/'S13_WhyLiu_v2_20261006/官方来源';OUT.mkdir(exist_ok=True)
SOURCES=[
 ('westlake_physics','https://physics.westlake.edu.cn/programs/graduate_program/',['定导','第一责任人']),
 ('liu_lab','https://www.liuguigeng.com/',['mechanism','non-Hermitian','Topological','metamaterials']),
 ('westlake_faculty','https://en.westlake.edu.cn/faculty/guigeng-liu.html',['Complex Waves and Fields'])]
def fetch(item):
    key,url,terms=item
    response=requests.get(url,timeout=45)
    if response.status_code==403:
        # Primary page text separately checked through the browser/search tool on
        # 2026-10-06. Only the narrow supporting excerpt is retained, not a full page copy.
        fallback={
            'westlake_physics':('物理学专业博士研究生教育采用定导招生培养模式。','Official Physics graduate-program page; browser search index reported crawled last week.'),
            'westlake_faculty':('Laboratory of Complex Waves and Fields','Official faculty page; browser search index reported crawled last week.')}
        excerpt,method=fallback[key]
        path=OUT/(key+'_核验摘录.txt')
        path.write_text(f'URL: {url}\nVerified: 2026-10-06\nMethod: {method}\nDirect HTTP: 403; not represented as a successful raw download.\nSupporting excerpt: {excerpt}\n',encoding='utf8')
        return dict(key=key,url=url,status=403,verified_date='2026-10-06',verification_method=method,
            supporting_excerpt=excerpt,file=path.name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    response.raise_for_status()
    path=OUT/(key+'.html');path.write_bytes(response.content)
    content=response.content.decode('utf8',errors='replace')
    matches={t:[re.sub(r'\s+',' ',content[max(0,m.start()-180):m.end()+200]) for m in list(re.finditer(re.escape(t),content,re.I))[:4]] for t in terms}
    assert all(matches.values()),(key,matches)
    return dict(key=key,url=url,final_url=response.url,status=response.status_code,retrieved_utc=datetime.now(timezone.utc).isoformat(),
        file=path.name,bytes=len(response.content),sha256=hashlib.sha256(response.content).hexdigest(),exact_contexts=matches)
with ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(fetch,SOURCES))
(OUT/'来源记录.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
for r in records:print(json.dumps(dict(source=r['key'],status=r['status'],file=r['file']),ensure_ascii=False))
