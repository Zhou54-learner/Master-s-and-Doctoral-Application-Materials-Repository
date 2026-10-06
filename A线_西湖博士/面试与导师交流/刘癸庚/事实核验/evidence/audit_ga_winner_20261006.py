"""Read the archived GA winning candidate and compare its saved curve."""
from pathlib import Path
import sys,json,hashlib,shutil,csv,math
sys.path.insert(0,r'F:\CST Studio Suite 2025\AMD64\python_cst_libraries')
import cst.results, cst.interface
OUT=Path(__file__).resolve().parent/'ga_winner'
OUT.mkdir(exist_ok=True)
SRC=Path(r'F:\biyesheji\最终结果ohmic_sheet_12x12_multitemplate_topology_ga\temp\temp_ohmic_sheet_20260503_180023_9979.cst')
DST=Path(r'F:\codex-temp-floquet-audit-20261006')/SRC.name
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
files=[SRC]+sorted(p for p in SRC.with_suffix('').rglob('*') if p.is_file())
before=[{'path':str(p),'size':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns,'sha256':digest(p)} for p in files]
(OUT/'source_manifest_before.json').write_text(json.dumps(before,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(SRC,DST)
shutil.copytree(SRC.with_suffix(''),DST.with_suffix(''),ignore=shutil.ignore_patterns('*.lok'),dirs_exist_ok=True)
r=cst.results.ProjectFile(str(DST),allow_interactive=False).get_3d()
tree=r.get_tree_items();summary={'source':str(SRC),'tree':tree,'curves':{}}
for i in (1,2):
    for j in (1,2):
        name=f'1D Results\\S-Parameters\\SZmax({i}),Zmax({j})'
        v=r.get_result_item(name);x=list(v.get_xdata());y=list(v.get_ydata())
        with (OUT/f'S{i}{j}.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['frequency_GHz','real','imag']);w.writerows((a,b.real,b.imag) for a,b in zip(x,y))
        db=[20*math.log10(max(abs(z),1e-300)) for z in y]
        summary['curves'][f'S{i}{j}']={'count':len(x),'min_dB':min(db),'max_dB':max(db)}
        if i==1 and j==1:
            original=list(csv.DictReader((SRC.parent.parent/'best_s11_ohmic_sheet_12x12.txt').open(),delimiter='\t'))
            assert len(original)==len(x)
            summary['matches_GA_text']={'max_frequency_difference':max(abs(a-float(b['freq_GHz'])) for a,b in zip(x,original)),
                                       'max_magnitude_difference':max(abs(abs(a)-float(b['s11_mag'])) for a,b in zip(y,original))}
del r
hist=SRC.with_suffix('')/'Model/3D/ModelHistory.json'
if hist.exists():
    h=json.loads(hist.read_text('utf-8-sig'))
    summary['history_count']=len(h['history'])
    (OUT/'history_port_and_solver.json').write_text(json.dumps({'general':h['general'],'history':[{'index':i,**b} for i,b in enumerate(h['history']) if i in (0,3,4,352,353)]},ensure_ascii=False,indent=2),encoding='utf-8')
for f in ['Model/Parameters.json','Result/Model.log']:
    p=SRC.with_suffix('')/f
    if p.exists(): (OUT/p.name).write_bytes(p.read_bytes())
de=cst.interface.DesignEnvironment.connect(int(sys.argv[1]))
p=de.open_project(str(DST))
for field in ['e1','e2','h1','h2']:
    item=f'2D/3D Results\\Port Modes\\Zmax\\In\\{field}'
    code='\n'.join(['Sub Main',f'If Not SelectTreeItem("{item}") Then Err.Raise 1001',
                    'With ASCIIExport','.Reset',f'.FileName "{OUT/("In_"+field+".txt")}"',
                    '.Mode "FixedNumber"','.StepX 3','.StepY 3','.StepZ 1','.Execute','End With','End Sub'])
    p.schematic.execute_vba_code(code)
    summary[f'field_{field}_frequency_GHz']=p.model3d.GetFieldFrequency()
p.close()
after=[{'path':str(p),'size':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns,'sha256':digest(p)} for p in files]
summary['originals_unchanged']=before==after
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='tree'},ensure_ascii=False,indent=2))
