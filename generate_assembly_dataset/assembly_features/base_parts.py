"""
Base part classes for assembly feature dataset
装配特征数据集的基体零件类
"""

import random
import math
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Ax2
from OCC.Core.GC import GC_MakeSegment
import sys
sys.path.append('../')
from Utils.geometry_utils import make_box, make_cylinder


class BasePart:
    """基体零件基类"""
    def __init__(self):
        self.shape = None
        self.part_type = "base"
        self.dimensions = {}

    def get_shape(self):
        """返回零件形状"""
        return self.shape

    def get_dimensions(self):
        """返回零件尺寸参数"""
        return self.dimensions


class PlateBase(BasePart):
    """板类零件基体"""
    def __init__(self, length=None, width=None, thickness=None):
        super().__init__()
        self.part_type = "plate"

        # 随机生成尺寸或使用指定尺寸
        self.length = length if length else random.uniform(40, 150)
        self.width = width if width else random.uniform(40, 150)
        self.thickness = thickness if thickness else random.uniform(5, 20)

        self.dimensions = {
            'length': self.length,
            'width': self.width,
            'thickness': self.thickness
        }

        self._create_shape()

    def _create_shape(self):
        """创建板类零件形状"""
        self.shape = make_box(self.length, self.width, self.thickness)

    def get_top_face_bounds(self):
        """获取顶面边界,用于放置特征"""
        return (0, self.length, 0, self.width)


class BlockBase(BasePart):
    """块类零件基体"""
    def __init__(self, length=None, width=None, height=None):
        super().__init__()
        self.part_type = "block"

        # 随机生成尺寸或使用指定尺寸
        self.length = length if length else random.uniform(30, 100)
        self.width = width if width else random.uniform(30, 100)
        self.height = height if height else random.uniform(30, 100)

        self.dimensions = {
            'length': self.length,
            'width': self.width,
            'height': self.height
        }

        self._create_shape()

    def _create_shape(self):
        """创建块类零件形状"""
        self.shape = make_box(self.length, self.width, self.height)

    def get_top_face_bounds(self):
        """获取顶面边界"""
        return (0, self.length, 0, self.width)

    def get_side_face_bounds(self):
        """获取侧面边界"""
        return (0, self.length, 0, self.height)


class ShaftBase(BasePart):
    """轴类零件基体"""
    def __init__(self, diameter=None, length=None):
        super().__init__()
        self.part_type = "shaft"

        # 随机生成尺寸或使用指定尺寸
        self.diameter = diameter if diameter else random.uniform(20, 80)
        self.length = length if length else random.uniform(50, 200)

        self.dimensions = {
            'diameter': self.diameter,
            'length': self.length,
            'radius': self.diameter / 2.0
        }

        self._create_shape()

    def _create_shape(self):
        """创建轴类零件形状"""
        # 轴沿Y轴方向
        origin = gp_Pnt(0, 0, 0)
        direction = gp_Dir(0, 1, 0)
        self.shape = make_cylinder(self.diameter / 2.0, self.length, origin, direction)

    def get_radial_surface_bounds(self):
        """获取径向表面的轴向范围"""
        return (5, self.length - 5)  # 留5mm间隙


class BoxBase(BasePart):
    """箱体类零件基体(空心)"""
    def __init__(self, outer_length=None, outer_width=None, outer_height=None, wall_thickness=None):
        super().__init__()
        self.part_type = "box"

        # 随机生成尺寸或使用指定尺寸
        self.outer_length = outer_length if outer_length else random.uniform(50, 120)
        self.outer_width = outer_width if outer_width else random.uniform(50, 120)
        self.outer_height = outer_height if outer_height else random.uniform(40, 100)
        self.wall_thickness = wall_thickness if wall_thickness else random.uniform(3, 8)

        self.inner_length = self.outer_length - 2 * self.wall_thickness
        self.inner_width = self.outer_width - 2 * self.wall_thickness
        self.inner_height = self.outer_height - self.wall_thickness  # 顶部开口

        self.dimensions = {
            'outer_length': self.outer_length,
            'outer_width': self.outer_width,
            'outer_height': self.outer_height,
            'wall_thickness': self.wall_thickness
        }

        self._create_shape()

    def _create_shape(self):
        """创建箱体形状"""
        # 创建外壳
        outer_box = make_box(self.outer_length, self.outer_width, self.outer_height)

        # 创建内腔
        inner_origin = gp_Pnt(self.wall_thickness, self.wall_thickness, self.wall_thickness)
        inner_box = make_box(self.inner_length, self.inner_width, self.inner_height, inner_origin)

        # 布尔减运算得到空心箱体
        self.shape = BRepAlgoAPI_Cut(outer_box, inner_box).Shape()

    def get_outer_face_bounds(self):
        """获取外表面边界"""
        return (0, self.outer_length, 0, self.outer_width)


class BracketBase(BasePart):
    """支架类零件基体(L型)"""
    def __init__(self, base_length=None, base_width=None, base_thickness=None,
                 vertical_height=None, vertical_thickness=None):
        super().__init__()
        self.part_type = "bracket"

        # 随机生成尺寸或使用指定尺寸
        self.base_length = base_length if base_length else random.uniform(50, 120)
        self.base_width = base_width if base_width else random.uniform(40, 100)
        self.base_thickness = base_thickness if base_thickness else random.uniform(5, 15)
        self.vertical_height = vertical_height if vertical_height else random.uniform(40, 100)
        self.vertical_thickness = vertical_thickness if vertical_thickness else random.uniform(5, 15)

        self.dimensions = {
            'base_length': self.base_length,
            'base_width': self.base_width,
            'base_thickness': self.base_thickness,
            'vertical_height': self.vertical_height,
            'vertical_thickness': self.vertical_thickness
        }

        self._create_shape()

    def _create_shape(self):
        """创建L型支架形状"""
        # 创建底板
        base_plate = make_box(self.base_length, self.base_width, self.base_thickness)

        # 创建竖板
        vertical_origin = gp_Pnt(0, 0, self.base_thickness)
        vertical_plate = make_box(self.base_length, self.vertical_thickness, self.vertical_height,
                                  vertical_origin)

        # 合并
        self.shape = BRepAlgoAPI_Fuse(base_plate, vertical_plate).Shape()

    def get_base_face_bounds(self):
        """获取底板表面边界"""
        return (0, self.base_length, 0, self.base_width)

    def get_vertical_face_bounds(self):
        """获取竖板表面边界"""
        return (0, self.base_length, self.base_thickness, self.base_thickness + self.vertical_height)


class FlangeBase(BasePart):
    """法兰类零件基体"""
    def __init__(self, outer_diameter=None, inner_diameter=None, thickness=None):
        super().__init__()
        self.part_type = "flange"

        # 随机生成尺寸或使用指定尺寸
        self.outer_diameter = outer_diameter if outer_diameter else random.uniform(60, 150)
        self.inner_diameter = inner_diameter if inner_diameter else random.uniform(20, self.outer_diameter * 0.6)
        self.thickness = thickness if thickness else random.uniform(8, 25)

        self.dimensions = {
            'outer_diameter': self.outer_diameter,
            'inner_diameter': self.inner_diameter,
            'thickness': self.thickness,
            'outer_radius': self.outer_diameter / 2.0,
            'inner_radius': self.inner_diameter / 2.0
        }

        self._create_shape()

    def _create_shape(self):
        """创建法兰形状"""
        # 创建外圆柱
        outer_cylinder = make_cylinder(self.outer_diameter / 2.0, self.thickness)

        # 创建内圆柱(中心孔)
        inner_cylinder = make_cylinder(self.inner_diameter / 2.0, self.thickness)

        # 布尔减运算
        self.shape = BRepAlgoAPI_Cut(outer_cylinder, inner_cylinder).Shape()

    def get_face_bounds(self):
        """获取法兰表面的圆环区域边界"""
        r_inner = self.inner_diameter / 2.0 + 5  # 内半径加间隙
        r_outer = self.outer_diameter / 2.0 - 5  # 外半径减间隙
        return (r_inner, r_outer)


# 工厂函数,用于随机生成基体
def create_random_base_part():
    """随机创建一个基体零件"""
    part_types = [PlateBase, BlockBase, ShaftBase, BoxBase, BracketBase, FlangeBase]
    weights = [0.25, 0.20, 0.20, 0.15, 0.10, 0.10]  # 各类型权重

    chosen_type = random.choices(part_types, weights=weights)[0]
    return chosen_type()
