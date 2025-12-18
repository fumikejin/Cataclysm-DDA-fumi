"""
测试游戏机制 - 技能和制作系统
"""

from src.systems.skill import SkillSystem
from src.systems.crafting import CraftingSystem, Recipe
from src.entities.player import Player
from src.entities.item import Item


def test_skill_system_creation():
    """测试技能系统创建"""
    skill_sys = SkillSystem()
    assert skill_sys is not None


def test_skill_names():
    """测试技能名称"""
    skill_sys = SkillSystem()
    
    assert skill_sys.get_skill_name("melee") == "近战"
    assert skill_sys.get_skill_name("crafting") == "制作"


def test_skill_check():
    """测试技能检定"""
    skill_sys = SkillSystem()
    player = Player("测试玩家")
    
    player.set_skill_level("melee", 5)
    
    # 多次检定，应该有成功和失败
    results = [skill_sys.skill_check(player, "melee", 10) for _ in range(20)]
    assert isinstance(results[0], bool)


def test_skill_bonus():
    """测试技能加成"""
    skill_sys = SkillSystem()
    player = Player("测试玩家")
    
    player.set_skill_level("crafting", 3)
    bonus = skill_sys.get_skill_bonus(player, "crafting")
    assert bonus == 3


def test_can_craft_check():
    """测试制作能力检查"""
    skill_sys = SkillSystem()
    player = Player("测试玩家")
    
    player.set_skill_level("crafting", 2)
    
    # 等级足够
    assert skill_sys.can_craft(player, "crafting", 2)
    assert skill_sys.can_craft(player, "crafting", 1)
    
    # 等级不够
    assert not skill_sys.can_craft(player, "crafting", 3)


def test_crafting_system_creation():
    """测试制作系统创建"""
    crafting = CraftingSystem()
    assert crafting is not None
    assert len(crafting.recipes) > 0


def test_recipe_registration():
    """测试配方注册"""
    crafting = CraftingSystem()
    initial_count = len(crafting.recipes)
    
    recipe = Recipe(
        id="test_recipe",
        name="测试配方",
        result="stick",
        components=[{"rock": 1}]
    )
    
    crafting.register_recipe(recipe)
    assert len(crafting.recipes) == initial_count + 1
    assert crafting.get_recipe("test_recipe") == recipe


def test_has_components():
    """测试材料检查"""
    crafting = CraftingSystem()
    player = Player("测试玩家")
    
    recipe = Recipe(
        id="test",
        name="测试",
        result="stick",
        components=[{"rock": 2}]
    )
    
    # 没有材料
    assert not crafting.has_components(player, recipe)
    
    # 添加材料
    player.inventory.add_item(Item("rock"))
    player.inventory.add_item(Item("rock"))
    
    # 现在有材料了
    assert crafting.has_components(player, recipe)


def test_crafting():
    """测试制作物品"""
    crafting = CraftingSystem()
    player = Player("测试玩家")
    
    # 设置技能和材料
    player.set_skill_level("crafting", 2)
    player.inventory.add_item(Item("rock"))
    player.inventory.add_item(Item("rock"))
    player.inventory.add_item(Item("stick"))
    
    # 获取配方
    recipe = crafting.get_recipe("recipe_stone_knife")
    assert recipe is not None
    
    # 检查是否可以制作
    if crafting.can_craft(player, recipe):
        initial_count = len(player.inventory.items)
        success = crafting.craft(player, recipe)
        assert success


def test_get_craftable_recipes():
    """测试获取可制作配方"""
    crafting = CraftingSystem()
    player = Player("测试玩家")
    
    # 设置技能
    player.set_skill_level("crafting", 5)
    
    # 添加各种材料
    for _ in range(3):
        player.inventory.add_item(Item("stick"))
        player.inventory.add_item(Item("rock"))
    
    craftable = crafting.get_craftable_recipes(player)
    assert isinstance(craftable, list)
