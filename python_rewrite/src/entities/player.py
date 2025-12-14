"""
实体系统 - 玩家

玩家角色类
"""

from ..utils.logger import logger
from .character import Character


class Player(Character):
    """玩家角色"""

    def __init__(self, name: str = "玩家"):
        """
        初始化玩家

        Args:
            name: 玩家名称
        """
        super().__init__(name)

        # 玩家特有属性
        self.profession = None  # 职业
        self.scenario = None  # 场景
        self.starting_location = None  # 起始位置

        # 玩家统计
        self.kills = 0  # 击杀数
        self.turns_survived = 0  # 存活回合数

        logger.info(f"玩家角色 '{name}' 已创建")

    def set_profession(self, profession_id: str):
        """
        设置职业

        Args:
            profession_id: 职业ID
        """
        self.profession = profession_id
        logger.info(f"玩家职业设置为: {profession_id}")
        # TODO: 根据职业应用起始技能和物品

    def set_scenario(self, scenario_id: str):
        """
        设置场景

        Args:
            scenario_id: 场景ID
        """
        self.scenario = scenario_id
        logger.info(f"玩家场景设置为: {scenario_id}")
        # TODO: 根据场景设置起始位置和条件

    def on_turn_end(self):
        """回合结束时调用"""
        self.turns_survived += 1

        # 处理需求增长
        self.thirst += 1
        self.hunger += 1
        self.fatigue += 1

        # TODO: 处理其他回合效果

    def on_kill(self):
        """击杀敌人时调用"""
        self.kills += 1
        logger.debug(f"{self.name} 击杀数: {self.kills}")

    def get_stats_summary(self) -> dict:
        """
        获取统计摘要

        Returns:
            统计信息字典
        """
        return {
            "name": self.name,
            "hp": f"{self.hp_cur}/{self.hp_max}",
            "stamina": f"{self.stamina_cur}/{self.stamina_max}",
            "str": self.str,
            "dex": self.dex,
            "int": self.int,
            "per": self.per,
            "kills": self.kills,
            "turns_survived": self.turns_survived,
            "inventory_items": len(self.inventory),
            "position": str(self.position)
        }

    def __repr__(self) -> str:
        """字符串表示"""
        return f"Player({self.name}, HP:{self.hp_cur}/{self.hp_max}, Kills:{self.kills})"
