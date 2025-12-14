"""
实体系统 - NPC

非玩家角色类
"""

from ..utils.logger import logger
from .character import Character


class NPC(Character):
    """NPC（非玩家角色）"""

    def __init__(self, name: str):
        """
        初始化NPC

        Args:
            name: NPC名称
        """
        super().__init__(name)

        # NPC特有属性
        self.personality = "neutral"  # 性格 (friendly, neutral, aggressive)
        self.faction = None  # 所属派系
        self.mission = None  # 当前任务
        self.attitude = 0  # 对玩家的态度 (-100到100)

        # AI行为
        self.ai_enabled = True  # 是否启用AI
        self.follow_player = False  # 是否跟随玩家
        self.guard_position = None  # 守卫位置

        logger.info(f"NPC '{name}' 已创建")

    def set_personality(self, personality: str):
        """
        设置性格

        Args:
            personality: 性格类型
        """
        self.personality = personality
        logger.debug(f"NPC {self.name} 性格设置为: {personality}")

    def set_faction(self, faction_id: str):
        """
        设置派系

        Args:
            faction_id: 派系ID
        """
        self.faction = faction_id
        logger.debug(f"NPC {self.name} 加入派系: {faction_id}")

    def adjust_attitude(self, amount: int):
        """
        调整态度

        Args:
            amount: 调整量（正值增加好感，负值减少）
        """
        self.attitude += amount
        self.attitude = max(-100, min(100, self.attitude))
        logger.debug(f"NPC {self.name} 态度调整为: {self.attitude}")

    def is_friendly(self) -> bool:
        """
        检查是否友好

        Returns:
            是否友好
        """
        return self.attitude > 0 or self.personality == "friendly"

    def is_hostile(self) -> bool:
        """
        检查是否敌对

        Returns:
            是否敌对
        """
        return self.attitude < -50 or self.personality == "aggressive"

    def start_following(self):
        """开始跟随玩家"""
        self.follow_player = True
        logger.info(f"NPC {self.name} 开始跟随玩家")

    def stop_following(self):
        """停止跟随玩家"""
        self.follow_player = False
        logger.info(f"NPC {self.name} 停止跟随玩家")

    def assign_mission(self, mission_id: str):
        """
        分配任务

        Args:
            mission_id: 任务ID
        """
        self.mission = mission_id
        logger.info(f"NPC {self.name} 接受任务: {mission_id}")

    def complete_mission(self):
        """完成任务"""
        if self.mission:
            logger.info(f"NPC {self.name} 完成任务: {self.mission}")
            self.mission = None

    def __repr__(self) -> str:
        """字符串表示"""
        return f"NPC({self.name}, Attitude:{self.attitude}, HP:{self.hp_cur}/{self.hp_max})"
