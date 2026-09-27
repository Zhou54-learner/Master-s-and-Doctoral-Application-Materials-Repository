# -*- coding: utf-8 -*-
import sys
import os
import random
import shutil
import traceback
import time
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
# 基础保存路径。所有本轮“表面片阻层 12x12 重新优化”结果会单独放到
# F:\biyesheji\ohmic_sheet_12x12_ga，避免覆盖你原来薄实体膜模型的结果。
BASE_SAVE_PATH = r"F:\biyesheji"
SAVE_PATH = os.path.join(BASE_SAVE_PATH, "ohmic_sheet_12x12_template_coverage85_ga")
TEMP_DIR = os.path.join(SAVE_PATH, "temp")

BEST_CST = os.path.join(SAVE_PATH, "best_design_ohmic_sheet_12x12.cst")
LOG_FILE = os.path.join(SAVE_PATH, "ga_log_ohmic_sheet_12x12.txt")
BEST_RESULT_FILE = os.path.join(SAVE_PATH, "best_result_ohmic_sheet_12x12.txt")
ERROR_LOG_FILE = os.path.join(SAVE_PATH, "error_log_ohmic_sheet_12x12.txt")
BEST_S11_FILE = os.path.join(SAVE_PATH, "best_s11_ohmic_sheet_12x12.txt")
BEST_S11_PNG = os.path.join(SAVE_PATH, "best_s11_ohmic_sheet_12x12.png")

# 固定当前 12x12 最优结构的单次检查输出路径。
FIXED_CHECK_DIR = os.path.join(SAVE_PATH, "fixed_best_ohmic_sheet_check")
FIXED_CHECK_RESULT_FILE = os.path.join(FIXED_CHECK_DIR, "fixed_best_ohmic_sheet_result.txt")
FIXED_CHECK_S11_FILE = os.path.join(FIXED_CHECK_DIR, "fixed_best_ohmic_sheet_s11.txt")
FIXED_CHECK_PNG = os.path.join(FIXED_CHECK_DIR, "fixed_best_ohmic_sheet_RL.png")

# 仍保留对比模式所需路径，但默认不启用。
COMPARE_DIR = os.path.join(SAVE_PATH, "comparison_thin_solid_vs_ohmic_sheet")
COMPARE_SUMMARY_FILE = os.path.join(COMPARE_DIR, "comparison_summary.txt")
COMPARE_OVERLAY_PNG = os.path.join(COMPARE_DIR, "comparison_overlay_RL.png")
COMPARE_OVERLAY_TXT = os.path.join(COMPARE_DIR, "comparison_overlay_data.txt")

os.makedirs(BASE_SAVE_PATH, exist_ok=True)
os.makedirs(SAVE_PATH, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(FIXED_CHECK_DIR, exist_ok=True)
os.makedirs(COMPARE_DIR, exist_ok=True)

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

# 原薄实体膜模型使用的绘制厚度。
# 该厚度用于把片阻 Rs 换算为体电导率 sigma，并辅助 CST 建立可刻蚀薄层；
# 它不代表实际电阻膜的真实物理厚度。
FILM_DRAW_THICKNESS = 0.02   # mm

# =========================
# 12x12 表面 Ohmic Sheet 模板化拓扑优化设置
# =========================
link = "\n"

# 本版不再使用 84 bit 纯像素随机搜索，而是使用“物理模板参数化 GA”。
# 目标：尽量把 2--18 GHz 内 RL<-10 dB 的连续有效带宽推向 85% 覆盖率。
# 2--18 GHz 总宽度为 16 GHz，85% 对应 13.6 GHz。
#
# DNA 结构共 36 bit：
#   0:6    -> p
#   6:12   -> h
#   12:14  -> template_type
#   14:16  -> Y frame width
#   16:19  -> Y central window width
#   19:22  -> Y central window height
#   22:24  -> Y bridge width
#   24:27  -> Y slot type
#   27:29  -> X strip width
#   29:32  -> X central gap width
#   32:34  -> X end loading type
#   34:36  -> X vertical offset type
#
# 这样每个个体都对应一个物理上较合理的外框/窗口/桥接/条带图案，
# 避免 12x12 完全随机图案空间过大和过碎图案导致的求解器卡顿。
OPTIMIZE_P_H = True
TOPOLOGY_N = 12
SEED_N = 6
SEED_BITS_PER_LAYER = SEED_N * SEED_N
TEMPLATE_MODE = True
dna_size = 36

# 为降低吸收起始频率，需要适当放宽 p 和 h。
# 如需更激进地冲击低频，可把 P_MAX 提到 15.0、H_MAX 提到 11.2，
# 但建议先用当前范围跑通一轮。
P_MIN = 13.00
P_MAX = 14.80
H_MIN = 8.40
H_MAX = 11.00

# 当前 9x9 Ohmic Sheet + p,h 微扰最优结果，用作模板初始化中心。
FIXED_P = 13.18
FIXED_H = 8.866

# 这些 seed 变量仅用于兼容 fixed_best 等旧接口；模板优化时并不直接使用。
# 真正的 X/Y 图案由 decode() 中的 build_x_mask_template/build_y_mask_template 生成。
FIXED_MASK_X_SEED = [0] * (TOPOLOGY_N * TOPOLOGY_N)
FIXED_MASK_Y_SEED = [0] * (TOPOLOGY_N * TOPOLOGY_N)

# 默认先用中等规模测试。若能稳定跑完，可提高到 pop_size=10、iterations=8。
pop_size = 8
iterations = 5
p_m_start = 0.08

# 初始种群围绕一组接近最终 9x9 结构物理特征的模板参数进行扰动。
SEED_POPULATION_WITH_FIXED_BEST = True
SEED_PERTURB_COUNT = 8
SEED_PERTURB_BITS = 2
RANDOM_INDIVIDUAL_MAX_TRIALS = 500
ENABLE_MASK_PREFILTER = True

# 模板生成的图案通常比较规整，筛选阈值主要用于防止极端参数或变异个体。
MIN_KEPT_PIXELS_PER_LAYER = 12
MAX_KEPT_PIXELS_PER_LAYER = 140
MIN_TOTAL_KEPT_PIXELS = 45
MAX_TOTAL_KEPT_PIXELS = 230
MAX_ISOLATED_PIXELS_PER_LAYER = 6
MAX_CONNECTED_COMPONENTS_PER_LAYER = 8

# 85% 覆盖率目标。
TARGET_TOTAL_BAND = 16.0
TARGET_COVERAGE = 0.85
TARGET_CONTIGUOUS_BW = TARGET_TOTAL_BAND * TARGET_COVERAGE
TARGET_LOW_EDGE = 18.0 - TARGET_CONTIGUOUS_BW

INDIVIDUAL_TRACE_FILE = os.path.join(SAVE_PATH, "individual_trace_ohmic_sheet_12x12.txt")
SKIPPED_INDIVIDUAL_FILE = os.path.join(SAVE_PATH, "skipped_individuals_ohmic_sheet_12x12.txt")

# GA 阶段关闭网格自适应；得到候选最优后再单独精算。
USE_MESH_ADAPTION_FOR_GA = False
RESULT_DATA_SAMPLES = 201

# 全局变量
de = cst.interface.DesignEnvironment()
pj = None
cache = {}

# =========================================================
# 分支1对比模式配置
# =========================================================
# RUN_MODE:
#   "fixed_best_ohmic" : 只用表面片阻层模型跑一次当前 12x12 最优图案，用于快速复核。
#   "optimize"         : 默认。沿用原遗传算法框架，但电阻膜统一改为表面 Ohmic Sheet。
#   "compare_fixed"    : 可选。重新对比薄实体膜与表面片阻层。
RUN_MODE = "optimize"

# 本轮优化统一采用 CST Ohmic Sheet 表面片阻层模型。
# 即：直接在 PET 表面生成二维片阻面，材料由 .OhmicSheetImpedance "60", "0" 定义。
OPTIMIZATION_FILM_MODEL = "ohmic_sheet"

# 当前 12x12 阶段最优结构，用于分支1固定结构对比
# FIXED_P/FIXED_H/FIXED_MASK_* 已在 12x12 配置区定义，这里不再重复定义。

# 分支1要对比的两种电阻膜建模方式
COMPARE_FILM_MODEL_TYPES = ["thin_solid", "ohmic_sheet"]

# CST Ohmic Sheet 材料名称。与原薄实体材料名称分开，便于在结果树和模型树中区分。
FILM_X_SHEET_NAME = "SMH188H_60_OhmicSheet"
FILM_Y_SHEET_NAME = "SMH188H_60_OhmicSheet"

# 片阻层模型创建方式：
#   "shape_from_helper_face"：根据你在 CST 2025 History List 中获得的命令：
#       Solid.CreateShapeFromFaces "solid2", "component1", "material1"
#   先创建一个极薄的临时辅助 brick，选取其外表面，再用 CreateShapeFromFaces
#   从被选中的 face 生成真正的 Ohmic Sheet 面对象，最后删除临时 brick。
#
# 这样生成的是 CST 认可的 “Ohmic sheet surf. imp.” 面对象，
# 而不是厚度为 0 的实体 brick。
OHMIC_SHEET_GEOMETRY_METHOD = "shape_from_helper_face"

# 临时辅助 brick 厚度，单位 mm。该 brick 只用于提供可 Pick 的 face，
# 生成 sheet 后会被删除，不参与最终电磁仿真。
HELPER_BRICK_THICKNESS = 1e-4

# 由你在 CST 2025 History List 中提供的命令可知，目标片阻面对应的 Pick face id 为 6：
#     Pick.PickFaceFromId "component1:pet_y", "6"
# 因此 v6 默认两个方向的临时辅助面都使用 face id = 6。
# 如果 X 膜位置仍不正确，可在 CST 中对 pet_x 的目标表面执行 Pick Face，
# 再把 History List 中的 face id 填到 FACE_ID_X_PLUS_Y。
FACE_ID_X_PLUS_Y = "6"
FACE_ID_Y_PLUS_X = "6"

# 是否把生成的 sheet 对象加入 meshgroup1。
# 你手动测试的 History List 中出现了：
# Group.AddItem "solid$component1:solid2", "meshgroup1"
# 这一步不是创建 sheet 的核心命令。v4 默认关闭，以减少调试阶段的额外报错来源。
ADD_SHEET_TO_MESHGROUP = False
MESHGROUP_NAME = "meshgroup1"

# CST 2025 的 Ohmic Sheet 材料在不同小版本中的 VBA 字段可能不同。
# 你的 error_log 已经证明：Material 对象没有 .Impedance 方法。
# v6 不再写死 .Impedance，而是先尝试读取你手动导出的材料历史命令；
# 若没有外部历史命令文件，则自动尝试若干常见字段，并把失败信息写入 error_log。
#
# 如果 v6 的自动候选仍失败，请在 CST History List 中点击第 2 行
# "define material: material1" -> Edit...，复制完整 VBA 到下面这个文件：
#     F:\biyesheji\code\ohmic_sheet_material_history.txt
# 然后重新运行本脚本。脚本会自动把其中的 material1 改名为所需材料名。
OHMIC_MATERIAL_HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ohmic_sheet_material_history.txt")


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
# 分支1新增：CST Ohmic Sheet / 无厚度片阻层材料
# =========================================================
def _append_error_log(message):
    """把材料候选命令失败原因写入 error_log，便于定位 CST VBA 字段。"""
    try:
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(str(message) + "\n")
    except Exception:
        pass


def _replace_material_name_in_history(history_text, target_name, rs):
    """把从 CST History List 复制出来的 material1 材料定义改名为目标材料名。"""
    text = history_text
    text = text.replace('.Name "material1"', f'.Name "{target_name}"')
    text = text.replace('.Name "Material1"', f'.Name "{target_name}"')
    text = text.replace('{MATERIAL_NAME}', target_name)
    text = text.replace('{SHEET_RESISTANCE}', str(rs))
    return text


def _try_create_material_from_external_history(target_name, rs, title):
    """优先使用用户从 CST History List 复制出来的完整 Ohmic Sheet 材料命令。"""
    if not os.path.exists(OHMIC_MATERIAL_HISTORY_FILE):
        return False

    with open(OHMIC_MATERIAL_HISTORY_FILE, "r", encoding="utf-8") as f:
        history_text = f.read().strip()

    if not history_text:
        return False

    cmd = _replace_material_name_in_history(history_text, target_name, rs)
    pj.model3d.add_to_history(title + " from external CST history", cmd)
    return True


def _candidate_ohmic_material_commands(material_name, rs, color_rgb):
    """生成多个 CST Ohmic Sheet 材料定义候选。

    你当前的报错已经确认 .Impedance 不是 Material 对象的方法。
    CST 不同版本的 Ohmic Sheet 参数名可能存在差异，因此这里使用候选法。
    """
    r, g, b = color_rgb
    candidates = []

    field_blocks = [
        ("SurfaceImpedance_pair", f'     .SurfaceImpedance "{rs}", "0"\n'),
        ("SurfaceImpedance_single", f'     .SurfaceImpedance "{rs}"\n'),
        ("SetSurfaceImpedance_pair", f'     .SetSurfaceImpedance "{rs}", "0"\n'),
        ("SetSurfaceImpedance_single", f'     .SetSurfaceImpedance "{rs}"\n'),
        ("SheetResistance", f'     .SheetResistance "{rs}"\n'),
        ("SetSheetResistance", f'     .SetSheetResistance "{rs}"\n'),
        ("SurfaceResistance", f'     .SurfaceResistance "{rs}"\n'),
        ("Resistance", f'     .Resistance "{rs}"\n'),
        ("OhmicSheetResistance", f'     .OhmicSheetResistance "{rs}"\n'),
        ("SetOhmicSheetResistance", f'     .SetOhmicSheetResistance "{rs}"\n'),
        ("TypeOnly", ''),
    ]

    type_strings = ["Ohmic sheet", "Ohmic Sheet", "OhmicSheet"]

    for type_string in type_strings:
        for label, field in field_blocks:
            cmd = f'''
With Material
     .Reset
     .Name "{material_name}"
     .Folder ""
     .FrqType "all"
     .Type "{type_string}"
     .MaterialUnit "Frequency", "GHz"
     .MaterialUnit "Geometry", "mm"
{field}     .Colour "{r}", "{g}", "{b}"
     .Transparency "0"
     .Create
End With
'''
            candidates.append((f"{type_string} + {label}", cmd))

    return candidates


def _create_ohmic_sheet_material_one(material_name, rs, color_rgb, title):
    """创建 CST 2025 可识别的 Ohmic Sheet 材料。

    这个命令来自你在 CST 2025 History List 中重新创建材料后导出的 VBA：
        .Type "Lossy metal"
        .OhmicSheetImpedance "60", "0"
        .OhmicSheetFreq "0"

    注意：CST 界面里显示为 Impedance = 60 [Ohm/sq]，但 VBA 字段不是 .Impedance，
    而是 .OhmicSheetImpedance。
    """
    r, g, b = color_rgb
    sCommand = f"""
With Material
     .Reset
     .Name "{material_name}"
     .Folder ""
     .Rho "0"
     .ThermalType "Normal"
     .ThermalConductivity "0"
     .SpecificHeat "0", "J/K/kg"
     .DynamicViscosity "0"
     .UseEmissivity "True"
     .Emissivity "0"
     .MetabolicRate "0.0"
     .VoxelConvection "0.0"
     .BloodFlow "0"
     .MechanicsType "Unused"
     .SolarRadiationAbsorptionType "Opaque"
     .Absorptance "0.0"
     .UseSemiTransparencyCalculator "False"
     .SolarRadTransmittance "0.0"
     .SolarRadReflectance "0.0"
     .SolarRadSpecimenThickness "0.0"
     .SolarRadRefractiveIndex "1.0"
     .SolarRadAbsorptionCoefficient "0.0"
     .IntrinsicCarrierDensityModel "none"
     .FrqType "all"
     .Type "Lossy metal"
     .MaterialUnit "Frequency", "GHz"
     .MaterialUnit "Geometry", "mm"
     .MaterialUnit "Time", "ns"
     .MaterialUnit "Temperature", "degC"
     .OhmicSheetImpedance "{rs}", "0"
     .OhmicSheetFreq "0"
     .ReferenceCoordSystem "Global"
     .CoordSystemType "Cartesian"
     .NLAnisotropy "False"
     .NLAStackingFactor "1"
     .NLADirectionX "1"
     .NLADirectionY "0"
     .NLADirectionZ "0"
     .Colour "{r}", "{g}", "{b}"
     .Wireframe "False"
     .Reflection "False"
     .Allowoutline "True"
     .Transparentoutline "False"
     .Transparency "0"
     .Create
End With
"""
    pj.model3d.add_to_history(title, sCommand)


def create_ohmic_sheet_material():
    """创建 CST Ohmic Sheet 材料。X/Y 膜片阻相同，因此默认共用同一种材料。"""
    created = set()
    material_specs = [
        (FILM_X_SHEET_NAME, FILM_X_SHEET_RESISTANCE, ("0", "1", "1"), "define material: ohmic sheet film x"),
        (FILM_Y_SHEET_NAME, FILM_Y_SHEET_RESISTANCE, ("0", "1", "1"), "define material: ohmic sheet film y"),
    ]
    for name, rs, color, title in material_specs:
        if name in created:
            continue
        _create_ohmic_sheet_material_one(name, rs, color, title)
        created.add(name)

# =========================================================
# 学长原版 gaoshang()
# =========================================================
def gaoshang():
    sCommand = ['With Material', '     .Reset', '     .Name "GAOSHANG"', '     .Folder ""', '     .Rho "0.0"', '     .ThermalType "Normal"', '     .ThermalConductivity "0"', '     .SpecificHeat "0", "J/K/kg"', '     .DynamicViscosity "0"', '     .Emissivity "0"', '     .MetabolicRate "0.0"', '     .VoxelConvection "0.0"', '     .BloodFlow "0"', '     .MechanicsType "Unused"', '     .IntrinsicCarrierDensity "0"', '     .FrqType "all"', '     .Type "Normal"', '     .MaterialUnit "Frequency", "GHz"', '     .MaterialUnit "Geometry", "mm"', '     .MaterialUnit "Time", "ns"', '     .MaterialUnit "Temperature", "Kelvin"', '     .Epsilon "1"', '     .Mu "1"', '     .Sigma "0"', '     .TanD "0.0"', '     .TanDFreq "0.0"', '     .TanDGiven "False"', '     .TanDModel "ConstTanD"', '     .SetConstTanDStrategyEps "AutomaticOrder"', '     .ConstTanDModelOrderEps "3"', '     .DjordjevicSarkarUpperFreqEps "0"', '     .SetElParametricConductivity "False"', '     .ReferenceCoordSystem "Global"', '     .CoordSystemType "Cartesian"', '     .SigmaM "0"', '     .TanDM "0.0"', '     .TanDMFreq "0.0"', '     .TanDMGiven "False"', '     .TanDMModel "ConstTanD"', '     .SetConstTanDStrategyMu "AutomaticOrder"', '     .ConstTanDModelOrderMu "3"', '     .DjordjevicSarkarUpperFreqMu "0"', '     .SetMagParametricConductivity "False"', '     .DispModelEps "None"', '     .DispModelMu "None"', '     .DispersiveFittingSchemeEps "Nth Order"', '     .MaximalOrderNthModelFitEps "10"', '     .ErrorLimitNthModelFitEps "0.1"', '     .DispersiveFittingSchemeMu "Nth Order"', '     .MaximalOrderNthModelFitMu "10"', '     .ErrorLimitNthModelFitMu "0.1"', '     .DispersiveFittingFormatEps "Real_Imag"', '     .AddDispersionFittingValueEps "2", "22.578", "8.3324", "1.0"', '     .AddDispersionFittingValueEps "2.08", "22.4146", "8.2213", "1.0"', '     .AddDispersionFittingValueEps "2.16", "22.2326", "8.1064", "1.0"', '     .AddDispersionFittingValueEps "2.24", "22.0849", "8.0342", "1.0"', '     .AddDispersionFittingValueEps "2.32", "21.9314", "7.9292", "1.0"', '     .AddDispersionFittingValueEps "2.4", "21.7808", "7.863", "1.0"', '     .AddDispersionFittingValueEps "2.48", "21.6598", "7.7878", "1.0"', '     .AddDispersionFittingValueEps "2.56", "21.5289", "7.7084", "1.0"', '     .AddDispersionFittingValueEps "2.64", "21.4164", "7.6481", "1.0"', '     .AddDispersionFittingValueEps "2.72", "21.2953", "7.5649", "1.0"', '     .AddDispersionFittingValueEps "2.8", "21.1965", "7.5103", "1.0"', '     .AddDispersionFittingValueEps "2.88", "21.087", "7.4356", "1.0"', '     .AddDispersionFittingValueEps "2.96", "20.9956", "7.3835", "1.0"', '     .AddDispersionFittingValueEps "3.04", "20.8994", "7.33", "1.0"', '     .AddDispersionFittingValueEps "3.12", "20.8143", "7.265", "1.0"', '     .AddDispersionFittingValueEps "3.2", "20.7213", "7.2184", "1.0"', '     .AddDispersionFittingValueEps "3.28", "20.6261", "7.1557", "1.0"', '     .AddDispersionFittingValueEps "3.36", "20.537", "7.1273", "1.0"', '     .AddDispersionFittingValueEps "3.44", "20.4611", "7.0929", "1.0"', '     .AddDispersionFittingValueEps "3.52", "20.39", "7.0429", "1.0"', '     .AddDispersionFittingValueEps "3.6", "20.3043", "6.9937", "1.0"', '     .AddDispersionFittingValueEps "3.68", "20.213", "6.9384", "1.0"', '     .AddDispersionFittingValueEps "3.76", "20.1303", "6.902", "1.0"', '     .AddDispersionFittingValueEps "3.84", "20.047", "6.8588", "1.0"', '     .AddDispersionFittingValueEps "3.92", "19.9736", "6.8167", "1.0"', '     .AddDispersionFittingValueEps "4", "19.8927", "6.7712", "1.0"', '     .AddDispersionFittingValueEps "4.08", "19.8287", "6.7207", "1.0"', '     .AddDispersionFittingValueEps "4.16", "19.7334", "6.6741", "1.0"', '     .AddDispersionFittingValueEps "4.24", "19.6777", "6.65", "1.0"', '     .AddDispersionFittingValueEps "4.32", "19.6077", "6.6015", "1.0"', '     .AddDispersionFittingValueEps "4.4", "19.5623", "6.5762", "1.0"', '     .AddDispersionFittingValueEps "4.48", "19.4983", "6.5265", "1.0"', '     .AddDispersionFittingValueEps "4.56", "19.4595", "6.5045", "1.0"', '     .AddDispersionFittingValueEps "4.64", "19.4098", "6.4557", "1.0"', '     .AddDispersionFittingValueEps "4.72", "19.3657", "6.4348", "1.0"', '     .AddDispersionFittingValueEps "4.8", "19.3212", "6.3956", "1.0"', '     .AddDispersionFittingValueEps "4.88", "19.2635", "6.3813", "1.0"', '     .AddDispersionFittingValueEps "4.96", "19.2168", "6.3701", "1.0"', '     .AddDispersionFittingValueEps "5.04", "19.1779", "6.3592", "1.0"', '     .AddDispersionFittingValueEps "5.12", "19.1363", "6.334", "1.0"', '     .AddDispersionFittingValueEps "5.2", "19.0876", "6.3549", "1.0"', '     .AddDispersionFittingValueEps "5.28", "19.0703", "6.3365", "1.0"', '     .AddDispersionFittingValueEps "5.36", "19.0192", "6.3405", "1.0"', '     .AddDispersionFittingValueEps "5.44", "18.9861", "6.3464", "1.0"', '     .AddDispersionFittingValueEps "5.52", "18.9619", "6.3625", "1.0"', '     .AddDispersionFittingValueEps "5.6", "18.9267", "6.3562", "1.0"', '     .AddDispersionFittingValueEps "5.68", "18.8762", "6.3836", "1.0"', '     .AddDispersionFittingValueEps "5.76", "18.8611", "6.4042", "1.0"', '     .AddDispersionFittingValueEps "5.84", "18.8189", "6.4068", "1.0"', '     .AddDispersionFittingValueEps "5.92", "18.7811", "6.4264", "1.0"', '     .AddDispersionFittingValueEps "6", "18.731", "6.4579", "1.0"', '     .AddDispersionFittingValueEps "6.08", "18.7031", "6.4749", "1.0"', '     .AddDispersionFittingValueEps "6.16", "18.6445", "6.491", "1.0"', '     .AddDispersionFittingValueEps "6.24", "18.5857", "6.5095", "1.0"', '     .AddDispersionFittingValueEps "6.32", "18.5261", "6.5179", "1.0"', '     .AddDispersionFittingValueEps "6.4", "18.4453", "6.5183", "1.0"', '     .AddDispersionFittingValueEps "6.48", "18.3572", "6.5315", "1.0"', '     .AddDispersionFittingValueEps "6.56", "18.2712", "6.5378", "1.0"', '     .AddDispersionFittingValueEps "6.64", "18.1768", "6.5334", "1.0"', '     .AddDispersionFittingValueEps "6.72", "18.1005", "6.5269", "1.0"', '     .AddDispersionFittingValueEps "6.8", "17.9967", "6.496", "1.0"', '     .AddDispersionFittingValueEps "6.88", "17.9147", "6.4778", "1.0"', '     .AddDispersionFittingValueEps "6.96", "17.8154", "6.4296", "1.0"', '     .AddDispersionFittingValueEps "7.04", "17.7311", "6.3975", "1.0"', '     .AddDispersionFittingValueEps "7.12", "17.6529", "6.3276", "1.0"', '     .AddDispersionFittingValueEps "7.2", "17.5732", "6.2505", "1.0"', '     .AddDispersionFittingValueEps "7.28", "17.4904", "6.1677", "1.0"', '     .AddDispersionFittingValueEps "7.36", "17.4018", "6.0896", "1.0"', '     .AddDispersionFittingValueEps "7.44", "17.34", "6.0183", "1.0"', '     .AddDispersionFittingValueEps "7.52", "17.2802", "5.9401", "1.0"', '     .AddDispersionFittingValueEps "7.6", "17.2461", "5.8661", "1.0"', '     .AddDispersionFittingValueEps "7.68", "17.2248", "5.7719", "1.0"', '     .AddDispersionFittingValueEps "7.76", "17.1984", "5.6968", "1.0"', '     .AddDispersionFittingValueEps "7.84", "17.2001", "5.6195", "1.0"', '     .AddDispersionFittingValueEps "7.92", "17.2085", "5.5369", "1.0"', '     .AddDispersionFittingValueEps "8", "17.2252", "5.4487", "1.0"', '     .AddDispersionFittingValueEps "8.08", "17.234", "5.3745", "1.0"', '     .AddDispersionFittingValueEps "8.16", "17.2512", "5.3061", "1.0"', '     .AddDispersionFittingValueEps "8.24", "17.2738", "5.2577", "1.0"', '     .AddDispersionFittingValueEps "8.32", "17.3105", "5.2103", "1.0"', '     .AddDispersionFittingValueEps "8.4", "17.3451", "5.1806", "1.0"', '     .AddDispersionFittingValueEps "8.48", "17.4137", "5.145", "1.0"', '     .AddDispersionFittingValueEps "8.56", "17.4534", "5.1133", "1.0"', '     .AddDispersionFittingValueEps "8.64", "17.5207", "5.1032", "1.0"', '     .AddDispersionFittingValueEps "8.72", "17.5857", "5.0993", "1.0"', '     .AddDispersionFittingValueEps "8.8", "17.6803", "5.0858", "1.0"', '     .AddDispersionFittingValueEps "8.88", "17.7482", "5.0689", "1.0"', '     .AddDispersionFittingValueEps "8.96", "17.8119", "5.0555", "1.0"', '     .AddDispersionFittingValueEps "9.04", "17.8569", "5.0344", "1.0"', '     .AddDispersionFittingValueEps "9.12", "17.8805", "5.0598", "1.0"', '     .AddDispersionFittingValueEps "9.2", "17.9402", "5.0979", "1.0"', '     .AddDispersionFittingValueEps "9.28", "17.9975", "5.1294", "1.0"', '     .AddDispersionFittingValueEps "9.36", "18.0268", "5.1744", "1.0"', '     .AddDispersionFittingValueEps "9.44", "18.1045", "5.234", "1.0"', '     .AddDispersionFittingValueEps "9.52", "18.1432", "5.2831", "1.0"', '     .AddDispersionFittingValueEps "9.6", "18.224", "5.3324", "1.0"', '     .AddDispersionFittingValueEps "9.68", "18.2583", "5.429", "1.0"', '     .AddDispersionFittingValueEps "9.76", "18.3846", "5.4503", "1.0"', '     .AddDispersionFittingValueEps "9.84", "18.3927", "5.4941", "1.0"', '     .AddDispersionFittingValueEps "9.92", "18.414", "5.537", "1.0"', '     .AddDispersionFittingValueEps "10", "18.4287", "5.6203", "1.0"', '     .AddDispersionFittingValueEps "10.08", "18.4387", "5.6789", "1.0"', '     .AddDispersionFittingValueEps "10.16", "18.4139", "5.7444", "1.0"', '     .AddDispersionFittingValueEps "10.24", "18.4024", "5.8695", "1.0"', '     .AddDispersionFittingValueEps "10.32", "18.4075", "5.9486", "1.0"', '     .AddDispersionFittingValueEps "10.4", "18.4598", "6.0628", "1.0"', '     .AddDispersionFittingValueEps "10.48", "18.4385", "6.0698", "1.0"', '     .AddDispersionFittingValueEps "10.56", "18.4318", "6.1826", "1.0"', '     .AddDispersionFittingValueEps "10.64", "18.3975", "6.2384", "1.0"', '     .AddDispersionFittingValueEps "10.72", "18.4421", "6.2775", "1.0"', '     .AddDispersionFittingValueEps "10.8", "18.4032", "6.3323", "1.0"', '     .AddDispersionFittingValueEps "10.88", "18.3909", "6.3605", "1.0"', '     .AddDispersionFittingValueEps "10.96", "18.3827", "6.3758", "1.0"', '     .AddDispersionFittingValueEps "11.04", "18.274", "6.3513", "1.0"', '     .AddDispersionFittingValueEps "11.12", "18.1945", "6.4128", "1.0"', '     .AddDispersionFittingValueEps "11.2", "18.1218", "6.478", "1.0"', '     .AddDispersionFittingValueEps "11.28", "18.1004", "6.5346", "1.0"', '     .AddDispersionFittingValueEps "11.36", "18.0579", "6.5974", "1.0"', '     .AddDispersionFittingValueEps "11.44", "17.9945", "6.6115", "1.0"', '     .AddDispersionFittingValueEps "11.52", "18.0509", "6.7536", "1.0"', '     .AddDispersionFittingValueEps "11.6", "18.0249", "6.6893", "1.0"', '     .AddDispersionFittingValueEps "11.68", "18.0159", "6.7287", "1.0"', '     .AddDispersionFittingValueEps "11.76", "17.948", "6.7568", "1.0"', '     .AddDispersionFittingValueEps "11.84", "17.944", "6.7866", "1.0"', '     .AddDispersionFittingValueEps "11.92", "17.877", "6.8224", "1.0"', '     .AddDispersionFittingValueEps "12", "17.8338", "6.8672", "1.0"', '     .AddDispersionFittingValueEps "12.08", "17.8411", "6.9503", "1.0"', '     .AddDispersionFittingValueEps "12.16", "17.7709", "6.9536", "1.0"', '     .AddDispersionFittingValueEps "12.24", "17.7161", "7.0588", "1.0"', '     .AddDispersionFittingValueEps "12.32", "17.6388", "7.2147", "1.0"', '     .AddDispersionFittingValueEps "12.4", "17.6959", "7.3237", "1.0"', '     .AddDispersionFittingValueEps "12.48", "17.7287", "7.4255", "1.0"', '     .AddDispersionFittingValueEps "12.56", "17.7586", "7.4362", "1.0"', '     .AddDispersionFittingValueEps "12.64", "17.7272", "7.5307", "1.0"', '     .AddDispersionFittingValueEps "12.72", "17.7188", "7.6129", "1.0"', '     .AddDispersionFittingValueEps "12.8", "17.7081", "7.668", "1.0"', '     .AddDispersionFittingValueEps "12.88", "17.688", "7.7815", "1.0"', '     .AddDispersionFittingValueEps "12.96", "17.69", "7.822", "1.0"', '     .AddDispersionFittingValueEps "13.04", "17.6508", "7.9207", "1.0"', '     .AddDispersionFittingValueEps "13.12", "17.589", "7.9549", "1.0"', '     .AddDispersionFittingValueEps "13.2", "17.5097", "8.164", "1.0"', '     .AddDispersionFittingValueEps "13.28", "17.574", "8.3232", "1.0"', '     .AddDispersionFittingValueEps "13.36", "17.5596", "8.3632", "1.0"', '     .AddDispersionFittingValueEps "13.44", "17.5337", "8.5234", "1.0"', '     .AddDispersionFittingValueEps "13.52", "17.5345", "8.6488", "1.0"', '     .AddDispersionFittingValueEps "13.6", "17.63", "8.6701", "1.0"', '     .AddDispersionFittingValueEps "13.68", "17.4669", "8.6766", "1.0"', '     .AddDispersionFittingValueEps "13.76", "17.4673", "8.8054", "1.0"', '     .AddDispersionFittingValueEps "13.84", "17.3551", "8.8", "1.0"', '     .AddDispersionFittingValueEps "13.92", "17.2607", "8.8513", "1.0"', '     .AddDispersionFittingValueEps "14", "17.1388", "8.9488", "1.0"', '     .AddDispersionFittingValueEps "14.08", "17.0908", "9.0705", "1.0"', '     .AddDispersionFittingValueEps "14.16", "17.0824", "9.0934", "1.0"', '     .AddDispersionFittingValueEps "14.24", "16.8587", "9.1144", "1.0"', '     .AddDispersionFittingValueEps "14.32", "16.7971", "9.236", "1.0"', '     .AddDispersionFittingValueEps "14.4", "16.6531", "9.3154", "1.0"', '     .AddDispersionFittingValueEps "14.48", "16.7009", "9.3846", "1.0"', '     .AddDispersionFittingValueEps "14.56", "16.5269", "9.3727", "1.0"', '     .AddDispersionFittingValueEps "14.64", "16.4701", "9.4703", "1.0"', '     .AddDispersionFittingValueEps "14.72", "16.3504", "9.4808", "1.0"', '     .AddDispersionFittingValueEps "14.8", "16.2558", "9.5787", "1.0"', '     .AddDispersionFittingValueEps "14.88", "16.1191", "9.5315", "1.0"', '     .AddDispersionFittingValueEps "14.96", "15.896", "9.659", "1.0"', '     .AddDispersionFittingValueEps "15.04", "15.7756", "9.7282", "1.0"', '     .AddDispersionFittingValueEps "15.12", "15.5865", "9.7815", "1.0"', '     .AddDispersionFittingValueEps "15.2", "15.466", "9.8964", "1.0"', '     .AddDispersionFittingValueEps "15.28", "15.3046", "9.9557", "1.0"', '     .AddDispersionFittingValueEps "15.36", "15.1292", "9.9666", "1.0"', '     .AddDispersionFittingValueEps "15.44", "14.7721", "9.9736", "1.0"', '     .AddDispersionFittingValueEps "15.52", "14.574", "10.1403", "1.0"', '     .AddDispersionFittingValueEps "15.6", "14.4947", "10.2389", "1.0"', '     .AddDispersionFittingValueEps "15.68", "14.44", "10.2328", "1.0"', '     .AddDispersionFittingValueEps "15.76", "14.2334", "10.2085", "1.0"', '     .AddDispersionFittingValueEps "15.84", "14.0489", "10.1267", "1.0"', '     .AddDispersionFittingValueEps "15.92", "13.7374", "10.1604", "1.0"', '     .AddDispersionFittingValueEps "16", "13.5979", "10.0449", "1.0"', '     .AddDispersionFittingValueEps "16.08", "13.4692", "10.0914", "1.0"', '     .AddDispersionFittingValueEps "16.16", "13.291", "9.8897", "1.0"', '     .AddDispersionFittingValueEps "16.24", "13.0422", "9.926", "1.0"', '     .AddDispersionFittingValueEps "16.32", "12.8426", "9.8474", "1.0"', '     .AddDispersionFittingValueEps "16.4", "12.6628", "9.8599", "1.0"', '     .AddDispersionFittingValueEps "16.48", "12.5293", "9.8657", "1.0"', '     .AddDispersionFittingValueEps "16.56", "12.3656", "9.8266", "1.0"', '     .AddDispersionFittingValueEps "16.64", "12.3297", "9.776", "1.0"', '     .AddDispersionFittingValueEps "16.72", "12.1159", "9.665", "1.0"', '     .AddDispersionFittingValueEps "16.8", "12.084", "9.6732", "1.0"', '     .AddDispersionFittingValueEps "16.88", "11.9724", "9.4574", "1.0"', '     .AddDispersionFittingValueEps "16.96", "11.8553", "9.3286", "1.0"', '     .AddDispersionFittingValueEps "17.04", "11.6536", "9.1656", "1.0"', '     .AddDispersionFittingValueEps "17.12", "11.5326", "9.1618", "1.0"', '     .AddDispersionFittingValueEps "17.2", "11.4273", "9.0407", "1.0"', '     .AddDispersionFittingValueEps "17.28", "11.3512", "9.0187", "1.0"', '     .AddDispersionFittingValueEps "17.36", "11.3162", "8.8558", "1.0"', '     .AddDispersionFittingValueEps "17.44", "11.2297", "8.7508", "1.0"', '     .AddDispersionFittingValueEps "17.52", "11.1667", "8.6607", "1.0"', '     .AddDispersionFittingValueEps "17.6", "11.1587", "8.6025", "1.0"', '     .AddDispersionFittingValueEps "17.68", "11.1817", "8.4953", "1.0"', '     .AddDispersionFittingValueEps "17.76", "11.194", "8.3737", "1.0"', '     .AddDispersionFittingValueEps "17.84", "11.2168", "8.1911", "1.0"', '     .AddDispersionFittingValueEps "17.92", "11.1145", "7.9831", "1.0"', '     .AddDispersionFittingValueEps "18", "11.0239", "7.9573", "1.0"', '     .UseGeneralDispersionEps "True"', '     .DispersiveFittingFormatMu "Real_Imag"', '     .AddDispersionFittingValueMu "2", "0.9581", "0.0433", "1.0"', '     .AddDispersionFittingValueMu "2.08", "0.957", "0.0381", "1.0"', '     .AddDispersionFittingValueMu "2.16", "0.9564", "0.0315", "1.0"', '     .AddDispersionFittingValueMu "2.24", "0.9536", "0.0215", "1.0"', '     .AddDispersionFittingValueMu "2.32", "0.9497", "0.0153", "1.0"', '     .AddDispersionFittingValueMu "2.4", "0.9525", "0.0085", "1.0"', '     .AddDispersionFittingValueMu "2.48", "0.9474", "0.0007", "1.0"', '     .AddDispersionFittingValueMu "2.56", "0.9534", "0", "1.0"', '     .AddDispersionFittingValueMu "2.64", "0.9549", "0", "1.0"', '     .AddDispersionFittingValueMu "2.72", "0.9556", "0", "1.0"', '     .AddDispersionFittingValueMu "2.8", "0.9614", "0", "1.0"', '     .AddDispersionFittingValueMu "2.88", "0.9627", "0", "1.0"', '     .AddDispersionFittingValueMu "2.96", "0.9693", "0", "1.0"', '     .AddDispersionFittingValueMu "3.04", "0.9707", "0", "1.0"', '     .AddDispersionFittingValueMu "3.12", "0.9769", "0", "1.0"', '     .AddDispersionFittingValueMu "3.2", "0.9777", "0", "1.0"', '     .AddDispersionFittingValueMu "3.28", "0.9818", "0", "1.0"', '     .AddDispersionFittingValueMu "3.36", "0.9836", "0", "1.0"', '     .AddDispersionFittingValueMu "3.44", "0.9839", "0", "1.0"', '     .AddDispersionFittingValueMu "3.52", "0.9854", "0", "1.0"', '     .AddDispersionFittingValueMu "3.6", "0.9878", "0", "1.0"', '     .AddDispersionFittingValueMu "3.68", "0.9874", "0", "1.0"', '     .AddDispersionFittingValueMu "3.76", "0.9854", "0", "1.0"', '     .AddDispersionFittingValueMu "3.84", "0.9851", "0", "1.0"', '     .AddDispersionFittingValueMu "3.92", "0.9831", "0", "1.0"', '     .AddDispersionFittingValueMu "4", "0.9837", "0", "1.0"', '     .AddDispersionFittingValueMu "4.08", "0.9813", "0", "1.0"', '     .AddDispersionFittingValueMu "4.16", "0.9819", "0", "1.0"', '     .AddDispersionFittingValueMu "4.24", "0.9788", "0", "1.0"', '     .AddDispersionFittingValueMu "4.32", "0.979", "0", "1.0"', '     .AddDispersionFittingValueMu "4.4", "0.9779", "0", "1.0"', '     .AddDispersionFittingValueMu "4.48", "0.9779", "0", "1.0"', '     .AddDispersionFittingValueMu "4.56", "0.9791", "0", "1.0"', '     .AddDispersionFittingValueMu "4.64", "0.9803", "0", "1.0"', '     .AddDispersionFittingValueMu "4.72", "0.9821", "0", "1.0"', '     .AddDispersionFittingValueMu "4.8", "0.9837", "0", "1.0"', '     .AddDispersionFittingValueMu "4.88", "0.9836", "0", "1.0"', '     .AddDispersionFittingValueMu "4.96", "0.9846", "0", "1.0"', '     .AddDispersionFittingValueMu "5.04", "0.9855", "0", "1.0"', '     .AddDispersionFittingValueMu "5.12", "0.989", "0", "1.0"', '     .AddDispersionFittingValueMu "5.2", "0.9873", "0", "1.0"', '     .AddDispersionFittingValueMu "5.28", "0.9896", "0", "1.0"', '     .AddDispersionFittingValueMu "5.36", "0.9931", "0", "1.0"', '     .AddDispersionFittingValueMu "5.44", "0.995", "0", "1.0"', '     .AddDispersionFittingValueMu "5.52", "0.9957", "0", "1.0"', '     .AddDispersionFittingValueMu "5.6", "1.0008", "0", "1.0"', '     .AddDispersionFittingValueMu "5.68", "0.9996", "0", "1.0"', '     .AddDispersionFittingValueMu "5.76", "0.9989", "0", "1.0"', '     .AddDispersionFittingValueMu "5.84", "1.0009", "0", "1.0"', '     .AddDispersionFittingValueMu "5.92", "1.0028", "0", "1.0"', '     .AddDispersionFittingValueMu "6", "1.0004", "0", "1.0"', '     .AddDispersionFittingValueMu "6.08", "1.0012", "0", "1.0"', '     .AddDispersionFittingValueMu "6.16", "1.0007", "0", "1.0"', '     .AddDispersionFittingValueMu "6.24", "1.0001", "0", "1.0"', '     .AddDispersionFittingValueMu "6.32", "1", "0", "1.0"', '     .AddDispersionFittingValueMu "6.4", "0.9999", "0", "1.0"', '     .AddDispersionFittingValueMu "6.48", "1", "0", "1.0"', '     .AddDispersionFittingValueMu "6.56", "0.9958", "0", "1.0"', '     .AddDispersionFittingValueMu "6.64", "0.9945", "0", "1.0"', '     .AddDispersionFittingValueMu "6.72", "0.9921", "0", "1.0"', '     .AddDispersionFittingValueMu "6.8", "0.9906", "0", "1.0"', '     .AddDispersionFittingValueMu "6.88", "0.9884", "0", "1.0"', '     .AddDispersionFittingValueMu "6.96", "0.9864", "0", "1.0"', '     .AddDispersionFittingValueMu "7.04", "0.984", "0", "1.0"', '     .AddDispersionFittingValueMu "7.12", "0.982", "0", "1.0"', '     .AddDispersionFittingValueMu "7.2", "0.9831", "0", "1.0"', '     .AddDispersionFittingValueMu "7.28", "0.9822", "0", "1.0"', '     .AddDispersionFittingValueMu "7.36", "0.981", "0", "1.0"', '     .AddDispersionFittingValueMu "7.44", "0.9795", "0", "1.0"', '     .AddDispersionFittingValueMu "7.52", "0.9779", "0", "1.0"', '     .AddDispersionFittingValueMu "7.6", "0.9769", "0", "1.0"', '     .AddDispersionFittingValueMu "7.68", "0.976", "0", "1.0"', '     .AddDispersionFittingValueMu "7.76", "0.976", "0", "1.0"', '     .AddDispersionFittingValueMu "7.84", "0.9736", "0", "1.0"', '     .AddDispersionFittingValueMu "7.92", "0.9728", "0", "1.0"', '     .AddDispersionFittingValueMu "8", "0.9716", "0", "1.0"', '     .AddDispersionFittingValueMu "8.08", "0.9716", "0", "1.0"', '     .AddDispersionFittingValueMu "8.16", "0.9713", "0", "1.0"', '     .AddDispersionFittingValueMu "8.24", "0.9717", "0", "1.0"', '     .AddDispersionFittingValueMu "8.32", "0.971", "0", "1.0"', '     .AddDispersionFittingValueMu "8.4", "0.9706", "0", "1.0"', '     .AddDispersionFittingValueMu "8.48", "0.9706", "0", "1.0"', '     .AddDispersionFittingValueMu "8.56", "0.9702", "0", "1.0"', '     .AddDispersionFittingValueMu "8.64", "0.9693", "0", "1.0"', '     .AddDispersionFittingValueMu "8.72", "0.9679", "0", "1.0"', '     .AddDispersionFittingValueMu "8.8", "0.9678", "0", "1.0"', '     .AddDispersionFittingValueMu "8.88", "0.9673", "0", "1.0"', '     .AddDispersionFittingValueMu "8.96", "0.968", "0", "1.0"', '     .AddDispersionFittingValueMu "9.04", "0.9688", "0", "1.0"', '     .AddDispersionFittingValueMu "9.12", "0.9688", "0", "1.0"', '     .AddDispersionFittingValueMu "9.2", "0.9685", "0", "1.0"', '     .AddDispersionFittingValueMu "9.28", "0.9683", "0", "1.0"', '     .AddDispersionFittingValueMu "9.36", "0.969", "0", "1.0"', '     .AddDispersionFittingValueMu "9.44", "0.9675", "0", "1.0"', '     .AddDispersionFittingValueMu "9.52", "0.968", "0", "1.0"', '     .AddDispersionFittingValueMu "9.6", "0.9669", "0", "1.0"', '     .AddDispersionFittingValueMu "9.68", "0.966", "0", "1.0"', '     .AddDispersionFittingValueMu "9.76", "0.9652", "0", "1.0"', '     .AddDispersionFittingValueMu "9.84", "0.9659", "0", "1.0"', '     .AddDispersionFittingValueMu "9.92", "0.9661", "0", "1.0"', '     .AddDispersionFittingValueMu "10", "0.9661", "0", "1.0"', '     .AddDispersionFittingValueMu "10.08", "0.9669", "0", "1.0"', '     .AddDispersionFittingValueMu "10.16", "0.9675", "0", "1.0"', '     .AddDispersionFittingValueMu "10.24", "0.9667", "0", "1.0"', '     .AddDispersionFittingValueMu "10.32", "0.9655", "0", "1.0"', '     .AddDispersionFittingValueMu "10.4", "0.9632", "0", "1.0"', '     .AddDispersionFittingValueMu "10.48", "0.9631", "0", "1.0"', '     .AddDispersionFittingValueMu "10.56", "0.9614", "0", "1.0"', '     .AddDispersionFittingValueMu "10.64", "0.9598", "0", "1.0"', '     .AddDispersionFittingValueMu "10.72", "0.958", "0", "1.0"', '     .AddDispersionFittingValueMu "10.8", "0.9568", "0", "1.0"', '     .AddDispersionFittingValueMu "10.88", "0.9562", "0", "1.0"', '     .AddDispersionFittingValueMu "10.96", "0.9556", "0", "1.0"', '     .AddDispersionFittingValueMu "11.04", "0.9567", "0", "1.0"', '     .AddDispersionFittingValueMu "11.12", "0.9565", "0", "1.0"', '     .AddDispersionFittingValueMu "11.2", "0.9554", "0", "1.0"', '     .AddDispersionFittingValueMu "11.28", "0.9549", "0", "1.0"', '     .AddDispersionFittingValueMu "11.36", "0.9529", "0", "1.0"', '     .AddDispersionFittingValueMu "11.44", "0.9531", "0", "1.0"', '     .AddDispersionFittingValueMu "11.52", "0.9491", "0", "1.0"', '     .AddDispersionFittingValueMu "11.6", "0.9489", "0", "1.0"', '     .AddDispersionFittingValueMu "11.68", "0.9477", "0", "1.0"', '     .AddDispersionFittingValueMu "11.76", "0.9469", "0", "1.0"', '     .AddDispersionFittingValueMu "11.84", "0.9464", "0", "1.0"', '     .AddDispersionFittingValueMu "11.92", "0.9459", "0", "1.0"', '     .AddDispersionFittingValueMu "12", "0.9456", "0", "1.0"', '     .AddDispersionFittingValueMu "12.08", "0.9436", "0", "1.0"', '     .AddDispersionFittingValueMu "12.16", "0.9437", "0", "1.0"', '     .AddDispersionFittingValueMu "12.24", "0.9423", "0", "1.0"', '     .AddDispersionFittingValueMu "12.32", "0.9408", "0", "1.0"', '     .AddDispersionFittingValueMu "12.4", "0.9373", "0", "1.0"', '     .AddDispersionFittingValueMu "12.48", "0.9343", "0", "1.0"', '     .AddDispersionFittingValueMu "12.56", "0.9319", "0", "1.0"', '     .AddDispersionFittingValueMu "12.64", "0.9305", "0", "1.0"', '     .AddDispersionFittingValueMu "12.72", "0.9282", "0", "1.0"', '     .AddDispersionFittingValueMu "12.8", "0.9269", "0", "1.0"', '     .AddDispersionFittingValueMu "12.88", "0.9247", "0", "1.0"', '     .AddDispersionFittingValueMu "12.96", "0.9225", "0", "1.0"', '     .AddDispersionFittingValueMu "13.04", "0.9204", "0", "1.0"', '     .AddDispersionFittingValueMu "13.12", "0.9194", "0", "1.0"', '     .AddDispersionFittingValueMu "13.2", "0.9173", "0", "1.0"', '     .AddDispersionFittingValueMu "13.28", "0.912", "0", "1.0"', '     .AddDispersionFittingValueMu "13.36", "0.91", "0", "1.0"', '     .AddDispersionFittingValueMu "13.44", "0.9065", "0", "1.0"', '     .AddDispersionFittingValueMu "13.52", "0.9037", "0", "1.0"', '     .AddDispersionFittingValueMu "13.6", "0.8986", "0", "1.0"', '     .AddDispersionFittingValueMu "13.68", "0.9007", "0", "1.0"', '     .AddDispersionFittingValueMu "13.76", "0.8974", "0", "1.0"', '     .AddDispersionFittingValueMu "13.84", "0.8986", "0", "1.0"', '     .AddDispersionFittingValueMu "13.92", "0.8982", "0", "1.0"', '     .AddDispersionFittingValueMu "14", "0.8984", "0", "1.0"', '     .AddDispersionFittingValueMu "14.08", "0.8966", "0", "1.0"', '     .AddDispersionFittingValueMu "14.16", "0.8941", "0", "1.0"', '     .AddDispersionFittingValueMu "14.24", "0.8987", "0", "1.0"', '     .AddDispersionFittingValueMu "14.32", "0.8968", "0", "1.0"', '     .AddDispersionFittingValueMu "14.4", "0.8986", "0", "1.0"', '     .AddDispersionFittingValueMu "14.48", "0.8941", "0", "1.0"', '     .AddDispersionFittingValueMu "14.56", "0.8983", "0", "1.0"', '     .AddDispersionFittingValueMu "14.64", "0.8968", "0", "1.0"', '     .AddDispersionFittingValueMu "14.72", "0.8988", "0", "1.0"', '     .AddDispersionFittingValueMu "14.8", "0.8985", "0", "1.0"', '     .AddDispersionFittingValueMu "14.88", "0.9016", "0", "1.0"', '     .AddDispersionFittingValueMu "14.96", "0.9051", "0", "1.0"', '     .AddDispersionFittingValueMu "15.04", "0.9059", "0", "1.0"', '     .AddDispersionFittingValueMu "15.12", "0.91", "0", "1.0"', '     .AddDispersionFittingValueMu "15.2", "0.9094", "0", "1.0"', '     .AddDispersionFittingValueMu "15.28", "0.9123", "0", "1.0"', '     .AddDispersionFittingValueMu "15.36", "0.9161", "0", "1.0"', '     .AddDispersionFittingValueMu "15.44", "0.9275", "0", "1.0"', '     .AddDispersionFittingValueMu "15.52", "0.9296", "0", "1.0"', '     .AddDispersionFittingValueMu "15.6", "0.928", "0", "1.0"', '     .AddDispersionFittingValueMu "15.68", "0.9273", "0", "1.0"', '     .AddDispersionFittingValueMu "15.76", "0.9338", "0", "1.0"', '     .AddDispersionFittingValueMu "15.84", "0.9409", "0", "1.0"', '     .AddDispersionFittingValueMu "15.92", "0.951", "0", "1.0"', '     .AddDispersionFittingValueMu "16", "0.9583", "0", "1.0"', '     .AddDispersionFittingValueMu "16.08", "0.96", "0", "1.0"', '     .AddDispersionFittingValueMu "16.16", "0.9722", "0", "1.0"', '     .AddDispersionFittingValueMu "16.24", "0.9804", "0", "1.0"', '     .AddDispersionFittingValueMu "16.32", "0.9909", "0", "1.0"', '     .AddDispersionFittingValueMu "16.4", "0.9968", "0", "1.0"', '     .AddDispersionFittingValueMu "16.48", "1.0015", "0", "1.0"', '     .AddDispersionFittingValueMu "16.56", "1.0084", "0", "1.0"', '     .AddDispersionFittingValueMu "16.64", "1.01", "0", "1.0"', '     .AddDispersionFittingValueMu "16.72", "1.0235", "0", "1.0"', '     .AddDispersionFittingValueMu "16.8", "1.0223", "0", "1.0"', '     .AddDispersionFittingValueMu "16.88", "1.0357", "0", "1.0"', '     .AddDispersionFittingValueMu "16.96", "1.0462", "0", "1.0"', '     .AddDispersionFittingValueMu "17.04", "1.0646", "0", "1.0"', '     .AddDispersionFittingValueMu "17.12", "1.0701", "0", "1.0"', '     .AddDispersionFittingValueMu "17.2", "1.0817", "0", "1.0"', '     .AddDispersionFittingValueMu "17.28", "1.0851", "0", "1.0"', '     .AddDispersionFittingValueMu "17.36", "1.0943", "0", "1.0"', '     .AddDispersionFittingValueMu "17.44", "1.1044", "0", "1.0"', '     .AddDispersionFittingValueMu "17.52", "1.1121", "0", "1.0"', '     .AddDispersionFittingValueMu "17.6", "1.1128", "0", "1.0"', '     .AddDispersionFittingValueMu "17.68", "1.116", "0", "1.0"', '     .AddDispersionFittingValueMu "17.76", "1.1188", "0", "1.0"', '     .AddDispersionFittingValueMu "17.84", "1.1259", "0", "1.0"', '     .AddDispersionFittingValueMu "17.92", "1.1437", "0", "1.0"', '     .AddDispersionFittingValueMu "18", "1.1512", "0", "1.0"', '     .UseGeneralDispersionMu "True"', '     .NLAnisotropy "False"', '     .NLAStackingFactor "1"', '     .NLADirectionX "1"', '     .NLADirectionY "0"', '     .NLADirectionZ "0"', '     .Colour "0", "1", "1" ', '     .Wireframe "False" ', '     .Reflection "False" ', '     .Allowoutline "True" ', '     .Transparentoutline "False" ', '     .Transparency "0" ', '     .Create', 'End With']
    sCommand = link.join(sCommand)
    pj.model3d.add_to_history("define material: GAOSHANG", sCommand)


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

def etch_to_I_shape_fixedcaps(p, h, w1, w2, cap_ratio):
    tx = SUBSTRATE_X_THICKNESS
    ty = SUBSTRATE_Y_THICKNESS
    df = FILM_DRAW_THICKNESS

    wx = min(w1, p - 0.2)
    wy = min(w2, p - 0.2)

    cap_h = cap_ratio * h
    z1 = cap_h
    z2 = h - cap_h

    if z2 <= z1:
        z1 = 0.35 * h
        z2 = 0.65 * h

    s1 = f'''
With Brick
     .Reset
     .Name "etch_x_left_mid"
     .Component "component1"
     .Material "Vacuum"
     .Xrange "-{p/2}", "-{wx/2}"
     .Yrange "{tx/2}", "{tx/2 + df}"
     .Zrange "{z1}", "{z2}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: etch_x_left_mid", s1)

    s2 = f'''
With Brick
     .Reset
     .Name "etch_x_right_mid"
     .Component "component1"
     .Material "Vacuum"
     .Xrange "{wx/2}", "{p/2}"
     .Yrange "{tx/2}", "{tx/2 + df}"
     .Zrange "{z1}", "{z2}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: etch_x_right_mid", s2)

    s3 = f'''
With Brick
     .Reset
     .Name "etch_y_bottom_mid"
     .Component "component1"
     .Material "Vacuum"
     .Xrange "{ty/2}", "{ty/2 + df}"
     .Yrange "-{p/2}", "-{wy/2}"
     .Zrange "{z1}", "{z2}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: etch_y_bottom_mid", s3)

    s4 = f'''
With Brick
     .Reset
     .Name "etch_y_top_mid"
     .Component "component1"
     .Material "Vacuum"
     .Xrange "{ty/2}", "{ty/2 + df}"
     .Yrange "{wy/2}", "{p/2}"
     .Zrange "{z1}", "{z2}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: etch_y_top_mid", s4)

    s5 = '''
Solid.Subtract "component1:film_x_full", "component1:etch_x_left_mid"
Solid.Subtract "component1:film_x_full", "component1:etch_x_right_mid"
Solid.Subtract "component1:film_y_full", "component1:etch_y_bottom_mid"
Solid.Subtract "component1:film_y_full", "component1:etch_y_top_mid"
'''
    pj.model3d.add_to_history("etch film to I-shape", s5)

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
        f'     .MeshAdaptionTet "{str(USE_MESH_ADAPTION_FOR_GA)}"',
        '     .StoreAllResults "False"',
        '     .StoreResultsInCache "False"',
        '     .UseDoublePrecision "False"',
        '     .UseParallelization "True"',
        '     .MaxCPUs "1024"',
        '     .MaximumNumberOfCPUDevices "2"',
        '     .RemoveAllStopCriteria "Tet"',
        '     .AddStopCriterion "All S-Parameters", "0.02", "2", "Tet", "True"',
        f'     .SetNumberOfResultDataSamples "{RESULT_DATA_SAMPLES}"',
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


def create_cross_with_endcaps(material, p, w1, w2, h1, h2, e):
    # 横向主条
    s1 = f'''
With Brick
     .Reset
     .Name "film1"
     .Component "component1"
     .Material "{material}"
     .Xrange "-{p/2}", "{p/2}"
     .Yrange "-{w1/2}", "{w1/2}"
     .Zrange "0", "{h1}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: film1", s1)

    # 纵向主条
    s2 = f'''
With Brick
     .Reset
     .Name "film2"
     .Component "component1"
     .Material "{material}"
     .Xrange "-{w2/2}", "{w2/2}"
     .Yrange "-{p/2}", "{p/2}"
     .Zrange "0", "{h2}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: film2", s2)

    # 横向左端帽
    s3 = f'''
With Brick
     .Reset
     .Name "cap_left"
     .Component "component1"
     .Material "{material}"
     .Xrange "-{p/2}", "-{p/2 - e}"
     .Yrange "-{e/2}", "{e/2}"
     .Zrange "0", "{h1}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: cap_left", s3)

    # 横向右端帽
    s4 = f'''
With Brick
     .Reset
     .Name "cap_right"
     .Component "component1"
     .Material "{material}"
     .Xrange "{p/2 - e}", "{p/2}"
     .Yrange "-{e/2}", "{e/2}"
     .Zrange "0", "{h1}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: cap_right", s4)

    # 纵向上端帽
    s5 = f'''
With Brick
     .Reset
     .Name "cap_top"
     .Component "component1"
     .Material "{material}"
     .Xrange "-{e/2}", "{e/2}"
     .Yrange "{p/2 - e}", "{p/2}"
     .Zrange "0", "{h2}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: cap_top", s5)

    # 纵向下端帽
    s6 = f'''
With Brick
     .Reset
     .Name "cap_bottom"
     .Component "component1"
     .Material "{material}"
     .Xrange "-{e/2}", "{e/2}"
     .Yrange "-{p/2}", "-{p/2 - e}"
     .Zrange "0", "{h2}"
     .Create
End With
'''
    pj.model3d.add_to_history("define brick: cap_bottom", s6)

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
def bits_to_int(bits):
    return int("".join(str(int(b)) for b in bits), 2)


def clamp_int(v, lo, hi):
    return max(lo, min(hi, int(v)))


def build_y_mask_template(frame_w, window_w, window_h, bridge_w, slot_type, template_type):
    """生成 12x12 Y 向片阻模板。

    Y 膜在前期场分布中承担主要欧姆损耗，因此模板以“大外框 + 中央窗口 + 桥接通道”
    为核心，用于增加低频长电流路径，同时通过边缘槽调节高频端阻抗匹配。
    """
    n = TOPOLOGY_N
    m = np.ones((n, n), dtype=int)

    frame_w = clamp_int(frame_w, 1, 4)
    bridge_w = clamp_int(bridge_w, 1, 4)
    window_w = clamp_int(window_w, 2, 9)
    window_h = clamp_int(window_h, 2, 9)

    # 中央矩形窗口。先挖空，再恢复中心竖向/横向桥。
    cx = n // 2
    cy = n // 2
    x0 = clamp_int(cx - window_w // 2, frame_w, n - frame_w - 1)
    x1 = clamp_int(x0 + window_w, frame_w + 1, n - frame_w)
    y0 = clamp_int(cy - window_h // 2, frame_w, n - frame_w - 1)
    y1 = clamp_int(y0 + window_h, frame_w + 1, n - frame_w)
    m[y0:y1, x0:x1] = 0

    # 恢复外框。
    m[:frame_w, :] = 1
    m[-frame_w:, :] = 1
    m[:, :frame_w] = 1
    m[:, -frame_w:] = 1

    # 中心桥，保证长路径连通，避免形成过多孤立岛。
    bx0 = clamp_int(cx - bridge_w // 2, 0, n - 1)
    bx1 = clamp_int(bx0 + bridge_w, 1, n)
    by0 = clamp_int(cy - bridge_w // 2, 0, n - 1)
    by1 = clamp_int(by0 + bridge_w, 1, n)
    m[:, bx0:bx1] = 1
    m[by0:by1, :] = 1

    # 按模板类型添加侧向窗口/保留块，形成多尺度电流路径。
    if template_type == 0:
        # 接近 9x9 最终结构：四个侧窗 + 中央桥。
        pass
    elif template_type == 1:
        # 更强外框，减小中心窗口，利于低频。
        pad = 2
        m[pad:pad+2, pad:pad+2] = 0
        m[pad:pad+2, n-pad-2:n-pad] = 0
        m[n-pad-2:n-pad, pad:pad+2] = 0
        m[n-pad-2:n-pad, n-pad-2:n-pad] = 0
    elif template_type == 2:
        # 增强上下横向损耗带。
        m[2:4, :] = 1
        m[n-4:n-2, :] = 1
        m[2:4, 3:n-3] = 0
        m[n-4:n-2, 3:n-3] = 0
        m[2:4, bx0:bx1] = 1
        m[n-4:n-2, bx0:bx1] = 1
    else:
        # 稍微稀疏：扩大侧向窗口，避免整体过密导致高频端变差。
        m[2:4, 2:5] = 0
        m[2:4, n-5:n-2] = 0
        m[n-4:n-2, 2:5] = 0
        m[n-4:n-2, n-5:n-2] = 0

    # 边缘槽：通过对称缺口调节高频端。
    st = int(slot_type) % 8
    slot_len = 2 + (st % 3)  # 2--4
    if st in [1, 3, 5, 7]:
        # 上下边中心开槽，但不破坏中心桥。
        c0 = max(frame_w, cx - slot_len // 2)
        c1 = min(n - frame_w, c0 + slot_len)
        m[:frame_w, c0:c1] = 0
        m[-frame_w:, c0:c1] = 0
    if st in [2, 3, 6, 7]:
        # 左右边中心开槽。
        r0 = max(frame_w, cy - slot_len // 2)
        r1 = min(n - frame_w, r0 + slot_len)
        m[r0:r1, :frame_w] = 0
        m[r0:r1, -frame_w:] = 0
    if st in [4, 5, 6, 7]:
        # 四角附近小槽，增加边缘多谐振。
        m[frame_w:frame_w+1, frame_w+1:frame_w+3] = 0
        m[frame_w:frame_w+1, n-frame_w-3:n-frame_w-1] = 0
        m[n-frame_w-1:n-frame_w, frame_w+1:frame_w+3] = 0
        m[n-frame_w-1:n-frame_w, n-frame_w-3:n-frame_w-1] = 0

    # 再次保证中心桥与外框基础连通。
    m[:, bx0:bx1] = 1
    m[by0:by1, :] = 1
    return m.astype(int).tolist()


def build_x_mask_template(strip_w, gap_w, end_load, vert_offset, template_type):
    """生成 12x12 X 向片阻模板。

    X 膜主要用于耦合和阻抗修正。模板采用中部横向侧块/条带，并允许中央开缝、
    端部加载和轻微垂直偏移，以调节高频端和主谐振位置。
    """
    n = TOPOLOGY_N
    m = np.zeros((n, n), dtype=int)

    strip_w = clamp_int(strip_w, 1, 4)
    gap_w = clamp_int(gap_w, 0, 8)
    end_load = clamp_int(end_load, 0, 3)
    offset_map = {0: -1, 1: 0, 2: 1, 3: 2}
    off = offset_map.get(int(vert_offset) % 4, 0)

    cy = n // 2 + off
    r0 = clamp_int(cy - strip_w // 2, 0, n - 1)
    r1 = clamp_int(r0 + strip_w, 1, n)

    if gap_w <= 0:
        m[r0:r1, :] = 1
    else:
        cx = n // 2
        g0 = clamp_int(cx - gap_w // 2, 1, n - 1)
        g1 = clamp_int(g0 + gap_w, 1, n - 1)
        m[r0:r1, :g0] = 1
        m[r0:r1, g1:] = 1

    # 端部加载：增加等效电长度，有利于低频，但保持中心开缝。
    if end_load >= 1:
        rr0 = max(0, r0 - 1)
        rr1 = min(n, r1 + 1)
        m[rr0:rr1, :2] = 1
        m[rr0:rr1, -2:] = 1
    if end_load >= 2:
        rr0 = max(0, r0 - 2)
        rr1 = min(n, r1 + 2)
        m[rr0:rr1, :1] = 1
        m[rr0:rr1, -1:] = 1
    if end_load >= 3:
        # 添加上下次级短条带，增加高频耦合通道。
        if r0 - 3 >= 0:
            m[r0-3:r0-2, 2:n-2] = 1
        if r1 + 2 <= n:
            m[r1+1:r1+2, 2:n-2] = 1

    if template_type == 1:
        # 轻微增加中心两侧加载。
        mid = n // 2
        m[max(0, r0-1):min(n, r1+1), mid-3:mid-2] = 1
        m[max(0, r0-1):min(n, r1+1), mid+2:mid+3] = 1
    elif template_type == 2:
        # 更稀疏，保留左右端块，降低过强高频反射风险。
        mid = n // 2
        m[:, mid-1:mid+1] = 0
    elif template_type == 3:
        # 双条带结构。
        if r0 - 2 >= 0:
            m[r0-2:r0-1, :max(1, n//2-gap_w//2)] = 1
            m[r0-2:r0-1, min(n-1, n//2+gap_w//2):] = 1
        if r1 + 1 <= n:
            m[r1:r1+1, :max(1, n//2-gap_w//2)] = 1
            m[r1:r1+1, min(n-1, n//2+gap_w//2):] = 1

    return m.astype(int).tolist()


def flatten_mask(mask):
    return [int(v) for row in mask for v in row]


def template_params_from_individual(individual):
    bits = [int(x) for x in individual]
    if len(bits) != dna_size:
        raise ValueError(f"Invalid DNA length: got {len(bits)}, expected {dna_size}")

    p_raw = bits_to_int(bits[0:6])
    h_raw = bits_to_int(bits[6:12])
    p = P_MIN + p_raw / 63.0 * (P_MAX - P_MIN)
    h = H_MIN + h_raw / 63.0 * (H_MAX - H_MIN)

    template_type = bits_to_int(bits[12:14])
    y_frame_w = 1 + bits_to_int(bits[14:16])                 # 1--4
    y_window_w = 2 + bits_to_int(bits[16:19])                # 2--9
    y_window_h = 2 + bits_to_int(bits[19:22])                # 2--9
    y_bridge_w = 1 + bits_to_int(bits[22:24])                # 1--4
    y_slot_type = bits_to_int(bits[24:27])                   # 0--7
    x_strip_w = 1 + bits_to_int(bits[27:29])                 # 1--4
    x_gap_w = bits_to_int(bits[29:32])                       # 0--7
    x_end_load = bits_to_int(bits[32:34])                    # 0--3
    x_vert_offset = bits_to_int(bits[34:36])                 # 0--3

    return {
        "p": round(p, 4),
        "h": round(h, 4),
        "template_type": template_type,
        "y_frame_w": y_frame_w,
        "y_window_w": y_window_w,
        "y_window_h": y_window_h,
        "y_bridge_w": y_bridge_w,
        "y_slot_type": y_slot_type,
        "x_strip_w": x_strip_w,
        "x_gap_w": x_gap_w,
        "x_end_load": x_end_load,
        "x_vert_offset": x_vert_offset,
    }


def decode(individual):
    """解码模板化个体，返回 p、h 以及两个完整 12x12 mask 的一维展开列表。"""
    params = template_params_from_individual(individual)
    mask_x = build_x_mask_template(
        strip_w=params["x_strip_w"],
        gap_w=params["x_gap_w"],
        end_load=params["x_end_load"],
        vert_offset=params["x_vert_offset"],
        template_type=params["template_type"],
    )
    mask_y = build_y_mask_template(
        frame_w=params["y_frame_w"],
        window_w=params["y_window_w"],
        window_h=params["y_window_h"],
        bridge_w=params["y_bridge_w"],
        slot_type=params["y_slot_type"],
        template_type=params["template_type"],
    )
    return params["p"], params["h"], flatten_mask(mask_x), flatten_mask(mask_y)


def expand_seed_to_mask(seed):
    """兼容旧接口。

    模板模式下 decode() 已经返回完整 12x12 mask 的一维展开列表；
    如果传入长度为 144，则直接还原为 12x12 矩阵。
    若传入长度为 36，则仍按 6x6 seed 镜像扩展。
    """
    if len(seed) == TOPOLOGY_N * TOPOLOGY_N:
        return [list(map(int, seed[i * TOPOLOGY_N:(i + 1) * TOPOLOGY_N])) for i in range(TOPOLOGY_N)]

    if len(seed) != SEED_BITS_PER_LAYER:
        raise ValueError(f"Topology requires full {TOPOLOGY_N}x{TOPOLOGY_N} mask or {SEED_N}x{SEED_N} seed, got length {len(seed)}")

    seed_rows = [seed[i * SEED_N:(i + 1) * SEED_N] for i in range(SEED_N)]
    if TOPOLOGY_N == 2 * SEED_N:
        top_rows = [row + row[::-1] for row in seed_rows]
        mask = top_rows + top_rows[::-1]
    elif TOPOLOGY_N == 2 * SEED_N - 1:
        top_rows = [row + row[-2::-1] for row in seed_rows]
        mask = top_rows + top_rows[-2::-1]
    else:
        raise ValueError(f"Unsupported topology/seed combination: N={TOPOLOGY_N}, SEED_N={SEED_N}")
    return mask


def template_summary(individual):
    try:
        p = template_params_from_individual(individual)
        return ", ".join(f"{k}={v}" for k, v in p.items())
    except Exception:
        return ""

def bitstring(individual):
    return "".join(str(int(x)) for x in individual)


def mask_to_compact_string(mask):
    return "/".join("".join(str(int(v)) for v in row) for row in mask)


def count_isolated_pixels(mask):
    """统计 4 邻域意义下的孤立保留像素。"""
    n = len(mask)
    m = len(mask[0]) if n else 0
    iso = 0
    for i in range(n):
        for j in range(m):
            if mask[i][j] != 1:
                continue
            has_neighbor = False
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ii, jj = i + di, j + dj
                if 0 <= ii < n and 0 <= jj < m and mask[ii][jj] == 1:
                    has_neighbor = True
                    break
            if not has_neighbor:
                iso += 1
    return iso


def count_connected_components(mask):
    """统计 4 邻域连通分量数，用于过滤过碎图案。"""
    n = len(mask)
    m = len(mask[0]) if n else 0
    visited = [[False] * m for _ in range(n)]
    comp = 0

    for i in range(n):
        for j in range(m):
            if mask[i][j] != 1 or visited[i][j]:
                continue
            comp += 1
            stack = [(i, j)]
            visited[i][j] = True
            while stack:
                x, y = stack.pop()
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < n and 0 <= yy < m and (not visited[xx][yy]) and mask[xx][yy] == 1:
                        visited[xx][yy] = True
                        stack.append((xx, yy))
    return comp


def mask_quality_report(mask):
    kept = int(sum(sum(row) for row in mask))
    isolated = count_isolated_pixels(mask)
    components = count_connected_components(mask)
    return {
        "kept": kept,
        "isolated": isolated,
        "components": components,
    }


def prefilter_individual(individual):
    """
    在进入 CST 前过滤明显不适合表面 Ohmic Sheet 求解的坏图案。
    返回: (ok, reason, report_dict)
    """
    if not ENABLE_MASK_PREFILTER:
        p, h, sx, sy = decode(individual)
        mx = expand_seed_to_mask(sx)
        my = expand_seed_to_mask(sy)
        return True, "prefilter_disabled", {
            "p": p, "h": h, "mask_x": mx, "mask_y": my,
            "x": mask_quality_report(mx), "y": mask_quality_report(my),
        }

    p, h, sx, sy = decode(individual)
    mx = expand_seed_to_mask(sx)
    my = expand_seed_to_mask(sy)
    rx = mask_quality_report(mx)
    ry = mask_quality_report(my)
    total = rx["kept"] + ry["kept"]

    reasons = []
    for label, r in [("X", rx), ("Y", ry)]:
        if r["kept"] < MIN_KEPT_PIXELS_PER_LAYER:
            reasons.append(f"{label}_too_few_kept={r['kept']}")
        if r["kept"] > MAX_KEPT_PIXELS_PER_LAYER:
            reasons.append(f"{label}_too_many_kept={r['kept']}")
        if r["isolated"] > MAX_ISOLATED_PIXELS_PER_LAYER:
            reasons.append(f"{label}_too_many_isolated={r['isolated']}")
        if r["components"] > MAX_CONNECTED_COMPONENTS_PER_LAYER:
            reasons.append(f"{label}_too_many_components={r['components']}")

    if total < MIN_TOTAL_KEPT_PIXELS:
        reasons.append(f"total_too_few_kept={total}")
    if total > MAX_TOTAL_KEPT_PIXELS:
        reasons.append(f"total_too_many_kept={total}")

    report = {
        "p": p, "h": h,
        "mask_x_seed": sx, "mask_y_seed": sy,
        "mask_x": mx, "mask_y": my,
        "x": rx, "y": ry, "total_kept": total,
    }

    if reasons:
        return False, ";".join(reasons), report
    return True, "ok", report


def log_individual_trace(generation, index, status, individual, reason="", report=None, metrics=None, cst_file=""):
    """记录每个个体的状态，便于定位卡住的 CST 个体。"""
    try:
        p, h, sx, sy = decode(individual)
        mx = expand_seed_to_mask(sx)
        my = expand_seed_to_mask(sy)
        if report is None:
            report = {
                "x": mask_quality_report(mx),
                "y": mask_quality_report(my),
                "total_kept": int(sum(sum(r) for r in mx) + sum(sum(r) for r in my)),
            }
        metric_str = ""
        if metrics is not None:
            metric_str = (
                f"	score={metrics.get('score', '')}"
                f"	bandwidth={metrics.get('bandwidth', '')}"
                f"	min_rl={metrics.get('min_rl', '')}"
            )
        line = (
            f"gen={generation}	idx={index}	status={status}	reason={reason}	"
            f"bitstring={bitstring(individual)}	template={template_summary(individual)}	p={p}	h={h}	"
            f"mask_x_seed={sx}	mask_y_seed={sy}	"
            f"mask_x={mask_to_compact_string(mx)}	mask_y={mask_to_compact_string(my)}	"
            f"x_report={report.get('x')}	y_report={report.get('y')}	"
            f"total_kept={report.get('total_kept')}	cst_file={cst_file}{metric_str}\n"
        )
        with open(INDIVIDUAL_TRACE_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        with open(INDIVIDUAL_TRACE_FILE, "a", encoding="utf-8") as f:
            f.write(f"gen={generation}\tidx={index}\tstatus=trace_failed\terror={repr(e)}\n")


def etch_mask_x_12x12(p, h, mask6):
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
def etch_mask_y_12x12(p, h, mask6):
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



# =========================================================
# 分支1新增：直接按 mask 创建片阻层图案，不再先全覆盖再布尔刻蚀
# =========================================================
def _add_sheet_to_meshgroup_if_needed(sheet_name):
    """把生成的 sheet 对象加入 meshgroup1。该步骤不是必需的，但与你手动测试的 History 保持一致。"""
    if not ADD_SHEET_TO_MESHGROUP:
        return

    s = f'''
On Error Resume Next
Group.New "{MESHGROUP_NAME}"
Group.AddItem "solid$component1:{sheet_name}", "{MESHGROUP_NAME}"
On Error GoTo 0
'''
    pj.model3d.add_to_history(f"add sheet to mesh group: {sheet_name}", s)


def _delete_helper_solid(helper_name):
    """删除用于取面的临时辅助实体。"""
    s = f'''
On Error Resume Next
Pick.ClearAllPicks
Solid.Delete "component1:{helper_name}"
On Error GoTo 0
'''
    pj.model3d.add_to_history(f"delete helper solid: {helper_name}", s)


def _create_ohmic_sheet_from_helper_face(sheet_name, helper_name, material, face_id):
    """从临时辅助实体的指定 face 生成 Ohmic Sheet 面对象。"""
    # 这是根据你在 CST 2025 History List 第12行获得的核心命令改写的：
    # Solid.CreateShapeFromFaces "solid2", "component1", "material1"
    s = f'''
Pick.ClearAllPicks
Pick.PickFaceFromId "component1:{helper_name}", "{face_id}"
Solid.CreateShapeFromFaces "{sheet_name}", "component1", "{material}"
Pick.ClearAllPicks
'''
    pj.model3d.add_to_history(f"make ohmic sheet from helper face: {sheet_name}", s)
    _add_sheet_to_meshgroup_if_needed(sheet_name)
    _delete_helper_solid(helper_name)


def create_surface_sheet_pixel_x(name, material, x1, x2, z1, z2):
    """在 X 向 PET 切片的 +Y 表面创建一个二维片阻像素。

    方法：
    1. 在 PET 表面内侧创建一个极薄的临时辅助 brick；
    2. 选中该 brick 的 +Y face；
    3. 用 Solid.CreateShapeFromFaces 生成真正的 Ohmic Sheet；
    4. 删除临时辅助 brick。

    最终保留下来的对象是 sheet，不是有厚度实体膜。
    """
    y0 = SUBSTRATE_X_THICKNESS / 2.0
    eps = HELPER_BRICK_THICKNESS
    helper_name = f"helper_{name}"

    # 为了让 +Y face 正好落在 PET 表面 y=y0，辅助 brick 放在 y0-eps 到 y0。
    s_helper = f'''
With Brick
     .Reset
     .Name "{helper_name}"
     .Component "component1"
     .Material "Vacuum"
     .Xrange "{x1}", "{x2}"
     .Yrange "{y0 - eps}", "{y0}"
     .Zrange "{z1}", "{z2}"
     .Create
End With
'''
    pj.model3d.add_to_history(f"create helper solid for x-sheet: {helper_name}", s_helper)
    _create_ohmic_sheet_from_helper_face(name, helper_name, material, FACE_ID_X_PLUS_Y)


def create_surface_sheet_pixel_y(name, material, y1, y2, z1, z2):
    """在 Y 向 PET 切片的 +X 表面创建一个二维片阻像素。

    方法：
    1. 在 PET 表面内侧创建一个极薄的临时辅助 brick；
    2. 选中该 brick 的 +X face；
    3. 用 Solid.CreateShapeFromFaces 生成真正的 Ohmic Sheet；
    4. 删除临时辅助 brick。

    最终保留下来的对象是 sheet，不是有厚度实体膜。
    """
    x0 = SUBSTRATE_Y_THICKNESS / 2.0
    eps = HELPER_BRICK_THICKNESS
    helper_name = f"helper_{name}"

    # 为了让 +X face 正好落在 PET 表面 x=x0，辅助 brick 放在 x0-eps 到 x0。
    s_helper = f'''
With Brick
     .Reset
     .Name "{helper_name}"
     .Component "component1"
     .Material "Vacuum"
     .Xrange "{x0 - eps}", "{x0}"
     .Yrange "{y1}", "{y2}"
     .Zrange "{z1}", "{z2}"
     .Create
End With
'''
    pj.model3d.add_to_history(f"create helper solid for y-sheet: {helper_name}", s_helper)
    _create_ohmic_sheet_from_helper_face(name, helper_name, material, FACE_ID_Y_PLUS_X)


def create_patterned_ohmic_sheet_film(p, h, mask_x, mask_y):
    '''按任意 N x N mask 直接生成保留区域的二维 Ohmic Sheet 片阻像素。默认 N=9。'''
    n_x = len(mask_x)
    n_y = len(mask_y)
    if n_x != n_y:
        raise ValueError(f"mask_x and mask_y must have the same size, got {n_x} and {n_y}")
    if n_x == 0 or any(len(row) != n_x for row in mask_x) or any(len(row) != n_y for row in mask_y):
        raise ValueError("mask_x/mask_y must be square matrices")

    n = n_x
    cell_x = p / float(n)
    cell_y = p / float(n)
    cell_z = h / float(n)

    idx = 0
    for i in range(n):
        for j in range(n):
            if mask_x[i][j] == 1:
                x1 = -p / 2 + j * cell_x
                x2 = x1 + cell_x
                z1 = i * cell_z
                z2 = z1 + cell_z
                create_surface_sheet_pixel_x(f"sheet_x_{idx}", FILM_X_SHEET_NAME, x1, x2, z1, z2)
                idx += 1

    idx = 0
    for i in range(n):
        for j in range(n):
            if mask_y[i][j] == 1:
                y1 = -p / 2 + j * cell_y
                y2 = y1 + cell_y
                z1 = i * cell_z
                z2 = z1 + cell_z
                create_surface_sheet_pixel_y(f"sheet_y_{idx}", FILM_Y_SHEET_NAME, y1, y2, z1, z2)
                idx += 1


def build_resistive_film_by_model_type(p, h, mask_x, mask_y, film_model_type):
    '''根据 film_model_type 建立电阻膜图案。'''
    if film_model_type == "thin_solid":
        create_resistive_film_material()
        create_full_cover_film(p, h)
        raise NotImplementedError("12x12 version is intended for ohmic_sheet model. Thin-solid etching is not used here.")
    elif film_model_type == "ohmic_sheet":
        create_ohmic_sheet_material()
        create_patterned_ohmic_sheet_film(p, h, mask_x, mask_y)
    else:
        raise ValueError(f"Unknown film_model_type: {film_model_type}")

#--------------------------------------------------------------------------------------------------------------------------
def _find_effective_intervals(freqs, rls, threshold=-10.0):
    below = rls <= threshold
    intervals = []
    start = None
    for i, ok in enumerate(below):
        if ok and start is None:
            start = i
        if (not ok or i == len(below) - 1) and start is not None:
            end = i - 1 if not ok else i
            if end >= start:
                intervals.append((start, end))
            start = None
    return intervals


def extract_metrics(cst_file):
    result = cst.results.ProjectFile(cst_file, allow_interactive=True)
    s11 = result.get_3d().get_result_item(r"1D Results\S-Parameters\SZmax(1),Zmax(1)")
    data = s11.get_data()

    freqs = []
    rls = []
    for row in data:
        if len(row) < 2:
            continue
        freq = float(row[0])
        mag = max(abs(row[1]), 1e-12)
        rl = 20 * np.log10(mag)
        freqs.append(freq)
        rls.append(float(rl))

    if not freqs:
        return {
            "score": 0.0, "bandwidth": 0.0, "coverage": 0.0, "min_rl": 0.0,
            "f_low": 0.0, "f_high": 0.0, "contiguous_bw": 0.0,
            "total_effective_bw": 0.0,
        }

    freqs = np.array(freqs, dtype=float)
    rls = np.array(rls, dtype=float)
    min_rl = float(np.min(rls))

    intervals = _find_effective_intervals(freqs, rls, threshold=-10.0)
    if intervals:
        best_start, best_end = max(intervals, key=lambda t: freqs[t[1]] - freqs[t[0]])
        f_low = float(freqs[best_start])
        f_high = float(freqs[best_end])
        contiguous_bw = max(0.0, f_high - f_low)
    else:
        f_low, f_high, contiguous_bw = 18.0, 2.0, 0.0

    # total_effective_bw 用点数估计，contiguous_bw 用最长连续区间估计。
    below = rls <= -10.0
    if len(freqs) > 1:
        df = float(np.mean(np.diff(freqs)))
    else:
        df = 0.0
    total_effective_bw = float(np.sum(below) * df)
    coverage = contiguous_bw / TARGET_TOTAL_BAND

    # 只在有效区间内计算平均吸收裕量，避免深谷奖励过强。
    if np.any(below):
        mean_margin = float(np.mean(np.maximum(0.0, -10.0 - rls[below])))
    else:
        mean_margin = 0.0

    # 评分重点：最长连续有效带宽、低频起点、高频端保持和 85% 目标奖励。
    score = 2.0 * contiguous_bw

    # 奖励低频边界下移。希望从 5.6 GHz 推向 4.4--5.0 GHz。
    if contiguous_bw > 0:
        score += 1.8 * max(0.0, 6.0 - f_low)
        if f_low <= 5.0:
            score += 2.5
        if f_low <= TARGET_LOW_EDGE + 0.25:
            score += 4.0

    # 惩罚高频端提前失效，鼓励一直延伸到 18 GHz 附近。
    if f_high >= 17.8:
        score += 2.5
    else:
        score -= 1.8 * max(0.0, 17.8 - f_high)

    # 达到或接近 85% 覆盖率给强奖励。
    if contiguous_bw >= TARGET_CONTIGUOUS_BW:
        score += 12.0 + 3.0 * (contiguous_bw - TARGET_CONTIGUOUS_BW)
    else:
        score += 1.0 * max(0.0, contiguous_bw - 12.3)

    # 吸收深度作为辅助，避免只追求 -10 dB 临界线；但不让深谷主导搜索。
    score += 0.05 * min(abs(min_rl), 45.0)
    score += 0.10 * min(mean_margin, 20.0)

    if contiguous_bw == 0:
        score = max(0.0, (-min_rl - 3.0) * 0.02)

    return {
        "score": float(score),
        "bandwidth": float(contiguous_bw),
        "coverage": float(coverage),
        "min_rl": float(min_rl),
        "f_low": float(f_low),
        "f_high": float(f_high),
        "contiguous_bw": float(contiguous_bw),
        "total_effective_bw": float(total_effective_bw),
        "mean_margin": float(mean_margin),
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
def remove_file_if_exists(path):
    """删除已经存在的文件，避免 CST 保存或复制时因为同名文件报错。"""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def make_run_tag():
    """生成短时间标签，让临时 CST 文件不重名。"""
    return time.strftime("%Y%m%d_%H%M%S") + f"_{random.randint(1000, 9999)}"

#--------------------------------------------------------------------------------------------------------------------------
def run_cst_for_params(p, h, mask_x_seed, mask_y_seed, film_model_type="thin_solid", cst_basename=None):
    '''对指定参数运行一次 CST 仿真。

    v4 修改：
    1. 每次运行使用不重名的临时 CST 文件，避免同名 .cst 已存在导致保存失败；
    2. 在关键步骤加入 stage 标记，若失败可从 error_log.txt 直接判断卡在哪一步。
    '''
    global pj
    stage = "new_mws"
    pj = None

    try:
        pj = safe_new_mws()

        stage = "template_and_materials"
        Type()
        create_pet_material()
        newc()

        stage = "expand_mask"
        mask_x = expand_seed_to_mask(mask_x_seed)
        mask_y = expand_seed_to_mask(mask_y_seed)

        print(
            f"Current parameters: "
            f"p={p:.4f}, h={h:.4f}, "
            f"film_model_type={film_model_type}, "
            f"mask_x_seed={mask_x_seed}, mask_y_seed={mask_y_seed}"
        )

        stage = "create_pet_substrates"
        create_pet_cross_substrates(p, h)

        stage = f"build_resistive_film_{film_model_type}"
        build_resistive_film_by_model_type(p, h, mask_x, mask_y, film_model_type)

        stage = "boundaries_and_solver_settings"
        set_ground_boundary()
        set_fast_solver()

        if cst_basename is None:
            cst_basename = f"temp_{film_model_type}_{make_run_tag()}.cst"
        cst_file = os.path.join(TEMP_DIR, cst_basename)
        remove_file_if_exists(cst_file)

        stage = "run_solver"
        print("Running CST solver...")
        pj.model3d.run_solver()

        stage = "save_cst_project"
        pj.save(cst_file)

        stage = "extract_metrics"
        metrics = extract_metrics(cst_file)
        return metrics, (p, h, mask_x_seed, mask_y_seed), cst_file

    except Exception as e:
        raise RuntimeError(
            f"CST run failed at stage='{stage}', film_model_type='{film_model_type}'. "
            f"Original error: {repr(e)}"
        ) from e

    finally:
        try:
            if pj is not None:
                pj.close()
        except Exception:
            pass


def run_cst(individual, film_model_type=None):
    '''保留原遗传算法接口：输入 72 bit individual，解码后调用 run_cst_for_params。'''
    if film_model_type is None:
        film_model_type = OPTIMIZATION_FILM_MODEL

    p, h, mask_x_seed, mask_y_seed = decode(individual)
    return run_cst_for_params(
        p=p,
        h=h,
        mask_x_seed=mask_x_seed,
        mask_y_seed=mask_y_seed,
        film_model_type=film_model_type,
    )


def int_to_bits(value, width):
    return [int(b) for b in format(value, f"0{width}b")]


def encode_template_params_to_individual(
    p=FIXED_P,
    h=FIXED_H,
    template_type=0,
    y_frame_w=1,
    y_window_w=6,
    y_window_h=7,
    y_bridge_w=2,
    y_slot_type=0,
    x_strip_w=3,
    x_gap_w=4,
    x_end_load=2,
    x_vert_offset=1,
):
    """把模板参数编码为 36 bit individual。"""
    p_raw = int(round((p - P_MIN) / (P_MAX - P_MIN) * 63.0))
    h_raw = int(round((h - H_MIN) / (H_MAX - H_MIN) * 63.0))
    p_raw = max(0, min(63, p_raw))
    h_raw = max(0, min(63, h_raw))

    vals = [
        (p_raw, 6),
        (h_raw, 6),
        (template_type, 2),
        (y_frame_w - 1, 2),
        (y_window_w - 2, 3),
        (y_window_h - 2, 3),
        (y_bridge_w - 1, 2),
        (y_slot_type, 3),
        (x_strip_w - 1, 2),
        (x_gap_w, 3),
        (x_end_load, 2),
        (x_vert_offset, 2),
    ]
    ind = []
    for value, width in vals:
        max_v = (1 << width) - 1
        value = max(0, min(max_v, int(value)))
        ind.extend(int_to_bits(value, width))
    if len(ind) != dna_size:
        raise ValueError(f"Encoded DNA length mismatch: {len(ind)} vs {dna_size}")
    return ind


def encode_params_to_individual(p, h, mask_x_seed=None, mask_y_seed=None):
    """兼容旧接口：模板版本忽略 mask_x_seed/mask_y_seed，只编码 p、h 和默认模板参数。"""
    return encode_template_params_to_individual(p=p, h=h)

def perturb_individual(individual, n_bits=2):
    child = individual.copy()
    idxs = random.sample(range(dna_size), k=min(n_bits, dna_size))
    for idx in idxs:
        child[idx] = 1 - child[idx]
    return child


def initialize_population(n):
    pop = []

    if SEED_POPULATION_WITH_FIXED_BEST:
        fixed_ind = encode_params_to_individual(
            FIXED_P,
            FIXED_H,
            FIXED_MASK_X_SEED,
            FIXED_MASK_Y_SEED,
        )
        pop.append(fixed_ind)

        # 加入多个围绕当前最优结构的局部扰动个体。
        # 只翻转 1 bit，优先保证图案不要突然变得过碎。
        trial = 0
        while len(pop) < min(n, 1 + SEED_PERTURB_COUNT) and trial < RANDOM_INDIVIDUAL_MAX_TRIALS:
            trial += 1
            child = perturb_individual(fixed_ind, SEED_PERTURB_BITS)
            ok, reason, report = prefilter_individual(child)
            if ok and child not in pop:
                pop.append(child)
            elif not ok:
                with open(SKIPPED_INDIVIDUAL_FILE, "a", encoding="utf-8") as f:
                    f.write(f"initial_seed_perturb_skipped\treason={reason}\tbitstring={bitstring(child)}\n")

    # 少量随机个体也要通过预筛选，避免 CST 被明显坏图案拖住。
    trial = 0
    while len(pop) < n and trial < RANDOM_INDIVIDUAL_MAX_TRIALS:
        trial += 1
        ind = [random.randint(0, 1) for _ in range(dna_size)]
        ok, reason, report = prefilter_individual(ind)
        if ok and ind not in pop:
            pop.append(ind)
        elif not ok:
            with open(SKIPPED_INDIVIDUAL_FILE, "a", encoding="utf-8") as f:
                f.write(f"initial_random_skipped\treason={reason}\tbitstring={bitstring(ind)}\n")

    # 如果筛选太严格导致数量不够，则用当前最优结构的扰动补齐。
    if SEED_POPULATION_WITH_FIXED_BEST:
        fixed_ind = encode_params_to_individual(FIXED_P, FIXED_H, FIXED_MASK_X_SEED, FIXED_MASK_Y_SEED)
        while len(pop) < n:
            child = perturb_individual(fixed_ind, 1)
            if child not in pop:
                pop.append(child)
    else:
        while len(pop) < n:
            ind = [random.randint(0, 1) for _ in range(dna_size)]
            if ind not in pop:
                pop.append(ind)

    return pop


def evaluate_individual(individual, generation=None, index=None):
    key = tuple(individual)
    if key in cache:
        metrics, params, cst_file = cache[key]
        log_individual_trace(generation, index, "cache_hit", individual, metrics=metrics, cst_file=cst_file)
        return cache[key]

    ok, reason, report = prefilter_individual(individual)
    if not ok:
        metrics = {"score": 0.0, "bandwidth": 0.0, "min_rl": 0.0}
        p, h, sx, sy = decode(individual)
        params = (p, h, sx, sy)
        cst_file = ""
        cache[key] = (metrics, params, cst_file)
        log_individual_trace(generation, index, "skipped_prefilter", individual, reason=reason, report=report, metrics=metrics)
        with open(SKIPPED_INDIVIDUAL_FILE, "a", encoding="utf-8") as f:
            f.write(f"gen={generation}\tidx={index}\treason={reason}\tbitstring={bitstring(individual)}\n")
        return cache[key]

    log_individual_trace(generation, index, "start_cst", individual, reason=reason, report=report)

    try:
        metrics, params, cst_file = run_cst(individual)
        log_individual_trace(generation, index, "finished_cst", individual, reason="ok", report=report, metrics=metrics, cst_file=cst_file)
    except Exception as e:
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"generation = {generation}, index = {index}\n")
            f.write(f"individual = {individual}\n")
            f.write(f"bitstring = {bitstring(individual)}\n")
            f.write(f"prefilter_report = {report}\n")
            f.write(repr(e) + "\n")
            f.write(traceback.format_exc() + "\n")

        metrics = {"score": 0.0, "bandwidth": 0.0, "min_rl": 0.0}
        p, h, sx, sy = decode(individual)
        params = (p, h, sx, sy)
        cst_file = ""
        log_individual_trace(generation, index, "failed_cst", individual, reason=repr(e), report=report, metrics=metrics)

    cache[key] = (metrics, params, cst_file)
    return cache[key]


def evaluate_population(pop, generation=None):
    fit_list = []
    info_list = []

    for idx, ind in enumerate(pop):
        print(f"\n--- Evaluating generation {generation}, individual {idx + 1}/{len(pop)} ---")
        print(f"bitstring = {bitstring(ind)}")
        metrics, params, cst_file = evaluate_individual(ind, generation=generation, index=idx)
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
    # 通用双点交叉，仍适用于当前 72 bit；之后扩展到 12x12 时也更方便复用。
    cross_point1 = random.randint(1, dna_size // 2 - 1)
    cross_point2 = random.randint(dna_size // 2, dna_size - 1)
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
    trial = 0
    while len(newpop) < pop_size and trial < RANDOM_INDIVIDUAL_MAX_TRIALS:
        trial += 1
        father = select_parent(pop, fit_list)
        mother = select_parent(pop, fit_list)
        child = crossover(father, mother)
        child = mutate(child, p_m)
        ok, reason, report = prefilter_individual(child)
        if ok and child not in newpop:
            newpop.append(child)
        elif not ok:
            with open(SKIPPED_INDIVIDUAL_FILE, "a", encoding="utf-8") as f:
                f.write(f"new_population_skipped\treason={reason}\tbitstring={bitstring(child)}\n")

    # 如果交叉/变异产生的合格新个体不足，则从精英附近做 1 bit 局部扰动补齐。
    while len(newpop) < pop_size:
        child = perturb_individual(elite, 1)
        ok, reason, report = prefilter_individual(child)
        if ok and child not in newpop:
            newpop.append(child)
        else:
            # 极端情况下允许重复精英，保证程序继续运行。
            if elite not in newpop or len(newpop) == 0:
                newpop.append(elite.copy())
            elif len(newpop) < pop_size:
                newpop.append(elite.copy())

    return newpop


def write_best_result(best_metrics, best_ind, best_params):
    with open(BEST_RESULT_FILE, "w", encoding="utf-8") as f:
        f.write(f"Best score: {best_metrics['score']}\n")
        f.write(f"Best contiguous bandwidth( RL<-10 dB ): {best_metrics['bandwidth']} GHz\n")
        f.write(f"Best coverage in 2-18 GHz: {best_metrics.get('coverage', 0.0) * 100.0} %\n")
        f.write(f"Best total effective bandwidth estimate: {best_metrics.get('total_effective_bw', 0.0)} GHz\n")
        f.write(f"Best low edge: {best_metrics.get('f_low', 0.0)} GHz\n")
        f.write(f"Best high edge: {best_metrics.get('f_high', 0.0)} GHz\n")
        f.write(f"Best min RL: {best_metrics['min_rl']} dB\n")
        f.write(f"Best individual: {best_ind}\n")
        f.write(f"Best template parameters: {template_summary(best_ind)}\n")
        f.write(f"Best parameters (p, h, mask_x_flatten, mask_y_flatten): {best_params}\n")
        f.write(f"Best CST file: {BEST_CST}\n")
        f.write(f"Best S11 txt file: {BEST_S11_FILE}\n")
        f.write(f"Best S11 png file: {BEST_S11_PNG}\n")

def optimize():
    pop = initialize_population(pop_size)

    best_metrics = {"score": -1.0, "bandwidth": 0.0, "min_rl": 0.0}
    best_ind = None
    best_params = None

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("iteration\tindividual\ttemplate\tscore\tbandwidth\tcoverage\tmin_rl\tf_low\tf_high\ttotal_effective_bw\tp\th\tmask_x_flatten\tmask_y_flatten\tcst_file\n")

    for it in range(iterations):
        current_pm = max(0.03, p_m_start - 0.008 * it)
        print(f"\n===== Iteration {it} =====")
        print(f"Current mutation rate = {current_pm:.3f}")

        fit_list, info_list = evaluate_population(pop, generation=it)

        for ind, fit, info in zip(pop, fit_list, info_list):
            metrics, params, cst_file = info
            print(
                f"score = {metrics['score']:.6f}, "
                f"bandwidth = {metrics['bandwidth']:.6f}, "
                f"coverage = {metrics.get('coverage', 0.0)*100:.2f}%, f_low = {metrics.get('f_low', 0.0):.3f}, f_high = {metrics.get('f_high', 0.0):.3f}, minRL = {metrics['min_rl']:.3f}"
            )

            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(
                    f"{it}\t{ind}\t{template_summary(ind)}\t{metrics['score']}\t{metrics['bandwidth']}\t"
                    f"{metrics.get('coverage', 0.0)}\t{metrics['min_rl']}\t{metrics.get('f_low', 0.0)}\t"
                    f"{metrics.get('f_high', 0.0)}\t{metrics.get('total_effective_bw', 0.0)}\t"
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
        print(f"best bandwidth so far = {best_metrics['bandwidth']:.6f} GHz, coverage = {best_metrics.get('coverage', 0.0)*100:.2f}%")
        print(f"best min RL so far = {best_metrics['min_rl']:.3f} dB")
        print(f"best params so far = {best_params}")

        pop = make_new_population(pop, fit_list, current_pm)

    print("\nOptimization finished.")
    print(f"Best score = {best_metrics['score']}")
    print(f"Best bandwidth = {best_metrics['bandwidth']} GHz, coverage = {best_metrics.get('coverage', 0.0)*100:.2f}%")
    print(f"Best min RL = {best_metrics['min_rl']} dB")
    print(f"Best params = {best_params}")
    print(f"Best CST file saved to: {BEST_CST}")




# =========================================================
# 单次运行：使用表面 Ohmic Sheet 模型复核当前 12x12 最优图案
# =========================================================
def run_fixed_best_ohmic_sheet_once():
    os.makedirs(FIXED_CHECK_DIR, exist_ok=True)
    print("\n" + "=" * 80)
    print("Running current 12x12 best topology with surface Ohmic Sheet model")
    print("=" * 80)

    cst_basename = f"fixed_best_ohmic_sheet_{make_run_tag()}.cst"
    metrics, params, cst_file = run_cst_for_params(
        p=FIXED_P,
        h=FIXED_H,
        mask_x_seed=FIXED_MASK_X_SEED,
        mask_y_seed=FIXED_MASK_Y_SEED,
        film_model_type="ohmic_sheet",
        cst_basename=cst_basename,
    )

    out_cst = os.path.join(FIXED_CHECK_DIR, cst_basename)
    remove_file_if_exists(out_cst)
    remove_file_if_exists(FIXED_CHECK_S11_FILE)
    remove_file_if_exists(FIXED_CHECK_PNG)

    if cst_file and os.path.exists(cst_file):
        shutil.copyfile(cst_file, out_cst)
        export_s11_curve(cst_file, FIXED_CHECK_S11_FILE)
        export_s11_plot(cst_file, FIXED_CHECK_PNG)

    with open(FIXED_CHECK_RESULT_FILE, "w", encoding="utf-8") as f:
        f.write("Fixed current 12x12 best topology with surface Ohmic Sheet model\n")
        f.write(f"score = {metrics['score']}\n")
        f.write(f"bandwidth_RL_lt_minus_10_dB_GHz = {metrics['bandwidth']}\n")
        f.write(f"min_RL_dB = {metrics['min_rl']}\n")
        f.write(f"parameters_p_h_mask_x_seed_mask_y_seed = {params}\n")
        f.write(f"cst_file = {out_cst}\n")
        f.write(f"s11_file = {FIXED_CHECK_S11_FILE}\n")
        f.write(f"png_file = {FIXED_CHECK_PNG}\n")

    print("Fixed Ohmic Sheet run finished.")
    print(f"Result saved to: {FIXED_CHECK_RESULT_FILE}")
    print(f"RL plot saved to: {FIXED_CHECK_PNG}")


# =========================================================
# 分支1：固定当前最优结构，比较薄实体膜与无厚度片阻层
# =========================================================
def write_single_run_result(out_file, film_model_type, metrics, params, cst_file, s11_file, png_file):
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"film_model_type: {film_model_type}\n")
        f.write(f"score: {metrics['score']}\n")
        f.write(f"bandwidth_RL_lt_minus_10_dB_GHz: {metrics['bandwidth']}\n")
        f.write(f"min_RL_dB: {metrics['min_rl']}\n")
        f.write(f"parameters_p_h_mask_x_seed_mask_y_seed: {params}\n")
        f.write(f"cst_file: {cst_file}\n")
        f.write(f"s11_file: {s11_file}\n")
        f.write(f"png_file: {png_file}\n")


def read_exported_s11_txt(path):
    freq = []
    rl = []
    with open(path, "r", encoding="utf-8") as f:
        next(f, None)
        for line in f:
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            freq.append(float(parts[0]))
            rl.append(float(parts[2]))
    return np.array(freq), np.array(rl)


def export_comparison_overlay(result_records):
    plt.figure(figsize=(8, 5))

    data_by_model = {}
    for rec in result_records:
        model = rec["model"]
        f, rl = read_exported_s11_txt(rec["s11_file"])
        data_by_model[model] = (f, rl)
        plt.plot(f, rl, label=model)

    plt.axhline(-10, linestyle="--")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Reflection Loss RL (dB)")
    plt.title("Comparison: thin solid film vs surface ohmic sheet")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(COMPARE_OVERLAY_PNG, dpi=300)
    plt.close()

    with open(COMPARE_OVERLAY_TXT, "w", encoding="utf-8") as f:
        for model, (freq, rl) in data_by_model.items():
            f.write(f"# model = {model}\n")
            f.write("freq_GHz\trl_dB\n")
            for ff, rr in zip(freq, rl):
                f.write(f"{ff}\t{rr}\n")
            f.write("\n")


def compare_fixed_best_structure():
    os.makedirs(COMPARE_DIR, exist_ok=True)
    records = []

    for film_model_type in COMPARE_FILM_MODEL_TYPES:
        model_dir = os.path.join(COMPARE_DIR, film_model_type)
        os.makedirs(model_dir, exist_ok=True)

        print("\n" + "=" * 80)
        print(f"Running fixed-structure comparison model: {film_model_type}")
        print("=" * 80)

        cst_basename = f"fixed_best_{film_model_type}_{make_run_tag()}.cst"
        try:
            metrics, params, cst_file = run_cst_for_params(
                p=FIXED_P,
                h=FIXED_H,
                mask_x_seed=FIXED_MASK_X_SEED,
                mask_y_seed=FIXED_MASK_Y_SEED,
                film_model_type=film_model_type,
                cst_basename=cst_basename,
            )

            out_cst = os.path.join(model_dir, cst_basename)
            out_s11 = os.path.join(model_dir, f"fixed_best_{film_model_type}_s11.txt")
            out_png = os.path.join(model_dir, f"fixed_best_{film_model_type}_RL.png")
            out_result = os.path.join(model_dir, f"fixed_best_{film_model_type}_result.txt")

            if cst_file and os.path.exists(cst_file):
                remove_file_if_exists(out_cst)
                remove_file_if_exists(out_s11)
                remove_file_if_exists(out_png)
                shutil.copyfile(cst_file, out_cst)
                export_s11_curve(cst_file, out_s11)
                export_s11_plot(cst_file, out_png)

            write_single_run_result(out_result, film_model_type, metrics, params, out_cst, out_s11, out_png)

            records.append({
                "model": film_model_type,
                "metrics": metrics,
                "params": params,
                "cst_file": out_cst,
                "s11_file": out_s11,
                "png_file": out_png,
                "result_file": out_result,
            })

        except Exception as e:
            with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"Fixed comparison failed for film_model_type = {film_model_type}\n")
                f.write(repr(e) + "\n")
                f.write(traceback.format_exc() + "\n")
            print(f"ERROR: model {film_model_type} failed. See error log: {ERROR_LOG_FILE}")

    with open(COMPARE_SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write("Branch 1 comparison: thin solid film vs surface ohmic sheet\n")
        f.write(f"Fixed p = {FIXED_P}\n")
        f.write(f"Fixed h = {FIXED_H}\n")
        f.write(f"Fixed mask_x_seed = {FIXED_MASK_X_SEED}\n")
        f.write(f"Fixed mask_y_seed = {FIXED_MASK_Y_SEED}\n\n")

        for rec in records:
            m = rec["metrics"]
            f.write(f"[{rec['model']}]\n")
            f.write(f"score = {m['score']}\n")
            f.write(f"bandwidth_RL_lt_minus_10_dB_GHz = {m['bandwidth']}\n")
            f.write(f"min_RL_dB = {m['min_rl']}\n")
            f.write(f"cst_file = {rec['cst_file']}\n")
            f.write(f"s11_file = {rec['s11_file']}\n")
            f.write(f"png_file = {rec['png_file']}\n\n")

        if len(records) == 2:
            bw0 = records[0]["metrics"]["bandwidth"]
            bw1 = records[1]["metrics"]["bandwidth"]
            min0 = records[0]["metrics"]["min_rl"]
            min1 = records[1]["metrics"]["min_rl"]
            f.write("[Difference]\n")
            f.write(f"delta_bandwidth_GHz = {bw1 - bw0}\n")
            f.write(f"delta_min_RL_dB = {min1 - min0}\n")

    if len(records) >= 2:
        export_comparison_overlay(records)
        print(f"Overlay plot saved to: {COMPARE_OVERLAY_PNG}")
        print(f"Overlay data saved to: {COMPARE_OVERLAY_TXT}")

    print("\nBranch 1 comparison finished.")
    print(f"Summary saved to: {COMPARE_SUMMARY_FILE}")


if __name__ == "__main__":
    if RUN_MODE == "fixed_best_ohmic":
        run_fixed_best_ohmic_sheet_once()
    elif RUN_MODE == "compare_fixed":
        compare_fixed_best_structure()
    elif RUN_MODE == "optimize":
        optimize()
    else:
        raise ValueError(f"Unknown RUN_MODE: {RUN_MODE}")
