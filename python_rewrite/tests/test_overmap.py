"""
测试大地图系统 (Overmap)
"""

import pytest
from src.utils.point import Tripoint
from src.world.overmap import (
    Overmap, OmTile, OmNote, OmSpecial, OmTerrainManager,
    tile_to_omt, omt_to_tile, submap_to_omt,
    OVERMAP_SIZE, OMT_SIZE
)


class TestOmTerrainManager:
    """测试大地图地形管理器"""
    
    def test_init_default_terrains(self):
        """测试默认地形初始化"""
        manager = OmTerrainManager()
        
        # 应该加载多种地形
        assert len(manager.terrains) > 20
        
        # 检查基础地形
        assert "field" in manager.terrains
        assert "forest" in manager.terrains
        assert "road" in manager.terrains
        assert "house" in manager.terrains
    
    def test_get_terrain(self):
        """测试获取地形数据"""
        manager = OmTerrainManager()
        
        field = manager.get_terrain("field")
        assert field is not None
        assert field.id == "field"
        assert field.name == "原野"
        assert field.symbol == "."
        
        # 不存在的地形
        assert manager.get_terrain("nonexistent") is None
    
    def test_terrain_properties(self):
        """测试地形属性"""
        manager = OmTerrainManager()
        
        # 原野允许建营地
        field = manager.get_terrain("field")
        assert field.allows_camp is True
        
        # 河流是水域
        river = manager.get_terrain("river")
        assert river.is_water is True
        
        # 道路是道路类型
        road = manager.get_terrain("road")
        assert road.is_road is True


class TestOmTile:
    """测试大地图格子"""
    
    def test_init(self):
        """测试初始化"""
        tile = OmTile()
        assert tile.terrain_id == "field"
        assert tile.seen is False
        assert tile.explored is False
        assert tile.note is None
        assert len(tile.specials) == 0
        
        tile2 = OmTile("forest")
        assert tile2.terrain_id == "forest"
    
    def test_add_special(self):
        """测试添加特殊位置"""
        tile = OmTile()
        special = OmSpecial("hospital_entrance", "医院入口")
        
        tile.add_special(special)
        assert len(tile.specials) == 1
        assert tile.has_special("hospital_entrance")
    
    def test_remove_special(self):
        """测试移除特殊位置"""
        tile = OmTile()
        special1 = OmSpecial("s1", "位置1")
        special2 = OmSpecial("s2", "位置2")
        
        tile.add_special(special1)
        tile.add_special(special2)
        assert len(tile.specials) == 2
        
        tile.remove_special("s1")
        assert len(tile.specials) == 1
        assert not tile.has_special("s1")
        assert tile.has_special("s2")


class TestOvermap:
    """测试大地图"""
    
    def test_init(self):
        """测试初始化"""
        overmap = Overmap()
        
        assert overmap.position == Tripoint(0, 0, 0)
        assert len(overmap.tiles) == 3  # Z层: -1, 0, 1
        assert len(overmap.tiles[0]) == OVERMAP_SIZE
        assert len(overmap.tiles[0][0]) == OVERMAP_SIZE
    
    def test_custom_position(self):
        """测试自定义位置"""
        pos = Tripoint(5, 10, 0)
        overmap = Overmap(pos)
        assert overmap.position == pos
    
    def test_is_valid_pos(self):
        """测试位置有效性检查"""
        overmap = Overmap()
        
        # 有效位置
        assert overmap.is_valid_pos(Tripoint(0, 0, 0))
        assert overmap.is_valid_pos(Tripoint(OVERMAP_SIZE - 1, OVERMAP_SIZE - 1, 0))
        assert overmap.is_valid_pos(Tripoint(50, 50, -1))
        assert overmap.is_valid_pos(Tripoint(50, 50, 1))
        
        # 无效位置
        assert not overmap.is_valid_pos(Tripoint(-1, 0, 0))
        assert not overmap.is_valid_pos(Tripoint(0, -1, 0))
        assert not overmap.is_valid_pos(Tripoint(OVERMAP_SIZE, 0, 0))
        assert not overmap.is_valid_pos(Tripoint(0, OVERMAP_SIZE, 0))
        assert not overmap.is_valid_pos(Tripoint(0, 0, -2))
        assert not overmap.is_valid_pos(Tripoint(0, 0, 2))
    
    def test_get_set_tile(self):
        """测试获取和设置格子"""
        overmap = Overmap()
        pos = Tripoint(10, 20, 0)
        
        # 获取格子
        tile = overmap.get_tile(pos)
        assert tile is not None
        assert tile.terrain_id == "field"  # 默认地形
        
        # 设置地形
        overmap.set_terrain(pos, "forest")
        tile = overmap.get_tile(pos)
        assert tile.terrain_id == "forest"
        
        # 无效位置
        assert overmap.get_tile(Tripoint(-1, 0, 0)) is None
    
    def test_get_terrain(self):
        """测试获取地形ID"""
        overmap = Overmap()
        pos = Tripoint(15, 25, 0)
        
        # 默认地形
        assert overmap.get_terrain(pos) == "field"
        
        # 设置后获取
        overmap.set_terrain(pos, "road")
        assert overmap.get_terrain(pos) == "road"
        
        # 无效位置
        assert overmap.get_terrain(Tripoint(-1, 0, 0)) is None
    
    def test_reveal(self):
        """测试揭示区域"""
        overmap = Overmap()
        center = Tripoint(50, 50, 0)
        
        # 揭示中心点
        overmap.reveal(center, 0)
        assert overmap.is_seen(center)
        
        # 揭示周围区域
        overmap.reveal(center, 2)
        assert overmap.is_seen(Tripoint(50, 50, 0))
        assert overmap.is_seen(Tripoint(51, 50, 0))
        assert overmap.is_seen(Tripoint(50, 51, 0))
        assert overmap.is_seen(Tripoint(52, 52, 0))
    
    def test_explore(self):
        """测试标记探索状态"""
        overmap = Overmap()
        pos = Tripoint(30, 40, 0)
        
        assert not overmap.is_explored(pos)
        assert not overmap.is_seen(pos)
        
        overmap.explore(pos)
        
        assert overmap.is_explored(pos)
        assert overmap.is_seen(pos)  # 探索后也会标记为已发现
    
    def test_notes(self):
        """测试笔记功能"""
        overmap = Overmap()
        pos = Tripoint(60, 70, 0)
        
        # 添加笔记
        overmap.add_note(pos, "这里有一个地堡", "!", "red")
        note = overmap.get_note(pos)
        
        assert note is not None
        assert note.text == "这里有一个地堡"
        assert note.symbol == "!"
        assert note.color == "red"
        
        # 移除笔记
        overmap.remove_note(pos)
        assert overmap.get_note(pos) is None
    
    def test_add_special(self):
        """测试添加特殊位置"""
        overmap = Overmap()
        pos = Tripoint(80, 90, 0)
        
        special = OmSpecial("hospital_1", "医院", "中央医院")
        overmap.add_special(pos, special)
        
        tile = overmap.get_tile(pos)
        assert tile.has_special("hospital_1")
        assert "hospital_1" in overmap.discovered_locations
    
    def test_find_special(self):
        """测试查找特殊位置"""
        overmap = Overmap()
        
        pos1 = Tripoint(10, 10, 0)
        pos2 = Tripoint(20, 20, 0)
        
        special1 = OmSpecial("quest_target_1", "任务目标")
        special2 = OmSpecial("quest_target_2", "任务目标2")
        
        overmap.add_special(pos1, special1)
        overmap.add_special(pos2, special2)
        
        # 查找存在的特殊位置
        found_pos = overmap.find_special("quest_target_1")
        assert found_pos == pos1
        
        found_pos2 = overmap.find_special("quest_target_2")
        assert found_pos2 == pos2
        
        # 查找不存在的特殊位置
        assert overmap.find_special("nonexistent") is None
    
    def test_find_terrain(self):
        """测试查找地形"""
        overmap = Overmap()
        start = Tripoint(50, 50, 0)
        
        # 设置一些森林
        forest_pos = Tripoint(55, 55, 0)
        overmap.set_terrain(forest_pos, "forest")
        
        # 查找最近的森林
        found = overmap.find_terrain("forest", start, max_dist=10)
        assert found == forest_pos
        
        # 查找不存在的地形
        found = overmap.find_terrain("ocean", start, max_dist=5)
        assert found is None
    
    def test_generate_simple(self):
        """测试简单地图生成"""
        overmap = Overmap()
        overmap.generate_simple()
        
        # 检查中心区域有道路
        center = OVERMAP_SIZE // 2
        center_pos = Tripoint(center, center, 0)
        
        # 周围应该有一些道路
        road_count = 0
        for dy in range(-10, 10):
            for dx in range(-10, 10):
                pos = Tripoint(center + dx, center + dy, 0)
                if overmap.get_terrain(pos) == "road":
                    road_count += 1
        
        assert road_count > 0
        
        # 应该有一些特殊建筑
        assert len(overmap.discovered_locations) > 0
    
    def test_serialization(self):
        """测试序列化和反序列化"""
        overmap = Overmap(Tripoint(1, 2, 0))
        
        # 设置一些数据
        pos1 = Tripoint(10, 10, 0)
        pos2 = Tripoint(20, 20, 0)
        
        overmap.set_terrain(pos1, "forest")
        overmap.set_terrain(pos2, "road")
        overmap.explore(pos1)
        overmap.add_note(pos2, "测试笔记", "T", "blue")
        overmap.add_special(pos1, OmSpecial("test_special", "测试位置"))
        
        # 序列化
        data = overmap.to_dict()
        
        assert data["position"] == [1, 2, 0]
        assert len(data["tiles"]) >= 2  # 至少有2个非默认格子
        assert "test_special" in data["discovered_locations"]
        
        # 反序列化
        overmap2 = Overmap.from_dict(data)
        
        assert overmap2.position == Tripoint(1, 2, 0)
        assert overmap2.get_terrain(pos1) == "forest"
        assert overmap2.get_terrain(pos2) == "road"
        assert overmap2.is_explored(pos1)
        assert overmap2.get_note(pos2) is not None
        assert overmap2.get_note(pos2).text == "测试笔记"
        assert "test_special" in overmap2.discovered_locations


class TestCoordinateConversions:
    """测试坐标转换函数"""
    
    def test_tile_to_omt(self):
        """测试格子坐标到OMT坐标转换"""
        # 一个OMT = 2个子地图 = 24个格子
        # (0,0,0) 格子 -> (0,0,0) OMT
        assert tile_to_omt(Tripoint(0, 0, 0)) == Tripoint(0, 0, 0)
        
        # (24,24,0) 格子 -> (1,1,0) OMT
        assert tile_to_omt(Tripoint(24, 24, 0)) == Tripoint(1, 1, 0)
        
        # (48,48,0) 格子 -> (2,2,0) OMT
        assert tile_to_omt(Tripoint(48, 48, 0)) == Tripoint(2, 2, 0)
        
        # (23,23,0) 格子 -> (0,0,0) OMT (仍在第一个OMT内)
        assert tile_to_omt(Tripoint(23, 23, 0)) == Tripoint(0, 0, 0)
    
    def test_omt_to_tile(self):
        """测试OMT坐标到格子坐标转换"""
        # (0,0,0) OMT -> (0,0,0) 格子（左上角）
        assert omt_to_tile(Tripoint(0, 0, 0)) == Tripoint(0, 0, 0)
        
        # (1,1,0) OMT -> (24,24,0) 格子
        assert omt_to_tile(Tripoint(1, 1, 0)) == Tripoint(24, 24, 0)
        
        # (2,3,0) OMT -> (48,72,0) 格子
        assert omt_to_tile(Tripoint(2, 3, 0)) == Tripoint(48, 72, 0)
    
    def test_submap_to_omt(self):
        """测试子地图坐标到OMT坐标转换"""
        # 一个OMT = 2个子地图
        # (0,0,0) 子地图 -> (0,0,0) OMT
        assert submap_to_omt(Tripoint(0, 0, 0)) == Tripoint(0, 0, 0)
        
        # (1,1,0) 子地图 -> (0,0,0) OMT (仍在第一个OMT内)
        assert submap_to_omt(Tripoint(1, 1, 0)) == Tripoint(0, 0, 0)
        
        # (2,2,0) 子地图 -> (1,1,0) OMT
        assert submap_to_omt(Tripoint(2, 2, 0)) == Tripoint(1, 1, 0)
        
        # (4,6,0) 子地图 -> (2,3,0) OMT
        assert submap_to_omt(Tripoint(4, 6, 0)) == Tripoint(2, 3, 0)
    
    def test_round_trip_conversion(self):
        """测试往返转换"""
        # OMT -> 格子 -> OMT 应该返回原始OMT
        omt_pos = Tripoint(5, 10, 0)
        tile_pos = omt_to_tile(omt_pos)
        omt_pos2 = tile_to_omt(tile_pos)
        assert omt_pos == omt_pos2
