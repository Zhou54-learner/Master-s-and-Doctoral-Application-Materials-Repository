# English Defense Script for PPT v2

## Slide 1
Good morning, professors. My name is Zhou Zijing. My thesis is "Resistive Film-Based Metamaterial Structure Design for Enhanced Broadband Microwave Absorption." I study a metal-backed absorber with two orthogonal Ohmic Sheet layers for 2 to 18 GHz. I will focus on the work process: structure design, CST modeling, Python automation, genetic algorithm optimization, staged improvement, and mechanism analysis.

## Slide 2
The motivation is the complex electromagnetic environment in radar, wireless communication, remote sensing, and electronic equipment. These systems need structures that can reduce microwave reflection over a wide band. Traditional absorbers often trade bandwidth for thickness, weight, or structural flexibility. My target is to design a light broadband absorber and maximize the continuous range where RL is below -10 dB.

## Slide 3
With a metal backplane, transmission is almost blocked, so absorption is mainly judged by reflection. The key result is S11, and reflection loss is 20 log10 of the magnitude of S11. I use RL below -10 dB as the effective absorption standard. The main index is the longest continuous effective bandwidth, not the deepest single point.

## Slide 4
The unit has a metal backplane, two PET substrates, an X-oriented resistive film, and a Y-oriented resistive film. The backplane blocks transmission, and the PET layers support the films. The X and Y films can have different patterns and sheet resistances, giving more design freedom. In the final design, Y mainly gives loss, while X helps matching and high-frequency compensation.

## Slide 5
This slide shows the CST setup. I model one periodic unit to represent an infinite array. Periodic boundaries are used in X and Y directions. An open boundary and a Floquet port are used for normal incidence. The frequency-domain solver scans 2 to 18 GHz. Because transmission is blocked by the metal backplane, I export S11 and calculate RL.

## Slide 6
I set two kinds of outputs. During optimization, S11 over 2 to 18 GHz is used to calculate bandwidth, coverage ratio, and minimum RL. For mechanism analysis, electric-field, magnetic-field, and surface power-loss monitors are set at 8.8, 12.0, and 15.5 GHz. These monitors do not guide the search directly; they explain why the final structure works.

## Slide 7
I compared two ways to model the resistive film. The thin solid film has real thickness and volume conductivity, but it increases meshing cost. The Ohmic Sheet model directly uses sheet resistance in ohms per square and treats the film as a surface layer. Because it matches sheet-resistance data and supports faster meshing, I chose the Ohmic Sheet model.

## Slide 8
After that, I describe the film by pixel topology. Each pixel is binary: 1 means the resistive sheet is kept, and 0 means it is removed. I used 6 by 6, 9 by 9, and 12 by 12 resolutions. In the final 12 by 12 case, independent X and Y layers give 288 binary variables, flattened into chromosomes.

## Slide 9
To test many candidates, I built a CST-Python closed loop. Python generates period, height, sheet resistances, and X/Y pixel matrices, then creates the CST model automatically. After CST simulation, Python reads S11 and calculates the RL curve, effective bandwidth, coverage ratio, and minimum RL. The genetic algorithm then uses these fitness values to update the population.

## Slide 10
This code comes from the final 12 by 12 optimization script. It sets the model as Ohmic Sheet and sets TOPOLOGY_N to 12. It also defines the ranges of period, height, Rs_x, and Rs_y. The population size is 16, the iteration number is 8, and the starting mutation rate is 0.23. So the final design is based on scripted search.

## Slide 11
This code shows how fitness is calculated. The script opens the CST result file, reads S11, and calculates RL with 20 log10 of the S11 magnitude at each frequency point. Then it finds all continuous regions where RL is below -10 dB and chooses the widest one. So the algorithm objective is directly linked to the full-wave result.

## Slide 12
The optimization is staged. The 6 by 6 stage checks whether the structure and workflow are feasible. The 9 by 9 stage increases topology freedom, giving more edges, windows, and bridges. The 12 by 12 stage uses a semi-constrained multi-template strategy for finer refinement. This step-by-step route keeps the search stable and problem-focused.

## Slide 13
In the 6 by 6 stage, the thin solid film baseline proves that the dual-orthogonal structure has broadband potential. Then I transfer the topology to the Ohmic Sheet model and re-optimize it. The effective band becomes 6.80 to 18.00 GHz, with a bandwidth of 11.20 GHz. This confirms the workflow, but the low-frequency boundary is still too high.

## Slide 14
The 9 by 9 stage improves the resolution. Pixels per layer increase from 36 to 81, so the pattern can form finer windows, edges, bridges, and local links. After a good topology is found, I further perturb and optimize the period p and height h. The effective band becomes 5.68 to 18.00 GHz, and the bandwidth reaches 12.32 GHz.

## Slide 15
The final 12 by 12 design uses independent X/Y topologies and sheet resistances. The optimized period is 13.1409 millimeters, the height is 10.0731 millimeters, Rs_x is 140.79 ohms per square, and Rs_y is 35.461 ohms per square. The RL curve stays below -10 dB from 4.80 to 18.00 GHz. The continuous bandwidth is 13.20 GHz, the coverage ratio is 82.5 percent, and the minimum RL is -23.485 dB.

## Slide 16
These figures explain the result. The metal backplane blocks transmission and supports magnetic coupling. The low-resistance Y layer provides the main loss path and helps the low-frequency response. The X layer helps matching and high-frequency compensation. The 12 by 12 pattern connects several local resonant paths into a wide band. In conclusion, the result comes from modeling, automatic optimization, staged refinement, and field-based verification. Thank you.

## 致谢

感谢各位评委老师的倾听与建议

Thank you to all the committee members for your attention and valuable suggestions.

Благодарю  всех  уважаемых  членов  комиссии  за  внимание  и  ценные  рекомендации.

bu-la-ga-da-**liu**  vcyeh  wu-va-**ra**-ye-mei-h  **chlie**-nof  ka-**mis**-ci-yi  za  vuni-**ma**-ni-ye  yi  **cen**-ne-ye  le-ke-men-**da**-ci-yi
