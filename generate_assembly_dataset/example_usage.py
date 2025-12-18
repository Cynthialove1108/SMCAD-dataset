"""
Example usage of the assembly feature dataset generator
装配特征数据集生成器使用示例
"""

import sys
sys.path.append('./')

from assembly_features.base_parts import PlateBase, BlockBase, ShaftBase, FlangeBase
from assembly_features.assembly_features import ThreadedHole, PinHole, KeySlot, Bolt
from generate_dataset import AssemblyPartGenerator, save_shape_to_step
from OCC.Core.gp import gp_Pnt


def example_1_simple_plate():
    """示例1: 带螺纹孔的简单板"""
    print("Example 1: Simple plate with threaded holes")
    print("-" * 80)

    # 创建板类基体
    base = PlateBase(length=120, width=100, thickness=12)

    # 创建生成器
    generator = AssemblyPartGenerator(
        base_part=base,
        num_subtractive_features=4,  # 4个螺纹孔
        num_additive_features=0       # 无增材特征
    )

    # 生成并组合
    generator.generate_features()
    combined = generator.combine_features()
    labels = generator.generate_labels()

    # 保存
    save_shape_to_step("example_1_plate.step", combined, labels)
    print(f"Generated: example_1_plate.step")
    print(f"Features: {generator.get_feature_summary()['subtractive_types']}\n")


def example_2_shaft_with_keyslot():
    """示例2: 带键槽的轴"""
    print("Example 2: Shaft with key slot")
    print("-" * 80)

    # 创建轴类基体
    base = ShaftBase(diameter=40, length=150)

    # 创建生成器
    generator = AssemblyPartGenerator(
        base_part=base,
        num_subtractive_features=3,  # 包含键槽
        num_additive_features=0
    )

    generator.generate_features()
    combined = generator.combine_features()
    labels = generator.generate_labels()

    save_shape_to_step("example_2_shaft.step", combined, labels)
    print(f"Generated: example_2_shaft.step")
    print(f"Features: {generator.get_feature_summary()['subtractive_types']}\n")


def example_3_flange_with_bolts():
    """示例3: 带螺栓的法兰"""
    print("Example 3: Flange with bolt holes and bolts")
    print("-" * 80)

    # 创建法兰基体
    base = FlangeBase(outer_diameter=150, inner_diameter=60, thickness=20)

    # 创建生成器
    generator = AssemblyPartGenerator(
        base_part=base,
        num_subtractive_features=6,  # 6个螺栓孔
        num_additive_features=3      # 3个螺栓
    )

    generator.generate_features()
    combined = generator.combine_features()
    labels = generator.generate_labels()

    save_shape_to_step("example_3_flange.step", combined, labels)
    print(f"Generated: example_3_flange.step")
    summary = generator.get_feature_summary()
    print(f"Subtractive features: {summary['subtractive_types']}")
    print(f"Additive features: {summary['additive_types']}\n")


def example_4_random_parts():
    """示例4: 随机生成多个零件"""
    print("Example 4: Generate 10 random parts")
    print("-" * 80)

    for i in range(10):
        # 完全随机生成
        generator = AssemblyPartGenerator()
        generator.generate_features()
        combined = generator.combine_features()
        labels = generator.generate_labels()

        filename = f"example_4_random_{i+1:02d}.step"
        save_shape_to_step(filename, combined, labels)

        summary = generator.get_feature_summary()
        print(f"Part {i+1}: {summary['base_type']} - "
              f"{summary['num_subtractive_features']} sub, "
              f"{summary['num_additive_features']} add")

    print("\nGenerated 10 random parts (example_4_random_01.step ~ 10.step)\n")


def example_5_custom_features():
    """示例5: 自定义特征位置"""
    print("Example 5: Custom feature positions")
    print("-" * 80)

    # 创建块类基体
    base = BlockBase(length=80, width=60, height=50)

    # 手动创建特征
    features = []

    # 创建4个角落的螺纹孔
    positions = [
        gp_Pnt(10, 10, 50),
        gp_Pnt(70, 10, 50),
        gp_Pnt(70, 50, 50),
        gp_Pnt(10, 50, 50)
    ]

    for pos in positions:
        hole = ThreadedHole(diameter=8, depth=40, position=pos)
        features.append(hole)

    # 中心位置添加大孔
    center_hole = ThreadedHole(diameter=20, depth=30, position=gp_Pnt(40, 30, 50))
    features.append(center_hole)

    # 手动组合
    from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
    combined = base.get_shape()

    for feature in features:
        cut_result = BRepAlgoAPI_Cut(combined, feature.get_shape())
        if cut_result.IsDone():
            combined = cut_result.Shape()

    # 简化标签
    from OCC.Extend.TopologyUtils import TopologyExplorer
    explorer = TopologyExplorer(combined)
    faces = list(explorer.faces())
    labels = {face: "custom_feature" for face in faces}

    save_shape_to_step("example_5_custom.step", combined, labels)
    print(f"Generated: example_5_custom.step")
    print(f"Features: 4 corner holes (M8) + 1 center hole (M20)\n")


def main():
    """运行所有示例"""
    print("\n" + "=" * 80)
    print("Assembly Feature Dataset Generator - Usage Examples")
    print("=" * 80)
    print()

    example_1_simple_plate()
    example_2_shaft_with_keyslot()
    example_3_flange_with_bolts()
    example_4_random_parts()
    example_5_custom_features()

    print("=" * 80)
    print("All examples completed!")
    print("=" * 80)
    print()
    print("Output files:")
    print("  - example_1_plate.step")
    print("  - example_2_shaft.step")
    print("  - example_3_flange.step")
    print("  - example_4_random_01.step ~ 10.step")
    print("  - example_5_custom.step")
    print()
    print("Open these STEP files in a CAD viewer to inspect the generated parts.")
    print()


if __name__ == '__main__':
    main()
