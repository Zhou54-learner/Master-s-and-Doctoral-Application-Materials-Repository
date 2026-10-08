from pathlib import Path
import sys,shutil,json,csv,hashlib
sys.path.insert(0,r'F:\CST Studio Suite 2025\AMD64\python_cst_libraries')
import cst.results
BASE=Path('F:/biyesheji/最终结果ohmic_sheet_12x12_multitemplate_topology_ga')
OUT=Path(__file__).resolve().parent/'native'
OUT.mkdir(exist_ok=True)
TMP=Path('F:/codex-temp-emergency-audit-20261008')
TMP.mkdir(exist_ok=True)
report={}
for tag,src in [('ga',BASE/'temp/temp_ohmic_sheet_20260503_180023_9979.cst'),('adaptive',BASE/'best_design_ohmic_sheet_12x12.cst')]:
    files=[src]+[p for p in src.with_suffix('').rglob('*') if p.is_file()]
    def snap(): return {str(p):dict(size=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files}
    before=snap()
    dst=TMP/src.name
    shutil.copy2(src,dst)
    shutil.copytree(src.with_suffix(''),dst.with_suffix(''),dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.lok'))
    r=cst.results.ProjectFile(str(dst),allow_interactive=False).get_3d()
    names={f'S{i}{j}':f'1D Results\\S-Parameters\\SZmax({i}),Zmax({j})' for i in [1,2] for j in [1,2]}
    for mode in [1,2]:
        for short,long in [('pin','Power Stimulated'),('pout','Power Outgoing all Ports'),('metal','Loss in Metals'),('dielectric','Loss in Dielectrics')]:
            names[f'{short}{mode}']=f'1D Results\\Power\\Excitation [Zmax({mode})]\\{long}'
    for short,name in names.items():
        item=r.get_result_item(name)
        with (OUT/f'{tag}_{short}.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.writer(f);w.writerow(['frequency_GHz','real','imag']);w.writerows((x,complex(y).real,complex(y).imag) for x,y in zip(item.get_xdata(),item.get_ydata()))
    report[tag]={'source':str(src),'originals_unchanged':before==snap(),'files_checked':len(files)}
    del r
(OUT/'原件保全.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
