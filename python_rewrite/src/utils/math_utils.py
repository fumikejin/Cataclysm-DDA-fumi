"""
工具模块 - 数学工具

提供常用的数学计算函数
"""

import math
import random
from typing import Tuple

from .point import Point, Tripoint


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    将值限制在指定范围内

    Args:
        value: 要限制的值
        min_value: 最小值
        max_value: 最大值

    Returns:
        限制后的值
    """
    return max(min_value, min(value, max_value))


def lerp(start: float, end: float, t: float) -> float:
    """
    线性插值

    Args:
        start: 起始值
        end: 结束值
        t: 插值参数 (0.0 到 1.0)

    Returns:
        插值结果
    """
    return start + (end - start) * t


def distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    计算二维欧几里得距离

    Args:
        x1, y1: 第一个点的坐标
        x2, y2: 第二个点的坐标

    Returns:
        距离
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def distance_3d(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    """
    计算三维欧几里得距离

    Args:
        x1, y1, z1: 第一个点的坐标
        x2, y2, z2: 第二个点的坐标

    Returns:
        距离
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def manhattan_distance_2d(x1: int, y1: int, x2: int, y2: int) -> int:
    """
    计算二维曼哈顿距离

    Args:
        x1, y1: 第一个点的坐标
        x2, y2: 第二个点的坐标

    Returns:
        曼哈顿距离
    """
    return abs(x2 - x1) + abs(y2 - y1)


def angle_between(p1: Point, p2: Point) -> float:
    """
    计算两点之间的角度（弧度）

    Args:
        p1: 第一个点
        p2: 第二个点

    Returns:
        角度（弧度）
    """
    return math.atan2(p2.y - p1.y, p2.x - p1.x)


def angle_to_degrees(radians: float) -> float:
    """
    将弧度转换为角度

    Args:
        radians: 弧度值

    Returns:
        角度值
    """
    return math.degrees(radians)


def degrees_to_radians(degrees: float) -> float:
    """
    将角度转换为弧度

    Args:
        degrees: 角度值

    Returns:
        弧度值
    """
    return math.radians(degrees)


def roll_dice(num_dice: int, num_sides: int) -> int:
    """
    掷骰子

    Args:
        num_dice: 骰子数量
        num_sides: 每个骰子的面数

    Returns:
        总点数
    """
    return sum(random.randint(1, num_sides) for _ in range(num_dice))


def random_range(min_value: float, max_value: float) -> float:
    """
    生成指定范围内的随机浮点数

    Args:
        min_value: 最小值
        max_value: 最大值

    Returns:
        随机值
    """
    return random.uniform(min_value, max_value)


def random_int(min_value: int, max_value: int) -> int:
    """
    生成指定范围内的随机整数

    Args:
        min_value: 最小值（包含）
        max_value: 最大值（包含）

    Returns:
        随机整数
    """
    return random.randint(min_value, max_value)


def chance(probability: float) -> bool:
    """
    按概率返回 True 或 False

    Args:
        probability: 概率值 (0.0 到 1.0)

    Returns:
        是否触发
    """
    return random.random() < probability


def one_in(n: int) -> bool:
    """
    1/n 的概率返回 True

    Args:
        n: 分母

    Returns:
        是否触发
    """
    return random.randint(1, n) == 1


def direction_from(from_pos: Point, to_pos: Point) -> Point:
    """
    获取从一个点指向另一个点的单位方向向量

    Args:
        from_pos: 起始点
        to_pos: 目标点

    Returns:
        方向向量（归一化）
    """
    dx = to_pos.x - from_pos.x
    dy = to_pos.y - from_pos.y

    # 归一化
    if dx == 0 and dy == 0:
        return Point(0, 0)

    # 返回八方向之一
    if abs(dx) > abs(dy):
        return Point(1 if dx > 0 else -1, 0)
    elif abs(dy) > abs(dx):
        return Point(0, 1 if dy > 0 else -1)
    else:
        return Point(1 if dx > 0 else -1, 1 if dy > 0 else -1)


def get_line(start: Point, end: Point) -> list[Point]:
    """
    获取从起点到终点的直线上的所有点（Bresenham 算法）

    Args:
        start: 起点
        end: 终点

    Returns:
        直线上的点列表
    """
    points = []
    x0, y0 = start.x, start.y
    x1, y1 = end.x, end.y

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        points.append(Point(x0, y0))

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return points


def circle_points(center: Point, radius: int) -> list[Point]:
    """
    获取以指定点为中心，指定半径的圆上的所有点

    Args:
        center: 圆心
        radius: 半径

    Returns:
        圆上的点列表
    """
    points = []
    for x in range(center.x - radius, center.x + radius + 1):
        for y in range(center.y - radius, center.y + radius + 1):
            if distance_2d(center.x, center.y, x, y) <= radius:
                points.append(Point(x, y))
    return points
