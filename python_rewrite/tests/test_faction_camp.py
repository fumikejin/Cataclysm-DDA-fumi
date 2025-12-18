"""
测试派系营地系统
"""

import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.world.faction_camp import (
    FactionCamp, CampManager, CampMission, 
    CampResource, CampBuilding
)
from src.utils.point import Point


def test_camp_creation():
    """测试营地创建"""
    position = Point(100, 200)
    camp = FactionCamp("camp1", "Base Camp", position, "faction1")
    
    assert camp.id == "camp1"
    assert camp.name == "Base Camp"
    assert camp.position == position
    assert camp.faction_id == "faction1"
    assert camp.level == 1
    assert camp.population == 0


def test_camp_resources():
    """测试资源管理"""
    camp = FactionCamp("camp1", "Base Camp", Point(0, 0), "faction1")
    
    # 添加资源
    camp.add_resource(CampResource.FOOD.value, 100)
    assert camp.resources[CampResource.FOOD.value] == 100
    
    # 检查资源
    assert camp.has_resource(CampResource.FOOD.value, 50)
    assert not camp.has_resource(CampResource.FOOD.value, 150)
    
    # 移除资源
    assert camp.remove_resource(CampResource.FOOD.value, 30)
    assert camp.resources[CampResource.FOOD.value] == 70
    
    # 资源不足
    assert not camp.remove_resource(CampResource.FOOD.value, 100)


def test_camp_buildings():
    """测试建筑管理"""
    camp = FactionCamp("camp1", "Base Camp", Point(0, 0), "faction1")
    
    # 添加建筑
    camp.add_building(CampBuilding.TENT.value)
    assert camp.has_building(CampBuilding.TENT.value)
    assert camp.buildings[CampBuilding.TENT.value] == 1
    
    # 添加更多建筑
    camp.add_building(CampBuilding.TENT.value)
    assert camp.buildings[CampBuilding.TENT.value] == 2
    
    # 检查不存在的建筑
    assert not camp.has_building(CampBuilding.WORKSHOP.value)


def test_camp_defense():
    """测试防御等级"""
    camp = FactionCamp("camp1", "Base Camp", Point(0, 0), "faction1")
    
    # 初始防御为0
    assert camp.defense_rating == 0
    
    # 添加防御建筑
    camp.add_building(CampBuilding.WOODEN_WALL.value)
    assert camp.defense_rating == 5
    
    camp.add_building(CampBuilding.WATCHTOWER.value)
    assert camp.defense_rating == 15


def test_camp_population():
    """测试人口管理"""
    camp = FactionCamp("camp1", "Base Camp", Point(0, 0), "faction1")
    
    # 添加人口
    camp.add_population(10)
    assert camp.population == 10
    assert camp.available_workers == 7  # 70%
    
    camp.add_population(20)
    assert camp.population == 30
    assert camp.available_workers == 21


def test_camp_mission_creation():
    """测试营地任务创建"""
    mission = CampMission("mission1", "Gather Wood", "gather")
    
    assert mission.id == "mission1"
    assert mission.name == "Gather Wood"
    assert mission.type == "gather"
    assert not mission.in_progress


def test_camp_mission_start():
    """测试任务开始"""
    mission = CampMission("mission1", "Gather Wood", "gather")
    mission.required_workers = 2
    
    # 成功开始
    assert mission.start(2)
    assert mission.in_progress
    assert mission.assigned_workers == 2
    
    # 已在进行中
    assert not mission.start(3)


def test_camp_mission_update():
    """测试任务更新"""
    mission = CampMission("mission1", "Gather Wood", "gather")
    mission.required_time = 2  # 2天
    mission.start(1)
    
    # 更新1天
    mission.update(1.0)
    assert mission.progress == pytest.approx(0.5)
    assert mission.in_progress
    
    # 再更新1天，完成
    mission.update(1.0)
    assert mission.progress >= 1.0
    assert not mission.in_progress


def test_camp_mission_cancel():
    """测试任务取消"""
    mission = CampMission("mission1", "Gather Wood", "gather")
    mission.start(1)
    
    mission.cancel()
    assert not mission.in_progress
    assert mission.progress == 0.0
    assert mission.assigned_workers == 0


def test_camp_start_mission():
    """测试营地开始任务"""
    camp = FactionCamp("camp1", "Base Camp", Point(0, 0), "faction1")
    camp.add_population(10)
    camp.add_resource(CampResource.WOOD.value, 50)
    
    # 创建任务
    mission = CampMission("mission1", "Build Workshop", "build")
    mission.required_workers = 2
    mission.required_resources = {CampResource.WOOD.value: 20}
    
    # 成功开始任务
    assert camp.start_mission(mission, 2)
    assert mission in camp.active_missions
    assert camp.available_workers == 5  # 7 - 2
    assert camp.resources[CampResource.WOOD.value] == 30  # 50 - 20


def test_camp_mission_insufficient_resources():
    """测试资源不足时无法开始任务"""
    camp = FactionCamp("camp1", "Base Camp", Point(0, 0), "faction1")
    camp.add_population(10)
    camp.add_resource(CampResource.WOOD.value, 10)
    
    mission = CampMission("mission1", "Build Workshop", "build")
    mission.required_workers = 2
    mission.required_resources = {CampResource.WOOD.value: 50}
    
    # 资源不足
    assert not camp.start_mission(mission, 2)
    assert mission not in camp.active_missions


def test_camp_mission_insufficient_workers():
    """测试工人不足时无法开始任务"""
    camp = FactionCamp("camp1", "Base Camp", Point(0, 0), "faction1")
    camp.add_population(2)  # 只有1个工人
    camp.add_resource(CampResource.WOOD.value, 100)
    
    mission = CampMission("mission1", "Build Workshop", "build")
    mission.required_workers = 2
    
    # 工人不足
    assert not camp.start_mission(mission, 2)


def test_camp_update_missions():
    """测试更新营地任务"""
    camp = FactionCamp("camp1", "Base Camp", Point(0, 0), "faction1")
    camp.add_population(10)
    camp.add_resource(CampResource.WOOD.value, 50)
    
    # 创建并开始任务
    mission = CampMission("mission1", "Gather Food", "gather")
    mission.required_time = 1
    mission.required_workers = 2
    mission.reward_resources = {CampResource.FOOD.value: 100}
    
    camp.start_mission(mission, 2)
    
    # 更新1天，任务完成
    camp.update_missions(1.0)
    
    assert mission not in camp.active_missions
    assert mission in camp.completed_missions
    assert camp.resources[CampResource.FOOD.value] == 100
    assert camp.available_workers == 7  # 工人被释放


def test_camp_upgrade():
    """测试营地升级"""
    camp = FactionCamp("camp1", "Base Camp", Point(0, 0), "faction1")
    
    assert camp.level == 1
    
    camp.upgrade_level()
    assert camp.level == 2
    
    # 升级到最高级
    for _ in range(3):
        camp.upgrade_level()
    assert camp.level == 5
    
    # 无法再升级
    camp.upgrade_level()
    assert camp.level == 5


def test_camp_serialization():
    """测试营地序列化"""
    position = Point(100, 200)
    camp = FactionCamp("camp1", "Base Camp", position, "faction1")
    camp.level = 2
    camp.add_population(20)
    camp.add_resource(CampResource.FOOD.value, 100)
    camp.add_building(CampBuilding.TENT.value)
    
    # 序列化
    data = camp.to_dict()
    
    # 反序列化
    loaded = FactionCamp.from_dict(data)
    
    assert loaded.id == camp.id
    assert loaded.name == camp.name
    assert loaded.position.x == position.x
    assert loaded.position.y == position.y
    assert loaded.level == 2
    assert loaded.population == 20
    assert loaded.resources[CampResource.FOOD.value] == 100
    assert loaded.has_building(CampBuilding.TENT.value)


def test_camp_manager_creation():
    """测试营地管理器创建"""
    manager = CampManager()
    
    position = Point(100, 200)
    camp = manager.create_camp("camp1", "Base Camp", position, "faction1")
    
    assert camp.id == "camp1"
    assert len(manager.camps) == 1
    
    # 重复创建返回现有营地
    same_camp = manager.create_camp("camp1", "Different Name", position, "faction1")
    assert same_camp.id == camp.id


def test_camp_manager_get_remove():
    """测试获取和移除营地"""
    manager = CampManager()
    
    camp1 = manager.create_camp("camp1", "Camp One", Point(0, 0), "faction1")
    camp2 = manager.create_camp("camp2", "Camp Two", Point(10, 10), "faction2")
    
    # 获取营地
    assert manager.get_camp("camp1") == camp1
    assert manager.get_camp("camp2") == camp2
    assert manager.get_camp("nonexistent") is None
    
    # 移除营地
    manager.remove_camp("camp1")
    assert manager.get_camp("camp1") is None
    assert len(manager.camps) == 1


def test_camp_manager_get_faction_camps():
    """测试获取派系营地"""
    manager = CampManager()
    
    camp1 = manager.create_camp("camp1", "Camp One", Point(0, 0), "faction1")
    camp2 = manager.create_camp("camp2", "Camp Two", Point(10, 10), "faction1")
    camp3 = manager.create_camp("camp3", "Camp Three", Point(20, 20), "faction2")
    
    faction1_camps = manager.get_faction_camps("faction1")
    assert len(faction1_camps) == 2
    assert camp1 in faction1_camps
    assert camp2 in faction1_camps
    
    faction2_camps = manager.get_faction_camps("faction2")
    assert len(faction2_camps) == 1
    assert camp3 in faction2_camps


def test_camp_manager_update_all():
    """测试更新所有营地"""
    manager = CampManager()
    
    # 创建营地和任务
    camp = manager.create_camp("camp1", "Base Camp", Point(0, 0), "faction1")
    camp.add_population(10)
    camp.add_resource(CampResource.WOOD.value, 50)
    
    mission = CampMission("mission1", "Gather Food", "gather")
    mission.required_time = 1
    mission.required_workers = 2
    mission.reward_resources = {CampResource.FOOD.value: 100}
    
    camp.start_mission(mission, 2)
    
    # 更新所有营地
    manager.update_all_camps(1.0)
    
    assert mission in camp.completed_missions


def test_camp_manager_serialization():
    """测试营地管理器序列化"""
    manager = CampManager()
    
    camp1 = manager.create_camp("camp1", "Camp One", Point(0, 0), "faction1")
    camp2 = manager.create_camp("camp2", "Camp Two", Point(10, 10), "faction2")
    camp1.add_population(20)
    camp2.add_resource(CampResource.FOOD.value, 100)
    
    # 序列化
    data = manager.to_dict()
    
    # 反序列化
    loaded_manager = CampManager.from_dict(data)
    
    assert len(loaded_manager.camps) == 2
    assert loaded_manager.get_camp("camp1").population == 20
    assert loaded_manager.get_camp("camp2").resources[CampResource.FOOD.value] == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
