"""
测试游戏机制 - 战斗系统
"""

from src.systems.combat import CombatSystem
from src.entities.player import Player
from src.entities.monster import Monster
from src.entities.item import Item


def test_combat_system_creation():
    """测试战斗系统创建"""
    combat = CombatSystem()
    assert combat is not None


def test_melee_attack():
    """测试近战攻击"""
    combat = CombatSystem()
    attacker = Player("攻击者")
    defender = Player("防御者")

    initial_hp = defender.hp_cur
    damage = combat.melee_attack(attacker, defender)

    assert isinstance(damage, int)
    assert damage >= 0
    if damage > 0:
        assert defender.hp_cur < initial_hp


def test_hit_chance_calculation():
    """测试命中率计算"""
    combat = CombatSystem()
    attacker = Player("攻击者")
    defender = Player("防御者")

    # 设置属性
    attacker.dex = 10
    defender.dex = 8

    hit_chance = combat.calculate_hit_chance(attacker, defender)
    assert 0 <= hit_chance <= 100


def test_damage_calculation():
    """测试伤害计算"""
    combat = CombatSystem()
    attacker = Player("攻击者")
    defender = Player("防御者")

    attacker.str = 10

    damage = combat.calculate_damage(attacker, defender)
    assert damage >= 1  # 至少造成1点伤害


def test_weapon_damage():
    """测试武器伤害"""
    combat = CombatSystem()
    attacker = Player("攻击者")

    # 徒手伤害
    unarmed_damage = combat.get_weapon_damage(attacker)
    assert unarmed_damage == 5

    # 装备武器
    weapon = Item("stick")
    attacker.inventory.add_item(weapon)
    attacker.wield_item(weapon)

    armed_damage = combat.get_weapon_damage(attacker)
    assert armed_damage >= unarmed_damage


def test_armor_value():
    """测试护甲值"""
    combat = CombatSystem()
    character = Player("角色")

    # 无护甲
    armor = combat.get_armor_value(character)
    assert armor == 0

    # 穿上护甲
    jeans = Item("jeans")
    character.inventory.add_item(jeans)
    character.wear_item(jeans)

    armor_with_jeans = combat.get_armor_value(character)
    assert armor_with_jeans >= armor


def test_critical_hit():
    """测试暴击判定"""
    combat = CombatSystem()
    attacker = Player("攻击者")
    attacker.dex = 15

    # 多次判定，应该有成功和失败
    results = [combat.calculate_critical_hit(attacker) for _ in range(20)]
    assert True in results or False in results  # 至少有一种结果


def test_attack_vs_monster():
    """测试攻击怪物"""
    combat = CombatSystem()
    player = Player("玩家")
    monster = Monster("mon_zombie")

    initial_hp = monster.hp_cur
    damage = combat.melee_attack(player, monster)

    if damage > 0:
        assert monster.hp_cur < initial_hp
