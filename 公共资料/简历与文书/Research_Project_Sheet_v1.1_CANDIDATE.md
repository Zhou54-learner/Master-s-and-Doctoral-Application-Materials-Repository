# Simulation-Guided Design of Resistive-Film Structures
Zijing Zhou | Undergraduate thesis, Harbin Institute of Technology | May 2026  
Research supervision: Prof. Jun Li | zhouzijing54@gmail.com

## Research Question
How can patterned, orthogonal resistive films above a metal backing be optimized for broadband low reflection, while keeping the electromagnetic model and evaluation criteria consistent?

## Approach and My Contribution
Starting from a group-provided structural concept and reference code, I adapted a Python-CST workflow with AI-assisted coding and debugging. I worked on staged 6x6, 9x9, and 12x12 pixel-pattern searches, expanded geometric and sheet-resistance variables, and adjusted candidate filtering and result processing. CST supplied the electromagnetic solver; I did not develop the solver or invent the genetic algorithm.

The study compared finite-thickness and Ohmic Sheet representations before continuing the staged searches with the latter. The final design used separate X/Y patterns and sheet resistances in a periodic, normally illuminated unit cell.

## Archived Simulation Result
The saved co-polar reflection curve has a sampled interval below -10 dB from 4.80 to 18.00 GHz: a 13.20 GHz interval within the 2-18 GHz study window. The minimum is -23.485 dB. The curve contains 201 samples at 0.08 GHz spacing; 18 GHz is the scan limit, not an independently located upper band edge.

Final parameters: period 13.1409 mm; height 10.0731 mm; X/Y sheet resistances 140.79 and 35.461 ohm/square.

## Interpretation and Limits
The project illustrates how model choice, search variables, and evaluation criteria affect a simulation-based design workflow. Field plots provide qualitative physical interpretation, not a unique modal decomposition. The reported curve is one reflection channel: total absorptance requires checking all relevant reflected/transmitted power. No fabrication or measured performance is claimed. Mesh/frequency convergence, polarization/angle dependence, and manufacturing tolerances remain validation tasks.

## Research Direction
I want to extend this experience toward computational materials physics and physics-informed scientific inference. My present experience is in electromagnetic simulation and optimization; first-principles calculations and machine-learned interatomic potentials are intended training directions, not established skills.

---

**Internal status:** CANDIDATE. Content is intentionally identical to `Research_Project_Sheet_v1.0_READY.md` except that the contact email is updated to the current Gmail address. The frozen v1.0 file is not overwritten. External PDF generation/visual review is still required before this candidate can become READY.