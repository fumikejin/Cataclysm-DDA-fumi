"""
测试游戏世界 - 坐标系统
"""

from src.utils.point import Tripoint
from src.world.coordinates import Coordinates, SUBMAP_SIZE


def test_tile_to_submap():
    """测试格子坐标转子地图坐标"""
    # (0, 0, 0) -> (0, 0, 0)
    pos = Tripoint(0, 0, 0)
    submap_pos = Coordinates.tile_to_submap(pos)
    assert submap_pos.x == 0
    assert submap_pos.y == 0
    assert submap_pos.z == 0

    # (12, 12, 0) -> (1, 1, 0)
    pos = Tripoint(12, 12, 0)
    submap_pos = Coordinates.tile_to_submap(pos)
    assert submap_pos.x == 1
    assert submap_pos.y == 1

    # 负坐标
    pos = Tripoint(-1, -1, 0)
    submap_pos = Coordinates.tile_to_submap(pos)
    assert submap_pos.x == -1
    assert submap_pos.y == -1


def test_tile_local():
    """测试局部坐标"""
    # (0, 0, 0) -> (0, 0, 0)
    pos = Tripoint(0, 0, 0)
    local = Coordinates.tile_local(pos)
    assert local.x == 0
    assert local.y == 0

    # (13, 14, 0) -> (1, 2, 0)
    pos = Tripoint(13, 14, 0)
    local = Coordinates.tile_local(pos)
    assert local.x == 1
    assert local.y == 2


def test_submap_to_tile():
    """测试子地图坐标转格子坐标"""
    submap_pos = Tripoint(1, 1, 0)
    local_pos = Tripoint(5, 6, 0)
    
    tile_pos = Coordinates.submap_to_tile(submap_pos, local_pos)
    assert tile_pos.x == 17  # 1*12 + 5
    assert tile_pos.y == 18  # 1*12 + 6


def test_is_valid_local():
    """测试局部坐标有效性"""
    assert Coordinates.is_valid_local(Tripoint(0, 0, 0)) is True
    assert Coordinates.is_valid_local(Tripoint(11, 11, 0)) is True
    assert Coordinates.is_valid_local(Tripoint(12, 0, 0)) is False
    assert Coordinates.is_valid_local(Tripoint(-1, 0, 0)) is False


def test_in_reality_bubble():
    """测试现实泡泡检测"""
    center = Tripoint(0, 0, 0)
    
    # 中心点应该在泡泡内
    assert Coordinates.in_reality_bubble(center, center) is True
    
    # 60格内应该在泡泡内
    assert Coordinates.in_reality_bubble(center, Tripoint(30, 30, 0)) is True
    
    # 超过60格应该不在泡泡内
    assert Coordinates.in_reality_bubble(center, Tripoint(100, 0, 0)) is False
    
    # 不同Z层不在泡泡内
    assert Coordinates.in_reality_bubble(center, Tripoint(0, 0, 1)) is False
