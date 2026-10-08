"""Capture pre-edit file hashes. Run once; an existing baseline is never replaced."""
from pathlib import Path
import hashlib, json

OUT=Path(__file__).resolve().parents[1]
PI=OUT.parent
ROOT=next(p for p in PI.parents if (p/'申请路线总览.md').exists())
BASELINE=OUT/'制作前保全基线.json'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def record(path): return dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,sha256=sha(path))

def main():
    assert not BASELINE.exists(), 'Never overwrite the pre-edit baseline'
    excluded={OUT,PI/'S12_WhyPhD_v2.1_20261006'}
    paths=[p for p in PI.rglob('*') if p.is_file() and p!=PI/'README.md'
           and '__pycache__' not in p.parts and not any(d in p.parents for d in excluded)]
    unrelated=[ROOT/p for p in [
        '公共资料/面试与导师交流中心/公共主干/README.md',
        '公共资料/面试与导师交流中心/公共主干/项目重建/本科毕设/README.md',
        '公共资料/面试与导师交流中心/公共主干/项目重建/本科毕设/13_实际工作梳理与研究叙事底稿.md']]
    data=dict(date='2026-10-06',branch='chatgpt/liu-interview-plan-20261004',
              protected_candidates=[record(p) for p in sorted(paths)],
              unrelated=[record(p) for p in unrelated],
              allowed_existing_document_updates=['A线_西湖博士/工作台.md', (PI/'README.md').relative_to(ROOT).as_posix()],
              policy='All existing slide files, shared builders, notes, review sheets and original S12 v2 remain byte-identical. S12 is patched into a new v2.1 directory.')
    BASELINE.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Protected:', len(paths),'existing PI files;',len(unrelated),'unrelated working files')

if __name__=='__main__':main()
