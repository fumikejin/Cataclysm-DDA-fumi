"""
游戏引擎 - 事件系统

管理游戏中的事件发布和订阅
"""

from typing import Dict, List, Callable, Any

from ..utils.logger import logger


class Event:
    """事件类"""

    def __init__(self, event_type: str, data: Any = None):
        """
        初始化事件

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        self.event_type = event_type
        self.data = data


class EventSystem:
    """事件系统"""

    def __init__(self):
        """初始化事件系统"""
        # 事件监听器字典: {事件类型: [回调函数列表]}
        self.listeners: Dict[str, List[Callable]] = {}

        # 事件队列
        self.event_queue: List[Event] = []

        logger.info("事件系统已初始化")

    def subscribe(self, event_type: str, callback: Callable):
        """
        订阅事件

        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []

        if callback not in self.listeners[event_type]:
            self.listeners[event_type].append(callback)
            logger.debug(f"订阅事件: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable):
        """
        取消订阅事件

        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        if event_type in self.listeners:
            if callback in self.listeners[event_type]:
                self.listeners[event_type].remove(callback)
                logger.debug(f"取消订阅事件: {event_type}")

    def publish(self, event: Event):
        """
        发布事件（加入队列）

        Args:
            event: 事件对象
        """
        self.event_queue.append(event)
        logger.debug(f"发布事件: {event.event_type}")

    def publish_immediate(self, event: Event):
        """
        立即发布事件（不加入队列）

        Args:
            event: 事件对象
        """
        self._dispatch_event(event)

    def process_events(self):
        """处理事件队列"""
        while self.event_queue:
            event = self.event_queue.pop(0)
            self._dispatch_event(event)

    def _dispatch_event(self, event: Event):
        """
        分发事件给监听器

        Args:
            event: 事件对象
        """
        if event.event_type in self.listeners:
            for callback in self.listeners[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"处理事件 {event.event_type} 时出错: {e}")

    def clear_queue(self):
        """清空事件队列"""
        self.event_queue.clear()
        logger.debug("事件队列已清空")

    def get_listener_count(self, event_type: str = None) -> int:
        """
        获取监听器数量

        Args:
            event_type: 事件类型，如果为 None 则返回所有监听器总数

        Returns:
            监听器数量
        """
        if event_type is None:
            return sum(len(listeners) for listeners in self.listeners.values())
        else:
            return len(self.listeners.get(event_type, []))


# 常用事件类型常量
class EventTypes:
    """事件类型常量"""

    # 游戏事件
    GAME_START = "game_start"
    GAME_PAUSE = "game_pause"
    GAME_RESUME = "game_resume"
    GAME_QUIT = "game_quit"

    # 角色事件
    PLAYER_MOVE = "player_move"
    PLAYER_ATTACK = "player_attack"
    PLAYER_DEATH = "player_death"
    PLAYER_LEVEL_UP = "player_level_up"

    # 物品事件
    ITEM_PICKUP = "item_pickup"
    ITEM_DROP = "item_drop"
    ITEM_USE = "item_use"
    ITEM_CRAFT = "item_craft"

    # 战斗事件
    COMBAT_START = "combat_start"
    COMBAT_END = "combat_end"
    DAMAGE_DEALT = "damage_dealt"
    DAMAGE_RECEIVED = "damage_received"

    # UI 事件
    UI_OPEN = "ui_open"
    UI_CLOSE = "ui_close"
    MESSAGE_DISPLAY = "message_display"
