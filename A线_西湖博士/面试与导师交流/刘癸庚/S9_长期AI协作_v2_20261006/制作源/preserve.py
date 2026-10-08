"""Freeze and compare read-only references; never restore or modify shared work."""
from pathlib import Path
import hashlib,json,subprocess,argparse
OUT=Path(__file__).resolve().parents[1];PI=OUT.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
OWN={'S8_项目AI协作_v2_20261006','S9_长期AI协作_v2_20261006'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT).decode('utf8').strip()
def freeze():
    dest=OUT/'检查证据/接手文件基线.json';dest.parent.mkdir(exist_ok=True)
    if dest.exists():raise RuntimeError('Baseline exists; do not overwrite.')
    files=[p for p in PI.rglob('*') if p.is_file() and p.relative_to(PI).parts[0] not in OWN and not p.name.startswith('~$')]
    files+=[ROOT/'A线_西湖博士/工作台.md',ROOT/'A线_西湖博士/联系记录.md']
    files+=list((ROOT/'公共资料/事实核验/个人探索_20261004').rglob('*.png'))
    files+=[ROOT/'公共资料/面试与导师交流中心/公共主干'/x for x in ['README.md','项目重建/本科毕设/README.md','项目重建/本科毕设/13_实际工作梳理与研究叙事底稿.md']]
    records=[]
    for p in sorted(set(files)):
        if not p.exists():continue
        rel=p.relative_to(ROOT).as_posix()
        active=('S7_乐音研究_v2_20261006' in rel or 'FULL_DRAFT_v0.1_20261006' in rel or rel=='A线_西湖博士/工作台.md' or rel.startswith('公共资料/面试与导师交流中心/'))
        records.append(dict(path=rel,bytes=p.stat().st_size,sha256=sha(p),concurrent_or_preexisting_dirty_scope=active))
    data=dict(head=git('rev-parse','HEAD'),branch=git('branch','--show-current'),
        status=git('-c','core.quotepath=false','status','--short'),records=records,
        excluded='PowerPoint ~$ lock files are open application locks, not content; excluded from hashing.',
        policy='Only new S8/S9 v2 directories may be written. Concurrent changes are recorded, never reverted.')
    dest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    print('Frozen',len(records),'existing files.')
def check():
    baseline=json.loads((OUT/'检查证据/接手文件基线.json').read_text(encoding='utf8'))
    changed=[]
    for r in baseline['records']:
        p=ROOT/r['path'];now=sha(p) if p.exists() else None
        if now!=r['sha256']:changed.append(dict(**r,after_sha256=now))
    result=dict(baseline_head=baseline['head'],current_head=git('rev-parse','HEAD'),
        checked=len(baseline['records']),unchanged=len(baseline['records'])-len(changed),changed=changed,
        note='A change in a concurrent scope is not attributed to this task; no restoration or overwrite is performed.')
    (OUT/'检查证据/既有文件保全.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['freeze','check']);a=parser.parse_args()
    freeze() if a.mode=='freeze' else check()
