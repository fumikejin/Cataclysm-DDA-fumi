"""
游戏世界 - 地形

地形类型的定义和管理
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

from ..utils.logger import logger


@dataclass
class TerrainType:
    """地形类型"""

    id: str  # 地形ID
    name: str  # 显示名称
    description: str = ""  # 描述
    symbol: str = " "  # ASCII 符号
    color: str = "white"  # 颜色
    bg_color: str = "black"  # 背景颜色
    move_cost: int = 100  # 移动成本 (0 = 不可通行)
    flags: List[str] = None  # 标志列表
    transparent: bool = True  # 是否透明（视线可穿透）
    bashable: bool = False  # 是否可破坏
    bash_str_min: int = 0  # 破坏所需最小力量
    bash_ter: str = None  # 破坏后变成的地形

    def __post_init__(self):
        if self.flags is None:
            self.flags = []


class TerrainManager:
    """地形管理器"""

    def __init__(self):
        """初始化地形管理器"""
        self.terrain_types: Dict[str, TerrainType] = {}
        self._load_default_terrains()
        logger.info("地形管理器已初始化")

    def _load_default_terrains(self):
        """加载默认地形类型"""
        # 基础地形
        self.register_terrain(TerrainType(
            id="t_null",
            name="虚空",
            symbol=" ",
            color="black",
            move_cost=0,
            transparent=False
        ))

        self.register_terrain(TerrainType(
            id="t_grass",
            name="草地",
            symbol=".",
            color="green",
            move_cost=100,
            transparent=True
        ))

        self.register_terrain(TerrainType(
            id="t_dirt",
            name="泥土",
            symbol=".",
            color="brown",
            move_cost=100,
            transparent=True
        ))

        self.register_terrain(TerrainType(
            id="t_floor",
            name="地板",
            symbol=".",
            color="lightGray",
            move_cost=100,
            transparent=True
        ))

        self.register_terrain(TerrainType(
            id="t_wall",
            name="墙壁",
            symbol="#",
            color="gray",
            move_cost=0,
            transparent=False,
            bashable=True,
            bash_str_min=50
        ))

        self.register_terrain(TerrainType(
            id="t_wall_wood",
            name="木墙",
            symbol="#",
            color="brown",
            move_cost=0,
            transparent=False,
            bashable=True,
            bash_str_min=30
        ))

        self.register_terrain(TerrainType(
            id="t_door_c",
            name="门（关闭）",
            symbol="+",
            color="brown",
            move_cost=0,
            transparent=False
        ))

        self.register_terrain(TerrainType(
            id="t_door_o",
            name="门（打开）",
            symbol="'",
            color="brown",
            move_cost=100,
            transparent=True
        ))

        self.register_terrain(TerrainType(
            id="t_window",
            name="窗户",
            symbol="0",
            color="cyan",
            move_cost=0,
            transparent=True,
            bashable=True,
            bash_str_min=20
        ))

        self.register_terrain(TerrainType(
            id="t_water_sh",
            name="浅水",
            symbol="~",
            color="blue",
            move_cost=150,
            transparent=True,
            flags=["SWIMMABLE"]
        ))

    def register_terrain(self, terrain: TerrainType):
        """
        注册地形类型

        Args:
            terrain: 地形类型
        """
        self.terrain_types[terrain.id] = terrain

    def get_terrain(self, terrain_id: str) -> Optional[TerrainType]:
        """
        获取地形类型

        Args:
            terrain_id: 地形ID

        Returns:
            地形类型，不存在则返回 None
        """
        return self.terrain_types.get(terrain_id)

    def get_terrain_or_default(self, terrain_id: str) -> TerrainType:
        """
        获取地形类型，不存在则返回默认地形

        Args:
            terrain_id: 地形ID

        Returns:
            地形类型
        """
        return self.terrain_types.get(terrain_id, self.terrain_types["t_null"])

    def load_from_data(self, terrain_data: dict):
        """
        从数据字典加载地形

        Args:
            terrain_data: 地形数据
        """
        terrain = TerrainType(
            id=terrain_data.get("id", ""),
            name=terrain_data.get("name", ""),
            description=terrain_data.get("description", ""),
            symbol=terrain_data.get("symbol", " "),
            color=terrain_data.get("color", "white"),
            bg_color=terrain_data.get("bgcolor", "black"),
            move_cost=terrain_data.get("move_cost", 100),
            flags=terrain_data.get("flags", []),
            transparent="TRANSPARENT" in terrain_data.get("flags", []),
            bashable="bash" in terrain_data
        )

        self.register_terrain(terrain)

    def get_terrain_count(self) -> int:
        """获取已注册的地形数量"""
        return len(self.terrain_types)


# 全局地形管理器实例
terrain_manager = TerrainManager()
