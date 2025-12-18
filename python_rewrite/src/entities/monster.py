"""
实体系统 - 怪物实例

怪物实例类
"""

from typing import Optional
from uuid import uuid4

from ..utils.point import Tripoint
from ..utils.logger import logger
from .monster_type import monster_type_manager, MonsterType


class Monster:
    """怪物实例"""

    def __init__(self, monster_type_id: str):
        """
        初始化怪物实例

        Args:
            monster_type_id: 怪物类型ID
        """
        self.type_id = monster_type_id
        self.uid = str(uuid4())  # 唯一ID

        # 获取怪物类型
        monster_type = self.get_type()

        # 位置
        self.position = Tripoint(0, 0, 0)

        # 生命值
        if monster_type:
            self.hp_max = monster_type.hp
            self.hp_cur = monster_type.hp
        else:
            self.hp_max = 10
            self.hp_cur = 10

        # AI 状态
        self.friendly = False  # 是否友好
        self.target_position: Optional[Tripoint] = None  # 目标位置
        self.anger = 0  # 愤怒值
        self.current_morale = 0  # 当前士气

        # 移动相关
        self.moves = 100  # 行动点数

    def get_type(self) -> Optional[MonsterType]:
        """
        获取怪物类型

        Returns:
            怪物类型对象
        """
        return monster_type_manager.get_monster_type(self.type_id)

    def get_name(self) -> str:
        """
        获取显示名称

        Returns:
            怪物名称
        """
        monster_type = self.get_type()
        if monster_type:
            return monster_type.name
        return "未知怪物"

    def get_symbol(self) -> str:
        """
        获取显示符号

        Returns:
            ASCII 符号
        """
        monster_type = self.get_type()
        if monster_type:
            return monster_type.symbol
        return "?"

    def get_color(self) -> str:
        """
        获取显示颜色

        Returns:
            颜色名称
        """
        monster_type = self.get_type()
        if monster_type:
            return monster_type.color
        return "red"

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

        self.anger += 10  # 受伤增加愤怒值

        logger.debug(f"{self.get_name()} 受到 {damage} 点伤害，剩余生命: {self.hp_cur}/{self.hp_max}")

    def get_speed(self) -> int:
        """
        获取移动速度

        Returns:
            移动速度
        """
        monster_type = self.get_type()
        if monster_type:
            return monster_type.speed
        return 100

    def can_see_target(self, target_pos: Tripoint, is_day: bool = True) -> bool:
        """
        检查是否能看到目标

        Args:
            target_pos: 目标位置
            is_day: 是否是白天

        Returns:
            是否能看到
        """
        monster_type = self.get_type()
        if not monster_type:
            return False

        # 计算距离
        distance = self.position.distance_to(target_pos)

        # 检查视野范围
        vision_range = monster_type.vision_day if is_day else monster_type.vision_night

        return distance <= vision_range

    def set_target(self, target_pos: Tripoint):
        """
        设置目标位置

        Args:
            target_pos: 目标位置
        """
        self.target_position = target_pos

    def clear_target(self):
        """清除目标"""
        self.target_position = None

    def has_target(self) -> bool:
        """检查是否有目标"""
        return self.target_position is not None

    def is_hostile(self) -> bool:
        """
        检查是否敌对

        Returns:
            是否敌对
        """
        if self.friendly:
            return False

        monster_type = self.get_type()
        if monster_type:
            return monster_type.aggression > 0 or self.anger > 0

        return False

    def __repr__(self) -> str:
        """字符串表示"""
        return f"Monster({self.get_name()}, HP:{self.hp_cur}/{self.hp_max}, Pos:{self.position})"


def spawn_monster(monster_type_id: str, position: Tripoint) -> Monster:
    """
    生成怪物

    Args:
        monster_type_id: 怪物类型ID
        position: 生成位置

    Returns:
        怪物实例
    """
    monster = Monster(monster_type_id)
    monster.position = position
    logger.info(f"生成怪物: {monster.get_name()} 在 {position}")
    return monster
