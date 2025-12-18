"""
UI 模块 - 渲染器

抽象渲染接口，支持不同的渲染模式
"""

from abc import ABC, abstractmethod
from typing import Any, Tuple

from PySide6.QtGui import QPainter, QColor


class Renderer(ABC):
    """渲染器抽象基类"""

    @abstractmethod
    def render_tile(
        self, painter: QPainter, x: int, y: int, tile_data: dict, tile_size: Tuple[int, int]
    ):
        """
        渲染单个格子

        Args:
            painter: Qt 绘图对象
            x: X 坐标
            y: Y 坐标
            tile_data: 格子数据
            tile_size: 格子大小 (width, height)
        """
        pass

    @abstractmethod
    def render_character(
        self,
        painter: QPainter,
        x: int,
        y: int,
        character_data: dict,
        tile_size: Tuple[int, int],
    ):
        """
        渲染角色

        Args:
            painter: Qt 绘图对象
            x: X 坐标
            y: Y 坐标
            character_data: 角色数据
            tile_size: 格子大小
        """
        pass


class ASCIIRenderer(Renderer):
    """ASCII 字符渲染器"""

    def __init__(self):
        """初始化 ASCII 渲染器"""
        self.color_map = {
            "white": QColor(255, 255, 255),
            "gray": QColor(128, 128, 128),
            "darkGray": QColor(64, 64, 64),
            "black": QColor(0, 0, 0),
            "red": QColor(255, 0, 0),
            "darkRed": QColor(128, 0, 0),
            "green": QColor(0, 255, 0),
            "darkGreen": QColor(0, 128, 0),
            "blue": QColor(0, 0, 255),
            "darkBlue": QColor(0, 0, 128),
            "yellow": QColor(255, 255, 0),
            "darkYellow": QColor(128, 128, 0),
            "cyan": QColor(0, 255, 255),
            "darkCyan": QColor(0, 128, 128),
            "magenta": QColor(255, 0, 255),
            "darkMagenta": QColor(128, 0, 128),
            "brown": QColor(165, 42, 42),
            "lightGray": QColor(192, 192, 192),
        }

    def render_tile(
        self, painter: QPainter, x: int, y: int, tile_data: dict, tile_size: Tuple[int, int]
    ):
        """渲染格子（ASCII 模式）"""
        symbol = tile_data.get("symbol", " ")
        color_name = tile_data.get("color", "white")
        bg_color_name = tile_data.get("bg_color", "black")

        # 绘制背景
        bg_color = self._get_color(bg_color_name)
        painter.fillRect(
            x * tile_size[0], y * tile_size[1], tile_size[0], tile_size[1], bg_color
        )

        # 绘制符号
        color = self._get_color(color_name)
        painter.setPen(color)
        from PySide6.QtCore import Qt

        painter.drawText(
            x * tile_size[0],
            y * tile_size[1],
            tile_size[0],
            tile_size[1],
            Qt.AlignCenter,
            symbol,
        )

    def render_character(
        self,
        painter: QPainter,
        x: int,
        y: int,
        character_data: dict,
        tile_size: Tuple[int, int],
    ):
        """渲染角色（ASCII 模式）"""
        # 角色使用相同的渲染方式
        self.render_tile(painter, x, y, character_data, tile_size)

    def _get_color(self, color_name: str) -> QColor:
        """
        获取颜色对象

        Args:
            color_name: 颜色名称

        Returns:
            QColor 对象
        """
        return self.color_map.get(color_name, QColor(255, 255, 255))


class TileRenderer(Renderer):
    """图块渲染器（未来实现）"""

    def __init__(self):
        """初始化图块渲染器"""
        self.tileset = {}  # 图块集合
        # TODO: 加载图块资源

    def render_tile(
        self, painter: QPainter, x: int, y: int, tile_data: dict, tile_size: Tuple[int, int]
    ):
        """渲染格子（图块模式）"""
        # TODO: 实现图块渲染
        # 目前先使用 ASCII 渲染作为后备
        ascii_renderer = ASCIIRenderer()
        ascii_renderer.render_tile(painter, x, y, tile_data, tile_size)

    def render_character(
        self,
        painter: QPainter,
        x: int,
        y: int,
        character_data: dict,
        tile_size: Tuple[int, int],
    ):
        """渲染角色（图块模式）"""
        # TODO: 实现图块渲染
        ascii_renderer = ASCIIRenderer()
        ascii_renderer.render_character(painter, x, y, character_data, tile_size)


def get_renderer(renderer_type: str = "ASCII") -> Renderer:
    """
    获取渲染器实例

    Args:
        renderer_type: 渲染器类型 ("ASCII" 或 "Tile")

    Returns:
        渲染器实例
    """
    if renderer_type.upper() == "ASCII":
        return ASCIIRenderer()
    elif renderer_type.upper() == "TILE":
        return TileRenderer()
    else:
        # 默认使用 ASCII
        return ASCIIRenderer()
