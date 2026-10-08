from pathlib import Path
import hashlib, json, ast, csv, math
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
AUD=ROOT/'公共资料/事实核验/本科毕设紧急审计_20261008'
(OUT/'证据').mkdir(exist_ok=True)
entries=json.loads((AUD/'来源哈希.json').read_text(encoding='utf-8-sig'))
report=[]
for x in entries:
    p=Path(x['path'])
    if p.exists():
        sha=hashlib.sha256(p.read_bytes()).hexdigest()
        report.append({'path':str(p),'sha256':sha,'matches_20261008':sha==x['sha256']})
    else: report.append({'path':str(p),'exists':False})
specs={
'ohmic_sheet_6x6_ga_stable_code.py':[(70,88),(903,945),(1333,1410)],
'ohmic_sheet_9x9_fixed_ph_ga_code.py':[(80,100),(923,970)],
'ohmic_sheet_12x12_multitemplate_topology_ga_code.py':[(4285,4335),(4480,4568),(4619,4803),(4958,4993),(5134,5172),(5187,5327),(5387,5464)]}
parts=[]
for name,ranges in specs.items():
    p=Path('F:/biyesheji/code')/name; data=p.read_bytes(); lines=data.decode('utf-8-sig').splitlines()
    parts.append(f'\n=== {p} ===\nSHA256: {hashlib.sha256(data).hexdigest()}\n显示时去除行尾空白；行号对应未改动原件。\n')
    for a,b in ranges:
        parts.append('\n'.join(f'{i}: {lines[i-1]}'.rstrip() for i in range(a,b+1)))
(OUT/'证据/阶段源码摘录.txt').write_text('\n\n'.join(parts),encoding='utf-8')
native={}
for tag in ['ga','adaptive']:
    rows=list(csv.DictReader((AUD/f'native/{tag}_S11.csv').open(encoding='utf-8-sig')))
    vals=[(float(r['frequency_GHz']),20*math.log10(abs(complex(float(r['real']),float(r['imag']))))) for r in rows]
    segments=[]; start=None
    for i,(f,v) in enumerate(vals):
        if v<=-10 and start is None: start=i
        if start is not None and (v>-10 or i==len(vals)-1):
            end=i-1 if v>-10 else i
            segments.append((vals[start][0],vals[end][0],vals[end][0]-vals[start][0]));start=None
    native[tag]={'rows':len(rows),'longest':max(segments,key=lambda t:t[2])}
base=ROOT/'A线_西湖博士/面试与导师交流/刘癸庚/完整PPT_v1.1_20261006/刘癸庚交流_完整PPT_v1.1_20261006.pptx'
result={'source_hashes':report,'recomputed_saved_native_curves':native,'liu_remote_base_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'scope':'只读原件与已归档原生数据；未启动CST求解或GA'}
(OUT/'证据/原件核对.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'checked':len(report),'mismatched':[x['path'] for x in report if x.get('matches_20261008') is False],'native':native},ensure_ascii=False))
