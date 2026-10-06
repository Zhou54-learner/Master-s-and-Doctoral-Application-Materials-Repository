"""Read-only forensic audit. Does not invoke a solver, history, save, or optimizer.
Run with Python 3.11 and the installed CST 2025 result reader. Outputs only here.
"""
from pathlib import Path
import sys, json, hashlib, csv, re, html

OUT = Path(__file__).resolve().parent
SRC = Path(r'F:\biyesheji\最终结果ohmic_sheet_12x12_multitemplate_topology_ga')
PROJECT = SRC / 'best_design_ohmic_sheet_12x12.cst'
DATA = PROJECT.with_suffix('')
CODE = Path(r'F:\biyesheji\code\ohmic_sheet_12x12_multitemplate_topology_ga_code.py')

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def write_json(name, data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def manifest():
    files = [PROJECT, CODE] + sorted(p for p in DATA.rglob('*') if p.is_file())
    files += sorted(p for p in SRC.glob('*') if p.is_file() and p != PROJECT)
    return [{'path':str(p),'size':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns,'sha256':sha(p)} for p in files]

def capture():
    write_json('source_manifest_before.json',manifest())
    h=json.loads((DATA/'Model/3D/ModelHistory.json').read_text('utf-8-sig'))
    blocks=[]
    for i,b in enumerate(h['history']):
        if i<7 or i>=352:
            blocks += [f"' HISTORY BLOCK {i}: {b['caption']}",*b['code'],'']
    (OUT/'history_selected.bas.txt').write_text('\n'.join(blocks),encoding='utf-8')
    for src,name in [(DATA/'Model/Parameters.json','parameters.json'),(DATA/'Result/Model.log','solver_original.log.txt')]:
        (OUT/name).write_bytes(src.read_bytes())
    modes=[]
    for p in sorted((DATA/'Result').glob('Port*_Info*.mmd')):
        modes.append({'source':str(p),'data':json.loads(p.read_text())})
    write_json('port_mode_metadata.json',modes)
    lines=CODE.read_text('utf-8-sig').splitlines()
    ranges=[(263,329),(770,810),(4670,4748),(5290,5480)]
    selected=[]
    for lo,hi in ranges:
        selected += [f'{i}: {lines[i-1]}' for i in range(lo,min(hi,len(lines))+1)]
    (OUT/'ga_code_numbered_excerpt.txt').write_text('\n'.join(selected),encoding='utf-8')
    print('Captured source hashes, history, log, metadata and code excerpts.')

def read_results():
    sys.path.insert(0,r'F:\CST Studio Suite 2025\AMD64\python_cst_libraries')
    import cst.results
    read_copy=Path(r'F:\codex-temp-floquet-audit-20261006')/PROJECT.name
    assert sha(read_copy)==sha(PROJECT)
    project=cst.results.ProjectFile(str(read_copy),allow_interactive=False)
    mod=project.get_3d()
    tree=mod.get_tree_items()
    write_json('native_result_tree.json',{'source':str(PROJECT),'reader':cst.results.get_version_info(),'items':tree,'run_ids':mod.get_all_run_ids()})
    summary=[]
    for item in tree:
        if any(k in item for k in ['S-Parameters','Port Information','Reference Impedance','Power','Balance']):
            try:
                result=mod.get_result_item(item)
                x=result.get_xdata(); y=result.get_ydata()
                filename=re.sub(r'[^a-zA-Z0-9(),_-]','_',item)+'.csv'
                with (OUT/filename).open('w',newline='',encoding='utf-8') as f:
                    w=csv.writer(f);w.writerow(['x','real','imag'])
                    w.writerows((a,complex(b).real,complex(b).imag) for a,b in zip(x,y))
                summary.append({'tree_item':item,'run_ids':mod.get_run_ids(item),'count':len(x),'x_min':min(x),'x_max':max(x),'file':filename})
            except Exception as e: summary.append({'tree_item':item,'error':str(e)})
    write_json('native_results_export.json',summary)
    runcheck=[]
    for rid in mod.get_all_run_ids():
        r={'run_id':rid,'parameters':mod.get_parameter_combination(rid),'s_curves':{}}
        for item in tree:
            if item.startswith('1D Results\\S-Parameters\\'):
                z=mod.get_result_item(item,run_id=rid)
                xy=[(float(x),complex(y).real,complex(y).imag) for x,y in zip(z.get_xdata(),z.get_ydata())]
                r['s_curves'][item]={'sha256_numeric_json':hashlib.sha256(json.dumps(xy).encode()).hexdigest(),'count':len(xy)}
        runcheck.append(r)
    write_json('run_ids_comparison.json',runcheck)
    print('Exported',len(summary),'curves; checked runs',mod.get_all_run_ids())

def verify():
    before=json.loads((OUT/'source_manifest_before.json').read_text('utf-8'))
    after=manifest()
    write_json('source_preservation_check.json',{'file_count':len(before),'all_equal':before==after,'differences':[b['path'] for b,a in zip(before,after) if b!=a]})
    print('Source preservation:',before==after,'files:',len(before))

if __name__=='__main__':
    {'capture':capture,'results':read_results,'verify':verify}[sys.argv[1]]()
