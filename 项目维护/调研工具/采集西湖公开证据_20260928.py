"""只采集公开网页，保留原始响应、解析正文、URL、日期与哈希；不运行科研原件。"""
from pathlib import Path
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
import requests, hashlib, json, sys, re

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'A线_西湖博士/导师资料'

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.links=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('p','div','br','li','h1','h2','h3','h4','tr'): self.parts.append('\n')
        if tag=='a':
            d=dict(attrs)
            if d.get('href'): self.links.append(d['href'])
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)

def parse(raw):
    p=Parser(); p.feed(raw)
    # 西湖新版教师页把正文存放于脚本的 JSON 字符串；只解码字符串，不执行脚本。
    for match in re.finditer(r'"(?:\\.|[^"\\])*"',raw):
        try: value=json.loads(match.group())
        except Exception: continue
        if isinstance(value,str) and ('<p' in value or '<div' in value): p.feed(value)
    return '\n'.join(x.strip() for x in ''.join(p.parts).splitlines() if x.strip()),p.links

def fetch(item):
    name,key,url=item
    folder=BASE/name/'公开证据'/'2026-09-28'; folder.mkdir(parents=True,exist_ok=True)
    meta={'source_url':url,'checked_date':'2026-09-28','key':key,'scope':'公开网页；HTTP成功不等于内容有效；正文须人工核读'}
    try:
        r=requests.get(url,timeout=35,headers={'User-Agent':'Mozilla/5.0'})
        meta.update(status=r.status_code,final_url=r.url)
        if r.status_code==200:
            raw=r.content; (folder/(key+'.html')).write_bytes(raw)
            r.encoding='utf-8'; txt,links=parse(r.text)
            (folder/(key+'.txt')).write_text(txt,encoding='utf-8')
            meta.update(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),links=list(dict.fromkeys(links)))
            result={'pi':name,'key':key,'status':r.status_code,'chars':len(txt)}
        else: result={'pi':name,'key':key,'status':r.status_code}
    except Exception as e:
        meta['error']=str(e); result={'pi':name,'key':key,'error':str(e)}
    (folder/(key+'.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    items=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
    with ThreadPoolExecutor(max_workers=8) as ex:
        for r in ex.map(fetch,items): print(json.dumps(r,ensure_ascii=False),flush=True)
