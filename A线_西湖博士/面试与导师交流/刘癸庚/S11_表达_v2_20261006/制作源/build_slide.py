"""Build this selected v2 slide only; archived v1 and S0-S9 are never executed or edited."""
from pathlib import Path
import runpy,sys
source=Path(__file__).resolve().parents[2]/'S10-S13_联合审阅_v2_20261006/制作源/build_v2.py'
sys.argv=[str(source),'--only','S11']
runpy.run_path(str(source),run_name='__main__')
