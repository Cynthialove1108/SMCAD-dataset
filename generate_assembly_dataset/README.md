# Assembly Feature Dataset Generator
# 装配特征数据集生成器

基于PythonOCC的装配特征参数化建模与数据集自动生成工具。

## 功能特点

### 1. 多样化基体类型
- **板类零件 (Plate)**: 平板基体,适合平面装配特征
- **块类零件 (Block)**: 立方体基体,可在多面添加特征
- **轴类零件 (Shaft)**: 圆柱体基体,适合轴向和径向特征
- **箱体类零件 (Box)**: 空心箱体,适合壁面装配
- **支架类零件 (Bracket)**: L型支架,双面特征
- **法兰类零件 (Flange)**: 圆盘带中心孔,典型装配件

### 2. 丰富的装配特征

#### 减材特征(孔/槽)
- **螺纹通孔** (Threaded Hole): M3-M30标准螺纹孔
- **螺纹盲孔** (Threaded Blind Hole): 有底螺纹孔
- **销孔** (Pin Hole): Φ2-Φ16销钉孔
- **键槽** (Key Slot): 3-25mm标准键槽
- **沉孔** (Counterbore): 螺栓头沉孔
- **沉头孔** (Countersink): 沉头螺钉孔
- **定位孔** (Positioning Hole): 精密定位孔

#### 增材特征(装配件)
- **螺栓** (Bolt): 简化螺栓模型
- **销钉** (Pin): 圆柱销
- **键** (Key): 平键

### 3. 自动标注系统
- 每个B-rep面自动标注特征类型
- 支持导出为带标签的STEP文件
- 生成数据集摘要文件

### 4. 批量生成
- 随机组合生成大量变体
- 自动避免特征碰撞
- 参数自动随机化

## 目录结构

```
generate_assembly_dataset/
├── Utils/
│   ├── parameters.py          # 参数定义
│   └── geometry_utils.py      # 几何工具函数
├── assembly_features/
│   ├── base_parts.py          # 基体零件类
│   ├── assembly_features.py   # 装配特征类
│   └── feature_labeling.py    # 特征标注系统
├── generate_dataset.py        # 主生成脚本
└── README.md                  # 本文件
```

## 依赖项

```bash
# 需要安装 PythonOCC
conda install -c conda-forge pythonocc-core
# 或
pip install pythonocc-core
```

## 使用方法

### 1. 基本使用

```python
# 批量生成100个装配零件
python generate_dataset.py
```

输出:
- `assembly_dataset_output/` 目录
- `assembly_part_000001.step` ~ `assembly_part_000100.step`
- `dataset_summary.txt` 摘要文件

### 2. 自定义参数

编辑 `generate_dataset.py` 中的配置:

```python
OUTPUT_DIR = "./my_dataset"  # 输出目录
START_ID = 1                  # 起始ID
NUM_PARTS = 1000             # 生成数量
```

### 3. 程序化使用

```python
from assembly_features.base_parts import PlateBase
from assembly_features.assembly_features import ThreadedHole
from generate_dataset import AssemblyPartGenerator

# 创建特定基体
base = PlateBase(length=100, width=80, thickness=10)

# 创建生成器
generator = AssemblyPartGenerator(
    base_part=base,
    num_subtractive_features=5,
    num_additive_features=2
)

# 生成特征
generator.generate_features()

# 组合
combined = generator.combine_features()

# 生成标签
labels = generator.generate_labels()

# 保存
from generate_dataset import save_shape_to_step
save_shape_to_step("my_part.step", combined, labels)
```

### 4. 查看生成的零件

使用CAD软件(如FreeCAD、SolidWorks)打开生成的STEP文件:
- 每个面的名称包含特征类型
- 例如: `threaded_hole_0`, `base_plate`, `bolt_1`

## 数据集格式

### STEP文件
- 标准STEP AP203/AP214格式
- 每个面包含特征标签(Name属性)

### 摘要文件
```
Part ID: 1
  Filename: assembly_part_000001.step
  Base Type: plate
  Subtractive Features: 4
    Types: threaded_hole, pin_hole, counterbore, positioning_hole
  Additive Features: 2
    Types: bolt, pin
```

## 特征标签格式

- 基体面: `base_{base_type}` (如 `base_plate`)
- 特征面: `{feature_type}_{feature_id}` (如 `threaded_hole_0`)

## 参数调整

### 修改尺寸范围

编辑 `Utils/parameters.py`:

```python
# 基体尺寸范围
base_min_length = 30.0
base_max_length = 200.0

# 螺纹规格
thread_diameters = [4, 6, 8, 10, 12, 16, 20]
```

### 修改特征分布

编辑 `assembly_features/base_parts.py`:

```python
def create_random_base_part():
    part_types = [PlateBase, BlockBase, ShaftBase]
    weights = [0.5, 0.3, 0.2]  # 调整各类型概率
    ...
```

## 扩展开发

### 添加新的基体类型

1. 在 `base_parts.py` 中继承 `BasePart`
2. 实现 `_create_shape()` 方法
3. 添加到工厂函数

### 添加新的装配特征

1. 在 `assembly_features.py` 中继承 `AssemblyFeature`
2. 实现 `_create_shape()` 方法
3. 添加到创建函数

## 性能优化

- 单个零件生成时间: ~0.5-2秒
- 100个零件: ~1-3分钟
- 建议分批生成大规模数据集

## 注意事项

1. 确保有足够磁盘空间(每个STEP文件约100KB-2MB)
2. 特征碰撞检测基于简化算法,极少数情况可能重叠
3. 复杂零件的布尔运算可能失败,已自动跳过

## 应用场景

- 机器学习训练数据集
- CAD特征识别研究
- 装配工艺规划
- 加工特征识别
- 3D形状分析

## 参考

本工具改编自SMCAD钣金特征数据集生成代码,扩展支持通用装配特征。

## 许可证

遵循原项目许可证。

## 联系

如有问题,请提交Issue或联系项目维护者。
