"""Public text-only evidence fetch; no personal data are sent."""
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib,json,re,html

OUT=Path(__file__).resolve().parent.parent/'公开来源'
OUT.mkdir(exist_ok=True)
assert not (OUT/'来源记录.json').exists(), 'Evidence archive already exists; use a new version directory.'
records=[]
for key,url in [('O01','https://en.westlake.edu.cn/faculty/guigeng-liu.html'),('P01','https://www.liuguigeng.com/')]:
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20) as response:
            data=response.read();status=response.status;final=response.url
        raw=OUT/(key+'.html')
        if raw.exists():raise FileExistsError('Do not overwrite archived source')
        raw.write_bytes(data)
        text=data.decode('utf-8',errors='replace')
        text=re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',text,flags=re.S|re.I)
        text=html.unescape(re.sub('<[^>]+>',' ',text));text=re.sub(r'\s+',' ',text)
        excerpts=[]
        for term in ['Laboratory of Complex Waves and Fields','topological photonics','non-Hermitian optics']:
            pos=text.lower().find(term.lower())
            if pos>=0:excerpts.append(dict(term=term,excerpt=text[max(0,pos-80):pos+450]))
        record=dict(id=key,url=url,final_url=final,status=status,access_date='2026-10-05',
                    sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),excerpts=excerpts,
                    evidence_type='University official page' if key=='O01' else 'Lab/PI self-description')
    except Exception as e:
        record=dict(id=key,url=url,access_date='2026-10-05',error=str(e),
                    fallback='Public web tool check and 2026-09-28 repository archive; not a successful local fetch.')
    records.append(record)
(OUT/'来源记录.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(records,ensure_ascii=False))
