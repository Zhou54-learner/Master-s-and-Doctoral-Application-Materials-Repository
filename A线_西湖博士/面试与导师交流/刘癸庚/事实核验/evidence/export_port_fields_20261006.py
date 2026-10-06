"""Export existing port fields from the isolated copy, without solve/save/history."""
from pathlib import Path
import sys,json
sys.path.insert(0,r'F:\CST Studio Suite 2025\AMD64\python_cst_libraries')
import cst.interface as ci
out=Path(__file__).resolve().parent
de=ci.DesignEnvironment.connect(int(sys.argv[1]))
p=de.get_open_project(r'F:\codex-temp-floquet-audit-20261006\best_design_ohmic_sheet_12x12.cst')
assert Path(p.filename()).parent == Path(r'F:\codex-temp-floquet-audit-20261006')
m=p.model3d
(out/'cst_full_tree.json').write_text(json.dumps(m.get_tree_items(),ensure_ascii=False,indent=2),encoding='utf-8')
logs=[]
for side in ['In','Out']:
    for field in ['e1','e2','h1','h2']:
        item=f'2D/3D Results\\Port Modes\\Zmax\\{side}\\{field}'
        target=out/f'port_Zmax_{side}_{field}.txt'
        code='\n'.join(['Sub Main',f'If Not SelectTreeItem("{item}") Then Err.Raise 1001, , "Missing tree item"',
                       'With ASCIIExport','.Reset',f'.FileName "{target}"','.Mode "FixedNumber"',
                       '.StepX 3','.StepY 3','.StepZ 1','.Execute','End With','End Sub'])
        (out/f'export_{side}_{field}.bas.txt').write_text(code,encoding='utf-8')
        try:
            p.schematic.execute_vba_code(code)
            logs.append({'item':item,'export':target.name,'exists':target.exists(),'size':target.stat().st_size if target.exists() else None})
        except Exception as e: logs.append({'item':item,'error':str(e)})
        print(logs[-1],flush=True)
(out/'port_export_log.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2),encoding='utf-8')
