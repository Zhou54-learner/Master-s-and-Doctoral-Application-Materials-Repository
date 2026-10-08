"""Read-only source validation for the 2026-10-05 handover; writes only its audit JSON.

Does not execute historical MATLAB code or COMSOL. Requires the existing NumPy
audit environment and FFmpeg/FFprobe used by inspect_chain.py; installs nothing.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

sys.dont_write_bytecode = True
sys.path.insert(0, 'C:/Users/zzj/AppData/Local/Temp/codex-music-audit-deps')
import numpy as np

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RESULT = OUT / '核验汇总.json'

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def cells(path):
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            strings = [''.join(x.itertext()) for x in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        result = {}
        for cell in ET.fromstring(archive.read('xl/worksheets/sheet1.xml')).findall('.//s:c', ns):
            val = cell.find('s:v', ns)
            if val is not None:
                result[cell.get('r')] = strings[int(val.text)] if cell.get('t') == 's' else val.text
            elif cell.get('t') == 'inlineStr':
                result[cell.get('r')] = ''.join(cell.find('s:is', ns).itertext())
        return result

report = dict(date='2026-10-05', checked_at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
              scope='接替原聊天进行验收；全部新计算仅核对历史来源，不倒写为本科贡献。')
records = []
manifests = []
for name in ['原件索引.json', '追加原件索引.json']:
    path = OUT / name
    records.extend(json.loads(path.read_text(encoding='utf8')))
    manifests.append(dict(file=name, sha256=digest(path)))
failures = []
mtime_changes = []
for row in records:
    path = Path(row['path'])
    if not path.is_file():
        failures.append(dict(path=row['path'], issue='missing'))
        continue
    if path.stat().st_size != row['bytes'] or digest(path) != row['sha256']:
        failures.append(dict(path=row['path'], issue='size/hash mismatch'))
    if abs(path.stat().st_mtime - datetime.datetime.fromisoformat(row['mtime']).timestamp()) > 0.00001:
        mtime_changes.append(row['path'])
report['source_preservation'] = dict(count=len(records), manifests=manifests, failures=failures, mtime_changes=mtime_changes)

copy_pairs = [(Path('E:/matlab/work') / name, OUT / ('历史源码_' + name)) for name in ['test3.m', 'test.m', 'pitch.m']]
copy_pairs += [(Path('E:/2023/traindata/数据处理/pitchtest.m'), OUT / '历史源码_pitchtest.m')]
asset_root = OUT.parent / '个人探索_20261004/素材'
copy_pairs += [(Path('E:/2023/traindata') / src, asset_root / dst) for src, dst in [
    ('R11.6mm_r8.0mm/100cm/图像/01_1.png', 'M01_历史波形与频谱.png'),
    ('数据处理/长度关系比较/数据图表1.jpg', 'M02_管长与频率比较.jpg'),
    ('数据处理/内外半径关系比较/比较1.jpg', 'M03_内外半径比较.jpg')]]
report['byte_copy_checks'] = [dict(source=a.as_posix(), copy=b.relative_to(ROOT).as_posix(), match=digest(a) == digest(b)) for a, b in copy_pairs]

checks = []
saved = json.loads((OUT / '音频FFT核对_本轮复算非历史结果.json').read_text(encoding='utf8'))
for row in saved:
    path = Path(row['path'])
    meta = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(path)]))
    fs = int(next(x for x in meta['streams'] if x['codec_type'] == 'audio')['sample_rate'])
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-af', 'pan=mono|c0=c0', '-f', 'f32le', '-'])
    y = np.frombuffer(raw, dtype='<f4').astype(float)
    spectrum = abs(np.fft.rfft(y)) / len(y)
    spectrum[1:-1] *= 2
    peak = int(spectrum.argmax())
    hz = peak * fs / len(y)
    table = path.parent / '数据' / ('数据' + row['group'] + '.xlsx')
    old_hz = float(cells(table)['B' + str(row['index'] + 1)])
    checks.append(dict(group=row['group'], index=row['index'], peak_hz=hz, historical_hz=old_hz,
                       historical_error_hz=abs(hz-old_hz), matches_saved_check=abs(hz-row['peak_hz']) < 1e-10 and abs(float(spectrum[peak])-row['peak_amplitude']) < 1e-10))
report['audio_checks'] = dict(count=len(checks), records=checks, max_historical_error_hz=max(x['historical_error_hz'] for x in checks),
                              tolerance_hz=5e-7, note='容差仅用于核对表格保留小数，非实验测量精度；15段样本长度均为偶数。')
work = cells(Path('E:/matlab/work/main_frequencies.xlsx'))
last = [x for x in saved if x['group'] == '03']
report['workbook_checks'] = dict(input_paths_match=all(work[chr(65+i)+'1'].replace('\\', '/') == x['path'] for i, x in enumerate(last)),
    peaks_match=all(abs(float(work[chr(65+i)+'2'])-x['peak_hz']) < 1e-9 for i, x in enumerate(last)),
    mean_match=abs(float(work['F2'])-sum(x['peak_hz'] for x in last)/5) < 1e-9)

link_count = 0
broken = []
for path in [OUT.parent / '乐音研究_历史内容与独立贡献考古_20261005.md', OUT / 'README.md']:
    for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf8')):
        if '://' in href or href.startswith('#'):
            continue
        target = path.parent / href.split('#')[0]
        link_count += 1
        if target.resolve() != RESULT.resolve() and not target.exists():
            broken.append(dict(file=path.name, link=href))
report['links'] = dict(checked=link_count, broken=broken)
json_files = list(OUT.glob('*.json'))
for path in json_files:
    json.loads(path.read_text(encoding='utf8'))
report['json_parse_count'] = len(json_files)
report['pass'] = (not failures and not mtime_changes and all(x['match'] for x in report['byte_copy_checks'])
                  and len(checks) == 15 and all(x['matches_saved_check'] and x['historical_error_hz'] < 5e-7 for x in checks)
                  and all(report['workbook_checks'].values()) and not broken)
RESULT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps(dict(passed=report['pass'], source_files=len(records), source_failures=failures, mtime_changes=mtime_changes,
                      audio_count=len(checks), max_error_hz=report['audio_checks']['max_historical_error_hz'], broken_links=broken), ensure_ascii=False))
if not report['pass']:
    sys.exit(1)
