"""
测试游戏世界 - 地图系统
"""

from src.utils.point import Tripoint
from src.world.map import Map
from src.world.coordinates import SUBMAP_SIZE


def test_map_creation():
    """测试地图创建"""
    game_map = Map()
    assert game_map is not None
    assert game_map.get_submap_count() == 0


def test_get_submap():
    """测试获取子地图"""
    game_map = Map()
    
    # 第一次获取应该创建子地图
    submap = game_map.get_submap(0, 0, 0)
    assert submap is not None
    assert submap.x == 0
    assert submap.y == 0
    assert submap.z == 0
    assert game_map.get_submap_count() == 1
    
    # 再次获取应该返回同一个子地图
    submap2 = game_map.get_submap(0, 0, 0)
    assert submap2 is submap


def test_get_tile():
    """测试获取格子"""
    game_map = Map()
    
    # 获取格子
    tile = game_map.get_tile(Tripoint(0, 0, 0))
    assert tile is not None
    
    # 获取不同位置的格子
    tile2 = game_map.get_tile(Tripoint(15, 15, 0))
    assert tile2 is not None
    assert tile2 is not tile


def test_set_terrain():
    """测试设置地形"""
    game_map = Map()
    
    pos = Tripoint(5, 5, 0)
    game_map.set_terrain(pos, "t_wall")
    
    tile = game_map.get_tile(pos)
    assert tile.terrain_id == "t_wall"


def test_set_furniture():
    """测试设置家具"""
    game_map = Map()
    
    pos = Tripoint(5, 5, 0)
    game_map.set_furniture(pos, "f_chair")
    
    tile = game_map.get_tile(pos)
    assert tile.furniture_id == "f_chair"


def test_is_passable():
    """测试可通行性检查"""
    game_map = Map()
    
    # 草地应该可通行
    pos1 = Tripoint(0, 0, 0)
    game_map.set_terrain(pos1, "t_grass")
    assert game_map.is_passable(pos1) is True
    
    # 墙壁不可通行
    pos2 = Tripoint(1, 0, 0)
    game_map.set_terrain(pos2, "t_wall")
    assert game_map.is_passable(pos2) is False


def test_generate_test_map():
    """测试生成测试地图"""
    game_map = Map()
    
    center = Tripoint(0, 0, 0)
    game_map.generate_test_map(center, radius=30)
    
    # 应该生成了一些子地图
    assert game_map.get_submap_count() > 0
    
    # 中心附近应该有地形
    tile = game_map.get_tile(center)
    assert tile is not None
