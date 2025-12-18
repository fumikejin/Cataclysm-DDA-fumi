"""
UI 模块 - 输入处理器

处理键盘和鼠标输入
"""

from typing import Callable, Dict, Optional
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QKeyEvent, QMouseEvent

from ..utils.logger import logger
from ..utils.config import config


class InputHandler(QObject):
    """输入处理器"""

    # 信号
    move_signal = Signal(int, int)  # 移动信号 (dx, dy)
    action_signal = Signal(str)  # 动作信号 (action_name)

    def __init__(self):
        """初始化输入处理器"""
        super().__init__()

        # 动作回调字典
        self.action_callbacks: Dict[str, Callable] = {}

        # 加载键位映射
        self._load_key_mappings()

        logger.info("输入处理器已初始化")

    def _load_key_mappings(self):
        """从配置加载键位映射"""
        self.key_mappings = {
            # 移动键
            config.get("controls.move_north", "k"): ("move", (0, -1)),
            config.get("controls.move_south", "j"): ("move", (0, 1)),
            config.get("controls.move_east", "l"): ("move", (1, 0)),
            config.get("controls.move_west", "h"): ("move", (-1, 0)),
            config.get("controls.move_northeast", "u"): ("move", (1, -1)),
            config.get("controls.move_northwest", "y"): ("move", (-1, -1)),
            config.get("controls.move_southeast", "n"): ("move", (1, 1)),
            config.get("controls.move_southwest", "b"): ("move", (-1, 1)),
            # 动作键
            config.get("controls.inventory", "i"): ("action", "inventory"),
            config.get("controls.pickup", ","): ("action", "pickup"),
            config.get("controls.drop", "d"): ("action", "drop"),
            config.get("controls.examine", "e"): ("action", "examine"),
            config.get("controls.crafting", "&"): ("action", "crafting"),
            config.get("controls.wait", "."): ("action", "wait"),
        }

    def handle_key_press(self, event: QKeyEvent) -> bool:
        """
        处理键盘按键事件

        Args:
            event: 键盘事件

        Returns:
            是否处理了事件
        """
        key = event.text().lower()

        if key in self.key_mappings:
            action_type, action_data = self.key_mappings[key]

            if action_type == "move":
                dx, dy = action_data
                self.move_signal.emit(dx, dy)
                logger.debug(f"移动: dx={dx}, dy={dy}")
                return True

            elif action_type == "action":
                action_name = action_data
                self.action_signal.emit(action_name)
                logger.debug(f"动作: {action_name}")

                # 调用注册的回调
                if action_name in self.action_callbacks:
                    self.action_callbacks[action_name]()

                return True

        return False

    def handle_mouse_press(self, event: QMouseEvent) -> bool:
        """
        处理鼠标按键事件

        Args:
            event: 鼠标事件

        Returns:
            是否处理了事件
        """
        # TODO: 实现鼠标输入处理
        return False

    def register_action(self, action_name: str, callback: Callable):
        """
        注册动作回调

        Args:
            action_name: 动作名称
            callback: 回调函数
        """
        self.action_callbacks[action_name] = callback
        logger.debug(f"注册动作回调: {action_name}")

    def unregister_action(self, action_name: str):
        """
        注销动作回调

        Args:
            action_name: 动作名称
        """
        if action_name in self.action_callbacks:
            del self.action_callbacks[action_name]
            logger.debug(f"注销动作回调: {action_name}")

    def reload_mappings(self):
        """重新加载键位映射"""
        self._load_key_mappings()
        logger.info("键位映射已重新加载")
