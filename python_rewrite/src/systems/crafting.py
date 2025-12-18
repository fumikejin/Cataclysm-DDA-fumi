"""
游戏机制系统 - 制作系统

处理物品制作和配方管理
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from ..utils.logger import logger
from ..entities.character import Character
from ..entities.item import Item, create_item
from ..entities.item_type import item_type_manager


@dataclass
class Recipe:
    """配方定义"""

    id: str  # 配方ID
    name: str  # 配方名称
    result: str  # 产出物品ID
    result_count: int = 1  # 产出数量
    skill_required: str = "crafting"  # 所需技能
    skill_level: int = 0  # 所需技能等级
    time: int = 100  # 制作时间（回合）
    components: List[Dict[str, int]] = field(default_factory=list)  # 材料 [{item_id: count}]
    tools: List[str] = field(default_factory=list)  # 所需工具ID列表


class CraftingSystem:
    """制作系统"""

    def __init__(self):
        """初始化制作系统"""
        self.recipes: Dict[str, Recipe] = {}
        self._load_default_recipes()
        logger.info("制作系统已初始化")

    def _load_default_recipes(self):
        """加载默认配方"""
        # 木矛配方
        self.register_recipe(Recipe(
            id="recipe_wooden_spear",
            name="木矛",
            result="stick",  # 简化：暂用木棍代替
            result_count=1,
            skill_required="crafting",
            skill_level=1,
            time=50,
            components=[{"stick": 1}],
            tools=[]
        ))

        # 简单工具配方
        self.register_recipe(Recipe(
            id="recipe_stone_knife",
            name="石刀",
            result="rock",  # 简化：暂用石头代替
            result_count=1,
            skill_required="crafting",
            skill_level=2,
            time=100,
            components=[{"rock": 2}, {"stick": 1}],
            tools=[]
        ))

    def register_recipe(self, recipe: Recipe):
        """
        注册配方

        Args:
            recipe: 配方对象
        """
        self.recipes[recipe.id] = recipe
        logger.debug(f"注册配方: {recipe.name}")

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """
        获取配方

        Args:
            recipe_id: 配方ID

        Returns:
            配方对象
        """
        return self.recipes.get(recipe_id)

    def can_craft(self, character: Character, recipe: Recipe) -> bool:
        """
        检查是否可以制作

        Args:
            character: 角色
            recipe: 配方

        Returns:
            是否可以制作
        """
        # 检查技能等级
        skill_level = character.get_skill_level(recipe.skill_required)
        if skill_level < recipe.skill_level:
            logger.debug(f"{character.name} 技能不足，无法制作 {recipe.name}")
            return False

        # 检查材料
        if not self.has_components(character, recipe):
            logger.debug(f"{character.name} 材料不足，无法制作 {recipe.name}")
            return False

        # TODO: 检查工具
        # if not self.has_tools(character, recipe):
        #     return False

        return True

    def has_components(self, character: Character, recipe: Recipe) -> bool:
        """
        检查是否有足够的材料

        Args:
            character: 角色
            recipe: 配方

        Returns:
            是否有足够材料
        """
        for component in recipe.components:
            for item_id, required_count in component.items():
                # 计算库存中该类型物品的数量
                items = character.inventory.find_all_items_by_type(item_id)
                if len(items) < required_count:
                    return False

        return True

    def consume_components(self, character: Character, recipe: Recipe):
        """
        消耗材料

        Args:
            character: 角色
            recipe: 配方
        """
        for component in recipe.components:
            for item_id, required_count in component.items():
                # 移除所需数量的物品
                items = character.inventory.find_all_items_by_type(item_id)
                for i in range(min(required_count, len(items))):
                    character.inventory.remove_item(items[i])

        logger.debug(f"{character.name} 消耗了制作材料")

    def craft(self, character: Character, recipe: Recipe) -> bool:
        """
        制作物品

        Args:
            character: 角色
            recipe: 配方

        Returns:
            是否成功制作
        """
        # 检查是否可以制作
        if not self.can_craft(character, recipe):
            logger.info(f"{character.name} 无法制作 {recipe.name}")
            return False

        # 消耗材料
        self.consume_components(character, recipe)

        # 创建产出物品
        result_items = create_item(recipe.result, recipe.result_count)

        # 添加到库存
        for item in result_items:
            if not character.inventory.add_item(item):
                # TODO: 如果库存满了，物品应该掉落在地上
                logger.warning(f"{character.name} 库存已满，无法获得 {item.get_name()}")

        logger.info(f"{character.name} 成功制作了 {recipe.name} x{recipe.result_count}")

        # TODO: 增加技能经验
        # skill_system.add_experience(character, recipe.skill_required, recipe.skill_level * 10)

        return True

    def get_craftable_recipes(self, character: Character) -> List[Recipe]:
        """
        获取角色可以制作的配方列表

        Args:
            character: 角色

        Returns:
            可制作的配方列表
        """
        craftable = []
        for recipe in self.recipes.values():
            if self.can_craft(character, recipe):
                craftable.append(recipe)

        return craftable

    def get_all_recipes(self) -> List[Recipe]:
        """
        获取所有配方

        Returns:
            配方列表
        """
        return list(self.recipes.values())

    def load_recipe_from_data(self, recipe_data: dict):
        """
        从数据字典加载配方

        Args:
            recipe_data: 配方数据
        """
        recipe = Recipe(
            id=recipe_data.get("id", ""),
            name=recipe_data.get("name", ""),
            result=recipe_data.get("result", ""),
            result_count=recipe_data.get("result_count", 1),
            skill_required=recipe_data.get("skill_required", "crafting"),
            skill_level=recipe_data.get("skill_level", 0),
            time=recipe_data.get("time", 100),
            components=recipe_data.get("components", []),
            tools=recipe_data.get("tools", [])
        )

        self.register_recipe(recipe)
