"""S8 v3 entry point. Uses the shared v3 builder, never a historical v2 script."""
from pathlib import Path
import runpy
shared=Path(__file__).resolve().parents[2]/'S9_个人AI外骨骼_v3_20261006/制作源/build_slides.py'
runpy.run_path(str(shared))['build_s8']()
