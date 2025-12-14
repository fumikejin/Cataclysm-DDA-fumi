"""
测试工具模块 - 数学工具
"""

import pytest
from src.utils.math_utils import *
from src.utils.point import Point


def test_clamp():
    """测试限制值"""
    assert clamp(5, 0, 10) == 5
    assert clamp(-5, 0, 10) == 0
    assert clamp(15, 0, 10) == 10


def test_lerp():
    """测试线性插值"""
    assert lerp(0, 10, 0.0) == 0
    assert lerp(0, 10, 1.0) == 10
    assert lerp(0, 10, 0.5) == 5


def test_distance_2d():
    """测试二维距离"""
    assert distance_2d(0, 0, 3, 4) == 5.0
    assert distance_2d(0, 0, 0, 0) == 0.0


def test_manhattan_distance_2d():
    """测试曼哈顿距离"""
    assert manhattan_distance_2d(0, 0, 3, 4) == 7
    assert manhattan_distance_2d(0, 0, 0, 0) == 0


def test_roll_dice():
    """测试掷骰子"""
    for _ in range(10):
        result = roll_dice(1, 6)
        assert 1 <= result <= 6
    
    for _ in range(10):
        result = roll_dice(2, 6)
        assert 2 <= result <= 12


def test_random_int():
    """测试随机整数"""
    for _ in range(10):
        result = random_int(1, 10)
        assert 1 <= result <= 10


def test_direction_from():
    """测试方向向量"""
    p1 = Point(0, 0)
    p2 = Point(5, 0)
    direction = direction_from(p1, p2)
    assert direction.x == 1
    assert direction.y == 0


def test_get_line():
    """测试获取直线点"""
    start = Point(0, 0)
    end = Point(3, 0)
    line = get_line(start, end)
    
    assert len(line) == 4
    assert line[0] == start
    assert line[-1] == end


def test_circle_points():
    """测试圆形点"""
    center = Point(0, 0)
    radius = 1
    points = circle_points(center, radius)
    
    # 半径为1的圆应该包含中心和相邻的点
    assert center in points
    assert len(points) > 1
