"""
Geometry utility functions for assembly feature dataset generation
装配特征数据集生成的几何工具函数
"""

import math
import random
import numpy as np
from OCC.Core.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire,
                                     BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox
from OCC.Core.GC import GC_MakeSegment, GC_MakeCircle, GC_MakeArcOfCircle
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Ax1, gp_Ax2, gp_Circ, gp_Trsf
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCC.Core.TopoDS import TopoDS_Shape


def make_box(length, width, height, origin=gp_Pnt(0, 0, 0)):
    """
    创建长方体
    Args:
        length: 长度(X方向)
        width: 宽度(Y方向)
        height: 高度(Z方向)
        origin: 起始点
    Returns:
        TopoDS_Shape: 长方体形状
    """
    corner = gp_Pnt(origin.X() + length, origin.Y() + width, origin.Z() + height)
    box = BRepPrimAPI_MakeBox(origin, corner)
    return box.Shape()


def make_cylinder(radius, height, origin=gp_Pnt(0, 0, 0), direction=gp_Dir(0, 0, 1)):
    """
    创建圆柱体
    Args:
        radius: 半径
        height: 高度
        origin: 底面圆心
        direction: 轴向方向
    Returns:
        TopoDS_Shape: 圆柱体形状
    """
    ax = gp_Ax2(origin, direction)
    cylinder = BRepPrimAPI_MakeCylinder(ax, radius, height)
    return cylinder.Shape()


def make_threaded_hole(diameter, depth, origin=gp_Pnt(0, 0, 0), direction=gp_Dir(0, 0, 1)):
    """
    创建螺纹孔(简化为光孔)
    Args:
        diameter: 螺纹直径
        depth: 孔深
        origin: 孔口位置
        direction: 孔轴向
    Returns:
        TopoDS_Shape: 螺纹孔形状
    """
    return make_cylinder(diameter / 2.0, depth, origin, direction)


def make_counterbore(hole_diameter, hole_depth, bore_diameter, bore_depth,
                     origin=gp_Pnt(0, 0, 0), direction=gp_Dir(0, 0, 1)):
    """
    创建沉孔
    Args:
        hole_diameter: 通孔直径
        hole_depth: 通孔深度
        bore_diameter: 沉孔直径
        bore_depth: 沉孔深度
        origin: 孔口位置
        direction: 孔轴向
    Returns:
        TopoDS_Shape: 沉孔形状
    """
    # 创建通孔
    ax = gp_Ax2(origin, direction)
    through_hole = BRepPrimAPI_MakeCylinder(ax, hole_diameter / 2.0, hole_depth).Shape()

    # 创建沉孔部分
    counterbore = BRepPrimAPI_MakeCylinder(ax, bore_diameter / 2.0, bore_depth).Shape()

    # 合并
    combined = BRepAlgoAPI_Fuse(through_hole, counterbore).Shape()
    return combined


def make_countersink(hole_diameter, hole_depth, sink_diameter, sink_angle=90,
                     origin=gp_Pnt(0, 0, 0), direction=gp_Dir(0, 0, 1)):
    """
    创建沉头孔
    Args:
        hole_diameter: 通孔直径
        hole_depth: 通孔深度
        sink_diameter: 沉头直径
        sink_angle: 沉头角度(度)
        origin: 孔口位置
        direction: 孔轴向
    Returns:
        TopoDS_Shape: 沉头孔形状
    """
    ax = gp_Ax2(origin, direction)

    # 创建通孔
    through_hole = BRepPrimAPI_MakeCylinder(ax, hole_diameter / 2.0, hole_depth).Shape()

    # 创建沉头圆锥部分(简化为圆柱)
    sink_depth = (sink_diameter - hole_diameter) / (2 * math.tan(math.radians(sink_angle / 2)))
    sink_cone = BRepPrimAPI_MakeCylinder(ax, sink_diameter / 2.0, sink_depth).Shape()

    # 合并
    combined = BRepAlgoAPI_Fuse(through_hole, sink_cone).Shape()
    return combined


def make_key_slot(width, length, depth, origin=gp_Pnt(0, 0, 0), direction=gp_Dir(0, 1, 0)):
    """
    创建键槽
    Args:
        width: 键槽宽度
        length: 键槽长度
        depth: 键槽深度
        origin: 键槽起点
        direction: 键槽长度方向
    Returns:
        TopoDS_Shape: 键槽形状
    """
    # 创建键槽底面矩形
    p1 = origin
    p2 = gp_Pnt(origin.X() + width, origin.Y(), origin.Z())
    p3 = gp_Pnt(origin.X() + width, origin.Y() + length, origin.Z())
    p4 = gp_Pnt(origin.X(), origin.Y() + length, origin.Z())

    e1 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p1, p2).Value()).Edge()
    e2 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p2, p3).Value()).Edge()
    e3 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p3, p4).Value()).Edge()
    e4 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p4, p1).Value()).Edge()

    wire = BRepBuilderAPI_MakeWire(e1, e2, e3, e4).Wire()
    face = BRepBuilderAPI_MakeFace(wire).Face()

    # 拉伸成键槽
    slot = BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, -depth))
    return slot.Shape()


def make_pin_hole(diameter, depth, origin=gp_Pnt(0, 0, 0), direction=gp_Dir(0, 0, 1)):
    """
    创建销孔
    Args:
        diameter: 销孔直径
        depth: 销孔深度
        origin: 孔口位置
        direction: 孔轴向
    Returns:
        TopoDS_Shape: 销孔形状
    """
    return make_cylinder(diameter / 2.0, depth, origin, direction)


def make_bolt(head_diameter, head_height, shaft_diameter, shaft_length,
              origin=gp_Pnt(0, 0, 0), direction=gp_Dir(0, 0, 1)):
    """
    创建螺栓(简化模型)
    Args:
        head_diameter: 螺栓头直径
        head_height: 螺栓头高度
        shaft_diameter: 螺栓杆直径
        shaft_length: 螺栓杆长度
        origin: 螺栓头底面中心
        direction: 螺栓轴向
    Returns:
        TopoDS_Shape: 螺栓形状
    """
    ax = gp_Ax2(origin, direction)

    # 创建螺栓头(六角简化为圆柱)
    head = BRepPrimAPI_MakeCylinder(ax, head_diameter / 2.0, head_height).Shape()

    # 创建螺栓杆
    shaft_origin = gp_Pnt(origin.X(), origin.Y(), origin.Z() + head_height)
    shaft_ax = gp_Ax2(shaft_origin, direction)
    shaft = BRepPrimAPI_MakeCylinder(shaft_ax, shaft_diameter / 2.0, shaft_length).Shape()

    # 合并
    bolt = BRepAlgoAPI_Fuse(head, shaft).Shape()
    return bolt


def make_pin(diameter, length, origin=gp_Pnt(0, 0, 0), direction=gp_Dir(0, 0, 1)):
    """
    创建销钉
    Args:
        diameter: 销钉直径
        length: 销钉长度
        origin: 销钉起点
        direction: 销钉轴向
    Returns:
        TopoDS_Shape: 销钉形状
    """
    return make_cylinder(diameter / 2.0, length, origin, direction)


def make_key(width, height, length, origin=gp_Pnt(0, 0, 0)):
    """
    创建平键
    Args:
        width: 键宽
        height: 键高
        length: 键长
        origin: 键的起点
    Returns:
        TopoDS_Shape: 键形状
    """
    return make_box(width, length, height, origin)


def random_position_on_face(face_bounds, clearance=5.0):
    """
    在面的边界内随机生成位置
    Args:
        face_bounds: (x_min, x_max, y_min, y_max)
        clearance: 边界间隙
    Returns:
        (x, y): 随机位置坐标
    """
    x_min, x_max, y_min, y_max = face_bounds
    x = random.uniform(x_min + clearance, x_max - clearance)
    y = random.uniform(y_min + clearance, y_max - clearance)
    return x, y


def check_collision(new_feature_pos, existing_positions, min_distance):
    """
    检查新特征位置是否与现有特征碰撞
    Args:
        new_feature_pos: (x, y) 新特征位置
        existing_positions: [(x, y), ...] 现有特征位置列表
        min_distance: 最小间距
    Returns:
        bool: True表示无碰撞,False表示有碰撞
    """
    for pos in existing_positions:
        dist = math.sqrt((new_feature_pos[0] - pos[0])**2 + (new_feature_pos[1] - pos[1])**2)
        if dist < min_distance:
            return False
    return True
