"""
测试实体系统 - 角色系统
"""

from src.utils.point import Tripoint
from src.entities.character import Character
from src.entities.player import Player
from src.entities.npc import NPC
from src.entities.item import Item


def test_character_creation():
    """测试角色创建"""
    char = Character("测试角色")
    assert char.name == "测试角色"
    assert char.is_alive()
    assert char.hp_cur == 84
    assert char.hp_max == 84


def test_character_damage():
    """测试角色受伤"""
    char = Character("测试角色")
    initial_hp = char.hp_cur
    
    char.take_damage(10)
    assert char.hp_cur == initial_hp - 10
    assert char.is_alive()
    
    char.take_damage(1000)
    assert char.hp_cur == 0
    assert not char.is_alive()


def test_character_heal():
    """测试角色治疗"""
    char = Character("测试角色")
    char.take_damage(20)
    
    char.heal(10)
    assert char.hp_cur == 74
    
    # 不能超过最大值
    char.heal(100)
    assert char.hp_cur == char.hp_max


def test_character_skills():
    """测试角色技能"""
    char = Character("测试角色")
    
    assert char.get_skill_level("cooking") == 0
    
    char.set_skill_level("cooking", 3)
    assert char.get_skill_level("cooking") == 3


def test_character_traits():
    """测试角色特征"""
    char = Character("测试角色")
    
    assert not char.has_trait("fast_learner")
    
    char.add_trait("fast_learner")
    assert char.has_trait("fast_learner")
    
    char.remove_trait("fast_learner")
    assert not char.has_trait("fast_learner")


def test_character_inventory():
    """测试角色库存"""
    char = Character("测试角色")
    
    item = Item("apple")
    char.inventory.add_item(item)
    
    assert len(char.inventory) == 1
    assert item in char.inventory.items


def test_player_creation():
    """测试玩家创建"""
    player = Player("英雄")
    assert player.name == "英雄"
    assert player.kills == 0
    assert player.turns_survived == 0


def test_player_profession():
    """测试玩家职业"""
    player = Player()
    player.set_profession("survivor")
    assert player.profession == "survivor"


def test_player_turns():
    """测试玩家回合"""
    player = Player()
    initial_turns = player.turns_survived
    
    player.on_turn_end()
    assert player.turns_survived == initial_turns + 1


def test_npc_creation():
    """测试NPC创建"""
    npc = NPC("商人")
    assert npc.name == "商人"
    assert npc.personality == "neutral"


def test_npc_attitude():
    """测试NPC态度"""
    npc = NPC("村民")
    assert npc.attitude == 0
    
    npc.adjust_attitude(50)
    assert npc.attitude == 50
    assert npc.is_friendly()
    
    npc.adjust_attitude(-100)
    assert npc.attitude == -50
    assert npc.is_hostile()


def test_npc_following():
    """测试NPC跟随"""
    npc = NPC("同伴")
    assert not npc.follow_player
    
    npc.start_following()
    assert npc.follow_player
    
    npc.stop_following()
    assert not npc.follow_player
