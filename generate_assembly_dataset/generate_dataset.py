"""
Main script for generating assembly feature dataset
装配特征数据集批量生成主脚本
"""

import os
import sys
import random
from itertools import combinations

sys.path.append('./')
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_StepModelType
from OCC.Core.STEPConstruct import stepconstruct_FindEntity
from OCC.Core.TCollection import TCollection_HAsciiString
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.gp import gp_Pnt

from assembly_features.base_parts import (PlateBase, BlockBase, ShaftBase, BoxBase,
                                          BracketBase, FlangeBase, create_random_base_part)
from assembly_features.assembly_features import (ThreadedHole, ThreadedBlindHole, PinHole,
                                                 KeySlot, Counterbore, Countersink,
                                                 PositioningHole, Bolt, Pin, Key,
                                                 create_random_subtractive_feature,
                                                 create_random_additive_feature)
from assembly_features.feature_labeling import FeatureLabelGenerator
from Utils.geometry_utils import random_position_on_face, check_collision


class AssemblyPartGenerator:
    """装配零件生成器"""
    def __init__(self, base_part=None, num_subtractive_features=None, num_additive_features=None):
        """
        Args:
            base_part: 基体零件,如果为None则随机生成
            num_subtractive_features: 减材特征数量,如果为None则随机
            num_additive_features: 增材特征数量,如果为None则随机
        """
        self.base_part = base_part if base_part else create_random_base_part()
        self.num_subtractive = num_subtractive_features if num_subtractive_features else random.randint(2, 8)
        self.num_additive = num_additive_features if num_additive_features else random.randint(0, 3)

        self.subtractive_features = []
        self.additive_features = []
        self.combined_shape = None
        self.label_map = {}

    def generate_features(self):
        """生成所有特征"""
        # 获取基体边界用于放置特征
        if hasattr(self.base_part, 'get_top_face_bounds'):
            bounds = self.base_part.get_top_face_bounds()
        else:
            # 默认边界
            bounds = (5, 95, 5, 95)

        existing_positions = []

        # 生成减材特征
        for i in range(self.num_subtractive):
            # 随机位置
            max_attempts = 50
            for attempt in range(max_attempts):
                x, y = random_position_on_face(bounds, clearance=8)

                if check_collision((x, y), existing_positions, min_distance=15):
                    existing_positions.append((x, y))

                    # 创建特征
                    feature = create_random_subtractive_feature()

                    # 设置位置
                    if self.base_part.part_type == "shaft":
                        # 轴类零件:径向孔
                        z = random.uniform(10, self.base_part.dimensions.get('length', 50) - 10)
                        feature.position = gp_Pnt(0, z, x)  # x用作径向偏移
                    else:
                        # 板类/块类:顶面孔
                        z = self.base_part.dimensions.get('thickness',
                                                          self.base_part.dimensions.get('height', 10))
                        feature.position = gp_Pnt(x, y, z)

                    # 重新生成特征形状
                    feature._create_shape()

                    self.subtractive_features.append(feature)
                    break

        # 生成增材特征(装配件)
        for i in range(self.num_additive):
            max_attempts = 50
            for attempt in range(max_attempts):
                x, y = random_position_on_face(bounds, clearance=8)

                if check_collision((x, y), existing_positions, min_distance=15):
                    existing_positions.append((x, y))

                    # 创建特征
                    feature = create_random_additive_feature()

                    # 设置位置
                    z = self.base_part.dimensions.get('thickness',
                                                      self.base_part.dimensions.get('height', 10))
                    feature.position = gp_Pnt(x, y, z)

                    # 重新生成特征形状
                    feature._create_shape()

                    self.additive_features.append(feature)
                    break

    def combine_features(self):
        """组合所有特征生成最终形状"""
        # 从基体开始
        self.combined_shape = self.base_part.get_shape()

        # 应用减材特征
        for feature in self.subtractive_features:
            try:
                cut_result = BRepAlgoAPI_Cut(self.combined_shape, feature.get_shape())
                if cut_result.IsDone():
                    self.combined_shape = cut_result.Shape()
            except Exception as e:
                print(f"Error applying subtractive feature: {e}")
                continue

        # 应用增材特征
        for feature in self.additive_features:
            try:
                fuse_result = BRepAlgoAPI_Fuse(self.combined_shape, feature.get_shape())
                if fuse_result.IsDone():
                    self.combined_shape = fuse_result.Shape()
            except Exception as e:
                print(f"Error applying additive feature: {e}")
                continue

        return self.combined_shape

    def generate_labels(self):
        """生成特征标签"""
        # 构建特征列表
        all_features = []

        for idx, feature in enumerate(self.subtractive_features):
            all_features.append((feature, 'cut'))

        for idx, feature in enumerate(self.additive_features):
            all_features.append((feature, 'fuse'))

        # 生成标签
        label_generator = FeatureLabelGenerator(self.base_part, all_features)
        self.label_map = label_generator.generate_labels(self.combined_shape)

        return self.label_map

    def get_feature_summary(self):
        """获取特征摘要"""
        summary = {
            'base_type': self.base_part.part_type,
            'base_dimensions': self.base_part.get_dimensions(),
            'num_subtractive_features': len(self.subtractive_features),
            'num_additive_features': len(self.additive_features),
            'subtractive_types': [f.get_type() for f in self.subtractive_features],
            'additive_types': [f.get_type() for f in self.additive_features]
        }
        return summary


def save_shape_to_step(filename, shape, label_map):
    """
    将形状保存为STEP文件,并标注面标签
    Args:
        filename: 输出文件名
        shape: 要保存的形状
        label_map: 面标签映射 {face: label}
    """
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_StepModelType(0))

    finder_p = writer.WS().TransferWriter().FinderProcess()

    face_set = list(TopologyExplorer(shape).faces())
    loc = TopLoc_Location()

    for face in face_set:
        item = stepconstruct_FindEntity(finder_p, face, loc)
        if item is None:
            continue

        # 从label_map获取标签
        label = label_map.get(face, "unknown")
        item.SetName(TCollection_HAsciiString(str(label)))

    writer.Write(filename)


def generate_single_part(output_dir, part_id):
    """
    生成单个装配零件
    Args:
        output_dir: 输出目录
        part_id: 零件ID
    Returns:
        dict: 零件信息
    """
    # 创建生成器
    generator = AssemblyPartGenerator()

    # 生成特征
    generator.generate_features()

    # 组合特征
    combined_shape = generator.combine_features()

    # 生成标签
    label_map = generator.generate_labels()

    # 保存STEP文件
    filename = os.path.join(output_dir, f"assembly_part_{part_id:06d}.step")
    save_shape_to_step(filename, combined_shape, label_map)

    # 获取特征摘要
    summary = generator.get_feature_summary()
    summary['part_id'] = part_id
    summary['filename'] = filename

    return summary


def generate_batch(output_dir, start_id, num_parts):
    """
    批量生成装配零件数据集
    Args:
        output_dir: 输出目录
        start_id: 起始ID
        num_parts: 生成数量
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 创建摘要文件
    summary_file = os.path.join(output_dir, "dataset_summary.txt")

    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("Assembly Feature Dataset Summary\n")
        f.write("=" * 80 + "\n\n")

        for i in range(num_parts):
            part_id = start_id + i

            try:
                # 生成零件
                summary = generate_single_part(output_dir, part_id)

                # 写入摘要
                f.write(f"Part ID: {part_id}\n")
                f.write(f"  Filename: {summary['filename']}\n")
                f.write(f"  Base Type: {summary['base_type']}\n")
                f.write(f"  Subtractive Features: {summary['num_subtractive_features']}\n")
                f.write(f"    Types: {', '.join(summary['subtractive_types'])}\n")
                f.write(f"  Additive Features: {summary['num_additive_features']}\n")
                f.write(f"    Types: {', '.join(summary['additive_types'])}\n")
                f.write("-" * 80 + "\n")

                print(f"Generated part {part_id}: {summary['base_type']} with "
                      f"{summary['num_subtractive_features']} subtractive and "
                      f"{summary['num_additive_features']} additive features")

            except Exception as e:
                print(f"Error generating part {part_id}: {e}")
                f.write(f"Part ID: {part_id} - ERROR: {e}\n")
                f.write("-" * 80 + "\n")
                continue

    print(f"\nBatch generation complete. {num_parts} parts generated.")
    print(f"Output directory: {output_dir}")
    print(f"Summary file: {summary_file}")


if __name__ == '__main__':
    # 配置参数
    OUTPUT_DIR = "./assembly_dataset_output"
    START_ID = 1
    NUM_PARTS = 100  # 生成100个零件样本

    print("Assembly Feature Dataset Generator")
    print("=" * 80)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Number of parts to generate: {NUM_PARTS}")
    print(f"Starting ID: {START_ID}")
    print("=" * 80)
    print()

    # 开始生成
    generate_batch(OUTPUT_DIR, START_ID, NUM_PARTS)

    print("\nDataset generation completed!")
