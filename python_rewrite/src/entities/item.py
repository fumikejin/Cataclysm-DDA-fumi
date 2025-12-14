"""
实体系统 - 物品实例

物品实例类，代表游戏中的实际物品
"""

from typing import List, Optional
from uuid import uuid4

from ..utils.point import Tripoint
from ..utils.logger import logger
from .item_type import item_type_manager, ItemType


class Item:
    """物品实例"""

    def __init__(self, item_type_id: str):
        """
        初始化物品实例

        Args:
            item_type_id: 物品类型ID
        """
        self.type_id = item_type_id
        self.uid = str(uuid4())  # 唯一ID

        # 物品状态
        self.charges = 0  # 充能/弹药数量
        self.damage_level = 0  # 损坏等级 (0=完好, >0=损坏)
        self.temperature = 0  # 温度（开尔文）
        self.active = False  # 是否激活
        self.contents: List[Item] = []  # 内容物（容器）
        self.position: Optional[Tripoint] = None  # 位置（如果在地图上）

        # 自定义属性
        self.custom_name: Optional[str] = None  # 自定义名称
        self.custom_description: Optional[str] = None  # 自定义描述

    def get_type(self) -> Optional[ItemType]:
        """
        获取物品类型

        Returns:
            物品类型对象
        """
        return item_type_manager.get_item_type(self.type_id)

    def get_name(self) -> str:
        """
        获取显示名称

        Returns:
            物品名称
        """
        if self.custom_name:
            return self.custom_name

        item_type = self.get_type()
        if item_type:
            return item_type.name
        return "未知物品"

    def get_description(self) -> str:
        """
        获取描述

        Returns:
            物品描述
        """
        if self.custom_description:
            return self.custom_description

        item_type = self.get_type()
        if item_type:
            return item_type.description
        return "未知物品"

    def get_weight(self) -> int:
        """
        获取重量（包括内容物）

        Returns:
            总重量（克）
        """
        item_type = self.get_type()
        if not item_type:
            return 0

        base_weight = item_type.weight

        # 添加内容物重量
        contents_weight = sum(item.get_weight() for item in self.contents)

        return base_weight + contents_weight

    def get_volume(self) -> int:
        """
        获取体积

        Returns:
            体积（毫升）
        """
        item_type = self.get_type()
        if not item_type:
            return 0
        return item_type.volume

    def get_symbol(self) -> str:
        """
        获取显示符号

        Returns:
            ASCII 符号
        """
        item_type = self.get_type()
        if item_type:
            return item_type.symbol
        return "?"

    def get_color(self) -> str:
        """
        获取显示颜色

        Returns:
            颜色名称
        """
        item_type = self.get_type()
        if item_type:
            return item_type.color
        return "white"

    def can_contain(self, other_item: "Item") -> bool:
        """
        检查是否可以容纳另一个物品

        Args:
            other_item: 要放入的物品

        Returns:
            是否可以容纳
        """
        # TODO: 实现容器检查逻辑
        return False

    def add_item(self, item: "Item") -> bool:
        """
        添加物品到内容物

        Args:
            item: 要添加的物品

        Returns:
            是否成功添加
        """
        if self.can_contain(item):
            self.contents.append(item)
            return True
        return False

    def remove_item(self, item: "Item"):
        """
        从内容物中移除物品

        Args:
            item: 要移除的物品
        """
        if item in self.contents:
            self.contents.remove(item)

    def is_damaged(self) -> bool:
        """
        检查是否损坏

        Returns:
            是否损坏
        """
        return self.damage_level > 0

    def get_damage_description(self) -> str:
        """
        获取损坏等级描述

        Returns:
            损坏描述
        """
        if self.damage_level == 0:
            return "完好"
        elif self.damage_level < 2:
            return "轻微损坏"
        elif self.damage_level < 4:
            return "损坏"
        else:
            return "严重损坏"

    def __repr__(self) -> str:
        """字符串表示"""
        return f"Item({self.get_name()}, uid={self.uid[:8]})"


def create_item(item_type_id: str, count: int = 1) -> List[Item]:
    """
    创建物品实例

    Args:
        item_type_id: 物品类型ID
        count: 创建数量

    Returns:
        物品实例列表
    """
    items = []
    for _ in range(count):
        items.append(Item(item_type_id))
    return items
