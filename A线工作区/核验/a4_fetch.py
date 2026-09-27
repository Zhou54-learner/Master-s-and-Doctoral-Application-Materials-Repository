from pathlib import Path
import sys, json, hashlib, concurrent.futures
from datetime import datetime
from urllib.request import Request, urlopen
sys.path.insert(0, str(Path(__file__).parent/'a4_runtime'))
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]/'联系/刘癸庚'
OUT=ROOT/'04_Background_Notes/official_snapshots'
OUT.mkdir(parents=True,exist_ok=True)
URLS={
 'faculty':'https://en.westlake.edu.cn/faculty/guigeng-liu.html',
 'lab':'https://www.liuguigeng.com/',
 'job':'https://www.liuguigeng.com/job/',
 'admissions':'https://www.westlake.edu.cn/admissions/graduate/brochure/general/',
 'notice_2027':'https://www.westlake.edu.cn/admissions/graduate/brochure/general/202608/t20260813_68957.html',
}
def fetch(item):
 key,url=item
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:
   raw=r.read(); meta={'url':url,'final_url':r.url,'status':r.status,'retrieved_local':datetime.now().isoformat(),'sha256':hashlib.sha256(raw).hexdigest()}
  (OUT/f'{key}.html').write_bytes(raw)
  soup=BeautifulSoup(raw,'html.parser')
  for s in soup.find_all('script'):
   if 'detailContent:' in s.get_text():
    try:
     article,_=json.JSONDecoder().raw_decode(s.get_text().split('detailContent:',1)[1].lstrip())
     soup=BeautifulSoup(article,'html.parser');break
    except Exception:pass
  for t in soup(['script','style','noscript']):t.decompose()
  txt=soup.get_text('\n',strip=True)
  (OUT/f'{key}.txt').write_text(txt,encoding='utf-8')
  meta['links']=[{'text':a.get_text(' ',strip=True),'href':a['href']} for a in soup.find_all('a',href=True)]
  (OUT/f'{key}.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
  return key,txt,meta['links']
 except Exception as e:return key,str(e),[]
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  for k,t,l in pool.map(fetch,URLS.items()):
   print(k,t[:18000],json.dumps(l,ensure_ascii=False))
