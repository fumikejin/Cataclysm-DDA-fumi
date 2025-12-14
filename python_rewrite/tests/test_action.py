"""
测试游戏机制 - 动作系统
"""

from src.utils.point import Point, Tripoint
from src.systems.action import (
    Action, MoveAction, PickupAction, DropAction,
    WieldAction, WaitAction, AttackAction
)
from src.systems.movement import MovementSystem
from src.entities.player import Player
from src.entities.item import Item
from src.world.map import Map


def test_wait_action():
    """测试等待动作"""
    player = Player("测试玩家")
    action = WaitAction(50)

    assert action.can_perform(player)
    assert action.perform(player)
    assert action.get_time_cost() == 50


def test_pickup_action():
    """测试拾取动作"""
    player = Player("测试玩家")
    item = Item("apple")

    action = PickupAction(item)
    assert action.can_perform(player)
    assert action.perform(player)
    assert item in player.inventory.items


def test_drop_action():
    """测试丢弃动作"""
    player = Player("测试玩家")
    item = Item("apple")
    player.inventory.add_item(item)

    action = DropAction(item)
    assert action.can_perform(player)
    assert action.perform(player)
    assert item not in player.inventory.items


def test_wield_action():
    """测试装备动作"""
    player = Player("测试玩家")
    item = Item("stick")
    player.inventory.add_item(item)

    action = WieldAction(item)
    assert action.can_perform(player)
    assert action.perform(player)
    assert player.wielded_item == item


def test_move_action():
    """测试移动动作"""
    game_map = Map()
    movement = MovementSystem(game_map)
    player = Player("测试玩家")
    player.position = Tripoint(5, 5, 0)
    player.moves = 200

    action = MoveAction(Point(1, 0), movement)
    # can_perform检查移动是否可行
    can_move = action.can_perform(player)
    assert isinstance(can_move, bool)


def test_action_time_cost():
    """测试动作时间成本"""
    action = WaitAction()
    assert action.get_time_cost() == 100

    pickup_action = PickupAction(Item("apple"))
    assert pickup_action.get_time_cost() == 50

    drop_action = DropAction(Item("apple"))
    assert drop_action.get_time_cost() == 30
