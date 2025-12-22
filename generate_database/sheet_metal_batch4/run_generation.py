#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
钣金特征数据集生成脚本 - 修改版
"""
import os
import random
from feature_test import Compound
from label import FaceLabel
from itertools import combinations
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_StepModelType
from OCC.Core.STEPConstruct import stepconstruct_FindEntity
from OCC.Core.TCollection import TCollection_HAsciiString
from OCC.Extend.TopologyUtils import TopologyExplorer


class Compose(object):
    def __init__(self, flange_length, flange_width, flange_thickness, bend_radius, bend_height, bend1_radius,
                 bend1_height, bend2_radius, bend2_length, bend3_radius, bend3_height, bend3_width, bend4_radius,
                 bend4_height, bend4_width, bend5_radius, bend5_length, bend5_width, index_combination=[]):

        self.flange_length = float(flange_length)
        self.flange_width = float(flange_width)
        self.flange_thickness = float(flange_thickness)
        self.bend_radius = float(bend_radius)
        self.bend_height = float(bend_height)
        self.bend1_radius = float(bend1_radius)
        self.bend1_height = float(bend1_height)
        self.bend2_radius = float(bend2_radius)
        self.bend2_length = float(bend2_length)
        self.bend3_radius = float(bend3_radius)
        self.bend3_height = float(bend3_height)
        self.bend3_width = float(bend3_width)
        self.bend4_radius = float(bend4_radius)
        self.bend4_height = float(bend4_height)
        self.bend4_width = float(bend4_width)
        self.bend5_radius = float(bend5_radius)
        self.bend5_length = float(bend5_length)
        self.bend5_width = float(bend5_width)
        self.index_combination = index_combination

    def compound(self):
        total_compound, base_sheet, flang_hole1, flang_hole2, swelling1, swelling2, bend_groove1, \
            bend_groove2, rib1, rib2, rip1, rip2, common_hole1, common_hole2, common_groove1, common_groove2, \
            vent1, vent2, array1, array2, profiled_groove1, profiled_groove2, profiled_array1, profiled_array2, \
            bend1, bend2, roll1, roll2, ear_plate1, ear_plate2 \
            = Compound(self.flange_length, self.flange_width, self.flange_thickness, self.bend_radius,
                       self.bend_height, self.bend1_radius, self.bend1_height, self.bend2_radius, self.bend2_length,
                       self.bend3_radius, self.bend3_height, self.bend3_width, self.bend4_radius, self.bend4_height,
                       self.bend4_width, self.bend5_radius, self.bend5_length, self.bend5_width).compound()

        flang_hole = [flang_hole1, flang_hole2]
        swelling = [swelling1, swelling2]
        bend_groove = [bend_groove1, bend_groove2]
        rib = [rib1, rib2]
        rip = [rip1, rip2]
        common_hole = [common_hole1, common_hole2]
        common_groove = [common_groove1, common_groove2]
        vent = [vent1, vent2]
        array = [array1, array2]
        profiled_groove = [profiled_groove1, profiled_groove2]
        profiled_array = [profiled_array1, profiled_array2]
        bend = [bend1, bend2]
        roll = [roll1, roll2]
        ear_plate = [ear_plate1, ear_plate2]
        feature_list = [flang_hole, swelling, bend_groove, rib,
                        rip, common_hole, common_groove, vent, array, profiled_groove, profiled_array,
                        bend, roll, ear_plate]
        compound = base_sheet.feature_local()

        for index, feature in enumerate(feature_list):
            if 0 <= index <= 3:
                if index in self.index_combination:
                    random_x = random.randrange(2)
                    common_feature = feature[random_x]
                    compound = BRepAlgoAPI_Cut(compound, common_feature.cut_flange())
                    compound = BRepAlgoAPI_Fuse(compound.Shape(), common_feature.feature_local())
                    compound = compound.Shape()
            elif 4 <= index <= 10:
                if index in self.index_combination:
                    random_y = random.randrange(2)
                    cut_feature = feature[random_y]
                    compound = BRepAlgoAPI_Cut(compound, cut_feature.feature_local())
                    compound = compound.Shape()
            elif 11 <= index <= 13:
                if index in self.index_combination:
                    random_z = random.randrange(2)
                    fuse_feature = feature[random_z]
                    compound = BRepAlgoAPI_Fuse(compound, fuse_feature.feature_local())
                    compound = compound.Shape()

        return compound


def shape_with_fid_to_step(filename, shape, label_map):
    """将组合体形状保存到step文件中"""
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_StepModelType(0))
    finder_p = writer.WS().TransferWriter().FinderProcess()
    face_set = list(TopologyExplorer(shape).faces())
    loc = TopLoc_Location()
    
    for face in face_set:
        item = stepconstruct_FindEntity(finder_p, face, loc)
        if item is None:
            continue
        item.SetName(TCollection_HAsciiString(str(label_map[face])))
    
    writer.Write(filename)


if __name__ == '__main__':
    # 创建输出目录
    output_dir = './sheet_metal_output'
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("钣金特征数据集生成器")
    print("=" * 80)
    print(f"输出目录: {output_dir}")
    print()
    
    # 配置参数
    START_ID = 1  # 起始编号（已修改）
    MAX_PARTS = 10  # 最多生成10个零件作为示例（原代码会生成数万个）
    
    index_list = []
    index_list1 = []
    index_list2 = []
    index_list3 = []
    a = [0, 1, 2, 3]
    b = [4, 5, 6, 7, 8, 9, 10]
    c = [11, 12, 13]
    n = START_ID
    count = 0
    
    # 生成数据集
    for num_1 in range(1, 5):
        for i in combinations(a, num_1):
            index_list1.extend(i)
            for num_2 in range(1, 8):
                for j in combinations(b, num_2):
                    index_list2.extend(j)
                    for num_3 in range(1, 4):
                        for k in combinations(c, num_3):
                            if count >= MAX_PARTS:
                                print(f"\n已生成 {MAX_PARTS} 个零件，停止生成")
                                print(f"如需生成更多，请修改 MAX_PARTS 参数")
                                exit(0)
                            
                            index_list3.extend(k)
                            index_list = index_list1 + index_list2 + index_list3
                            
                            # 生成零件
                            new_compound = Compose(50, 90, 0.8, 3, 44, 4, 5, 3, 28, 2, 30, 60, 
                                                   3, 25, 33, 2.5, 17, 50, index_list).compound()
                            face_label = FaceLabel(new_compound).generate_label()
                            
                            # 保存文件（修改为Linux路径）
                            filename = os.path.join(output_dir, f'sheet_metal_{n:06d}.step')
                            shape_with_fid_to_step(filename, new_compound, face_label)
                            
                            print(f"[{count+1}/{MAX_PARTS}] 生成: {filename}")
                            print(f"  特征组合: {index_list}")
                            
                            n += 1
                            count += 1
                            index_list3 = []
                    index_list2 = []
            index_list1 = []
        index_list = []
    
    print()
    print("=" * 80)
    print("生成完成！")
    print(f"共生成 {count} 个STEP文件")
    print(f"保存在目录: {output_dir}")
    print("=" * 80)
