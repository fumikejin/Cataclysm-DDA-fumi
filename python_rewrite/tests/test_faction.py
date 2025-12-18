"""
测试派系系统
"""

import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.systems.faction import Faction, FactionManager, FactionRelation, FactionPower
from src.utils.point import Point


def test_faction_creation():
    """测试派系创建"""
    faction = Faction("test_faction", "Test Faction")
    
    assert faction.id == "test_faction"
    assert faction.name == "Test Faction"
    assert faction.power == FactionPower.SMALL
    assert faction.size == 10
    assert faction.player_attitude == 0


def test_faction_add_remove_member():
    """测试添加和移除成员"""
    faction = Faction("faction1", "Faction One")
    
    # 添加成员
    faction.add_member("npc_001")
    faction.add_member("npc_002")
    assert len(faction.members) == 2
    assert faction.size == 2
    
    # 移除成员
    faction.remove_member("npc_001")
    assert len(faction.members) == 1
    assert "npc_001" not in faction.members


def test_faction_leader():
    """测试设置领袖"""
    faction = Faction("faction1", "Faction One")
    
    faction.add_member("npc_001")
    faction.add_member("npc_002")
    
    # 设置领袖
    faction.set_leader("npc_001")
    assert faction.leader_id == "npc_001"
    
    # 移除领袖
    faction.remove_member("npc_001")
    assert faction.leader_id is None


def test_faction_attitude():
    """测试态度调整"""
    faction = Faction("faction1", "Faction One")
    
    # 增加态度
    faction.adjust_player_attitude(50)
    assert faction.player_attitude == 50
    
    # 超过上限
    faction.adjust_player_attitude(60)
    assert faction.player_attitude == 100
    
    # 减少态度
    faction.adjust_player_attitude(-150)
    assert faction.player_attitude == -50
    
    # 超过下限
    faction.adjust_player_attitude(-60)
    assert faction.player_attitude == -100


def test_faction_relations():
    """测试派系关系"""
    faction1 = Faction("faction1", "Faction One")
    faction2_id = "faction2"
    
    # 设置为盟友
    faction1.set_relation(faction2_id, FactionRelation.ALLY)
    assert faction1.is_ally(faction2_id)
    assert not faction1.is_enemy(faction2_id)
    assert faction2_id in faction1.liked_factions
    
    # 设置为敌人
    faction1.set_relation(faction2_id, FactionRelation.ENEMY)
    assert faction1.is_enemy(faction2_id)
    assert not faction1.is_ally(faction2_id)
    assert faction2_id in faction1.disliked_factions
    
    # 设置为中立
    faction1.set_relation(faction2_id, FactionRelation.NEUTRAL)
    assert not faction1.is_ally(faction2_id)
    assert not faction1.is_enemy(faction2_id)


def test_faction_base():
    """测试基地管理"""
    faction = Faction("faction1", "Faction One")
    
    pos1 = Point(10, 20)
    pos2 = Point(30, 40)
    
    faction.add_base(pos1)
    faction.add_base(pos2)
    
    assert len(faction.base_positions) == 2
    assert pos1 in faction.base_positions
    assert pos2 in faction.base_positions


def test_faction_wealth_respect():
    """测试财富和声望"""
    faction = Faction("faction1", "Faction One")
    
    # 调整财富
    faction.adjust_wealth(1000)
    assert faction.wealth == 1000
    
    faction.adjust_wealth(-500)
    assert faction.wealth == 500
    
    # 不能为负
    faction.adjust_wealth(-1000)
    assert faction.wealth == 0
    
    # 调整声望
    faction.adjust_respect(50)
    assert faction.respect == 50
    
    faction.adjust_respect(-30)
    assert faction.respect == 20


def test_faction_power_update():
    """测试影响力更新"""
    faction = Faction("faction1", "Faction One")
    
    # 小型
    faction.size = 5
    faction.update_power()
    assert faction.power == FactionPower.TINY
    
    # 小型
    faction.size = 30
    faction.update_power()
    assert faction.power == FactionPower.SMALL
    
    # 中型
    faction.size = 100
    faction.update_power()
    assert faction.power == FactionPower.MEDIUM
    
    # 大型
    faction.size = 300
    faction.update_power()
    assert faction.power == FactionPower.LARGE
    
    # 巨大
    faction.size = 600
    faction.update_power()
    assert faction.power == FactionPower.HUGE


def test_faction_serialization():
    """测试派系序列化"""
    faction = Faction("faction1", "Faction One")
    faction.description = "Test description"
    faction.add_member("npc_001")
    faction.add_base(Point(10, 20))
    faction.adjust_player_attitude(50)
    faction.set_relation("faction2", FactionRelation.ALLY)
    
    # 序列化
    data = faction.to_dict()
    
    # 反序列化
    loaded = Faction.from_dict(data)
    
    assert loaded.id == faction.id
    assert loaded.name == faction.name
    assert loaded.description == faction.description
    assert len(loaded.members) == 1
    assert len(loaded.base_positions) == 1
    assert loaded.player_attitude == 50
    assert loaded.is_ally("faction2")


def test_faction_manager_creation():
    """测试派系管理器创建"""
    manager = FactionManager()
    
    faction = manager.create_faction("faction1", "Faction One")
    
    assert faction.id == "faction1"
    assert faction.name == "Faction One"
    assert len(manager.factions) == 1
    
    # 重复创建返回现有派系
    same_faction = manager.create_faction("faction1", "Different Name")
    assert same_faction.id == faction.id
    assert same_faction.name == "Faction One"


def test_faction_manager_get_remove():
    """测试获取和移除派系"""
    manager = FactionManager()
    
    faction1 = manager.create_faction("faction1", "Faction One")
    faction2 = manager.create_faction("faction2", "Faction Two")
    
    # 获取派系
    assert manager.get_faction("faction1") == faction1
    assert manager.get_faction("faction2") == faction2
    assert manager.get_faction("nonexistent") is None
    
    # 移除派系
    manager.remove_faction("faction1")
    assert manager.get_faction("faction1") is None
    assert len(manager.factions) == 1


def test_faction_manager_player_faction():
    """测试玩家派系"""
    manager = FactionManager()
    
    faction1 = manager.create_faction("faction1", "Faction One")
    
    # 设置玩家派系
    manager.set_player_faction("faction1")
    assert manager.player_faction_id == "faction1"
    assert manager.get_player_faction() == faction1


def test_faction_manager_relations():
    """测试派系关系管理"""
    manager = FactionManager()
    
    faction1 = manager.create_faction("faction1", "Faction One")
    faction2 = manager.create_faction("faction2", "Faction Two")
    
    # 设置关系
    manager.set_relations("faction1", "faction2", FactionRelation.ALLY)
    
    # 双向关系
    assert manager.get_relations("faction1", "faction2") == FactionRelation.ALLY
    assert manager.get_relations("faction2", "faction1") == FactionRelation.ALLY


def test_faction_manager_get_all():
    """测试获取所有派系"""
    manager = FactionManager()
    
    faction1 = manager.create_faction("faction1", "Faction One")
    faction2 = manager.create_faction("faction2", "Faction Two")
    faction3 = manager.create_faction("faction3", "Faction Three")
    
    all_factions = manager.get_all_factions()
    assert len(all_factions) == 3
    assert faction1 in all_factions
    assert faction2 in all_factions
    assert faction3 in all_factions


def test_faction_manager_serialization():
    """测试派系管理器序列化"""
    manager = FactionManager()
    
    faction1 = manager.create_faction("faction1", "Faction One")
    faction2 = manager.create_faction("faction2", "Faction Two")
    manager.set_player_faction("faction1")
    manager.set_relations("faction1", "faction2", FactionRelation.ENEMY)
    
    # 序列化
    data = manager.to_dict()
    
    # 反序列化
    loaded_manager = FactionManager.from_dict(data)
    
    assert len(loaded_manager.factions) == 2
    assert loaded_manager.player_faction_id == "faction1"
    assert loaded_manager.get_relations("faction1", "faction2") == FactionRelation.ENEMY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
