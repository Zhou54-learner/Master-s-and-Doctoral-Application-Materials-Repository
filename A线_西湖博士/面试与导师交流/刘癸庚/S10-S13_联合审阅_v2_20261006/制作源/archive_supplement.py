"""Archive the two user-supplied files without altering originals."""
from pathlib import Path
import json,shutil,hashlib
from PIL import Image
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'申请路线总览.md').exists())
FACTS=ROOT/'公共资料/事实核验/个人探索_20261006'
records=[]
for source,name,role in [
    (Path('E:/2022/download/知识与未来的对话.png'),'AgentNative_文章封面原图_用户提供.png','Article cover matching the first article screenshot. Supplementary source only; not the webpage homepage and not used as a replacement screenshot.'),
    (Path('C:/Users/zzj/AppData/Local/Temp/codex-clipboard-f1d6b191-e28c-4e9d-a356-041d838573a7.png'),'个人艺术网页首页_用户补图_20261006.png','User-supplied actual homepage screenshot; selected for S11 v2.')]:
    data=source.read_bytes();target=FACTS/'素材'/name
    if target.exists():assert target.read_bytes()==data
    else:shutil.copyfile(source,target)
    records.append(dict(source=str(source),copy=target.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),pixels=list(Image.open(target).size),role=role,original_unchanged=source.read_bytes()==data))
(FACTS/'本人补充素材核验.json').write_text(json.dumps(dict(date='2026-10-06',files=records),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(records,ensure_ascii=False))
