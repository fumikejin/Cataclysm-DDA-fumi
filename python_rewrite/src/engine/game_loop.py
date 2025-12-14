"""
游戏引擎 - 游戏循环

管理游戏的主循环，使用 Qt 的事件循环
"""

from PySide6.QtCore import QTimer

from ..utils.logger import logger


class GameLoop:
    """游戏循环管理器"""

    def __init__(self, game):
        """
        初始化游戏循环

        Args:
            game: 游戏实例
        """
        self.game = game
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

        # 目标帧率
        self.target_fps = 60
        self.frame_time = 1000 // self.target_fps  # 毫秒

        # 时间追踪
        self.last_update_time = 0
        self.delta_time = 0.0

        logger.info(f"游戏循环已初始化，目标 FPS: {self.target_fps}")

    def start(self):
        """启动游戏循环"""
        logger.info("游戏循环已启动")
        self.timer.start(self.frame_time)

    def stop(self):
        """停止游戏循环"""
        logger.info("游戏循环已停止")
        self.timer.stop()

    def update(self):
        """更新游戏状态（每帧调用）"""
        # 计算 delta time
        from PySide6.QtCore import QTime

        current_time = QTime.currentTime().msecsSinceStartOfDay()
        self.delta_time = (current_time - self.last_update_time) / 1000.0
        self.last_update_time = current_time

        # 更新游戏
        if self.game.running:
            self.game.update(self.delta_time)

    def set_fps(self, fps: int):
        """
        设置目标帧率

        Args:
            fps: 目标帧率
        """
        self.target_fps = fps
        self.frame_time = 1000 // fps
        if self.timer.isActive():
            self.timer.setInterval(self.frame_time)
        logger.info(f"目标 FPS 已设置为: {fps}")
