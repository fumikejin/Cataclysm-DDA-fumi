"""
测试工具模块 - Point 类
"""

import pytest
from src.utils.point import Point, Tripoint, DIRECTION_NORTH, DIRECTION_EAST


def test_point_creation():
    """测试点的创建"""
    p = Point(3, 4)
    assert p.x == 3
    assert p.y == 4


def test_point_addition():
    """测试点的加法"""
    p1 = Point(1, 2)
    p2 = Point(3, 4)
    result = p1 + p2
    assert result.x == 4
    assert result.y == 6


def test_point_subtraction():
    """测试点的减法"""
    p1 = Point(5, 7)
    p2 = Point(2, 3)
    result = p1 - p2
    assert result.x == 3
    assert result.y == 4


def test_point_distance():
    """测试欧几里得距离"""
    p1 = Point(0, 0)
    p2 = Point(3, 4)
    distance = p1.distance_to(p2)
    assert distance == 5.0


def test_point_manhattan_distance():
    """测试曼哈顿距离"""
    p1 = Point(0, 0)
    p2 = Point(3, 4)
    distance = p1.manhattan_distance_to(p2)
    assert distance == 7


def test_tripoint_creation():
    """测试三维点的创建"""
    tp = Tripoint(1, 2, 3)
    assert tp.x == 1
    assert tp.y == 2
    assert tp.z == 3


def test_tripoint_addition():
    """测试三维点的加法"""
    tp1 = Tripoint(1, 2, 3)
    tp2 = Tripoint(4, 5, 6)
    result = tp1 + tp2
    assert result.x == 5
    assert result.y == 7
    assert result.z == 9


def test_tripoint_to_point():
    """测试三维点转二维点"""
    tp = Tripoint(5, 7, 2)
    p = tp.xy()
    assert p.x == 5
    assert p.y == 7


def test_direction_constants():
    """测试方向常量"""
    assert DIRECTION_NORTH.x == 0
    assert DIRECTION_NORTH.y == -1
    assert DIRECTION_EAST.x == 1
    assert DIRECTION_EAST.y == 0
