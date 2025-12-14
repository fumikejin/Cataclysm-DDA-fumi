"""
游戏世界 - 地图

管理子地图集合和格子访问
"""

from typing import Dict, Tuple, Optional

from ..utils.point import Tripoint
from ..utils.logger import logger
from .tile import Tile
from .submap import Submap
from .coordinates import Coordinates, SUBMAP_SIZE


class Map:
    """游戏地图管理器"""

    def __init__(self):
        """初始化地图"""
        # 子地图字典: {(x, y, z): Submap}
        self.submaps: Dict[Tuple[int, int, int], Submap] = {}

        # 中心位置（现实泡泡中心）
        self.center = Tripoint(0, 0, 0)

        logger.info("地图已初始化")

    def get_submap(self, x: int, y: int, z: int) -> Submap:
        """
        获取或创建子地图

        Args:
            x: 子地图X坐标
            y: 子地图Y坐标
            z: 子地图Z层级

        Returns:
            子地图对象
        """
        key = (x, y, z)
        if key not in self.submaps:
            self.submaps[key] = Submap(x, y, z)
            logger.debug(f"创建新子地图: ({x}, {y}, {z})")

        return self.submaps[key]

    def get_tile(self, pos: Tripoint) -> Optional[Tile]:
        """
        获取全局坐标的格子

        Args:
            pos: 全局坐标

        Returns:
            格子对象，坐标无效则返回 None
        """
        # 转换为子地图坐标和局部坐标
        submap_pos = Coordinates.tile_to_submap(pos)
        local_pos = Coordinates.tile_local(pos)

        # 获取子地图
        submap = self.get_submap(submap_pos.x, submap_pos.y, submap_pos.z)

        # 获取格子
        return submap.get_tile(local_pos.x, local_pos.y)

    def set_terrain(self, pos: Tripoint, terrain_id: str):
        """
        设置全局坐标的地形

        Args:
            pos: 全局坐标
            terrain_id: 地形ID
        """
        submap_pos = Coordinates.tile_to_submap(pos)
        local_pos = Coordinates.tile_local(pos)

        submap = self.get_submap(submap_pos.x, submap_pos.y, submap_pos.z)
        submap.set_terrain(local_pos.x, local_pos.y, terrain_id)

    def set_furniture(self, pos: Tripoint, furniture_id: Optional[str]):
        """
        设置全局坐标的家具

        Args:
            pos: 全局坐标
            furniture_id: 家具ID
        """
        submap_pos = Coordinates.tile_to_submap(pos)
        local_pos = Coordinates.tile_local(pos)

        submap = self.get_submap(submap_pos.x, submap_pos.y, submap_pos.z)
        submap.set_furniture(local_pos.x, local_pos.y, furniture_id)

    def is_passable(self, pos: Tripoint) -> bool:
        """
        检查位置是否可通行

        Args:
            pos: 全局坐标

        Returns:
            是否可通行
        """
        tile = self.get_tile(pos)
        return tile.is_passable() if tile else False

    def is_transparent(self, pos: Tripoint) -> bool:
        """
        检查位置是否透明

        Args:
            pos: 全局坐标

        Returns:
            是否透明
        """
        tile = self.get_tile(pos)
        return tile.is_transparent() if tile else False

    def generate_test_map(self, center_pos: Tripoint, radius: int = 30):
        """
        生成测试地图（简单的房间）

        Args:
            center_pos: 中心位置
            radius: 生成半径
        """
        logger.info(f"生成测试地图，中心: {center_pos}, 半径: {radius}")

        # 填充草地
        for x in range(center_pos.x - radius, center_pos.x + radius):
            for y in range(center_pos.y - radius, center_pos.y + radius):
                pos = Tripoint(x, y, center_pos.z)
                self.set_terrain(pos, "t_grass")

        # 创建一个房间
        room_x = center_pos.x - 10
        room_y = center_pos.y - 10
        room_width = 20
        room_height = 15

        # 地板
        for x in range(room_x, room_x + room_width):
            for y in range(room_y, room_y + room_height):
                pos = Tripoint(x, y, center_pos.z)
                self.set_terrain(pos, "t_floor")

        # 墙壁
        for x in range(room_x, room_x + room_width):
            self.set_terrain(Tripoint(x, room_y, center_pos.z), "t_wall")
            self.set_terrain(Tripoint(x, room_y + room_height - 1, center_pos.z), "t_wall")

        for y in range(room_y, room_y + room_height):
            self.set_terrain(Tripoint(room_x, y, center_pos.z), "t_wall")
            self.set_terrain(Tripoint(room_x + room_width - 1, y, center_pos.z), "t_wall")

        # 门
        door_x = room_x + room_width // 2
        door_y = room_y
        self.set_terrain(Tripoint(door_x, door_y, center_pos.z), "t_door_c")

        # 一些家具
        self.set_furniture(Tripoint(room_x + 2, room_y + 2, center_pos.z), "f_chair")
        self.set_furniture(Tripoint(room_x + 3, room_y + 2, center_pos.z), "f_table")
        self.set_furniture(Tripoint(room_x + 5, room_y + 2, center_pos.z), "f_bed")

        logger.info("测试地图生成完成")

    def get_submap_count(self) -> int:
        """获取已加载的子地图数量"""
        return len(self.submaps)

    def set_center(self, center: Tripoint):
        """
        设置中心位置（现实泡泡中心）

        Args:
            center: 新的中心位置
        """
        self.center = center

    def clear_distant_submaps(self, keep_radius: int = 100):
        """
        清理远离中心的子地图以节省内存

        Args:
            keep_radius: 保留的子地图半径（子地图单位）
        """
        center_submap = Coordinates.tile_to_submap(self.center)
        to_remove = []

        for key in self.submaps.keys():
            x, y, z = key
            if z != center_submap.z:
                continue

            dx = abs(x - center_submap.x)
            dy = abs(y - center_submap.y)

            if dx > keep_radius or dy > keep_radius:
                to_remove.append(key)

        for key in to_remove:
            del self.submaps[key]

        if to_remove:
            logger.info(f"清理了 {len(to_remove)} 个远离的子地图")
