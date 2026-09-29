# Simulation-Guided Design of Resistive-Film Structures
Zijing Zhou | Undergraduate thesis, Harbin Institute of Technology | May 2026  
Research supervision: Prof. Jun Li | zhouzijing54@gmail.com

## Research Question
How can patterned, orthogonal resistive films above a metal backing be optimized for broadband low reflection while keeping the electromagnetic model and evaluation criteria consistent?

## Approach and My Contribution
Starting from a group-provided structural concept and reference code, I adapted a Python–CST workflow with AI-assisted coding and debugging. I worked on staged 6×6, 9×9, and 12×12 pixel-pattern searches, expanded geometric, pattern, and two-direction sheet-resistance variables, and adjusted candidate filtering and result processing. CST supplied the electromagnetic solver; I did not develop the solver or originate the search algorithm.

The study compared finite-thickness and Ohmic Sheet representations before continuing the staged searches with the latter. The final design used separate X/Y patterns and sheet resistances in a periodic, normally illuminated unit cell.

## Archived Simulation Result
The saved co-polar reflection curve has a sampled interval below -10 dB from 4.80 to 18.00 GHz: a 13.20 GHz interval within the 2–18 GHz study window. The minimum is -23.485 dB. The curve contains 201 samples at 0.08 GHz spacing; 18 GHz is the scan limit, not an independently located upper band edge.

Final parameters: period 13.1409 mm; height 10.0731 mm; X/Y sheet resistances 140.79 and 35.461 ohm/square.

## Interpretation and Limits
The project illustrates how model choice, structural variables, and evaluation criteria interact in a simulation-guided design workflow. Field plots provide qualitative physical interpretation, not a unique modal decomposition. The reported curve is one reflection channel: total absorptance requires checking all relevant reflected/transmitted power. No fabrication or measured performance is claimed. Mesh/frequency convergence, polarization/angle dependence, and manufacturing tolerances remain validation tasks.

## Transferable Research Training
This project trained me to connect artificial-structure parameters with wave response, organize parameterized simulations into a reproducible workflow, and keep the interpretation consistent with the limits of the electromagnetic model. I hope to transfer this training to research on metamaterials, photonics, acoustic/mechanical wave structures, or other physics-informed design problems. My current hands-on experience is in frequency-domain electromagnetic simulation and structured numerical search; nanofabrication, optical spectroscopy, FDTD, first-principles calculations, molecular dynamics, and machine-learning model development are not claimed as established skills.

---

**Internal status:** CANDIDATE. v1.2 is tuned for the 2027 Hong Kong PI-contact batch. It preserves the verified numerical result and ownership boundaries of v1.1 while broadening the final research-direction paragraph so that the sheet can support WAVE/OPT-oriented contacts without implying an established DFT/ML specialization. External PDF generation and visual review are still required before READY.