"""S9 uses the paired design source maintained next to S8; no duplicated style source."""
from pathlib import Path
import runpy
import sys
source=Path(__file__).resolve().parents[2]/'S8_项目级AI协作_v1_20261005/制作源/build_pair.py'
sys.argv=[str(source),'--only','s9']
runpy.run_path(str(source),run_name='__main__')
