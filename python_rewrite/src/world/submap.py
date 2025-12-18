"""
游戏世界 - 子地图

12x12 格子的子地图
"""

from typing import List, Optional

from ..utils.point import Tripoint
from .tile import Tile
from .coordinates import SUBMAP_SIZE


class Submap:
    """子地图 (12x12 格子)"""

    def __init__(self, x: int, y: int, z: int):
        """
        初始化子地图

        Args:
            x: 子地图X坐标
            y: 子地图Y坐标
            z: 子地图Z层级
        """
        self.x = x
        self.y = y
        self.z = z

        # 创建格子网格
        self.tiles: List[List[Tile]] = [
            [Tile(terrain_id="t_grass") for _ in range(SUBMAP_SIZE)]
            for _ in range(SUBMAP_SIZE)
        ]

        # 生成点列表
        self.spawns: List = []  # 怪物生成点
        self.vehicles: List = []  # 车辆列表
        self.npcs: List = []  # NPC 列表

        # 子地图属性
        self.temperature: int = 293  # 温度（开尔文）
        self.last_touched: int = 0  # 上次活动时间

    def get_tile(self, local_x: int, local_y: int) -> Optional[Tile]:
        """
        获取局部坐标的格子

        Args:
            local_x: 局部X坐标 (0-11)
            local_y: 局部Y坐标 (0-11)

        Returns:
            格子对象，坐标无效则返回 None
        """
        if 0 <= local_x < SUBMAP_SIZE and 0 <= local_y < SUBMAP_SIZE:
            return self.tiles[local_y][local_x]
        return None

    def set_terrain(self, local_x: int, local_y: int, terrain_id: str):
        """
        设置地形

        Args:
            local_x: 局部X坐标
            local_y: 局部Y坐标
            terrain_id: 地形ID
        """
        tile = self.get_tile(local_x, local_y)
        if tile:
            tile.terrain_id = terrain_id

    def set_furniture(self, local_x: int, local_y: int, furniture_id: Optional[str]):
        """
        设置家具

        Args:
            local_x: 局部X坐标
            local_y: 局部Y坐标
            furniture_id: 家具ID，None表示移除家具
        """
        tile = self.get_tile(local_x, local_y)
        if tile:
            tile.furniture_id = furniture_id

    def fill_terrain(self, terrain_id: str):
        """
        用指定地形填充整个子地图

        Args:
            terrain_id: 地形ID
        """
        for y in range(SUBMAP_SIZE):
            for x in range(SUBMAP_SIZE):
                self.tiles[y][x].terrain_id = terrain_id

    def add_spawn(self, spawn_data: dict):
        """
        添加怪物生成点

        Args:
            spawn_data: 生成点数据
        """
        self.spawns.append(spawn_data)

    def get_position(self) -> Tripoint:
        """
        获取子地图位置

        Returns:
            子地图坐标
        """
        return Tripoint(self.x, self.y, self.z)
