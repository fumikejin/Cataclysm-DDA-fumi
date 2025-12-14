"""
游戏机制系统 - 技能系统

处理技能等级、经验和技能检定
"""

from typing import Dict, Optional

from ..utils.logger import logger
from ..entities.character import Character


class SkillSystem:
    """技能系统"""

    # 技能列表
    SKILLS = {
        "melee": "近战",
        "dodge": "闪避",
        "ranged": "远程",
        "survival": "生存",
        "crafting": "制作",
        "cooking": "烹饪",
        "mechanics": "机械",
        "electronics": "电子",
        "construction": "建造",
        "first_aid": "急救",
        "speech": "交涉",
        "barter": "交易",
        "computer": "计算机",
        "driving": "驾驶"
    }

    # 技能等级对应的经验值
    LEVEL_EXP = {
        0: 0,
        1: 100,
        2: 300,
        3: 600,
        4: 1000,
        5: 1500,
        6: 2100,
        7: 2800,
        8: 3600,
        9: 4500,
        10: 5500
    }

    def __init__(self):
        """初始化技能系统"""
        logger.info("技能系统已初始化")

    def get_skill_name(self, skill_id: str) -> str:
        """
        获取技能名称

        Args:
            skill_id: 技能ID

        Returns:
            技能名称
        """
        return self.SKILLS.get(skill_id, skill_id)

    def add_experience(self, character: Character, skill_id: str, exp: int):
        """
        增加技能经验

        Args:
            character: 角色
            skill_id: 技能ID
            exp: 经验值
        """
        current_level = character.get_skill_level(skill_id)

        # TODO: 实现完整的经验系统
        # 当前简化为：每100点经验提升1级
        if exp >= 100:
            new_level = current_level + 1
            character.set_skill_level(skill_id, new_level)
            logger.info(f"{character.name} 的 {self.get_skill_name(skill_id)} 技能提升到 {new_level} 级")

    def skill_check(self, character: Character, skill_id: str, difficulty: int) -> bool:
        """
        技能检定

        Args:
            character: 角色
            skill_id: 技能ID
            difficulty: 难度（0-20）

        Returns:
            是否成功
        """
        skill_level = character.get_skill_level(skill_id)

        # 简单的检定：技能等级 + 1d10 vs 难度
        import random
        roll = skill_level + random.randint(1, 10)

        success = roll >= difficulty
        logger.debug(f"{character.name} 技能检定 {self.get_skill_name(skill_id)}: {roll} vs {difficulty} - {'成功' if success else '失败'}")

        return success

    def get_skill_bonus(self, character: Character, skill_id: str) -> int:
        """
        获取技能加成

        Args:
            character: 角色
            skill_id: 技能ID

        Returns:
            加成值
        """
        return character.get_skill_level(skill_id)

    def can_craft(self, character: Character, recipe_skill: str, recipe_level: int) -> bool:
        """
        检查是否可以制作

        Args:
            character: 角色
            recipe_skill: 配方所需技能
            recipe_level: 配方所需等级

        Returns:
            是否可以制作
        """
        character_skill = character.get_skill_level(recipe_skill)
        return character_skill >= recipe_level

    def learn_recipe(self, character: Character, recipe_id: str):
        """
        学习配方

        Args:
            character: 角色
            recipe_id: 配方ID
        """
        # TODO: 实现配方系统
        logger.info(f"{character.name} 学习了配方: {recipe_id}")

    def get_all_skills(self) -> Dict[str, str]:
        """
        获取所有技能

        Returns:
            技能字典 {id: name}
        """
        return self.SKILLS.copy()
