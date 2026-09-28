import sys
sys.path.append(r"F:\CST Studio Suite 2025\AMD64\python_cst_libraries")

import cst.interface

de = cst.interface.DesignEnvironment()
pj = de.new_mws()

pj.model3d.add_to_history(
    "solver",
    """
Solver.FrequencyRange "2", "18"
"""
)

pj.model3d.run_solver()

print("Solver started")