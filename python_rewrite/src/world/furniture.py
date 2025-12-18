"""
游戏世界 - 家具

家具类型的定义和管理
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

from ..utils.logger import logger


@dataclass
class FurnitureType:
    """家具类型"""

    id: str  # 家具ID
    name: str  # 显示名称
    description: str = ""  # 描述
    symbol: str = "f"  # ASCII 符号
    color: str = "white"  # 颜色
    bg_color: str = "black"  # 背景颜色
    move_cost: int = 0  # 移动成本 (0 = 不可通行)
    flags: List[str] = None  # 标志列表
    transparent: bool = True  # 是否透明
    bashable: bool = False  # 是否可破坏
    bash_str_min: int = 0  # 破坏所需最小力量
    max_volume: int = 0  # 最大容量（容器家具）

    def __post_init__(self):
        if self.flags is None:
            self.flags = []


class FurnitureManager:
    """家具管理器"""

    def __init__(self):
        """初始化家具管理器"""
        self.furniture_types: Dict[str, FurnitureType] = {}
        self._load_default_furniture()
        logger.info("家具管理器已初始化")

    def _load_default_furniture(self):
        """加载默认家具类型"""
        # 基础家具
        self.register_furniture(FurnitureType(
            id="f_null",
            name="无",
            symbol=" ",
            color="white",
            move_cost=100,
            transparent=True
        ))

        self.register_furniture(FurnitureType(
            id="f_chair",
            name="椅子",
            symbol="H",
            color="brown",
            move_cost=150,
            transparent=True,
            bashable=True,
            bash_str_min=10
        ))

        self.register_furniture(FurnitureType(
            id="f_table",
            name="桌子",
            symbol="T",
            color="brown",
            move_cost=200,
            transparent=True,
            bashable=True,
            bash_str_min=20
        ))

        self.register_furniture(FurnitureType(
            id="f_bed",
            name="床",
            symbol="o",
            color="cyan",
            move_cost=200,
            transparent=True,
            flags=["BED"],
            bashable=True,
            bash_str_min=15
        ))

        self.register_furniture(FurnitureType(
            id="f_bookcase",
            name="书架",
            symbol="|",
            color="brown",
            move_cost=0,
            transparent=False,
            max_volume=400000,
            bashable=True,
            bash_str_min=25
        ))

        self.register_furniture(FurnitureType(
            id="f_locker",
            name="储物柜",
            symbol="{",
            color="lightGray",
            move_cost=0,
            transparent=False,
            max_volume=200000,
            bashable=True,
            bash_str_min=30
        ))

        self.register_furniture(FurnitureType(
            id="f_rack",
            name="货架",
            symbol="&",
            color="gray",
            move_cost=0,
            transparent=True,
            max_volume=300000,
            bashable=True,
            bash_str_min=20
        ))

        self.register_furniture(FurnitureType(
            id="f_counter",
            name="柜台",
            symbol="=",
            color="cyan",
            move_cost=0,
            transparent=True,
            bashable=True,
            bash_str_min=25
        ))

        self.register_furniture(FurnitureType(
            id="f_fridge",
            name="冰箱",
            symbol="{",
            color="white",
            move_cost=0,
            transparent=False,
            max_volume=150000,
            flags=["COLD"],
            bashable=True,
            bash_str_min=40
        ))

    def register_furniture(self, furniture: FurnitureType):
        """
        注册家具类型

        Args:
            furniture: 家具类型
        """
        self.furniture_types[furniture.id] = furniture

    def get_furniture(self, furniture_id: str) -> Optional[FurnitureType]:
        """
        获取家具类型

        Args:
            furniture_id: 家具ID

        Returns:
            家具类型，不存在则返回 None
        """
        return self.furniture_types.get(furniture_id)

    def get_furniture_or_default(self, furniture_id: str) -> FurnitureType:
        """
        获取家具类型，不存在则返回默认家具

        Args:
            furniture_id: 家具ID

        Returns:
            家具类型
        """
        return self.furniture_types.get(furniture_id, self.furniture_types["f_null"])

    def load_from_data(self, furniture_data: dict):
        """
        从数据字典加载家具

        Args:
            furniture_data: 家具数据
        """
        furniture = FurnitureType(
            id=furniture_data.get("id", ""),
            name=furniture_data.get("name", ""),
            description=furniture_data.get("description", ""),
            symbol=furniture_data.get("symbol", "f"),
            color=furniture_data.get("color", "white"),
            bg_color=furniture_data.get("bgcolor", "black"),
            move_cost=furniture_data.get("move_cost", 0),
            flags=furniture_data.get("flags", []),
            transparent="TRANSPARENT" in furniture_data.get("flags", []),
            bashable="bash" in furniture_data,
            max_volume=furniture_data.get("max_volume", 0)
        )

        self.register_furniture(furniture)

    def get_furniture_count(self) -> int:
        """获取已注册的家具数量"""
        return len(self.furniture_types)


# 全局家具管理器实例
furniture_manager = FurnitureManager()
