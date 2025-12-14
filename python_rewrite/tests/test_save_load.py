"""
测试 - 保存/加载系统
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.systems.save_load import SaveLoadSystem
from src.entities.player import Player
from src.entities.item import Item
from src.world.map import Map
from src.utils.point import Tripoint
from src.engine.turn_manager import TurnManager


class MockGame:
    """模拟游戏对象用于测试"""

    def __init__(self):
        self.player = None
        self.world = None
        self.turn_manager = TurnManager()


def test_save_load_system_init():
    """测试保存/加载系统初始化"""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = SaveLoadSystem(save_dir=tmpdir)
        assert system.save_dir == Path(tmpdir)
        assert system.save_dir.exists()


def test_get_save_path():
    """测试获取存档路径"""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = SaveLoadSystem(save_dir=tmpdir)
        path = system.get_save_path("test_world")
        assert path.name == "test_world.json.gz"
        assert path.parent == Path(tmpdir)


def test_save_and_load_player():
    """测试保存和加载玩家数据"""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = SaveLoadSystem(save_dir=tmpdir)
        game = MockGame()

        # 创建测试玩家
        player = Player("测试玩家")
        player.position = Tripoint(10, 20, 0)
        player.str = 12
        player.hp_cur = 70
        player.skills["melee"] = 3
        player.traits.append("QUICK")
        player.profession = "survivor"
        player.kills = 5

        game.player = player
        game.world = Map()

        # 保存游戏
        assert system.save_game(game, "test_world")

        # 验证存档文件存在
        assert system.get_save_path("test_world").exists()

        # 加载游戏
        new_game = MockGame()
        assert system.load_game(new_game, "test_world")

        # 验证玩家数据
        assert new_game.player is not None
        assert new_game.player.name == "测试玩家"
        assert new_game.player.position.x == 10
        assert new_game.player.position.y == 20
        assert new_game.player.str == 12
        assert new_game.player.hp_cur == 70
        assert new_game.player.skills["melee"] == 3
        assert "QUICK" in new_game.player.traits
        assert new_game.player.profession == "survivor"
        assert new_game.player.kills == 5


def test_save_and_load_inventory():
    """测试保存和加载库存"""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = SaveLoadSystem(save_dir=tmpdir)
        game = MockGame()

        # 创建带物品的玩家
        player = Player("测试玩家")
        
        # 添加物品到库存
        item1 = Item("stick")
        item1.charges = 3
        player.inventory.add_item(item1)

        item2 = Item("rock")
        item2.charges = 5
        item2.damage_level = 2
        player.inventory.add_item(item2)

        # 手持物品
        player.wielded_item = Item("stick")

        game.player = player
        game.world = Map()

        # 保存和加载
        assert system.save_game(game, "test_inv")
        new_game = MockGame()
        assert system.load_game(new_game, "test_inv")

        # 验证库存
        assert len(new_game.player.inventory.items) == 2
        assert new_game.player.inventory.items[0].type_id == "stick"
        assert new_game.player.inventory.items[0].charges == 3
        assert new_game.player.inventory.items[1].type_id == "rock"
        assert new_game.player.inventory.items[1].charges == 5
        assert new_game.player.inventory.items[1].damage_level == 2

        # 验证手持物品
        assert new_game.player.wielded_item is not None
        assert new_game.player.wielded_item.type_id == "stick"


def test_save_and_load_world():
    """测试保存和加载世界地图"""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = SaveLoadSystem(save_dir=tmpdir)
        game = MockGame()

        # 创建玩家和地图
        player = Player("测试玩家")
        game.player = player

        world = Map()
        world.center = Tripoint(5, 10, 0)

        # 修改一些格子
        tile1 = world.get_tile(Tripoint(0, 0, 0))
        if tile1:
            tile1.terrain_id = "t_floor"

        tile2 = world.get_tile(Tripoint(1, 1, 0))
        if tile2:
            tile2.furniture_id = "f_chair"

        game.world = world

        # 保存和加载
        assert system.save_game(game, "test_map")
        new_game = MockGame()
        assert system.load_game(new_game, "test_map")

        # 验证地图
        assert new_game.world is not None
        assert new_game.world.center.x == 5
        assert new_game.world.center.y == 10

        # 验证格子状态
        new_tile1 = new_game.world.get_tile(Tripoint(0, 0, 0))
        assert new_tile1.terrain_id == "t_floor"

        new_tile2 = new_game.world.get_tile(Tripoint(1, 1, 0))
        assert new_tile2.furniture_id == "f_chair"


def test_list_saves():
    """测试列出存档"""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = SaveLoadSystem(save_dir=tmpdir)

        # 创建几个存档
        game1 = MockGame()
        game1.player = Player("玩家1")
        game1.world = Map()
        system.save_game(game1, "world1")

        game2 = MockGame()
        game2.player = Player("玩家2")
        game2.world = Map()
        system.save_game(game2, "world2")

        # 列出存档
        saves = system.list_saves()
        assert len(saves) == 2
        assert any(s["name"] == "world1" for s in saves)
        assert any(s["name"] == "world2" for s in saves)
        assert any(s["player_name"] == "玩家1" for s in saves)
        assert any(s["player_name"] == "玩家2" for s in saves)


def test_delete_save():
    """测试删除存档"""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = SaveLoadSystem(save_dir=tmpdir)

        # 创建存档
        game = MockGame()
        game.player = Player("测试玩家")
        game.world = Map()
        system.save_game(game, "test_delete")

        # 验证存档存在
        assert system.get_save_path("test_delete").exists()

        # 删除存档
        assert system.delete_save("test_delete")

        # 验证存档已删除
        assert not system.get_save_path("test_delete").exists()

        # 再次删除应该失败
        assert not system.delete_save("test_delete")


def test_save_nonexistent_world():
    """测试保存不存在的世界"""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = SaveLoadSystem(save_dir=tmpdir)
        game = MockGame()
        game.player = Player("测试玩家")
        game.world = None  # 没有世界

        # 应该仍然能保存（世界数据为None）
        assert system.save_game(game, "no_world")


def test_load_nonexistent_save():
    """测试加载不存在的存档"""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = SaveLoadSystem(save_dir=tmpdir)
        game = MockGame()

        # 加载不存在的存档应该失败
        assert not system.load_game(game, "nonexistent")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
