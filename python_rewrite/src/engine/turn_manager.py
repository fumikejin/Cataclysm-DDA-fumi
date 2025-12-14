"""
游戏引擎 - 回合管理器

管理游戏的回合制时间系统
"""

from typing import List, Tuple, Callable

from ..utils.logger import logger


class TurnManager:
    """回合管理器"""

    def __init__(self):
        """初始化回合管理器"""
        self.current_turn = 0  # 当前回合数
        self.current_time = 0  # 当前游戏内时间（秒）
        self.time_scale = 6  # 时间缩放：1回合 = 6秒

        # 行动队列：(角色, 行动点数)
        self.action_queue: List[Tuple[any, int]] = []

        # 定时事件：(触发时间, 回调函数)
        self.scheduled_events: List[Tuple[int, Callable]] = []

        logger.info("回合管理器已初始化")

    def update(self, delta_time: float):
        """
        更新回合

        Args:
            delta_time: 经过的真实时间（秒）
        """
        # TODO: 实现实时更新逻辑
        pass

    def next_turn(self):
        """进入下一回合"""
        self.current_turn += 1
        self.current_time += self.time_scale

        logger.debug(f"回合 {self.current_turn}, 时间 {self.current_time}s")

        # 处理行动队列
        self._process_action_queue()

        # 处理定时事件
        self._process_scheduled_events()

    def _process_action_queue(self):
        """处理行动队列"""
        # 移除行动点数已用完的角色
        self.action_queue = [(char, ap - 100) for char, ap in self.action_queue if ap > 0]

        # TODO: 让有行动点的角色执行动作

    def _process_scheduled_events(self):
        """处理定时事件"""
        # 执行到达触发时间的事件
        events_to_execute = [
            callback for trigger_time, callback in self.scheduled_events if trigger_time <= self.current_time
        ]

        # 移除已执行的事件
        self.scheduled_events = [
            (time, callback)
            for time, callback in self.scheduled_events
            if time > self.current_time
        ]

        # 执行事件
        for callback in events_to_execute:
            try:
                callback()
            except Exception as e:
                logger.error(f"执行定时事件失败: {e}")

    def add_character(self, character, action_points: int = 100):
        """
        添加角色到行动队列

        Args:
            character: 角色对象
            action_points: 初始行动点数
        """
        self.action_queue.append((character, action_points))
        logger.debug(f"角色 {character} 加入行动队列")

    def remove_character(self, character):
        """
        从行动队列移除角色

        Args:
            character: 角色对象
        """
        self.action_queue = [(char, ap) for char, ap in self.action_queue if char != character]
        logger.debug(f"角色 {character} 离开行动队列")

    def schedule_event(self, delay: int, callback: Callable):
        """
        安排定时事件

        Args:
            delay: 延迟时间（游戏内秒数）
            callback: 回调函数
        """
        trigger_time = self.current_time + delay
        self.scheduled_events.append((trigger_time, callback))
        self.scheduled_events.sort(key=lambda x: x[0])  # 按时间排序
        logger.debug(f"安排定时事件，将在 {trigger_time}s 触发")

    def get_time_string(self) -> str:
        """
        获取格式化的游戏时间字符串

        Returns:
            时间字符串
        """
        total_seconds = self.current_time
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds // 60) % 60
        seconds = total_seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_turn_info(self) -> dict:
        """
        获取回合信息

        Returns:
            包含回合信息的字典
        """
        return {
            "turn": self.current_turn,
            "time": self.current_time,
            "time_string": self.get_time_string(),
            "action_queue_size": len(self.action_queue),
            "scheduled_events": len(self.scheduled_events),
        }
