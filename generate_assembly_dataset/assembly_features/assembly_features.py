"""
Assembly feature classes for dataset generation
装配特征类定义
"""

import random
import sys
sys.path.append('../')
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Vec
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from Utils.geometry_utils import (make_threaded_hole, make_counterbore, make_countersink,
                                   make_key_slot, make_pin_hole, make_cylinder, make_bolt,
                                   make_pin, make_key)
from Utils.parameters import thread_diameters, pin_diameters, key_widths


class AssemblyFeature:
    """装配特征基类"""
    def __init__(self, feature_type):
        self.feature_type = feature_type
        self.shape = None
        self.position = None
        self.parameters = {}
        self.faces = []  # 该特征包含的面

    def get_shape(self):
        return self.shape

    def get_type(self):
        return self.feature_type

    def get_parameters(self):
        return self.parameters

    def get_faces(self):
        return self.faces


class ThreadedHole(AssemblyFeature):
    """螺纹通孔特征"""
    def __init__(self, diameter=None, depth=None, position=None):
        super().__init__("threaded_hole")

        self.diameter = diameter if diameter else random.choice(thread_diameters)
        self.depth = depth if depth else random.uniform(15, 50)
        self.position = position if position else gp_Pnt(0, 0, 0)

        self.parameters = {
            'diameter': self.diameter,
            'depth': self.depth,
            'position': (self.position.X(), self.position.Y(), self.position.Z())
        }

        self._create_shape()

    def _create_shape(self):
        """创建螺纹孔形状"""
        self.shape = make_threaded_hole(self.diameter, self.depth, self.position, gp_Dir(0, 0, 1))


class ThreadedBlindHole(AssemblyFeature):
    """螺纹盲孔特征"""
    def __init__(self, diameter=None, depth=None, position=None):
        super().__init__("threaded_blind_hole")

        self.diameter = diameter if diameter else random.choice(thread_diameters)
        self.depth = depth if depth else random.uniform(10, 30)
        self.position = position if position else gp_Pnt(0, 0, 0)

        self.parameters = {
            'diameter': self.diameter,
            'depth': self.depth,
            'position': (self.position.X(), self.position.Y(), self.position.Z())
        }

        self._create_shape()

    def _create_shape(self):
        """创建盲螺纹孔形状"""
        self.shape = make_threaded_hole(self.diameter, self.depth, self.position, gp_Dir(0, 0, -1))


class PinHole(AssemblyFeature):
    """销孔特征"""
    def __init__(self, diameter=None, depth=None, position=None, direction=None):
        super().__init__("pin_hole")

        self.diameter = diameter if diameter else random.choice(pin_diameters)
        self.depth = depth if depth else random.uniform(10, 40)
        self.position = position if position else gp_Pnt(0, 0, 0)
        self.direction = direction if direction else gp_Dir(0, 0, 1)

        self.parameters = {
            'diameter': self.diameter,
            'depth': self.depth,
            'position': (self.position.X(), self.position.Y(), self.position.Z()),
            'direction': (self.direction.X(), self.direction.Y(), self.direction.Z())
        }

        self._create_shape()

    def _create_shape(self):
        """创建销孔形状"""
        self.shape = make_pin_hole(self.diameter, self.depth, self.position, self.direction)


class KeySlot(AssemblyFeature):
    """键槽特征"""
    def __init__(self, width=None, length=None, depth=None, position=None):
        super().__init__("key_slot")

        self.width = width if width else random.choice(key_widths)
        self.length = length if length else random.uniform(15, 50)
        self.depth = depth if depth else self.width * 0.6  # 深度通常为宽度的0.6倍

        self.position = position if position else gp_Pnt(0, 0, 0)

        self.parameters = {
            'width': self.width,
            'length': self.length,
            'depth': self.depth,
            'position': (self.position.X(), self.position.Y(), self.position.Z())
        }

        self._create_shape()

    def _create_shape(self):
        """创建键槽形状"""
        self.shape = make_key_slot(self.width, self.length, self.depth, self.position)


class Counterbore(AssemblyFeature):
    """沉孔特征"""
    def __init__(self, hole_diameter=None, hole_depth=None, bore_diameter=None,
                 bore_depth=None, position=None):
        super().__init__("counterbore")

        self.hole_diameter = hole_diameter if hole_diameter else random.choice(thread_diameters)
        self.hole_depth = hole_depth if hole_depth else random.uniform(20, 50)
        self.bore_diameter = bore_diameter if bore_diameter else self.hole_diameter * 1.8
        self.bore_depth = bore_depth if bore_depth else random.uniform(3, 8)

        self.position = position if position else gp_Pnt(0, 0, 0)

        self.parameters = {
            'hole_diameter': self.hole_diameter,
            'hole_depth': self.hole_depth,
            'bore_diameter': self.bore_diameter,
            'bore_depth': self.bore_depth,
            'position': (self.position.X(), self.position.Y(), self.position.Z())
        }

        self._create_shape()

    def _create_shape(self):
        """创建沉孔形状"""
        self.shape = make_counterbore(self.hole_diameter, self.hole_depth,
                                      self.bore_diameter, self.bore_depth,
                                      self.position, gp_Dir(0, 0, -1))


class Countersink(AssemblyFeature):
    """沉头孔特征"""
    def __init__(self, hole_diameter=None, hole_depth=None, sink_diameter=None,
                 sink_angle=90, position=None):
        super().__init__("countersink")

        self.hole_diameter = hole_diameter if hole_diameter else random.choice(thread_diameters)
        self.hole_depth = hole_depth if hole_depth else random.uniform(20, 50)
        self.sink_diameter = sink_diameter if sink_diameter else self.hole_diameter * 2.0
        self.sink_angle = sink_angle

        self.position = position if position else gp_Pnt(0, 0, 0)

        self.parameters = {
            'hole_diameter': self.hole_diameter,
            'hole_depth': self.hole_depth,
            'sink_diameter': self.sink_diameter,
            'sink_angle': self.sink_angle,
            'position': (self.position.X(), self.position.Y(), self.position.Z())
        }

        self._create_shape()

    def _create_shape(self):
        """创建沉头孔形状"""
        self.shape = make_countersink(self.hole_diameter, self.hole_depth,
                                      self.sink_diameter, self.sink_angle,
                                      self.position, gp_Dir(0, 0, -1))


class PositioningHole(AssemblyFeature):
    """定位孔特征(较小直径的精确孔)"""
    def __init__(self, diameter=None, depth=None, position=None):
        super().__init__("positioning_hole")

        self.diameter = diameter if diameter else random.uniform(2, 6)
        self.depth = depth if depth else random.uniform(8, 20)
        self.position = position if position else gp_Pnt(0, 0, 0)

        self.parameters = {
            'diameter': self.diameter,
            'depth': self.depth,
            'position': (self.position.X(), self.position.Y(), self.position.Z())
        }

        self._create_shape()

    def _create_shape(self):
        """创建定位孔形状"""
        self.shape = make_pin_hole(self.diameter, self.depth, self.position, gp_Dir(0, 0, -1))


# 装配件类(增材特征)
class Bolt(AssemblyFeature):
    """螺栓特征"""
    def __init__(self, shaft_diameter=None, shaft_length=None, position=None):
        super().__init__("bolt")

        self.shaft_diameter = shaft_diameter if shaft_diameter else random.choice(thread_diameters)
        self.shaft_length = shaft_length if shaft_length else random.uniform(20, 60)
        self.head_diameter = self.shaft_diameter * 1.5
        self.head_height = self.shaft_diameter * 0.7

        self.position = position if position else gp_Pnt(0, 0, 0)

        self.parameters = {
            'shaft_diameter': self.shaft_diameter,
            'shaft_length': self.shaft_length,
            'head_diameter': self.head_diameter,
            'head_height': self.head_height,
            'position': (self.position.X(), self.position.Y(), self.position.Z())
        }

        self._create_shape()

    def _create_shape(self):
        """创建螺栓形状"""
        self.shape = make_bolt(self.head_diameter, self.head_height,
                              self.shaft_diameter, self.shaft_length,
                              self.position, gp_Dir(0, 0, 1))


class Pin(AssemblyFeature):
    """销钉特征"""
    def __init__(self, diameter=None, length=None, position=None, direction=None):
        super().__init__("pin")

        self.diameter = diameter if diameter else random.choice(pin_diameters)
        self.length = length if length else random.uniform(15, 40)
        self.position = position if position else gp_Pnt(0, 0, 0)
        self.direction = direction if direction else gp_Dir(0, 0, 1)

        self.parameters = {
            'diameter': self.diameter,
            'length': self.length,
            'position': (self.position.X(), self.position.Y(), self.position.Z()),
            'direction': (self.direction.X(), self.direction.Y(), self.direction.Z())
        }

        self._create_shape()

    def _create_shape(self):
        """创建销钉形状"""
        self.shape = make_pin(self.diameter, self.length, self.position, self.direction)


class Key(AssemblyFeature):
    """键特征"""
    def __init__(self, width=None, height=None, length=None, position=None):
        super().__init__("key")

        self.width = width if width else random.choice(key_widths)
        self.height = height if height else self.width * 0.6
        self.length = length if length else random.uniform(15, 50)
        self.position = position if position else gp_Pnt(0, 0, 0)

        self.parameters = {
            'width': self.width,
            'height': self.height,
            'length': self.length,
            'position': (self.position.X(), self.position.Y(), self.position.Z())
        }

        self._create_shape()

    def _create_shape(self):
        """创建键形状"""
        self.shape = make_key(self.width, self.height, self.length, self.position)


# 特征创建工厂函数
def create_random_subtractive_feature(feature_type=None):
    """随机创建减材装配特征"""
    if feature_type is None:
        feature_types = [ThreadedHole, ThreadedBlindHole, PinHole, KeySlot,
                        Counterbore, Countersink, PositioningHole]
        weights = [0.25, 0.20, 0.15, 0.15, 0.10, 0.10, 0.05]
        feature_class = random.choices(feature_types, weights=weights)[0]
    else:
        feature_map = {
            'threaded_hole': ThreadedHole,
            'threaded_blind_hole': ThreadedBlindHole,
            'pin_hole': PinHole,
            'key_slot': KeySlot,
            'counterbore': Counterbore,
            'countersink': Countersink,
            'positioning_hole': PositioningHole
        }
        feature_class = feature_map.get(feature_type, ThreadedHole)

    return feature_class()


def create_random_additive_feature(feature_type=None):
    """随机创建增材装配特征(装配件)"""
    if feature_type is None:
        feature_types = [Bolt, Pin, Key]
        weights = [0.6, 0.3, 0.1]
        feature_class = random.choices(feature_types, weights=weights)[0]
    else:
        feature_map = {
            'bolt': Bolt,
            'pin': Pin,
            'key': Key
        }
        feature_class = feature_map.get(feature_type, Bolt)

    return feature_class()
