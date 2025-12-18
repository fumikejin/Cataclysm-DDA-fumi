"""
实体系统 - 物品类型

定义物品类型的数据结构
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from ..utils.logger import logger


@dataclass
class ItemType:
    """物品类型定义"""

    id: str  # 物品ID
    name: str  # 显示名称
    description: str = ""  # 描述
    symbol: str = "?"  # ASCII 符号
    color: str = "white"  # 颜色
    weight: int = 0  # 重量（克）
    volume: int = 0  # 体积（毫升）
    category: str = "other"  # 类别
    material: List[str] = field(default_factory=list)  # 材料列表
    flags: List[str] = field(default_factory=list)  # 标志列表
    price: int = 0  # 价格
    damage: Dict[str, int] = field(default_factory=dict)  # 伤害（如果是武器）
    armor: Dict[str, int] = field(default_factory=dict)  # 护甲值（如果是防具）
    max_charges: int = 0  # 最大充能/弹药
    use_action: str = None  # 使用动作


class ItemTypeManager:
    """物品类型管理器"""

    def __init__(self):
        """初始化物品类型管理器"""
        self.item_types: Dict[str, ItemType] = {}
        self._load_default_items()
        logger.info("物品类型管理器已初始化")

    def _load_default_items(self):
        """加载默认物品类型"""
        # 基础物品
        self.register_item(ItemType(
            id="stick",
            name="木棍",
            description="一根普通的木棍",
            symbol="/",
            color="brown",
            weight=500,
            volume=1000,
            category="weapon",
            material=["wood"],
            damage={"bash": 6}
        ))

        self.register_item(ItemType(
            id="rock",
            name="石头",
            description="一块普通的石头",
            symbol="*",
            color="gray",
            weight=200,
            volume=250,
            category="weapon",
            material=["stone"],
            damage={"bash": 4}
        ))

        self.register_item(ItemType(
            id="bottle_plastic",
            name="塑料瓶",
            description="一个空的塑料瓶",
            symbol=")",
            color="cyan",
            weight=10,
            volume=500,
            category="container",
            material=["plastic"]
        ))

        self.register_item(ItemType(
            id="water",
            name="水",
            description="干净的饮用水",
            symbol="~",
            color="blue",
            weight=1,  # 1克/毫升
            volume=1,  # 1毫升
            category="food",
            material=["liquid"]
        ))

        self.register_item(ItemType(
            id="apple",
            name="苹果",
            description="新鲜的红苹果",
            symbol="%",
            color="red",
            weight=200,
            volume=250,
            category="food",
            material=["fruit"]
        ))

        self.register_item(ItemType(
            id="jeans",
            name="牛仔裤",
            description="耐用的牛仔裤",
            symbol="[",
            color="blue",
            weight=800,
            volume=1500,
            category="armor",
            material=["cotton"],
            armor={"bash": 2, "cut": 4}
        ))

        self.register_item(ItemType(
            id="tshirt",
            name="T恤",
            description="普通的T恤",
            symbol="[",
            color="white",
            weight=200,
            volume=500,
            category="armor",
            material=["cotton"],
            armor={"bash": 1, "cut": 1}
        ))

    def register_item(self, item_type: ItemType):
        """
        注册物品类型

        Args:
            item_type: 物品类型
        """
        self.item_types[item_type.id] = item_type

    def get_item_type(self, item_id: str) -> Optional[ItemType]:
        """
        获取物品类型

        Args:
            item_id: 物品ID

        Returns:
            物品类型，不存在则返回 None
        """
        return self.item_types.get(item_id)

    def load_from_data(self, item_data: dict):
        """
        从数据字典加载物品类型

        Args:
            item_data: 物品数据
        """
        item_type = ItemType(
            id=item_data.get("id", ""),
            name=item_data.get("name", ""),
            description=item_data.get("description", ""),
            symbol=item_data.get("symbol", "?"),
            color=item_data.get("color", "white"),
            weight=item_data.get("weight", 0),
            volume=item_data.get("volume", 0),
            category=item_data.get("category", "other"),
            material=item_data.get("material", []),
            flags=item_data.get("flags", []),
            price=item_data.get("price", 0),
            damage=item_data.get("damage", {}),
            armor=item_data.get("armor", {}),
            max_charges=item_data.get("max_charges", 0),
            use_action=item_data.get("use_action")
        )

        self.register_item(item_type)

    def get_item_count(self) -> int:
        """获取已注册的物品类型数量"""
        return len(self.item_types)

    def get_items_by_category(self, category: str) -> List[ItemType]:
        """
        按类别获取物品类型列表

        Args:
            category: 类别名称

        Returns:
            物品类型列表
        """
        return [item for item in self.item_types.values() if item.category == category]


# 全局物品类型管理器实例
item_type_manager = ItemTypeManager()
