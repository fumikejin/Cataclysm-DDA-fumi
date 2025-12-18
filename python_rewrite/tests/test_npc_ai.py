"""
测试 - NPC AI系统
"""

import pytest
from src.utils.point import Tripoint
from src.world.map import Map
from src.entities.npc import NPC
from src.entities.player import Player
from src.entities.monster import Monster
from src.entities.monster_type import monster_type_manager
from src.ai.npc_ai import NPCAI, NPCGoal


@pytest.fixture
def game_map():
    """创建测试地图"""
    game_map = Map()
    # 创建一个10x10的地图
    for x in range(10):
        for y in range(10):
            pos = Tripoint(x, y, 0)
            tile = game_map.get_tile(pos)
            tile.terrain_id = "t_floor"
    return game_map


@pytest.fixture
def npc_ai(game_map):
    """创建NPC AI系统"""
    return NPCAI(game_map)


@pytest.fixture
def test_npc():
    """创建测试NPC"""
    npc = NPC("TestNPC")
    npc.position = Tripoint(5, 5, 0)
    npc.hp = 100
    npc.max_hp = 100
    return npc


def test_npcai_init(game_map):
    """测试NPC AI初始化"""
    npc_ai = NPCAI(game_map)
    assert npc_ai.game_map == game_map
    assert npc_ai.pathfinding is not None


def test_decide_goal_idle(npc_ai, test_npc):
    """测试决定目标 - 空闲"""
    test_npc.ai_enabled = False
    goal = npc_ai.decide_goal(test_npc)
    assert goal == NPCGoal.IDLE


def test_decide_goal_flee(npc_ai, test_npc):
    """测试决定目标 - 逃跑"""
    test_npc.hp = 20  # 低于30%
    test_npc.max_hp = 100
    goal = npc_ai.decide_goal(test_npc)
    assert goal == NPCGoal.FLEE


def test_decide_goal_attack(npc_ai, test_npc):
    """测试决定目标 - 攻击"""
    test_npc.personality = "aggressive"
    
    # 创建怪物
    monster = Monster("zombie", Tripoint(6, 6, 0))
    nearby_monsters = [monster]
    
    goal = npc_ai.decide_goal(test_npc, nearby_monsters=nearby_monsters)
    assert goal == NPCGoal.ATTACK


def test_decide_goal_follow_player(npc_ai, test_npc):
    """测试决定目标 - 跟随玩家"""
    test_npc.follow_player = True
    player = Player("TestPlayer")
    player.position = Tripoint(3, 3, 0)
    
    goal = npc_ai.decide_goal(test_npc, player=player)
    assert goal == NPCGoal.FOLLOW_PLAYER


def test_decide_goal_guard_position(npc_ai, test_npc):
    """测试决定目标 - 守卫位置"""
    test_npc.guard_position = Tripoint(7, 7, 0)
    goal = npc_ai.decide_goal(test_npc)
    assert goal == NPCGoal.GUARD_POSITION


def test_decide_goal_wander(npc_ai, test_npc):
    """测试决定目标 - 徘徊"""
    # 没有特殊目标，应该徘徊
    goal = npc_ai.decide_goal(test_npc)
    assert goal == NPCGoal.WANDER


def test_execute_goal_idle(npc_ai, test_npc):
    """测试执行目标 - 空闲"""
    next_pos = npc_ai.execute_goal(test_npc, NPCGoal.IDLE)
    assert next_pos is None


def test_execute_goal_follow_player(npc_ai, test_npc):
    """测试执行目标 - 跟随玩家"""
    player = Player("TestPlayer")
    player.position = Tripoint(8, 8, 0)
    
    next_pos = npc_ai.execute_goal(test_npc, NPCGoal.FOLLOW_PLAYER, player=player)
    # 应该返回一个移动位置（向玩家靠近）
    assert next_pos is not None or npc_ai._manhattan_distance(test_npc.position, player.position) <= 2


def test_execute_goal_guard_position(npc_ai, test_npc):
    """测试执行目标 - 守卫位置"""
    guard_pos = Tripoint(2, 2, 0)
    test_npc.guard_position = guard_pos
    
    next_pos = npc_ai.execute_goal(test_npc, NPCGoal.GUARD_POSITION)
    # 应该返回一个移动位置（向守卫位置移动）
    assert next_pos is not None


def test_execute_goal_wander(npc_ai, test_npc):
    """测试执行目标 - 徘徊"""
    next_pos = npc_ai.execute_goal(test_npc, NPCGoal.WANDER)
    # 应该返回一个随机相邻位置
    if next_pos:
        distance = npc_ai._manhattan_distance(test_npc.position, next_pos)
        assert distance <= 2  # 相邻位置（包括对角线）


def test_follow_target(npc_ai, test_npc):
    """测试跟随目标"""
    target_pos = Tripoint(8, 8, 0)
    next_pos = npc_ai._follow_target(test_npc, target_pos, follow_distance=2)
    
    # 应该返回一个移动位置
    assert next_pos is not None or npc_ai._manhattan_distance(test_npc.position, target_pos) <= 5


def test_move_to_position(npc_ai, test_npc):
    """测试移动到位置"""
    target_pos = Tripoint(3, 3, 0)
    next_pos = npc_ai._move_to_position(test_npc, target_pos)
    
    if next_pos:
        # 下一个位置应该比当前位置更接近目标
        current_dist = npc_ai._manhattan_distance(test_npc.position, target_pos)
        next_dist = npc_ai._manhattan_distance(next_pos, target_pos)
        assert next_dist <= current_dist


def test_approach_target(npc_ai, test_npc):
    """测试接近目标"""
    target_pos = Tripoint(8, 8, 0)
    next_pos = npc_ai._approach_target(test_npc, target_pos, attack_range=1)
    
    # 应该返回移动位置或已经在范围内
    if next_pos:
        distance = npc_ai._manhattan_distance(test_npc.position, target_pos)
        assert distance > 1  # 不在攻击范围内才移动


def test_wander(npc_ai, test_npc):
    """测试徘徊"""
    next_pos = npc_ai._wander(test_npc)
    
    if next_pos:
        # 应该是相邻位置
        distance = npc_ai._manhattan_distance(test_npc.position, next_pos)
        assert distance <= 2


def test_move_away_from(npc_ai, test_npc):
    """测试远离"""
    threat_pos = Tripoint(6, 6, 0)
    next_pos = npc_ai._move_away_from(test_npc, threat_pos)
    
    if next_pos:
        # 下一个位置应该比当前位置离威胁更远
        current_dist = npc_ai._manhattan_distance(test_npc.position, threat_pos)
        next_dist = npc_ai._manhattan_distance(next_pos, threat_pos)
        assert next_dist >= current_dist


def test_manhattan_distance(npc_ai):
    """测试曼哈顿距离计算"""
    pos1 = Tripoint(0, 0, 0)
    pos2 = Tripoint(3, 4, 0)
    
    distance = npc_ai._manhattan_distance(pos1, pos2)
    assert distance == 7  # 3 + 4


def test_update_npc(npc_ai, test_npc):
    """测试更新NPC"""
    player = Player("TestPlayer")
    player.position = Tripoint(8, 8, 0)
    test_npc.follow_player = True
    
    next_pos = npc_ai.update_npc(test_npc, player=player)
    # 应该返回移动位置或None
    assert next_pos is None or isinstance(next_pos, Tripoint)


def test_set_follow_player(npc_ai, test_npc):
    """测试设置跟随玩家"""
    npc_ai.set_follow_player(test_npc, True)
    assert test_npc.follow_player == True
    
    npc_ai.set_follow_player(test_npc, False)
    assert test_npc.follow_player == False


def test_set_guard_position(npc_ai, test_npc):
    """测试设置守卫位置"""
    guard_pos = Tripoint(7, 7, 0)
    npc_ai.set_guard_position(test_npc, guard_pos)
    assert test_npc.guard_position == guard_pos
    
    npc_ai.set_guard_position(test_npc, None)
    assert test_npc.guard_position is None


def test_enable_ai(npc_ai, test_npc):
    """测试启用/禁用AI"""
    npc_ai.enable_ai(test_npc, False)
    assert test_npc.ai_enabled == False
    
    npc_ai.enable_ai(test_npc, True)
    assert test_npc.ai_enabled == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
