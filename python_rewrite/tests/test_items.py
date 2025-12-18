"""
测试实体系统 - 物品系统
"""

from src.entities.item_type import item_type_manager, ItemType
from src.entities.item import Item, create_item
from src.entities.inventory import Inventory


def test_item_type_manager():
    """测试物品类型管理器"""
    # 应该有默认物品
    assert item_type_manager.get_item_count() > 0
    
    # 获取特定物品
    stick = item_type_manager.get_item_type("stick")
    assert stick is not None
    assert stick.name == "木棍"


def test_item_creation():
    """测试物品创建"""
    item = Item("stick")
    assert item is not None
    assert item.type_id == "stick"
    assert item.get_name() == "木棍"


def test_item_weight():
    """测试物品重量"""
    item = Item("stick")
    weight = item.get_weight()
    assert weight == 500  # 木棍重500克


def test_create_item():
    """测试批量创建物品"""
    items = create_item("apple", count=3)
    assert len(items) == 3
    for item in items:
        assert item.type_id == "apple"


def test_inventory():
    """测试库存系统"""
    inv = Inventory()
    assert inv.is_empty()
    
    # 添加物品
    item = Item("apple")
    assert inv.add_item(item)
    assert not inv.is_empty()
    assert len(inv) == 1
    
    # 移除物品
    assert inv.remove_item(item)
    assert inv.is_empty()


def test_inventory_capacity():
    """测试库存容量"""
    inv = Inventory(volume_capacity=1000, weight_capacity=1000)
    
    # 添加多个物品
    item1 = Item("apple")  # 250ml, 200g
    item2 = Item("apple")
    
    assert inv.add_item(item1)
    assert inv.add_item(item2)
    
    # 检查容量
    assert inv.get_total_volume() == 500
    assert inv.get_total_weight() == 400


def test_inventory_find():
    """测试库存查找"""
    inv = Inventory()
    
    apple1 = Item("apple")
    apple2 = Item("apple")
    rock = Item("rock")
    
    inv.add_item(apple1)
    inv.add_item(apple2)
    inv.add_item(rock)
    
    # 查找单个
    found = inv.find_item_by_type("rock")
    assert found is rock
    
    # 查找所有
    apples = inv.find_all_items_by_type("apple")
    assert len(apples) == 2
