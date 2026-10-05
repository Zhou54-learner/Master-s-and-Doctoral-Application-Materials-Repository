"""The render audit is paired by design: it checks S8 and both S9 frames together."""
from pathlib import Path
import runpy
source=Path(__file__).resolve().parents[2]/'S8_项目级AI协作_v1_20261005/制作源/render_pair.py'
runpy.run_path(str(source),run_name='__main__')
