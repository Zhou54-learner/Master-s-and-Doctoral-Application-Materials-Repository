"""Record and check existing assets. Never writes any source or earlier candidate."""
from pathlib import Path
import argparse, hashlib, json, subprocess
OUT=Path(__file__).resolve().parents[1]
PI=OUT.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
S8=PI/'S8_项目AI协作_v3_20261006'
QA=OUT/'检查证据'
METHOD=Path('F:/Physics_Learning_Assistant/docs/methodology')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(*args): return subprocess.check_output(args,cwd=ROOT).decode('utf8').strip()
def snapshot():
    QA.mkdir(parents=True,exist_ok=True)
    dst=QA/'接手文件基线.json'
    assert not dst.exists(), 'Do not overwrite the baseline.'
    paths=[p for p in PI.rglob('*') if p.is_file() and not p.is_relative_to(OUT) and not p.is_relative_to(S8) and p!=PI/'README.md' and '__pycache__' not in p.parts and not p.name.startswith('~$')]
    paths+=list((ROOT/'公共资料/事实核验/个人探索_20261004').rglob('*'))
    paths+=list(METHOD.glob('*.md'))
    paths += [ROOT/'公共资料/面试与导师交流中心/公共主干/README.md', ROOT/'公共资料/面试与导师交流中心/公共主干/项目重建/本科毕设/README.md', ROOT/'公共资料/面试与导师交流中心/公共主干/项目重建/本科毕设/13_实际工作梳理与研究叙事底稿.md']
    paths=sorted(set(p for p in paths if p.is_file()))
    data={'date':'2026-10-06','branch':run('git','branch','--show-current'),'head':run('git','rev-parse','HEAD'),
          'git_status':run('git','-c','core.quotepath=false','status','--short'),
          'pr':json.loads(run('gh','pr','view','15','--json','number,state,autoMergeRequest,headRefName,baseRefName,url')),
          'intentional_index_updates':['A线_西湖博士/工作台.md',str((PI/'README.md').relative_to(ROOT))],
          'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]}
    dst.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    print('Preservation baseline:',len(paths),'files')
def check():
    data=json.loads((QA/'接手文件基线.json').read_text(encoding='utf8'))
    changed=[{**r,'current_sha256':sha(Path(r['path'])) if Path(r['path']).exists() else None} for r in data['files'] if not Path(r['path']).exists() or sha(Path(r['path']))!=r['sha256']]
    result={'checked':len(data['files']),'unchanged':len(data['files'])-len(changed),'changed':changed,
            'note':'Comparison is to actual working files on entry, including the already modified FULL_DRAFT; not to git HEAD.'}
    (QA/'既有文件保全.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False))
    assert not changed
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['snapshot','check'])
    snapshot() if a.parse_args().mode=='snapshot' else check()
