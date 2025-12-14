"""
实体系统 - 角色基类

玩家和NPC的共同基类
"""

from typing import List, Dict, Optional

from ..utils.point import Tripoint
from ..utils.logger import logger
from .inventory import Inventory
from .item import Item


class Character:
    """角色基类（玩家和NPC的共同基类）"""

    def __init__(self, name: str):
        """
        初始化角色

        Args:
            name: 角色名称
        """
        self.name = name
        self.position = Tripoint(0, 0, 0)

        # 基础属性 (SPECIAL)
        self.str = 8  # 力量 (Strength)
        self.dex = 8  # 敏捷 (Dexterity)
        self.int = 8  # 智力 (Intelligence)
        self.per = 8  # 感知 (Perception)

        # 生命值
        self.hp_max = 84  # 最大生命值
        self.hp_cur = 84  # 当前生命值

        # 体力
        self.stamina_max = 10000
        self.stamina_cur = 10000

        # 需求
        self.pain = 0  # 疼痛
        self.thirst = 0  # 口渴
        self.hunger = 0  # 饥饿
        self.fatigue = 0  # 疲劳

        # 技能字典 {技能名: 等级}
        self.skills: Dict[str, int] = {}

        # 特征和突变
        self.traits: List[str] = []
        self.mutations: List[str] = []

        # 生化插件
        self.bionics: List[str] = []

        # 库存
        self.inventory = Inventory()
        self.worn_items: List[Item] = []  # 穿戴的物品
        self.wielded_item: Optional[Item] = None  # 手持的物品

        # 移动相关
        self.moves = 100  # 行动点数

        logger.info(f"角色 '{name}' 已创建")

    def move_to(self, new_pos: Tripoint):
        """
        移动到新位置

        Args:
            new_pos: 新位置
        """
        self.position = new_pos
        logger.debug(f"{self.name} 移动到 {new_pos}")

    def get_speed(self) -> int:
        """
        获取移动速度

        Returns:
            移动速度（影响回合行动）
        """
        base_speed = 100

        # 根据负重调整
        encumbrance_penalty = self._calculate_encumbrance_penalty()
        speed = base_speed - encumbrance_penalty

        # 根据状态调整
        if self.pain > 0:
            speed -= self.pain // 2

        return max(25, speed)  # 最小速度25

    def _calculate_encumbrance_penalty(self) -> int:
        """计算负重惩罚"""
        total_weight = self.inventory.get_total_weight()
        # 简化的负重计算
        if total_weight > self.inventory.weight_capacity * 0.8:
            return 20
        elif total_weight > self.inventory.weight_capacity * 0.5:
            return 10
        return 0

    def is_alive(self) -> bool:
        """
        检查是否存活

        Returns:
            是否存活
        """
        return self.hp_cur > 0

    def take_damage(self, damage: int):
        """
        受到伤害

        Args:
            damage: 伤害值
        """
        self.hp_cur -= damage
        if self.hp_cur < 0:
            self.hp_cur = 0
        logger.info(f"{self.name} 受到 {damage} 点伤害，剩余生命: {self.hp_cur}/{self.hp_max}")

    def heal(self, amount: int):
        """
        治疗

        Args:
            amount: 治疗量
        """
        self.hp_cur += amount
        if self.hp_cur > self.hp_max:
            self.hp_cur = self.hp_max
        logger.debug(f"{self.name} 恢复 {amount} 点生命，当前生命: {self.hp_cur}/{self.hp_max}")

    def get_skill_level(self, skill_name: str) -> int:
        """
        获取技能等级

        Args:
            skill_name: 技能名称

        Returns:
            技能等级
        """
        return self.skills.get(skill_name, 0)

    def set_skill_level(self, skill_name: str, level: int):
        """
        设置技能等级

        Args:
            skill_name: 技能名称
            level: 技能等级
        """
        self.skills[skill_name] = level
        logger.debug(f"{self.name} 的 {skill_name} 技能设置为 {level}")

    def has_trait(self, trait_name: str) -> bool:
        """
        检查是否有特定特征

        Args:
            trait_name: 特征名称

        Returns:
            是否拥有该特征
        """
        return trait_name in self.traits

    def add_trait(self, trait_name: str):
        """
        添加特征

        Args:
            trait_name: 特征名称
        """
        if trait_name not in self.traits:
            self.traits.append(trait_name)
            logger.info(f"{self.name} 获得特征: {trait_name}")

    def remove_trait(self, trait_name: str):
        """
        移除特征

        Args:
            trait_name: 特征名称
        """
        if trait_name in self.traits:
            self.traits.remove(trait_name)
            logger.info(f"{self.name} 失去特征: {trait_name}")

    def wield_item(self, item: Item) -> bool:
        """
        手持物品

        Args:
            item: 要手持的物品

        Returns:
            是否成功
        """
        if item in self.inventory.items:
            self.wielded_item = item
            logger.info(f"{self.name} 手持 {item.get_name()}")
            return True
        return False

    def unwield(self):
        """放下手持物品"""
        if self.wielded_item:
            logger.info(f"{self.name} 放下 {self.wielded_item.get_name()}")
            self.wielded_item = None

    def wear_item(self, item: Item) -> bool:
        """
        穿戴物品

        Args:
            item: 要穿戴的物品

        Returns:
            是否成功
        """
        if item in self.inventory.items:
            self.worn_items.append(item)
            self.inventory.remove_item(item)
            logger.info(f"{self.name} 穿上 {item.get_name()}")
            return True
        return False

    def remove_worn_item(self, item: Item) -> bool:
        """
        脱下穿戴的物品

        Args:
            item: 要脱下的物品

        Returns:
            是否成功
        """
        if item in self.worn_items:
            self.worn_items.remove(item)
            self.inventory.add_item(item)
            logger.info(f"{self.name} 脱下 {item.get_name()}")
            return True
        return False

    def __repr__(self) -> str:
        """字符串表示"""
        return f"Character({self.name}, HP:{self.hp_cur}/{self.hp_max}, Pos:{self.position})"
