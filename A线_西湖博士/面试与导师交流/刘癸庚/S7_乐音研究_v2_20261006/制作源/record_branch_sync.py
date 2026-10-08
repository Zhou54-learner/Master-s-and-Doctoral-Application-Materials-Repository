"""Record exact upstream-only note changes that arrived during S7 production."""
from pathlib import Path
import subprocess,json,hashlib
OUT=Path(__file__).resolve().parent.parent
ROOT=next(p for p in OUT.parents if (p/'申请路线总览.md').exists())
remote='03ea41f66ba46b9e901af35742ce243b6e27df28'
names=['FULL_DRAFT_v0.1_20261006/逐页备注/04_S3.md','FULL_DRAFT_v0.1_20261006/逐页备注/05_S4.md','FULL_DRAFT_v0.1_20261006/逐页备注/06_S5.md','完整讲稿_当前版本合并版_v2_20261006.md']
records=[]
for name in names:
 p=OUT.parent/name;rel=p.relative_to(ROOT).as_posix()
 b=subprocess.check_output(['git','show',remote+':'+rel],cwd=ROOT)
 digest=hashlib.sha256(b).hexdigest();assert digest==hashlib.sha256(p.read_bytes()).hexdigest()
 records.append(dict(path=p.as_posix(),remote_sha256=digest,remote_commit=remote,task_action='Read and preserve exact upstream content; no S7-authored edits.'))
(OUT/'检查证据/同期远端更新保全.json').write_text(json.dumps(dict(before_sync='31bf0da',upstream_commit=remote,reason='First push rejected because same branch advanced independently; retained six remote commits through a same-branch merge, never main. S7 delta relative to upstream remains its candidate folder and A workbench only.',files=records),ensure_ascii=False,indent=2),encoding='utf8')
