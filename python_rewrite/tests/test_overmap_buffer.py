"""
测试大地图缓冲区系统
"""

import pytest
import os
import shutil
import tempfile

from src.world.overmap_buffer import OvermapBuffer, OvermapMetadata
from src.world.overmap import Overmap, OmTile, OVERMAP_SIZE
from src.utils.point import Tripoint


@pytest.fixture
def temp_save_dir():
    """创建临时保存目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # 清理
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def test_overmap_buffer_creation(temp_save_dir):
    """测试大地图缓冲区创建"""
    buffer = OvermapBuffer(save_dir=temp_save_dir, cache_size=5)
    assert buffer is not None
    assert buffer.cache_size == 5
    assert os.path.exists(temp_save_dir)


def test_get_overmap_at(temp_save_dir):
    """测试获取大地图"""
    buffer = OvermapBuffer(save_dir=temp_save_dir)
    
    # 获取(0,0,0)处的大地图
    om_pos = Tripoint(0, 0, 0)
    overmap = buffer.get_overmap_at(om_pos)
    
    assert overmap is not None
    assert len(buffer.overmaps) == 1


def test_overmap_coords_conversion(temp_save_dir):
    """测试大地图坐标转换"""
    buffer = OvermapBuffer(save_dir=temp_save_dir)
    
    # 测试不同的OMT坐标
    test_cases = [
        (Tripoint(0, 0, 0), (0, 0, 0)),
        (Tripoint(180, 0, 0), (1, 0, 0)),  # 下一个大地图
        (Tripoint(-180, 0, 0), (-1, 0, 0)),  # 负方向
        (Tripoint(90, 90, 0), (0, 0, 0)),  # 同一个大地图内
        (Tripoint(200, 200, 1), (1, 1, 1)),  # 不同Z层
    ]
    
    for om_pos, expected_coords in test_cases:
        coords = buffer._overmap_coords_from_om_pos(om_pos)
        assert coords == expected_coords


def test_local_om_coords(temp_save_dir):
    """测试本地OMT坐标转换"""
    buffer = OvermapBuffer(save_dir=temp_save_dir)
    
    # 测试坐标转换
    test_cases = [
        (Tripoint(0, 0, 0), Tripoint(0, 0, 0)),
        (Tripoint(90, 90, 0), Tripoint(90, 90, 0)),
        (Tripoint(180, 0, 0), Tripoint(0, 0, 0)),  # 回绕到0
        (Tripoint(185, 5, 0), Tripoint(5, 5, 0)),
    ]
    
    for global_pos, expected_local in test_cases:
        local_pos = buffer._local_om_coords(global_pos)
        assert local_pos.x == expected_local.x
        assert local_pos.y == expected_local.y


def test_get_tile(temp_save_dir):
    """测试获取大地图格子"""
    buffer = OvermapBuffer(save_dir=temp_save_dir)
    
    om_pos = Tripoint(10, 10, 0)
    tile = buffer.get_tile(om_pos)
    
    assert tile is not None
    assert isinstance(tile, OmTile)
    assert tile.terrain_id == "field"  # 默认地形


def test_set_tile_terrain(temp_save_dir):
    """测试设置大地图格子地形"""
    buffer = OvermapBuffer(save_dir=temp_save_dir)
    
    om_pos = Tripoint(10, 10, 0)
    buffer.set_tile_terrain(om_pos, "forest")
    
    tile = buffer.get_tile(om_pos)
    assert tile.terrain_id == "forest"


def test_mark_seen(temp_save_dir):
    """测试标记已见过"""
    buffer = OvermapBuffer(save_dir=temp_save_dir)
    
    om_pos = Tripoint(15, 15, 0)
    tile = buffer.get_tile(om_pos)
    assert not tile.seen
    
    buffer.mark_seen(om_pos)
    tile = buffer.get_tile(om_pos)
    assert tile.seen


def test_is_explored(temp_save_dir):
    """测试探索状态"""
    buffer = OvermapBuffer(save_dir=temp_save_dir)
    
    om_pos = Tripoint(20, 20, 0)
    assert not buffer.is_explored(om_pos)
    
    # 手动设置探索状态
    tile = buffer.get_tile(om_pos)
    tile.explored = True
    
    assert buffer.is_explored(om_pos)


def test_cache_lru_eviction(temp_save_dir):
    """测试LRU缓存淘汰"""
    buffer = OvermapBuffer(save_dir=temp_save_dir, cache_size=3)
    
    # 加载多个大地图
    positions = [
        Tripoint(0, 0, 0),
        Tripoint(180, 0, 0),
        Tripoint(360, 0, 0),
        Tripoint(540, 0, 0),  # 这个会导致缓存溢出
    ]
    
    for pos in positions:
        buffer.get_overmap_at(pos)
    
    # 缓存大小应该保持为3
    assert len(buffer.overmaps) == 3


def test_save_and_load_overmap(temp_save_dir):
    """测试保存和加载大地图"""
    buffer = OvermapBuffer(save_dir=temp_save_dir)
    
    # 修改一个大地图
    om_pos = Tripoint(50, 50, 0)
    buffer.set_tile_terrain(om_pos, "city_house")
    buffer.mark_seen(om_pos)
    
    # 保存所有大地图
    buffer.save_all()
    
    # 清空缓存
    buffer.overmaps.clear()
    buffer.metadata.clear()
    
    # 重新加载
    tile = buffer.get_tile(om_pos)
    assert tile.terrain_id == "city_house"
    assert tile.seen


def test_preload_region(temp_save_dir):
    """测试预加载区域"""
    buffer = OvermapBuffer(save_dir=temp_save_dir, cache_size=10)
    
    center_pos = Tripoint(180, 180, 0)  # 位于(1,1,0)大地图中
    buffer.preload_region(center_pos, radius=1)
    
    # 应该加载3x3=9个大地图
    assert len(buffer.overmaps) == 9


def test_get_terrain_at(temp_save_dir):
    """测试获取指定位置的地形"""
    buffer = OvermapBuffer(save_dir=temp_save_dir)
    
    om_pos = Tripoint(30, 30, 0)
    
    # 默认地形
    assert buffer.get_terrain_at(om_pos) == "field"
    
    # 设置新地形
    buffer.set_tile_terrain(om_pos, "forest")
    assert buffer.get_terrain_at(om_pos) == "forest"


def test_find_nearest_terrain(temp_save_dir):
    """测试查找最近的地形"""
    buffer = OvermapBuffer(save_dir=temp_save_dir)
    
    # 设置一些地形
    start_pos = Tripoint(50, 50, 0)
    forest_pos = Tripoint(55, 52, 0)
    buffer.set_tile_terrain(forest_pos, "forest")
    
    # 查找最近的森林
    found_pos = buffer.find_nearest_terrain(start_pos, "forest", max_distance=10)
    
    assert found_pos is not None
    assert found_pos.x == forest_pos.x
    assert found_pos.y == forest_pos.y


def test_clear_cache(temp_save_dir):
    """测试清空缓存"""
    buffer = OvermapBuffer(save_dir=temp_save_dir)
    
    # 加载几个大地图
    buffer.get_overmap_at(Tripoint(0, 0, 0))
    buffer.get_overmap_at(Tripoint(180, 0, 0))
    
    assert len(buffer.overmaps) > 0
    
    buffer.clear_cache()
    
    assert len(buffer.overmaps) == 0
    assert len(buffer.metadata) == 0


def test_get_cached_overmaps(temp_save_dir):
    """测试获取缓存的大地图列表"""
    buffer = OvermapBuffer(save_dir=temp_save_dir)
    
    # 加载几个大地图
    positions = [
        Tripoint(0, 0, 0),
        Tripoint(180, 0, 0),
        Tripoint(0, 180, 0),
    ]
    
    for pos in positions:
        buffer.get_overmap_at(pos)
    
    cached = buffer.get_cached_overmaps()
    assert len(cached) == 3
    
    # 检查坐标
    expected_coords = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
    for coords in expected_coords:
        assert coords in cached
