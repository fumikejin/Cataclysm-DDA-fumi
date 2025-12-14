"""
UI 模块 - 游戏视图

游戏画面的渲染区域
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QKeyEvent

from ..utils.logger import logger
from ..utils.config import config


class GameView(QWidget):
    """游戏视图组件"""

    def __init__(self):
        """初始化游戏视图"""
        super().__init__()

        # 设置焦点策略，以接收键盘事件
        self.setFocusPolicy(Qt.StrongFocus)

        # 视图大小
        self.tile_width = 24  # 每个格子的宽度（像素）
        self.tile_height = 24  # 每个格子的高度（像素）
        self.view_width = 40  # 可见格子宽度
        self.view_height = 30  # 可见格子高度

        # 设置最小大小
        self.setMinimumSize(
            self.tile_width * self.view_width, self.tile_height * self.view_height
        )

        # 字体设置
        font_size = config.get("graphics.font_size", 14)
        self.font = QFont("Monospace", font_size)
        self.font.setStyleHint(QFont.TypeWriter)

        # FPS 计数
        self.fps = 0
        self.frame_count = 0
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self._update_fps)
        self.fps_timer.start(1000)  # 每秒更新一次

        # 渲染定时器
        fps_limit = config.get("graphics.fps_limit", 60)
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.update)
        self.render_timer.start(1000 // fps_limit)

        # 测试数据 - 简单的地图
        self.test_map = self._generate_test_map()

        logger.info("游戏视图已初始化")

    def _generate_test_map(self):
        """生成测试地图数据"""
        # 创建一个简单的测试地图
        map_data = []
        for y in range(self.view_height):
            row = []
            for x in range(self.view_width):
                # 边界是墙
                if x == 0 or x == self.view_width - 1 or y == 0 or y == self.view_height - 1:
                    row.append({"symbol": "#", "color": "gray", "name": "墙"})
                # 中心位置是玩家
                elif x == self.view_width // 2 and y == self.view_height // 2:
                    row.append({"symbol": "@", "color": "white", "name": "你"})
                # 其他是地板
                else:
                    row.append({"symbol": ".", "color": "darkGray", "name": "地板"})
            map_data.append(row)
        return map_data

    def _update_fps(self):
        """更新 FPS 计数"""
        self.fps = self.frame_count
        self.frame_count = 0

    def paintEvent(self, event):
        """
        绘制事件

        Args:
            event: 绘制事件
        """
        painter = QPainter(self)
        painter.setFont(self.font)

        # 填充背景
        painter.fillRect(self.rect(), QColor(0, 0, 0))

        # 绘制地图
        self._draw_map(painter)

        # 绘制 FPS（如果启用）
        if config.get("debug.show_fps", False):
            self._draw_fps(painter)

        self.frame_count += 1

    def _draw_map(self, painter: QPainter):
        """
        绘制地图

        Args:
            painter: 绘图对象
        """
        for y in range(min(len(self.test_map), self.view_height)):
            for x in range(min(len(self.test_map[y]), self.view_width)):
                tile = self.test_map[y][x]

                # 设置颜色
                color_name = tile.get("color", "white")
                color = self._get_color(color_name)
                painter.setPen(QPen(color))

                # 绘制符号
                symbol = tile.get("symbol", " ")
                painter.drawText(
                    x * self.tile_width,
                    y * self.tile_height,
                    self.tile_width,
                    self.tile_height,
                    Qt.AlignCenter,
                    symbol,
                )

    def _draw_fps(self, painter: QPainter):
        """
        绘制 FPS

        Args:
            painter: 绘图对象
        """
        painter.setPen(QPen(QColor(255, 255, 0)))
        painter.drawText(10, 20, f"FPS: {self.fps}")

    def _get_color(self, color_name: str) -> QColor:
        """
        获取颜色对象

        Args:
            color_name: 颜色名称

        Returns:
            QColor 对象
        """
        color_map = {
            "white": QColor(255, 255, 255),
            "gray": QColor(128, 128, 128),
            "darkGray": QColor(64, 64, 64),
            "black": QColor(0, 0, 0),
            "red": QColor(255, 0, 0),
            "green": QColor(0, 255, 0),
            "blue": QColor(0, 0, 255),
            "yellow": QColor(255, 255, 0),
            "cyan": QColor(0, 255, 255),
            "magenta": QColor(255, 0, 255),
        }
        return color_map.get(color_name, QColor(255, 255, 255))

    def keyPressEvent(self, event: QKeyEvent):
        """
        键盘按键事件

        Args:
            event: 键盘事件
        """
        key = event.text().lower()

        # 获取移动键配置
        move_keys = {
            config.get("controls.move_north", "k"): (0, -1),
            config.get("controls.move_south", "j"): (0, 1),
            config.get("controls.move_east", "l"): (1, 0),
            config.get("controls.move_west", "h"): (-1, 0),
            config.get("controls.move_northeast", "u"): (1, -1),
            config.get("controls.move_northwest", "y"): (-1, -1),
            config.get("controls.move_southeast", "n"): (1, 1),
            config.get("controls.move_southwest", "b"): (-1, 1),
        }

        if key in move_keys:
            dx, dy = move_keys[key]
            logger.debug(f"移动: dx={dx}, dy={dy}")
            # TODO: 实际移动玩家
        elif key == config.get("controls.inventory", "i"):
            logger.info("打开库存")
            # TODO: 打开库存界面
        elif key == config.get("controls.examine", "e"):
            logger.info("检查")
            # TODO: 检查当前位置
        else:
            logger.debug(f"按键: {key}")

        event.accept()
