"""
工具模块 - 坐标点类

提供二维和三维坐标点的基础实现
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Point:
    """二维坐标点"""

    x: int
    y: int

    def __add__(self, other: "Point") -> "Point":
        """点加法"""
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        """点减法"""
        return Point(self.x - other.x, self.y - other.y)

    def distance_to(self, other: "Point") -> float:
        """计算到另一点的欧几里得距离"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def manhattan_distance_to(self, other: "Point") -> int:
        """计算到另一点的曼哈顿距离"""
        return abs(self.x - other.x) + abs(self.y - other.y)

    def to_tuple(self) -> Tuple[int, int]:
        """转换为元组"""
        return (self.x, self.y)


@dataclass(frozen=True)
class Tripoint:
    """三维坐标点"""

    x: int
    y: int
    z: int

    def __add__(self, other: "Tripoint") -> "Tripoint":
        """点加法"""
        return Tripoint(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Tripoint") -> "Tripoint":
        """点减法"""
        return Tripoint(self.x - other.x, self.y - other.y, self.z - other.z)

    def distance_to(self, other: "Tripoint") -> float:
        """计算到另一点的欧几里得距离"""
        return (
            (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
        ) ** 0.5

    def xy(self) -> Point:
        """获取 XY 平面坐标"""
        return Point(self.x, self.y)

    def to_tuple(self) -> Tuple[int, int, int]:
        """转换为元组"""
        return (self.x, self.y, self.z)


# 方向常量
DIRECTION_NORTH = Point(0, -1)
DIRECTION_SOUTH = Point(0, 1)
DIRECTION_EAST = Point(1, 0)
DIRECTION_WEST = Point(-1, 0)
DIRECTION_NORTHEAST = Point(1, -1)
DIRECTION_NORTHWEST = Point(-1, -1)
DIRECTION_SOUTHEAST = Point(1, 1)
DIRECTION_SOUTHWEST = Point(-1, 1)

# 所有八个方向
ALL_DIRECTIONS = [
    DIRECTION_NORTH,
    DIRECTION_NORTHEAST,
    DIRECTION_EAST,
    DIRECTION_SOUTHEAST,
    DIRECTION_SOUTH,
    DIRECTION_SOUTHWEST,
    DIRECTION_WEST,
    DIRECTION_NORTHWEST,
]
