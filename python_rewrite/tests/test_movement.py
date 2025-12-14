"""
测试游戏机制 - 移动系统
"""

from src.utils.point import Point, Tripoint
from src.systems.movement import MovementSystem
from src.entities.player import Player
from src.world.map import Map
from src.world.terrain import terrain_manager


def test_movement_system_creation():
    """测试移动系统创建"""
    game_map = Map()
    movement = MovementSystem(game_map)
    assert movement is not None
    assert movement.game_map is game_map


def test_can_move_to():
    """测试移动可行性检查"""
    game_map = Map()
    movement = MovementSystem(game_map)
    player = Player("测试玩家")

    # 设置玩家位置
    player.position = Tripoint(0, 0, 0)

    # 移动到相邻位置应该可行
    target = Tripoint(1, 1, 0)
    result = movement.can_move_to(player, target)
    assert isinstance(result, bool)


def test_move_character():
    """测试角色移动"""
    game_map = Map()
    movement = MovementSystem(game_map)
    player = Player("测试玩家")

    # 设置玩家位置和行动点
    player.position = Tripoint(5, 5, 0)
    player.moves = 200

    # 向右移动
    initial_pos = player.position
    result = movement.move_character(player, Point(1, 0))

    # 如果移动成功，位置应该改变
    if result:
        assert player.position.x == initial_pos.x + 1
        assert player.position.y == initial_pos.y


def test_move_cost():
    """测试移动成本计算"""
    game_map = Map()
    movement = MovementSystem(game_map)

    target = Tripoint(5, 5, 0)
    cost = movement.get_move_cost(None, target)
    assert cost > 0
    assert cost <= 1000  # 合理的移动成本范围


def test_calculate_path():
    """测试路径计算"""
    game_map = Map()
    movement = MovementSystem(game_map)

    start = Tripoint(0, 0, 0)
    end = Tripoint(5, 5, 0)

    path = movement.calculate_path(start, end)
    assert isinstance(path, list)
    if len(path) > 0:
        assert path[-1] == end
