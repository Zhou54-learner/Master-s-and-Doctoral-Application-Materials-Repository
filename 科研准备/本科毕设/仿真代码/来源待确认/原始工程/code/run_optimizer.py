# -*- coding: utf-8 -*-
import sys
import os
import random
import shutil
import traceback
import numpy as np
import matplotlib.pyplot as plt

# =========================
# CST Python库路径
# =========================
cst_lib_path = r"F:\CST Studio Suite 2025\AMD64\python_cst_libraries"
sys.path.append(cst_lib_path)

import cst
import cst.interface
import cst.results

# =========================
# 保存路径
# =========================
SAVE_PATH = r"F:\biyesheji"
TEMP_DIR = os.path.join(SAVE_PATH, "temp")
BEST_CST = os.path.join(SAVE_PATH, "best_design.cst")
LOG_FILE = os.path.join(SAVE_PATH, "ga_log.txt")
BEST_RESULT_FILE = os.path.join(SAVE_PATH, "best_result.txt")
ERROR_LOG_FILE = os.path.join(SAVE_PATH, "error_log.txt")
BEST_S11_FILE = os.path.join(SAVE_PATH, "best_s11.txt")
BEST_S11_PNG = os.path.join(SAVE_PATH, "best_s11.png")


os.makedirs(SAVE_PATH, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# =========================
# 真实结构固定参数（第一轮先固定一种工业膜）
# =========================
PET_ER = 3.1
PET_TAND = 0.01

FILM_X_NAME = "SMH188H-60"
FILM_X_SHEET_RESISTANCE = 60.0
SUBSTRATE_X_THICKNESS = 0.188

FILM_Y_NAME = "SMH188H-60"
FILM_Y_SHEET_RESISTANCE = 60.0
SUBSTRATE_Y_THICKNESS = 0.188

# 电阻膜是单面覆膜，这里先按“无厚度片阻层”处理
# 下面这个值只是给后续几何区分表面用，不代表真实厚度
FILM_DRAW_THICKNESS = 0.02   # mm

# =========================
link = "\n"
dna_size = 30
pop_size = 8
iterations = 5
p_m_start = 0.08

# 全局变量
de = cst.interface.DesignEnvironment()
pj = None
cache = {}


# =========================================================
# 学长原版 Type()
# =========================================================
def Type():
    sCommand = [
        "'set the units",
        'With Units',
        '    .Geometry "mm"',
        '    .Frequency "GHz"',
        '    .Voltage "V"',
        '    .Resistance "Ohm"',
        '    .Inductance "H"',
        '    .TemperatureUnit  "Kelvin"',
        '    .Time "ns"',
        '    .Current "A"',
        '    .Conductance "Siemens"',
        '    .Capacitance "F"',
        'End With',
        '',
        "'----------------------------------------------------------------------------",
        '',
        "'set the frequency range",
        'Solver.FrequencyRange "2", "18"',
        '',
        "'----------------------------------------------------------------------------",
        '',
        'Plot.DrawBox True',
        '',
        'With Background',
        '     .Type "Normal"',
        '     .Epsilon "1.0"',
        '     .Mu "1.0"',
        '     .Rho "1.204"',
        '     .ThermalType "Normal"',
        '     .ThermalConductivity "0.026"',
        '      .SpecificHeat "1005", "J/K/kg"',
        '     .XminSpace "0.0"',
        '     .XmaxSpace "0.0"',
        '     .YminSpace "0.0"',
        '     .YmaxSpace "0.0"',
        '     .ZminSpace "0.0"',
        '     .ZmaxSpace "0.0"',
        'End With',
        '',
        "' define Floquet port boundaries",
        '',
        'With FloquetPort',
        '     .Reset',
        '     .SetDialogTheta "0"',
        '     .SetDialogPhi "0"',
        '     .SetSortCode "+beta/pw"',
        '     .SetCustomizedListFlag "False"',
        '     .Port "Zmin"',
        '     .SetNumberOfModesConsidered "2"',
        '     .Port "Zmax"',
        '     .SetNumberOfModesConsidered "2"',
        'End With',
        '',
        'MakeSureParameterExists "theta", "0"',
        'SetParameterDescription "theta", "spherical angle of incident plane wave"',
        'MakeSureParameterExists "phi", "0"',
        'SetParameterDescription "phi", "spherical angle of incident plane wave"',
        '',
        "' define boundaries, the open boundaries define floquet port",
        '',
        'With Boundary',
        '     .Xmin "unit cell"',
        '     .Xmax "unit cell"',
        '     .Ymin "unit cell"',
        '     .Ymax "unit cell"',
        '     .Zmin "expanded open"',
        '     .Zmax "expanded open"',
        '     .Xsymmetry "none"',
        '     .Ysymmetry "none"',
        '     .Zsymmetry "none"',
        '     .XPeriodicShift "0.0"',
        '     .YPeriodicShift "0.0"',
        '     .ZPeriodicShift "0.0"',
        '     .PeriodicUseConstantAngles "False"',
        '     .SetPeriodicBoundaryAngles "theta", "phi"',
        '     .SetPeriodicBoundaryAnglesDirection "inward"',
        '     .UnitCellFitToBoundingBox "True"',
        '     .UnitCellDs1 "0.0"',
        '     .UnitCellDs2 "0.0"',
        '     .UnitCellAngle "90.0"',
        'End With',
        '',
        "' set tet mesh as default",
        '',
        'With Mesh',
        '     .MeshType "Tetrahedral"',
        'End With',
        '',
        "' FD solver excitation with incoming plane wave at Zmax",
        '',
        'With FDSolver',
        '     .Reset',
        '     .Stimulation "List", "List"',
        '     .ResetExcitationList',
        '     .AddToExcitationList "Zmax", "TE(0,0);TM(0,0)"',
        '     .LowFrequencyStabilization "False"',
        'End With',
        '',
        "'----------------------------------------------------------------------------",
        '',
        'With MeshSettings',
        '     .SetMeshType "Tet"',
        '     .Set "Version", 1%',
        'End With',
        '',
        'With Mesh',
        '     .MeshType "Tetrahedral"',
        'End With',
        '',
        "'set the solver type",
        'ChangeSolverType("HF Frequency Domain")',
        '',
        "'----------------------------------------------------------------------------"
    ]
    sCommand = link.join(sCommand)
    pj.model3d.add_to_history("use template: FSS, Metamaterial - Unit Cell_3.cfg", sCommand)

# =========================================================

def create_pet_material():
    sCommand = f'''
With Material
     .Reset
     .Name "PET"
     .Folder ""
     .Type "Normal"
     .Epsilon "{PET_ER}"
     .Mu "1.0"
     .Sigma "0"
     .TanD "{PET_TAND}"
     .Create
End With
'''
    pj.model3d.add_to_history("define material: PET", sCommand)


def create_resistive_film_material():
    film_thickness_m = FILM_DRAW_THICKNESS * 1e-3

    sigma_x = 1.0 / (FILM_X_SHEET_RESISTANCE * film_thickness_m)
    sigma_y = 1.0 / (FILM_Y_SHEET_RESISTANCE * film_thickness_m)

    sCommand1 = f'''
With Material
     .Reset
     .Name "{FILM_X_NAME}"
     .Folder ""
     .Type "Normal"
     .Epsilon "1.0"
     .Mu "1.0"
     .Sigma "{sigma_x}"
     .TanD "0.0"
     .Create
End With
'''
    pj.model3d.add_to_history("define material: resistive film x", sCommand1)

    sCommand2 = f'''
With Material
     .Reset
     .Name "{FILM_Y_NAME}"
     .Folder ""
     .Type "Normal"
     .Epsilon "1.0"
     .Mu "1.0"
     .Sigma "{sigma_y}"
     .TanD "0.0"
     .Create
End With
'''
    pj.model3d.add_to_history("define material: resistive film y", sCommand2)

# =========================================================
# 学长原版 newc()
# =========================================================
def newc():
    sCommand = ['Component.New "component1" ']
    sCommand = link.join(sCommand)
    pj.model3d.add_to_history("new component: component1", sCommand)

# =========================================================

def create_pet_cross_substrates(p, h):
    tx = SUBSTRATE_X_THICKNESS
    ty = SUBSTRATE_Y_THICKNESS

    s1 = f'''
With Brick
     .Reset
     .Name "pet_x"
     .Component "component1"
     .Material "PET"
     .Xrange "-{p/2}", "{p/2}"
     .Yrange "-{tx/2}", "{tx/2}"
     .Zrange "0", "{h}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: pet_x", s1)

    s2 = f'''
With Brick
     .Reset
     .Name "pet_y"
     .Component "component1"
     .Material "PET"
     .Xrange "-{ty/2}", "{ty/2}"
     .Yrange "-{p/2}", "{p/2}"
     .Zrange "0", "{h}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: pet_y", s2)

# =========================================================

def create_full_cover_film(p, h):
    tx = SUBSTRATE_X_THICKNESS
    ty = SUBSTRATE_Y_THICKNESS
    df = FILM_DRAW_THICKNESS

    # X向切片：膜固定在 +Y 面
    s1 = f'''
With Brick
     .Reset
     .Name "film_x_full"
     .Component "component1"
     .Material "{FILM_X_NAME}"
     .Xrange "-{p/2}", "{p/2}"
     .Yrange "{tx/2}", "{tx/2 + df}"
     .Zrange "0", "{h}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: film_x_full", s1)

    # Y向切片：膜固定在 +X 面
    s2 = f'''
With Brick
     .Reset
     .Name "film_y_full"
     .Component "component1"
     .Material "{FILM_Y_NAME}"
     .Xrange "{ty/2}", "{ty/2 + df}"
     .Yrange "-{p/2}", "{p/2}"
     .Zrange "0", "{h}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: film_y_full", s2)


# =========================================================
# 边界、求解器、结构
# =========================================================
def set_ground_boundary():
    sCommand = [
        'With Boundary',
        '     .Xmin "unit cell"',
        '     .Xmax "unit cell"',
        '     .Ymin "unit cell"',
        '     .Ymax "unit cell"',
        '     .Zmin "electric"',
        '     .Zmax "expanded open"',
        '     .Xsymmetry "none"',
        '     .Ysymmetry "none"',
        '     .Zsymmetry "none"',
        '     .ApplyInAllDirections "False"',
        '     .OpenAddSpaceFactor "0.5"',
        '     .XPeriodicShift "0.0"',
        '     .YPeriodicShift "0.0"',
        '     .ZPeriodicShift "0.0"',
        '     .PeriodicUseConstantAngles "False"',
        '     .SetPeriodicBoundaryAngles "theta", "phi"',
        '     .SetPeriodicBoundaryAnglesDirection "inward"',
        '     .UnitCellFitToBoundingBox "True"',
        '     .UnitCellDs1 "0.0"',
        '     .UnitCellDs2 "0.0"',
        '     .UnitCellAngle "90.0"',
        'End With'
    ]
    sCommand = link.join(sCommand)
    pj.model3d.add_to_history("define grounded boundaries", sCommand)


def set_fast_solver():
    sCommand = [
        'Mesh.SetCreator "High Frequency"',
        '',
        'With FDSolver',
        '     .Reset',
        '     .SetMethod "Tetrahedral", "General purpose"',
        '     .OrderTet "Second"',
        '     .OrderSrf "First"',
        '     .Stimulation "Zmax", "All"',
        '     .ResetExcitationList',
        '     .AddToExcitationList "Zmax", "TE(0,0);TM(0,0)"',
        '     .AutoNormImpedance "False"',
        '     .NormingImpedance "50"',
        '     .ModesOnly "False"',
        '     .ConsiderPortLossesTet "True"',
        '     .LowFrequencyStabilization "False"',
        '     .Type "Auto"',
        '     .MeshAdaptionTet "True"',
        '     .StoreAllResults "False"',
        '     .StoreResultsInCache "False"',
        '     .UseDoublePrecision "False"',
        '     .UseParallelization "True"',
        '     .MaxCPUs "1024"',
        '     .MaximumNumberOfCPUDevices "2"',
        '     .RemoveAllStopCriteria "Tet"',
        '     .AddStopCriterion "All S-Parameters", "0.02", "2", "Tet", "True"',
        '     .SetNumberOfResultDataSamples "201"',
        'End With',
        '',
        'With MeshSettings',
        '     .SetMeshType "Tet"',
        '     .Set "Version", 1%',
        '     .Set "StepsPerWaveNear", "3"',
        '     .Set "StepsPerWaveFar", "3"',
        '     .Set "PhaseErrorNear", "0.05"',
        '     .Set "PhaseErrorFar", "0.05"',
        '     .Set "CellsPerWavelengthPolicy", "automatic"',
        '     .Set "StepsPerBoxNear", "4"',
        '     .Set "StepsPerBoxFar", "1"',
        '     .Set "UseRatioLimit", "0"',
        '     .Set "RatioLimit", "100"',
        '     .Set "MinStep", "0"',
        'End With',
        '',
        'With Mesh',
        '     .MeshType "Tetrahedral"',
        '     .SetCreator "High Frequency"',
        'End With'
    ]
    sCommand = link.join(sCommand)
    pj.model3d.add_to_history("define fast FD solver and mesh", sCommand)


# =========================================================
# GA辅助函数
# =========================================================
def reconnect_de():
    global de
    try:
        de = cst.interface.DesignEnvironment()
    except Exception:
        pass


def safe_new_mws():
    global de
    try:
        return de.new_mws()
    except Exception:
        reconnect_de()
        return de.new_mws()

#--------------------------------------------------------------------------------------------------------------------------
def decode(individual):
    bits = "".join(str(i) for i in individual)

    p_raw  = int(bits[0:6], 2)
    h_raw  = int(bits[6:12], 2)
    mask_x_seed = [int(b) for b in bits[12:21]] 
    mask_y_seed = [int(b) for b in bits[21:30]]


    p = 13.10 + p_raw / 63.0 * 0.30
    h = 8.70 + h_raw / 63.0 * 0.30

    return (
        round(p, 4),
        round(h, 4),
        mask_x_seed,
        mask_y_seed,
    )

#--------------------------------------------------------------------------------------------------------------------------
def expand_seed_to_6x6(seed):
    # seed 是长度为 9 的列表，按 3x3 排列
    r1 = seed[0:3]
    r2 = seed[3:6]
    r3 = seed[6:9]

    row1 = r1 + r1[::-1]
    row2 = r2 + r2[::-1]
    row3 = r3 + r3[::-1]

    return [
        row1,
        row2,
        row3,
        row3,
        row2,
        row1,
    ]


def etch_mask_x_6x6(p, h, mask6):
    tx = SUBSTRATE_X_THICKNESS
    df = FILM_DRAW_THICKNESS

    cell_x = p / 6.0
    cell_z = h / 6.0

    idx = 0
    for i in range(6):
        for j in range(6):
            # mask6[i][j] == 1 表示保留
            # mask6[i][j] == 0 表示蚀刻掉
            if mask6[i][j] == 0:
                x1 = -p / 2 + j * cell_x
                x2 = x1 + cell_x
                z1 = i * cell_z
                z2 = z1 + cell_z

                name = f"etch_x_{idx}"
                s = f'''
With Brick
     .Reset
     .Name "{name}"
     .Component "component1"
     .Material "Vacuum"
     .Xrange "{x1}", "{x2}"
     .Yrange "{tx/2}", "{tx/2 + df}"
     .Zrange "{z1}", "{z2}"
     .Create
End With
'''
                pj.model3d.add_to_history(f"define brick: {name}", s)

                sub = f'''
Solid.Subtract "component1:film_x_full", "component1:{name}"
'''
                pj.model3d.add_to_history(f"subtract: {name}", sub)

                idx += 1

#--------------------------------------------------------------------------------------------------------------------------
def etch_mask_y_6x6(p, h, mask6):
    ty = SUBSTRATE_Y_THICKNESS
    df = FILM_DRAW_THICKNESS

    cell_y = p / 6.0
    cell_z = h / 6.0

    idx = 0
    for i in range(6):
        for j in range(6):
            # mask6[i][j] == 1 表示保留
            # mask6[i][j] == 0 表示蚀刻掉
            if mask6[i][j] == 0:
                y1 = -p / 2 + j * cell_y
                y2 = y1 + cell_y
                z1 = i * cell_z
                z2 = z1 + cell_z

                name = f"etch_y_{idx}"
                s = f'''
With Brick
     .Reset
     .Name "{name}"
     .Component "component1"
     .Material "Vacuum"
     .Xrange "{ty/2}", "{ty/2 + df}"
     .Yrange "{y1}", "{y2}"
     .Zrange "{z1}", "{z2}"
     .Create
End With
'''
                pj.model3d.add_to_history(f"define brick: {name}", s)

                sub = f'''
Solid.Subtract "component1:film_y_full", "component1:{name}"
'''
                pj.model3d.add_to_history(f"subtract: {name}", sub)

                idx += 1

#--------------------------------------------------------------------------------------------------------------------------
def extract_metrics(cst_file):
    result = cst.results.ProjectFile(cst_file, allow_interactive=True)
    s11 = result.get_3d().get_result_item(r"1D Results\S-Parameters\SZmax(1),Zmax(1)")
    data = s11.get_data()

    point_num = 0
    band_num = 0
    min_rl = 1e9
    below10_depth = 0.0

    for row in data:
        if len(row) < 2:
            continue

        mag = max(abs(row[1]), 1e-12)
        rl = 20 * np.log10(mag)

        point_num += 1
        min_rl = min(min_rl, rl)

        if rl < -10:
            band_num += 1
            below10_depth += (-10.0 - rl)

    if point_num == 0:
        return {"score": 0.0, "bandwidth": 0.0, "min_rl": 0.0}

    bandwidth = band_num / point_num * 16.0
    depth_bonus = below10_depth / point_num

    if bandwidth > 0:
        score = bandwidth + 0.12 * depth_bonus
    else:
        score = max(0.0, (-min_rl - 3.0) * 0.02)

    return {
        "score": float(score),
        "bandwidth": float(bandwidth),
        "min_rl": float(min_rl)
    }
#--------------------------------------------------------------------------------------------------------------------------
def export_s11_plot(cst_file, out_png):
    result = cst.results.ProjectFile(cst_file, allow_interactive=True)
    s11 = result.get_3d().get_result_item(r"1D Results\S-Parameters\SZmax(1),Zmax(1)")
    data = s11.get_data()

    freq_list = [ ]
    rl_list = [ ]
    for row in data:
        if len(row) < 2:
            continue

        freq = row[0]
        mag = max(abs(row[1]), 1e-12)
        rl = 20 * np.log10(mag)

        freq_list.append(freq)
        rl_list.append(rl)
    plt.figure(figsize=(8, 5))
    plt.plot(freq_list, rl_list)
    plt.axhline(-10, linestyle="--")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("S11 / RL (dB)")
    plt.title("Best S11 Curve")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.close()


def export_s11_curve(cst_file, out_file):
    result = cst.results.ProjectFile(cst_file, allow_interactive=True)
    s11 = result.get_3d().get_result_item(r"1D Results\S-Parameters\SZmax(1),Zmax(1)")
    data = s11.get_data()

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("freq_GHz\ts11_mag\trl_dB\n")
        for row in data:
            if len(row) < 2:
                continue
            freq = row[0]
            mag = max(abs(row[1]), 1e-12)
            rl = 20 * np.log10(mag)
            f.write(f"{freq}\t{mag}\t{rl}\n")
#--------------------------------------------------------------------------------------------------------------------------
def run_cst(individual):
    global pj
    pj = safe_new_mws()

    try:
        Type()
        create_pet_material()
        create_resistive_film_material()
        newc()

        p, h, mask_x_seed, mask_y_seed = decode(individual)

        mask_x = expand_seed_to_6x6(mask_x_seed)
        mask_y = expand_seed_to_6x6(mask_y_seed)

        print(
            f"Current parameters: "
            f"p={p:.3f}, h={h:.3f}, "
            f"mask_x_seed={mask_x_seed}, mask_y_seed={mask_y_seed}"
        )

        create_pet_cross_substrates(p, h)
        create_full_cover_film(p, h)
        etch_mask_x_6x6(p, h, mask_x)
        etch_mask_y_6x6(p, h, mask_y)

        set_ground_boundary()
        set_fast_solver()

        temp_name = f"temp_{random.randint(1000, 999999)}.cst"
        cst_file = os.path.join(TEMP_DIR, temp_name)

        print("Running CST solver...")
        pj.model3d.run_solver()
        pj.save(cst_file)

        metrics = extract_metrics(cst_file)
        return metrics, (p, h, mask_x_seed, mask_y_seed), cst_file

    finally:
        try:
            pj.close()
        except Exception:
            pass

def initialize_population(n):
    pop = []
    while len(pop) < n:
        ind = [random.randint(0, 1) for _ in range(dna_size)]
        if ind not in pop:
            pop.append(ind)
    return pop


def evaluate_individual(individual):
    key = tuple(individual)
    if key in cache:
        return cache[key]

    try:
        metrics, params, cst_file = run_cst(individual)
    except Exception as e:
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"individual = {individual}\n")
            f.write(repr(e) + "\n")
            f.write(traceback.format_exc() + "\n")

        metrics = {"score": 0.0, "bandwidth": 0.0, "min_rl": 0.0}
        params = (0.0, 0.0, 0.0, 0.0)
        cst_file = ""

    cache[key] = (metrics, params, cst_file)
    return cache[key]


def evaluate_population(pop):
    fit_list = []
    info_list = []

    for ind in pop:
        metrics, params, cst_file = evaluate_individual(ind)
        fit_list.append(metrics["score"])
        info_list.append((metrics, params, cst_file))

    return fit_list, info_list


def select_parent(pop, fit_list):
    positive = [max(0.0, x) for x in fit_list]
    total = sum(positive)

    if total <= 0:
        return random.choice(pop).copy()

    r = random.random() * total
    s = 0.0
    for ind, fit in zip(pop, positive):
        s += fit
        if r <= s:
            return ind.copy()

    return pop[-1].copy()


def crossover(father, mother):
    cross_point1 = random.randint(0, 14)
    cross_point2 = random.randint(15, 29)
    return father[:cross_point1] + mother[cross_point1:cross_point2] + father[cross_point2:]


def mutate(individual, p_m):
    child = individual.copy()
    if random.random() < p_m:
        mp1 = random.randint(0, dna_size - 1)
        mp2 = random.randint(0, dna_size - 1)
        child[mp1] = 1 - child[mp1]
        child[mp2] = 1 - child[mp2]
    return child


def make_new_population(pop, fit_list, p_m):
    elite_idx = int(np.argmax(fit_list))
    elite = pop[elite_idx].copy()

    newpop = [elite]
    while len(newpop) < pop_size:
        father = select_parent(pop, fit_list)
        mother = select_parent(pop, fit_list)
        child = crossover(father, mother)
        child = mutate(child, p_m)
        if child not in newpop:
            newpop.append(child)

    return newpop


def write_best_result(best_metrics, best_ind, best_params):
    with open(BEST_RESULT_FILE, "w", encoding="utf-8") as f:
        f.write(f"Best score: {best_metrics['score']}\n")
        f.write(f"Best bandwidth( RL<-10 dB ): {best_metrics['bandwidth']} GHz\n")
        f.write(f"Best min RL: {best_metrics['min_rl']} dB\n")
        f.write(f"Best individual: {best_ind}\n")
        f.write(f"Best parameters (p, h, mask_x_seed, mask_y_seed): {best_params}\n")
        f.write(f"Best CST file: {BEST_CST}\n")
        f.write(f"Best S11 txt file: {BEST_S11_FILE}\n")
        f.write(f"Best S11 png file: {BEST_S11_PNG}\n")

def optimize():
    pop = initialize_population(pop_size)

    best_metrics = {"score": -1.0, "bandwidth": 0.0, "min_rl": 0.0}
    best_ind = None
    best_params = None

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("iteration\tindividual\tscore\tbandwidth\tmin_rl\tp\th\tmask_x_seed\tmask_y_seed\tcst_file\n")

    for it in range(iterations):
        current_pm = max(0.03, p_m_start - 0.008 * it)
        print(f"\n===== Iteration {it} =====")
        print(f"Current mutation rate = {current_pm:.3f}")

        fit_list, info_list = evaluate_population(pop)

        for ind, fit, info in zip(pop, fit_list, info_list):
            metrics, params, cst_file = info
            print(
                f"score = {metrics['score']:.6f}, "
                f"bandwidth = {metrics['bandwidth']:.6f}, "
                f"minRL = {metrics['min_rl']:.3f}"
            )

            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(
                    f"{it}\t{ind}\t{metrics['score']}\t{metrics['bandwidth']}\t{metrics['min_rl']}\t"
                    f"{params[0]}\t{params[1]}\t{params[2]}\t{params[3]}\t{cst_file}\n"
                )

        idx = int(np.argmax(fit_list))
        current_best_metrics, current_best_params, current_best_cst = info_list[idx]

        if current_best_metrics["score"] > best_metrics["score"]:
            best_metrics = current_best_metrics
            best_ind = pop[idx].copy()
            best_params = current_best_params

            if current_best_cst and os.path.exists(current_best_cst):
                shutil.copyfile(current_best_cst, BEST_CST)
                export_s11_curve(current_best_cst, BEST_S11_FILE)
                export_s11_plot(current_best_cst, BEST_S11_PNG)

            write_best_result(best_metrics, best_ind, best_params)

        print(f"best score so far = {best_metrics['score']:.6f}")
        print(f"best bandwidth so far = {best_metrics['bandwidth']:.6f} GHz")
        print(f"best min RL so far = {best_metrics['min_rl']:.3f} dB")
        print(f"best params so far = {best_params}")

        pop = make_new_population(pop, fit_list, current_pm)

    print("\nOptimization finished.")
    print(f"Best score = {best_metrics['score']}")
    print(f"Best bandwidth = {best_metrics['bandwidth']} GHz")
    print(f"Best min RL = {best_metrics['min_rl']} dB")
    print(f"Best params = {best_params}")
    print(f"Best CST file saved to: {BEST_CST}")


if __name__ == "__main__":
    optimize()