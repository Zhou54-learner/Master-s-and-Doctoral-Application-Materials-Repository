# test_ohmic_sheet_assign.py
# 目的：
# 1) 新建一个 Ohmic Sheet 材料
# 2) 画一个二维 sheet（矩形面）
# 3) 尝试把 Ohmic Sheet 材料赋给这个 sheet
# 4) 保存工程，检查是否成功

import sys

cst_lib_path = r"F:\CST Studio Suite 2025\AMD64\python_cst_libraries"
sys.path.append(cst_lib_path)

import cst
import cst.interface

de = cst.interface.DesignEnvironment()
pj = de.new_mws()

def add_history(title, lines):
    pj.model3d.add_to_history(title, "\n".join(lines))

# 基本单位
add_history("set units", [
    "With Units",
    '    .Geometry "mm"',
    '    .Frequency "GHz"',
    "End With"
])

# 创建一个 Ohmic Sheet 材料
add_history("create ohmic sheet material", [
    "With Material",
    "    .Reset",
    '    .Name "TEST_OHMIC_SHEET"',
    '    .Folder ""',
    '    .Type "Ohmic Sheet"',
    '    .Colour "1", "0", "0"',
    "    .Create",w
    "End With"
])

# 新建组件
add_history("new component", [
    'Component.New "component1"'
])

# 画一个矩形面（sheet）
# 如果你的版本不认 Rectangle，也没关系，运行后把第一条报错发给 ChatGPT
add_history("new curve", [
    'Curve.NewCurve "curve1"'
])
add_history("create test rectangle curve", [
    "With Rectangle",
    "    .Reset",
    '    .Name "rect1"',
    '    .Curve "curve1"',
    '    .Xrange "-5", "5"',
    '    .Yrange "-5", "5"',
    "    .Create",
    "End With"
])

# 尝试给这个面赋 Ohmic Sheet 材料
# 如果你的版本不认 ChangeMaterial，也把报错发给 ChatGPT
add_history("assign ohmic sheet material", [
    'Solid.ChangeMaterial "component1:sheet1", "TEST_OHMIC_SHEET"'
])

test_file = r"F:\biyesheji\ohmic_sheet_assign_probe.cst"
pj.save(test_file)
print("Saved:", test_file)
print("Done.")
