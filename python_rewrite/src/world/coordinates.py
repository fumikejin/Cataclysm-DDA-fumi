"""
游戏世界 - 坐标系统

实现 CDDA 的多层坐标系统和转换
"""

from ..utils.point import Tripoint


# 地图常量
SUBMAP_SIZE = 12  # 子地图大小 (12x12 格子)
REALITY_BUBBLE_RADIUS = 60  # 现实泡泡半径（格子）


class Coordinates:
    """坐标转换工具类"""

    @staticmethod
    def tile_to_submap(tile_pos: Tripoint) -> Tripoint:
        """
        将格子坐标转换为子地图坐标

        Args:
            tile_pos: 格子全局坐标

        Returns:
            子地图坐标
        """
        return Tripoint(
            tile_pos.x // SUBMAP_SIZE,
            tile_pos.y // SUBMAP_SIZE,
            tile_pos.z
        )

    @staticmethod
    def tile_local(tile_pos: Tripoint) -> Tripoint:
        """
        获取格子在子地图内的局部坐标

        Args:
            tile_pos: 格子全局坐标

        Returns:
            局部坐标 (0-11)
        """
        return Tripoint(
            tile_pos.x % SUBMAP_SIZE,
            tile_pos.y % SUBMAP_SIZE,
            tile_pos.z
        )

    @staticmethod
    def submap_to_tile(submap_pos: Tripoint, local_pos: Tripoint) -> Tripoint:
        """
        将子地图坐标和局部坐标转换为格子全局坐标

        Args:
            submap_pos: 子地图坐标
            local_pos: 局部坐标

        Returns:
            格子全局坐标
        """
        return Tripoint(
            submap_pos.x * SUBMAP_SIZE + local_pos.x,
            submap_pos.y * SUBMAP_SIZE + local_pos.y,
            submap_pos.z
        )

    @staticmethod
    def is_valid_local(local_pos: Tripoint) -> bool:
        """
        检查局部坐标是否有效

        Args:
            local_pos: 局部坐标

        Returns:
            是否有效 (0 <= x,y < SUBMAP_SIZE)
        """
        return (0 <= local_pos.x < SUBMAP_SIZE and
                0 <= local_pos.y < SUBMAP_SIZE)

    @staticmethod
    def in_reality_bubble(center: Tripoint, pos: Tripoint) -> bool:
        """
        检查位置是否在现实泡泡内

        Args:
            center: 中心位置（通常是玩家位置）
            pos: 要检查的位置

        Returns:
            是否在现实泡泡内
        """
        dx = abs(pos.x - center.x)
        dy = abs(pos.y - center.y)
        return (dx <= REALITY_BUBBLE_RADIUS and
                dy <= REALITY_BUBBLE_RADIUS and
                pos.z == center.z)
