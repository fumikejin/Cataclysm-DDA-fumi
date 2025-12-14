"""
测试世界工厂系统
"""

import pytest
import os
import shutil
import tempfile
import time

from src.world.world_factory import WorldFactory, World, WorldMetadata
from src.utils.point import Tripoint


@pytest.fixture
def temp_worlds_dir():
    """创建临时世界目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # 清理
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def test_world_factory_creation(temp_worlds_dir):
    """测试世界工厂创建"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    assert factory is not None
    assert os.path.exists(temp_worlds_dir)


def test_create_world(temp_worlds_dir):
    """测试创建世界"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    world = factory.create_world("Test World", seed=12345)
    
    assert world is not None
    assert world.metadata.name == "Test World"
    assert world.metadata.seed == 12345
    assert factory.current_world == world


def test_world_sanitize_name():
    """测试清理世界名称"""
    test_cases = [
        ("Normal Name", "Normal Name"),
        ("Name/With\\Slash", "Name_With_Slash"),
        ("<Invalid>", "_Invalid_"),
        ("", "world"),  # 空名称
    ]
    
    for input_name, expected_output in test_cases:
        sanitized = World._sanitize_name(input_name)
        assert sanitized == expected_output


def test_world_metadata_serialization():
    """测试世界元数据序列化"""
    metadata = WorldMetadata(
        name="Test",
        seed=123,
        created_time="2024-01-01T00:00:00",
        last_played="2024-01-02T00:00:00",
        play_time=3600,
        turn_count=1000
    )
    
    # 转换为字典
    data = metadata.to_dict()
    assert data["name"] == "Test"
    assert data["seed"] == 123
    
    # 从字典恢复
    restored = WorldMetadata.from_dict(data)
    assert restored.name == metadata.name
    assert restored.seed == metadata.seed
    assert restored.play_time == metadata.play_time


def test_save_and_load_world_metadata(temp_worlds_dir):
    """测试保存和加载世界元数据"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    # 创建世界
    world = factory.create_world("Save Test", seed=99999)
    world.update_play_time(1800)
    world.increment_turn_count()
    world.save_metadata()
    
    # 清空当前世界
    factory.current_world = None
    
    # 重新加载
    loaded_world = factory.load_world("Save Test")
    
    assert loaded_world is not None
    assert loaded_world.metadata.name == "Save Test"
    assert loaded_world.metadata.seed == 99999
    assert loaded_world.metadata.play_time == 1800
    assert loaded_world.metadata.turn_count == 1


def test_world_exists(temp_worlds_dir):
    """测试检查世界是否存在"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    assert not factory.world_exists("Nonexistent World")
    
    factory.create_world("Existing World")
    assert factory.world_exists("Existing World")


def test_delete_world(temp_worlds_dir):
    """测试删除世界"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    # 创建并删除世界
    factory.create_world("Doomed World")
    assert factory.world_exists("Doomed World")
    
    success = factory.delete_world("Doomed World")
    assert success
    assert not factory.world_exists("Doomed World")


def test_list_worlds(temp_worlds_dir):
    """测试列出所有世界"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    # 创建多个世界
    world_names = ["World 1", "World 2", "World 3"]
    for name in world_names:
        factory.create_world(name, set_as_current=False)
        time.sleep(0.01)  # 确保last_played时间不同
    
    # 列出世界
    worlds = factory.list_worlds()
    
    assert len(worlds) == 3
    # 应该按last_played排序（最新的在前）
    assert worlds[0].name == "World 3"


def test_world_center_position(temp_worlds_dir):
    """测试世界中心位置"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    world = factory.create_world("Position Test")
    
    # 默认中心位置
    assert world.center_pos == Tripoint(0, 0, 0)
    
    # 修改中心位置
    new_pos = Tripoint(100, 200, 0)
    world.center_pos = new_pos
    world.save_metadata()
    
    # 重新加载
    loaded_world = factory.load_world("Position Test")
    assert loaded_world.center_pos == new_pos


def test_world_overmap_buffer(temp_worlds_dir):
    """测试世界的大地图缓冲区"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    world = factory.create_world("Overmap Test")
    
    # 世界应该有大地图缓冲区
    assert world.overmap_buffer is not None
    
    # 使用大地图缓冲区
    om_pos = Tripoint(10, 10, 0)
    world.overmap_buffer.set_tile_terrain(om_pos, "forest")
    
    terrain = world.overmap_buffer.get_terrain_at(om_pos)
    assert terrain == "forest"


def test_save_current_world(temp_worlds_dir):
    """测试保存当前世界"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    # 没有当前世界时
    factory.save_current_world()  # 不应该崩溃
    
    # 创建并修改世界
    world = factory.create_world("Current World")
    world.update_play_time(3600)
    
    # 保存当前世界
    factory.save_current_world()
    
    # 重新加载验证
    loaded_world = factory.load_world("Current World")
    assert loaded_world.metadata.play_time == 3600


def test_close_current_world(temp_worlds_dir):
    """测试关闭当前世界"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    world = factory.create_world("Closing World")
    world.update_play_time(7200)
    
    assert factory.current_world is not None
    
    factory.close_current_world()
    
    assert factory.current_world is None


def test_get_current_world(temp_worlds_dir):
    """测试获取当前世界"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    # 初始时没有当前世界
    assert factory.get_current_world() is None
    
    # 创建世界
    world = factory.create_world("Current")
    assert factory.get_current_world() == world


def test_world_play_time_tracking(temp_worlds_dir):
    """测试游玩时间追踪"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    world = factory.create_world("Time Test")
    
    assert world.metadata.play_time == 0
    
    world.update_play_time(600)  # 10分钟
    assert world.metadata.play_time == 600
    
    world.update_play_time(1200)  # 再加20分钟
    assert world.metadata.play_time == 1800


def test_world_turn_count(temp_worlds_dir):
    """测试回合数追踪"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    world = factory.create_world("Turn Test")
    
    assert world.metadata.turn_count == 0
    
    for i in range(100):
        world.increment_turn_count()
    
    assert world.metadata.turn_count == 100


def test_multiple_worlds_independence(temp_worlds_dir):
    """测试多个世界的独立性"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    # 创建两个世界
    world1 = factory.create_world("World A", seed=111, set_as_current=False)
    world2 = factory.create_world("World B", seed=222, set_as_current=False)
    
    # 它们应该有不同的种子
    assert world1.metadata.seed != world2.metadata.seed
    
    # 修改world1不应该影响world2
    world1.update_play_time(1000)
    assert world2.metadata.play_time == 0


def test_world_version_tracking(temp_worlds_dir):
    """测试版本追踪"""
    factory = WorldFactory(saves_dir=temp_worlds_dir)
    
    world = factory.create_world("Version Test")
    
    # 应该有版本号
    assert world.metadata.version is not None
    assert isinstance(world.metadata.version, str)
