"""
Test script for assembly feature dataset generation
装配特征数据集生成测试脚本
"""

import sys
sys.path.append('./')

from assembly_features.base_parts import (PlateBase, BlockBase, ShaftBase,
                                          BoxBase, BracketBase, FlangeBase)
from assembly_features.assembly_features import (ThreadedHole, PinHole, KeySlot,
                                                 Bolt, Pin, create_random_subtractive_feature)
from generate_dataset import AssemblyPartGenerator, save_shape_to_step
from OCC.Core.gp import gp_Pnt


def test_base_parts():
    """测试基体零件生成"""
    print("=" * 80)
    print("Testing Base Part Generation")
    print("=" * 80)

    # 测试各种基体类型
    base_types = [
        ("Plate", PlateBase()),
        ("Block", BlockBase()),
        ("Shaft", ShaftBase()),
        ("Box", BoxBase()),
        ("Bracket", BracketBase()),
        ("Flange", FlangeBase())
    ]

    for name, base in base_types:
        print(f"\n{name}:")
        print(f"  Type: {base.part_type}")
        print(f"  Dimensions: {base.get_dimensions()}")
        print(f"  Shape created: {base.get_shape() is not None}")

    print("\n✓ Base part generation test passed")


def test_assembly_features():
    """测试装配特征生成"""
    print("\n" + "=" * 80)
    print("Testing Assembly Feature Generation")
    print("=" * 80)

    # 测试减材特征
    print("\nSubtractive Features:")
    threaded_hole = ThreadedHole(diameter=8, depth=25, position=gp_Pnt(10, 10, 0))
    print(f"  Threaded Hole: {threaded_hole.get_parameters()}")

    pin_hole = PinHole(diameter=6, depth=20, position=gp_Pnt(30, 30, 0))
    print(f"  Pin Hole: {pin_hole.get_parameters()}")

    key_slot = KeySlot(width=8, length=30, depth=5, position=gp_Pnt(50, 10, 0))
    print(f"  Key Slot: {key_slot.get_parameters()}")

    # 测试增材特征
    print("\nAdditive Features:")
    bolt = Bolt(shaft_diameter=10, shaft_length=40, position=gp_Pnt(20, 20, 10))
    print(f"  Bolt: {bolt.get_parameters()}")

    pin = Pin(diameter=5, length=25, position=gp_Pnt(40, 40, 10))
    print(f"  Pin: {pin.get_parameters()}")

    print("\n✓ Assembly feature generation test passed")


def test_random_generation():
    """测试随机特征生成"""
    print("\n" + "=" * 80)
    print("Testing Random Feature Generation")
    print("=" * 80)

    for i in range(5):
        feature = create_random_subtractive_feature()
        print(f"  Random feature {i+1}: {feature.get_type()}")

    print("\n✓ Random feature generation test passed")


def test_complete_part_generation():
    """测试完整零件生成"""
    print("\n" + "=" * 80)
    print("Testing Complete Part Generation")
    print("=" * 80)

    # 使用板类基体
    base = PlateBase(length=100, width=80, thickness=15)
    print(f"\nBase part: {base.part_type}")
    print(f"Dimensions: {base.get_dimensions()}")

    # 创建生成器
    generator = AssemblyPartGenerator(
        base_part=base,
        num_subtractive_features=4,
        num_additive_features=2
    )

    # 生成特征
    print("\nGenerating features...")
    generator.generate_features()
    print(f"  Subtractive features: {len(generator.subtractive_features)}")
    print(f"  Additive features: {len(generator.additive_features)}")

    # 组合
    print("\nCombining features...")
    combined = generator.combine_features()
    print(f"  Combined shape created: {combined is not None}")

    # 生成标签
    print("\nGenerating labels...")
    labels = generator.generate_labels()
    print(f"  Number of labeled faces: {len(labels)}")

    # 获取摘要
    summary = generator.get_feature_summary()
    print("\nPart Summary:")
    print(f"  Base type: {summary['base_type']}")
    print(f"  Subtractive features: {summary['num_subtractive_features']}")
    print(f"  Feature types: {summary['subtractive_types']}")
    print(f"  Additive features: {summary['num_additive_features']}")
    print(f"  Feature types: {summary['additive_types']}")

    # 保存测试文件
    print("\nSaving test part...")
    save_shape_to_step("test_assembly_part.step", combined, labels)
    print("  Saved to: test_assembly_part.step")

    print("\n✓ Complete part generation test passed")


def main():
    """运行所有测试"""
    print("\n")
    print("*" * 80)
    print("Assembly Feature Dataset Generation - Test Suite")
    print("*" * 80)
    print()

    try:
        test_base_parts()
        test_assembly_features()
        test_random_generation()
        test_complete_part_generation()

        print("\n" + "=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        print()

        print("Next steps:")
        print("1. Check the generated 'test_assembly_part.step' file in a CAD viewer")
        print("2. Run 'python generate_dataset.py' to generate the full dataset")
        print()

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
