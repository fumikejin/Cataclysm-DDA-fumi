"""
游戏机制系统 - 动作系统

统一的动作处理框架
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..utils.point import Point, Tripoint
from ..utils.logger import logger
from ..entities.character import Character
from ..entities.item import Item


class Action(ABC):
    """动作基类"""

    def __init__(self):
        """初始化动作"""
        self.success = False
        self.message = ""

    @abstractmethod
    def can_perform(self, character: Character) -> bool:
        """
        检查是否可以执行动作

        Args:
            character: 执行动作的角色

        Returns:
            是否可以执行
        """
        pass

    @abstractmethod
    def perform(self, character: Character) -> bool:
        """
        执行动作

        Args:
            character: 执行动作的角色

        Returns:
            是否成功执行
        """
        pass

    def get_time_cost(self) -> int:
        """
        获取动作的时间花费（行动点）

        Returns:
            时间花费
        """
        return 100

    def __repr__(self) -> str:
        """字符串表示"""
        return f"{self.__class__.__name__}()"


class MoveAction(Action):
    """移动动作"""

    def __init__(self, direction: Point, movement_system=None):
        """
        初始化移动动作

        Args:
            direction: 移动方向
            movement_system: 移动系统实例
        """
        super().__init__()
        self.direction = direction
        self.movement_system = movement_system

    def can_perform(self, character: Character) -> bool:
        """检查是否可以移动"""
        if not self.movement_system:
            return False

        # 计算目标位置
        target_pos = Tripoint(
            character.position.x + self.direction.x,
            character.position.y + self.direction.y,
            character.position.z
        )

        return self.movement_system.can_move_to(character, target_pos)

    def perform(self, character: Character) -> bool:
        """执行移动"""
        if not self.movement_system:
            self.message = "移动系统未初始化"
            return False

        success = self.movement_system.move_character(character, self.direction)
        self.success = success

        if success:
            self.message = f"{character.name} 移动了"
        else:
            self.message = f"{character.name} 无法移动到该位置"

        return success

    def __repr__(self) -> str:
        return f"MoveAction(direction={self.direction})"


class PickupAction(Action):
    """拾取物品动作"""

    def __init__(self, item: Item):
        """
        初始化拾取动作

        Args:
            item: 要拾取的物品
        """
        super().__init__()
        self.item = item

    def can_perform(self, character: Character) -> bool:
        """检查是否可以拾取"""
        # 检查库存是否有空间
        return character.inventory.can_add(self.item)

    def perform(self, character: Character) -> bool:
        """执行拾取"""
        if character.inventory.add_item(self.item):
            self.success = True
            self.message = f"{character.name} 拾取了 {self.item.get_name()}"
            logger.info(self.message)
            return True
        else:
            self.message = f"{character.name} 库存已满，无法拾取 {self.item.get_name()}"
            logger.debug(self.message)
            return False

    def get_time_cost(self) -> int:
        """拾取花费较少时间"""
        return 50


class DropAction(Action):
    """丢弃物品动作"""

    def __init__(self, item: Item):
        """
        初始化丢弃动作

        Args:
            item: 要丢弃的物品
        """
        super().__init__()
        self.item = item

    def can_perform(self, character: Character) -> bool:
        """检查是否可以丢弃"""
        return self.item in character.inventory.items

    def perform(self, character: Character) -> bool:
        """执行丢弃"""
        if character.inventory.remove_item(self.item):
            self.success = True
            self.message = f"{character.name} 丢弃了 {self.item.get_name()}"
            # TODO: 将物品放置在地图上角色的位置
            logger.info(self.message)
            return True
        else:
            self.message = f"{character.name} 没有 {self.item.get_name()}"
            return False

    def get_time_cost(self) -> int:
        """丢弃花费较少时间"""
        return 30


class WieldAction(Action):
    """装备武器动作"""

    def __init__(self, item: Item):
        """
        初始化装备动作

        Args:
            item: 要装备的物品
        """
        super().__init__()
        self.item = item

    def can_perform(self, character: Character) -> bool:
        """检查是否可以装备"""
        return self.item in character.inventory.items

    def perform(self, character: Character) -> bool:
        """执行装备"""
        if character.wield_item(self.item):
            self.success = True
            self.message = f"{character.name} 装备了 {self.item.get_name()}"
            logger.info(self.message)
            return True
        else:
            self.message = f"{character.name} 无法装备 {self.item.get_name()}"
            return False

    def get_time_cost(self) -> int:
        """装备花费一些时间"""
        return 80


class WaitAction(Action):
    """等待动作"""

    def __init__(self, duration: int = 100):
        """
        初始化等待动作

        Args:
            duration: 等待时长（行动点）
        """
        super().__init__()
        self.duration = duration

    def can_perform(self, character: Character) -> bool:
        """总是可以等待"""
        return True

    def perform(self, character: Character) -> bool:
        """执行等待"""
        self.success = True
        self.message = f"{character.name} 等待了一会"
        logger.debug(self.message)
        return True

    def get_time_cost(self) -> int:
        """返回等待时长"""
        return self.duration


class AttackAction(Action):
    """攻击动作"""

    def __init__(self, target: Character, combat_system=None):
        """
        初始化攻击动作

        Args:
            target: 攻击目标
            combat_system: 战斗系统实例
        """
        super().__init__()
        self.target = target
        self.combat_system = combat_system

    def can_perform(self, character: Character) -> bool:
        """检查是否可以攻击"""
        # 检查目标是否存活
        if not self.target.is_alive():
            return False

        # 检查距离（简单检查：是否相邻）
        distance = character.position.distance_to(self.target.position)
        return distance <= 1.5  # 允许对角线攻击

    def perform(self, character: Character) -> bool:
        """执行攻击"""
        if not self.combat_system:
            self.message = "战斗系统未初始化"
            return False

        # 执行近战攻击
        damage = self.combat_system.melee_attack(character, self.target)

        self.success = damage > 0
        if damage > 0:
            self.message = f"{character.name} 攻击 {self.target.name}，造成 {damage} 点伤害"
        else:
            self.message = f"{character.name} 的攻击未命中 {self.target.name}"

        logger.info(self.message)
        return self.success

    def get_time_cost(self) -> int:
        """攻击花费标准时间"""
        return 100
