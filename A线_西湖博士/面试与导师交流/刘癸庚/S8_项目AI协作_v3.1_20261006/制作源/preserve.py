"""Snapshot/check pre-existing working files without touching earlier candidates."""
from pathlib import Path
import argparse, hashlib, json, subprocess

OUT = Path(__file__).resolve().parents[1]
PI = OUT.parent
ROOT = next(p for p in PI.parents if (p / '申请路线总览.md').exists())
QA = OUT / '检查证据'
EDITABLE_INDEXES = [ROOT / 'A线_西湖博士/工作台.md', PI / 'README.md']
EXTERNAL = [
    Path('C:/Users/zzj/AppData/Local/Temp/codex-clipboard-b644b31b-e1b9-4b9b-b47f-885f6e5b9b78.png'),
    Path('C:/Users/zzj/AppData/Local/Temp/codex-clipboard-0e0a1748-18db-43bd-8fe8-e1ffa9e05484.png'),
]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def snapshot():
    QA.mkdir(parents=True, exist_ok=True)
    dest = QA / '接手文件基线.json'
    assert not dest.exists(), 'Never overwrite the entry baseline.'
    paths = [p for p in PI.rglob('*') if p.is_file() and not p.is_relative_to(OUT)
             and p not in EDITABLE_INDEXES and '__pycache__' not in p.parts and not p.name.startswith('~$')]
    paths += [p for p in (ROOT / '公共资料/事实核验/个人探索_20261004').rglob('*') if p.is_file()]
    paths += [ROOT / '公共资料/事实核验/个人探索_20261006/S8S9_协作方法续核.md']
    paths += [ROOT / '公共资料/面试与导师交流中心/公共主干/README.md',
              ROOT / '公共资料/面试与导师交流中心/公共主干/项目重建/本科毕设/README.md',
              ROOT / '公共资料/面试与导师交流中心/公共主干/项目重建/本科毕设/13_实际工作梳理与研究叙事底稿.md']
    paths += EXTERNAL
    paths = sorted(set(paths))
    def git(*args):
        return subprocess.check_output(['git', '-c', 'core.quotepath=false', *args], cwd=ROOT).decode('utf8').strip()
    data = {'date': '2026-10-06', 'branch': git('branch', '--show-current'), 'head': git('rev-parse', 'HEAD'),
            'git_status_on_entry': git('status', '--short'),
            'intentional_index_updates': [str(p.relative_to(ROOT)) for p in EDITABLE_INDEXES],
            'files': [{'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in paths]}
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf8')
    print('Preservation baseline:', len(paths), 'files')

def check():
    baseline = json.loads((QA / '接手文件基线.json').read_text(encoding='utf8'))
    changes = [{**r, 'current_sha256': sha(Path(r['path'])) if Path(r['path']).exists() else None}
               for r in baseline['files'] if not Path(r['path']).exists() or sha(Path(r['path'])) != r['sha256']]
    report = {'checked': len(baseline['files']), 'unchanged': len(baseline['files']) - len(changes), 'changed': changes,
              'baseline': 'Actual working files on entry, including the already modified FULL_DRAFT; not git HEAD.'}
    (QA / '既有文件保全.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps(report, ensure_ascii=False))
    assert not changes

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['snapshot', 'check'])
    snapshot() if parser.parse_args().mode == 'snapshot' else check()
