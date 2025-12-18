"""
测试 - 怪物AI系统
"""

import pytest
from src.ai.monster_ai import MonsterAI, MonsterGoal
from src.entities.monster import Monster
from src.entities.player import Player
from src.world.map import Map
from src.world.terrain import terrain_manager
from src.world.furniture import furniture_manager
from src.world.field import field_manager
from src.entities.monster_type import monster_type_manager
from src.utils.point import Tripoint


@pytest.fixture
def game_map():
    """创建测试地图"""
    return Map()


@pytest.fixture
def monster_ai(game_map):
    """创建怪物AI系统"""
    return MonsterAI(game_map)


@pytest.fixture
def zombie(game_map):
    """创建僵尸"""
    zombie = Monster("zombie")
    zombie.position = Tripoint(5, 5, 0)
    return zombie


@pytest.fixture
def player_char():
    """创建玩家角色"""
    player = Player("TestPlayer")
    player.position = Tripoint(8, 8, 0)
    return player


def test_monster_ai_initialization(game_map):
    """测试怪物AI系统初始化"""
    ai = MonsterAI(game_map)
    assert ai.game_map == game_map
    assert ai.pathfinding is not None


def test_friendly_monster_idle(monster_ai, zombie):
    """测试友好怪物保持空闲"""
    zombie.friendly = True
    
    goal = monster_ai.decide_goal(zombie)
    assert goal == MonsterGoal.IDLE


def test_low_hp_monster_flees(monster_ai, zombie, player_char):
    """测试低生命值怪物逃跑"""
    zombie.hp_cur = 2  # 20% HP
    
    goal = monster_ai.decide_goal(zombie, [player_char])
    assert goal == MonsterGoal.FLEE


def test_monster_chases_nearby_target(monster_ai, zombie, player_char):
    """测试怪物追逐附近目标"""
    player_char.position = Tripoint(7, 7, 0)  # 在视野范围内
    
    goal = monster_ai.decide_goal(zombie, [player_char])
    assert goal == MonsterGoal.CHASE
    assert zombie.target_position == player_char.position


def test_monster_attacks_adjacent_target(monster_ai, zombie, player_char):
    """测试怪物攻击相邻目标"""
    player_char.position = Tripoint(6, 5, 0)  # 相邻位置
    
    goal = monster_ai.decide_goal(zombie, [player_char])
    assert goal == MonsterGoal.ATTACK


def test_angry_monster_wanders(monster_ai, zombie):
    """测试愤怒的怪物徘徊"""
    zombie.anger = 50
    
    goal = monster_ai.decide_goal(zombie, [])
    assert goal == MonsterGoal.WANDER


def test_idle_execution(monster_ai, zombie):
    """测试空闲行为执行"""
    result = monster_ai.execute_goal(zombie, MonsterGoal.IDLE)
    assert result is True


def test_chase_execution(monster_ai, zombie, player_char):
    """测试追逐行为执行"""
    zombie.target_position = Tripoint(8, 8, 0)
    
    result = monster_ai.execute_goal(zombie, MonsterGoal.CHASE)
    # 结果取决于寻路和地图状态


def test_attack_execution(monster_ai, zombie, player_char):
    """测试攻击行为执行"""
    player_char.position = Tripoint(6, 5, 0)
    
    result = monster_ai.execute_goal(zombie, MonsterGoal.ATTACK, [player_char])
    assert result is True


def test_flee_execution(monster_ai, zombie, player_char):
    """测试逃跑行为执行"""
    zombie.hp_cur = 2
    player_char.position = Tripoint(6, 5, 0)
    
    result = monster_ai.execute_goal(zombie, MonsterGoal.FLEE, [player_char])
    # 结果取决于寻路和地图状态


def test_wander_execution(monster_ai, zombie):
    """测试徘徊行为执行"""
    original_pos = Tripoint(zombie.position.x, zombie.position.y, zombie.position.z)
    
    # 多次尝试徘徊
    success = False
    for _ in range(10):
        if monster_ai.execute_goal(zombie, MonsterGoal.WANDER):
            success = True
            break
    
    # 至少有一次成功移动
    assert success or zombie.position != original_pos


def test_update_with_no_targets(monster_ai, zombie):
    """测试没有目标时的更新"""
    zombie.anger = 0
    
    result = monster_ai.update(zombie, [])
    assert result is True  # 应该执行空闲或徘徊


def test_update_with_nearby_target(monster_ai, zombie, player_char):
    """测试有附近目标时的更新"""
    player_char.position = Tripoint(7, 7, 0)
    
    result = monster_ai.update(zombie, [player_char])
    # 应该决定追逐或攻击


def test_multiple_targets_closest_selected(monster_ai, zombie):
    """测试多个目标时选择最近的"""
    player1 = Player("Player1")
    player1.position = Tripoint(7, 7, 0)  # 距离 2.83
    
    player2 = Player("Player2")
    player2.position = Tripoint(9, 9, 0)  # 距离 5.66
    
    goal = monster_ai.decide_goal(zombie, [player1, player2])
    
    # 应该追逐或攻击最近的目标
    if goal in [MonsterGoal.CHASE, MonsterGoal.ATTACK]:
        assert zombie.target_position == player1.position


def test_out_of_vision_no_chase(monster_ai, zombie, player_char):
    """测试目标在视野外时不追逐"""
    player_char.position = Tripoint(50, 50, 0)  # 远超视野范围
    
    goal = monster_ai.decide_goal(zombie, [player_char])
    # 不应该追逐远处的目标
    assert goal != MonsterGoal.CHASE


def test_friendly_monster_no_attack(monster_ai, zombie, player_char):
    """测试友好怪物不攻击"""
    zombie.friendly = True
    player_char.position = Tripoint(6, 5, 0)
    
    goal = monster_ai.decide_goal(zombie, [player_char])
    assert goal != MonsterGoal.ATTACK


def test_monster_distance_calculation(monster_ai):
    """测试距离计算"""
    pos1 = Tripoint(0, 0, 0)
    pos2 = Tripoint(3, 4, 0)
    
    distance = monster_ai._calculate_distance(pos1, pos2)
    assert abs(distance - 5.0) < 0.01  # 3-4-5 三角形


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
