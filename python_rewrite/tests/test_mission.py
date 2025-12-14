"""
Tests for mission system.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.systems.mission import (
    Mission, MissionType, MissionStatus, MissionOrigin,
    MissionManager
)
from src.utils.point import Tripoint


class TestMissionBasics:
    """测试任务基础功能"""
    
    def test_mission_creation(self):
        """测试任务创建"""
        mission = Mission("test_mission", MissionType.FIND_ITEM)
        
        assert mission.type_id == "test_mission"
        assert mission.mission_type == MissionType.FIND_ITEM
        assert mission.status == MissionStatus.INACTIVE
        assert mission.mission_id >= 0
    
    def test_mission_activation(self):
        """测试任务激活"""
        mission = Mission("test", MissionType.KILL)
        assert mission.status == MissionStatus.INACTIVE
        
        mission.activate()
        assert mission.status == MissionStatus.ACTIVE
    
    def test_mission_progress(self):
        """测试任务进度更新"""
        mission = Mission("test", MissionType.KILL_MONSTER)
        mission.target_count = 5
        mission.activate()
        
        mission.update_progress(2)
        assert mission.current_count == 2
        assert mission.status == MissionStatus.ACTIVE
        
        mission.update_progress(3)
        assert mission.current_count == 5
        assert mission.status == MissionStatus.SUCCESS
    
    def test_mission_complete(self):
        """测试任务完成"""
        mission = Mission("test", MissionType.REACH)
        mission.activate()
        
        mission.complete()
        assert mission.is_complete()
        assert mission.status == MissionStatus.SUCCESS
    
    def test_mission_fail(self):
        """测试任务失败"""
        mission = Mission("test", MissionType.RESCUE)
        mission.activate()
        
        mission.fail("NPC died")
        assert mission.is_failed()
        assert mission.status == MissionStatus.FAILURE
    
    def test_mission_callback(self):
        """测试任务回调函数"""
        completed = []
        failed = []
        
        def on_complete(m):
            completed.append(m.mission_id)
        
        def on_fail(m):
            failed.append(m.mission_id)
        
        mission1 = Mission("test1", MissionType.KILL)
        mission1.on_complete = on_complete
        mission1.activate()
        mission1.complete()
        
        mission2 = Mission("test2", MissionType.FIND_ITEM)
        mission2.on_fail = on_fail
        mission2.activate()
        mission2.fail()
        
        assert len(completed) == 1
        assert len(failed) == 1


class TestMissionTypes:
    """测试不同任务类型"""
    
    def test_kill_mission(self):
        """测试击杀任务"""
        mission = Mission("kill_test", MissionType.KILL_MONSTER)
        mission.title = "Kill 5 zombies"
        mission.target_monster_type = "zombie"
        mission.target_count = 5
        mission.activate()
        
        for i in range(5):
            mission.update_progress()
        
        assert mission.is_complete()
    
    def test_find_item_mission(self):
        """测试找物品任务"""
        mission = Mission("find_test", MissionType.FIND_ITEM)
        mission.title = "Find antibiotics"
        mission.target_item_id = "antibiotics"
        mission.target_count = 1
        mission.activate()
        
        mission.update_progress()
        assert mission.is_complete()
    
    def test_reach_mission(self):
        """测试到达任务"""
        mission = Mission("reach_test", MissionType.REACH)
        mission.title = "Reach refugee center"
        mission.target_pos = Tripoint(10, 20, 0)
        mission.target_count = 1
        mission.activate()
        
        mission.complete()
        assert mission.is_complete()
    
    def test_escort_mission(self):
        """测试护送任务"""
        mission = Mission("escort_test", MissionType.ESCORT)
        mission.title = "Escort survivor"
        mission.npc_id = 123
        mission.fail_on_npc_death = True
        mission.activate()
        
        # Simulate NPC death
        mission.fail("NPC died")
        assert mission.is_failed()


class TestMissionManager:
    """测试任务管理器"""
    
    def test_manager_creation(self):
        """测试管理器创建"""
        manager = MissionManager()
        assert len(manager.active_missions) == 0
        assert len(manager.completed_missions) == 0
        assert len(manager.failed_missions) == 0
    
    def test_add_mission_definition(self):
        """测试添加任务定义"""
        manager = MissionManager()
        
        definition = {
            "id": "TEST_MISSION",
            "type": "FIND_ITEM",
            "title": "Test Mission",
            "description": "Test description",
            "target_count": 1,
            "target_item_id": "test_item",
            "reward_money": 100
        }
        
        manager.add_mission_definition(definition)
        assert "TEST_MISSION" in manager.mission_definitions
    
    def test_create_mission_from_definition(self):
        """测试从定义创建任务"""
        manager = MissionManager()
        
        definition = {
            "id": "GET_ANTIBIOTICS",
            "type": "FIND_ITEM",
            "title": "Find Antibiotics",
            "description": "Find antibiotics",
            "target_count": 1,
            "target_item_id": "antibiotics",
            "reward_money": 100,
            "reward_items": ["water"]
        }
        
        manager.add_mission_definition(definition)
        mission = manager.create_mission("GET_ANTIBIOTICS")
        
        assert mission is not None
        assert mission.title == "Find Antibiotics"
        assert mission.target_item_id == "antibiotics"
        assert mission.reward_money == 100
        assert "water" in mission.reward_items
    
    def test_add_active_mission(self):
        """测试添加激活任务"""
        manager = MissionManager()
        mission = Mission("test", MissionType.KILL)
        
        manager.add_mission(mission)
        assert len(manager.active_missions) == 1
        assert mission.is_active()
    
    def test_remove_completed_mission(self):
        """测试移除完成的任务"""
        manager = MissionManager()
        mission = Mission("test", MissionType.REACH)
        mission.activate()
        manager.active_missions.append(mission)
        
        mission.complete()
        manager.remove_mission(mission)
        
        assert len(manager.active_missions) == 0
        assert len(manager.completed_missions) == 1
    
    def test_remove_failed_mission(self):
        """测试移除失败的任务"""
        manager = MissionManager()
        mission = Mission("test", MissionType.RESCUE)
        mission.activate()
        manager.active_missions.append(mission)
        
        mission.fail()
        manager.remove_mission(mission)
        
        assert len(manager.active_missions) == 0
        assert len(manager.failed_missions) == 1
    
    def test_get_mission_by_id(self):
        """测试通过ID获取任务"""
        manager = MissionManager()
        mission1 = Mission("test1", MissionType.KILL)
        mission2 = Mission("test2", MissionType.FIND_ITEM)
        
        manager.add_mission(mission1)
        manager.add_mission(mission2)
        
        found = manager.get_mission_by_id(mission1.mission_id)
        assert found is mission1
    
    def test_update_kill_mission(self):
        """测试更新击杀任务"""
        manager = MissionManager()
        
        mission = Mission("kill_zombie", MissionType.KILL_MONSTER)
        mission.target_monster_type = "zombie"
        mission.target_count = 3
        manager.add_mission(mission)
        
        manager.update_kill_mission("zombie")
        assert mission.current_count == 1
        
        manager.update_kill_mission("zombie")
        manager.update_kill_mission("zombie")
        assert mission.is_complete()
    
    def test_update_item_mission(self):
        """测试更新物品任务"""
        manager = MissionManager()
        
        mission = Mission("find_water", MissionType.FIND_ITEM)
        mission.target_item_id = "water"
        mission.target_count = 2
        manager.add_mission(mission)
        
        manager.update_item_mission("water")
        assert mission.current_count == 1
        
        manager.update_item_mission("water")
        assert mission.is_complete()
    
    def test_check_position_missions(self):
        """测试检查位置任务"""
        manager = MissionManager()
        
        mission = Mission("reach_place", MissionType.REACH)
        mission.target_pos = Tripoint(10, 10, 0)
        mission.target_count = 1
        manager.add_mission(mission)
        
        # Not at target yet
        manager.check_position_missions(Tripoint(5, 5, 0))
        assert not mission.is_complete()
        
        # At target
        manager.check_position_missions(Tripoint(10, 10, 0))
        assert mission.is_complete()
    
    def test_load_mission_definitions(self):
        """测试加载任务定义文件"""
        # Create temporary directory with mission files
        temp_dir = tempfile.mkdtemp()
        missions_dir = Path(temp_dir) / "missions"
        missions_dir.mkdir()
        
        try:
            # Create test mission file
            mission_file = missions_dir / "test_missions.json"
            import json
            with open(mission_file, 'w') as f:
                json.dump([
                    {
                        "id": "TEST_LOAD",
                        "type": "FIND_ITEM",
                        "title": "Test Load Mission",
                        "target_count": 1
                    }
                ], f)
            
            manager = MissionManager()
            manager.load_mission_definitions(Path(temp_dir))
            
            assert "TEST_LOAD" in manager.mission_definitions
        finally:
            shutil.rmtree(temp_dir)


class TestMissionSerialization:
    """测试任务序列化"""
    
    def test_mission_to_dict(self):
        """测试任务序列化为字典"""
        mission = Mission("test", MissionType.KILL_MONSTER)
        mission.title = "Kill zombies"
        mission.target_monster_type = "zombie"
        mission.target_count = 5
        mission.current_count = 2
        mission.activate()
        
        data = mission.to_dict()
        
        assert data["type_id"] == "test"
        assert data["mission_type"] == "KILL_MONSTER"
        assert data["status"] == "ACTIVE"
        assert data["title"] == "Kill zombies"
        assert data["target_count"] == 5
        assert data["current_count"] == 2
    
    def test_mission_from_dict(self):
        """测试从字典反序列化任务"""
        data = {
            "mission_id": 42,
            "type_id": "test",
            "mission_type": "FIND_ITEM",
            "status": "ACTIVE",
            "origin": "NPC",
            "title": "Find item",
            "description": "Find the item",
            "target_count": 1,
            "current_count": 0,
            "target_pos": [10, 20, 0],
            "target_item_id": "water",
            "target_monster_type": None,
            "npc_id": 123,
            "faction_id": "survivors",
            "deadline": 1000,
            "reward_items": ["apple"],
            "reward_money": 50,
            "fail_on_npc_death": True
        }
        
        mission = Mission.from_dict(data)
        
        assert mission.mission_id == 42
        assert mission.type_id == "test"
        assert mission.mission_type == MissionType.FIND_ITEM
        assert mission.status == MissionStatus.ACTIVE
        assert mission.target_pos.x == 10
        assert mission.target_item_id == "water"
        assert mission.npc_id == 123
    
    def test_manager_serialization(self):
        """测试管理器序列化"""
        manager = MissionManager()
        
        mission1 = Mission("test1", MissionType.KILL)
        mission1.activate()
        manager.active_missions.append(mission1)
        
        mission2 = Mission("test2", MissionType.FIND_ITEM)
        mission2.activate()
        mission2.complete()
        manager.completed_missions.append(mission2)
        
        data = manager.to_dict()
        
        assert len(data["active_missions"]) == 1
        assert len(data["completed_missions"]) == 1
        
        # Load into new manager
        new_manager = MissionManager()
        new_manager.from_dict(data)
        
        assert len(new_manager.active_missions) == 1
        assert len(new_manager.completed_missions) == 1


class TestMissionRewards:
    """测试任务奖励"""
    
    def test_mission_with_rewards(self):
        """测试带奖励的任务"""
        mission = Mission("reward_test", MissionType.KILL)
        mission.reward_money = 100
        mission.reward_items = ["apple", "water", "stick"]
        
        assert mission.reward_money == 100
        assert len(mission.reward_items) == 3
        assert "apple" in mission.reward_items
    
    def test_mission_without_rewards(self):
        """测试无奖励任务"""
        mission = Mission("no_reward", MissionType.REACH)
        
        assert mission.reward_money == 0
        assert len(mission.reward_items) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
