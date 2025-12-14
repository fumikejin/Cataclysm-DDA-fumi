"""
游戏世界 - 格子

单个地图格子的定义
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Tile:
    """地图格子"""

    terrain_id: str = "t_null"  # 地形ID
    furniture_id: Optional[str] = None  # 家具ID
    items: List = field(default_factory=list)  # 地面上的物品
    field: Dict = field(default_factory=dict)  # 场地效果
    light_level: int = 0  # 光照等级 (0-100)
    scent: int = 0  # 气味强度
    radiation: int = 0  # 辐射值
    temperature: int = 0  # 温度（开尔文）

    def get_move_cost(self) -> int:
        """
        获取移动成本

        Returns:
            移动成本
        """
        from .terrain import terrain_manager
        from .furniture import furniture_manager

        # 获取地形移动成本
        terrain = terrain_manager.get_terrain_or_default(self.terrain_id)
        move_cost = terrain.move_cost

        # 如果有家具，使用家具的移动成本
        if self.furniture_id:
            furniture = furniture_manager.get_furniture(self.furniture_id)
            if furniture and furniture.move_cost < move_cost:
                move_cost = furniture.move_cost

        return move_cost

    def is_passable(self) -> bool:
        """
        检查是否可通行

        Returns:
            是否可通行
        """
        return self.get_move_cost() > 0

    def is_transparent(self) -> bool:
        """
        检查是否透明（视线可穿透）

        Returns:
            是否透明
        """
        from .terrain import terrain_manager
        from .furniture import furniture_manager

        # 检查地形透明度
        terrain = terrain_manager.get_terrain_or_default(self.terrain_id)
        if not terrain.transparent:
            return False

        # 检查家具透明度
        if self.furniture_id:
            furniture = furniture_manager.get_furniture(self.furniture_id)
            if furniture and not furniture.transparent:
                return False

        return True

    def get_symbol(self) -> str:
        """
        获取显示符号

        Returns:
            符号字符
        """
        from .terrain import terrain_manager
        from .furniture import furniture_manager

        # 优先显示家具符号
        if self.furniture_id:
            furniture = furniture_manager.get_furniture(self.furniture_id)
            if furniture:
                return furniture.symbol

        # 否则显示地形符号
        terrain = terrain_manager.get_terrain_or_default(self.terrain_id)
        return terrain.symbol

    def get_color(self) -> str:
        """
        获取显示颜色

        Returns:
            颜色名称
        """
        from .terrain import terrain_manager
        from .furniture import furniture_manager

        # 优先使用家具颜色
        if self.furniture_id:
            furniture = furniture_manager.get_furniture(self.furniture_id)
            if furniture:
                return furniture.color

        # 否则使用地形颜色
        terrain = terrain_manager.get_terrain_or_default(self.terrain_id)
        return terrain.color

    def get_name(self) -> str:
        """
        获取名称

        Returns:
            格子名称
        """
        from .terrain import terrain_manager
        from .furniture import furniture_manager

        # 优先显示家具名称
        if self.furniture_id:
            furniture = furniture_manager.get_furniture(self.furniture_id)
            if furniture:
                return furniture.name

        # 否则显示地形名称
        terrain = terrain_manager.get_terrain_or_default(self.terrain_id)
        return terrain.name
