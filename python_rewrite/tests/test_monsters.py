"""
测试实体系统 - 怪物系统
"""

from src.utils.point import Tripoint
from src.entities.monster_type import monster_type_manager, MonsterType
from src.entities.monster import Monster, spawn_monster


def test_monster_type_manager():
    """测试怪物类型管理器"""
    # 应该有默认怪物
    assert monster_type_manager.get_monster_count() > 0
    
    # 获取特定怪物
    zombie = monster_type_manager.get_monster_type("mon_zombie")
    assert zombie is not None
    assert zombie.name == "僵尸"


def test_monster_creation():
    """测试怪物创建"""
    monster = Monster("mon_zombie")
    assert monster is not None
    assert monster.type_id == "mon_zombie"
    assert monster.get_name() == "僵尸"


def test_monster_hp():
    """测试怪物生命值"""
    monster = Monster("mon_zombie")
    assert monster.is_alive()
    assert monster.hp_cur == 80
    assert monster.hp_max == 80


def test_monster_damage():
    """测试怪物受伤"""
    monster = Monster("mon_zombie")
    initial_hp = monster.hp_cur
    
    monster.take_damage(20)
    assert monster.hp_cur == initial_hp - 20
    assert monster.is_alive()
    
    monster.take_damage(1000)
    assert monster.hp_cur == 0
    assert not monster.is_alive()


def test_monster_speed():
    """测试怪物速度"""
    zombie = Monster("mon_zombie")
    rat = Monster("mon_rat_giant")
    
    # 僵尸应该慢
    assert zombie.get_speed() == 70
    
    # 老鼠应该快
    assert rat.get_speed() == 120


def test_monster_hostility():
    """测试怪物敌对性"""
    monster = Monster("mon_zombie")
    assert monster.is_hostile()  # 僵尸默认敌对
    
    monster.friendly = True
    assert not monster.is_hostile()


def test_monster_target():
    """测试怪物目标"""
    monster = Monster("mon_zombie")
    assert not monster.has_target()
    
    target_pos = Tripoint(10, 10, 0)
    monster.set_target(target_pos)
    assert monster.has_target()
    assert monster.target_position == target_pos
    
    monster.clear_target()
    assert not monster.has_target()


def test_spawn_monster():
    """测试生成怪物"""
    pos = Tripoint(5, 5, 0)
    monster = spawn_monster("mon_rat_giant", pos)
    
    assert monster.position == pos
    assert monster.get_name() == "巨型老鼠"
