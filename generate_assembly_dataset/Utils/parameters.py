# Assembly Feature Dataset Parameters
# 参数化装配特征数据集参数定义

# Base Part Dimension Parameters
# 基体尺寸参数
base_min_length = 20.0
base_max_length = 150.0
base_min_width = 20.0
base_max_width = 150.0
base_min_height = 5.0
base_max_height = 100.0

# Shaft Parameters
# 轴类零件参数
shaft_min_diameter = 10.0
shaft_max_diameter = 80.0
shaft_min_length = 30.0
shaft_max_length = 200.0

# Thread Parameters
# 螺纹参数
thread_diameters = [3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 30]  # Standard metric thread sizes
thread_min_depth = 10.0
thread_max_depth = 50.0

# Pin Parameters
# 销钉参数
pin_diameters = [2, 3, 4, 5, 6, 8, 10, 12, 16]
pin_min_depth = 8.0
pin_max_depth = 40.0

# Key Slot Parameters
# 键槽参数
key_widths = [3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 25]  # Standard key widths
key_min_length = 10.0
key_max_length = 50.0
key_min_depth = 3.0
key_max_depth = 12.0

# Clearance and Tolerance
# 间隙和公差
min_clearance = 2.0
wall_thickness_min = 3.0

# Assembly Feature Types
# 装配特征类型
assembly_feature_names = [
    'threaded_hole',      # 0: 螺纹孔
    'threaded_blind_hole', # 1: 盲螺纹孔
    'pin_hole',           # 2: 销孔
    'key_slot',           # 3: 键槽
    'spline',             # 4: 花键
    'fitting_surface',    # 5: 配合面
    'positioning_hole',   # 6: 定位孔
    'bolt',               # 7: 螺栓
    'pin',                # 8: 销钉
    'key',                # 9: 键
    'counterbore',        # 10: 沉孔
    'countersink',        # 11: 沉头孔
    'base_part'           # 12: 基体
]

# Base Part Types
# 基体类型
base_part_types = [
    'plate',              # 0: 板类零件
    'block',              # 1: 块类零件
    'shaft',              # 2: 轴类零件
    'box',                # 3: 箱体类零件
    'bracket',            # 4: 支架类零件
    'flange',             # 5: 法兰类零件
]
