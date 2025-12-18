"""
实体系统 - 库存系统

管理物品集合和容量限制
"""

from typing import List, Optional

from ..utils.logger import logger
from .item import Item


class Inventory:
    """库存系统"""

    def __init__(self, volume_capacity: int = 2500, weight_capacity: int = 13000):
        """
        初始化库存

        Args:
            volume_capacity: 体积容量（毫升）
            weight_capacity: 重量容量（克）
        """
        self.items: List[Item] = []
        self.volume_capacity = volume_capacity
        self.weight_capacity = weight_capacity

    def add_item(self, item: Item) -> bool:
        """
        添加物品

        Args:
            item: 要添加的物品

        Returns:
            是否成功添加
        """
        if self.can_add(item):
            self.items.append(item)
            logger.debug(f"添加物品到库存: {item.get_name()}")
            return True
        else:
            logger.debug(f"库存已满，无法添加: {item.get_name()}")
            return False

    def remove_item(self, item: Item) -> bool:
        """
        移除物品

        Args:
            item: 要移除的物品

        Returns:
            是否成功移除
        """
        if item in self.items:
            self.items.remove(item)
            logger.debug(f"从库存移除物品: {item.get_name()}")
            return True
        return False

    def can_add(self, item: Item) -> bool:
        """
        检查是否可以添加物品

        Args:
            item: 要添加的物品

        Returns:
            是否可以添加
        """
        new_volume = self.get_total_volume() + item.get_volume()
        new_weight = self.get_total_weight() + item.get_weight()

        return (new_volume <= self.volume_capacity and
                new_weight <= self.weight_capacity)

    def get_total_volume(self) -> int:
        """
        获取总体积

        Returns:
            总体积（毫升）
        """
        return sum(item.get_volume() for item in self.items)

    def get_total_weight(self) -> int:
        """
        获取总重量

        Returns:
            总重量（克）
        """
        return sum(item.get_weight() for item in self.items)

    def get_remaining_volume(self) -> int:
        """获取剩余体积"""
        return self.volume_capacity - self.get_total_volume()

    def get_remaining_weight(self) -> int:
        """获取剩余承重"""
        return self.weight_capacity - self.get_total_weight()

    def find_item_by_type(self, item_type_id: str) -> Optional[Item]:
        """
        按类型查找物品

        Args:
            item_type_id: 物品类型ID

        Returns:
            找到的物品，没有则返回 None
        """
        for item in self.items:
            if item.type_id == item_type_id:
                return item
        return None

    def find_all_items_by_type(self, item_type_id: str) -> List[Item]:
        """
        按类型查找所有物品

        Args:
            item_type_id: 物品类型ID

        Returns:
            物品列表
        """
        return [item for item in self.items if item.type_id == item_type_id]

    def get_item_count(self) -> int:
        """获取物品总数"""
        return len(self.items)

    def is_empty(self) -> bool:
        """检查库存是否为空"""
        return len(self.items) == 0

    def is_full(self) -> bool:
        """检查库存是否已满"""
        return (self.get_total_volume() >= self.volume_capacity or
                self.get_total_weight() >= self.weight_capacity)

    def clear(self):
        """清空库存"""
        self.items.clear()
        logger.debug("库存已清空")

    def get_items_by_category(self, category: str) -> List[Item]:
        """
        按类别获取物品

        Args:
            category: 类别名称

        Returns:
            物品列表
        """
        return [item for item in self.items if item.get_type() and item.get_type().category == category]

    def __len__(self) -> int:
        """返回物品数量"""
        return len(self.items)

    def __iter__(self):
        """迭代器"""
        return iter(self.items)

    def __repr__(self) -> str:
        """字符串表示"""
        return f"Inventory({len(self.items)} items, {self.get_total_volume()}/{self.volume_capacity}ml, {self.get_total_weight()}/{self.weight_capacity}g)"
