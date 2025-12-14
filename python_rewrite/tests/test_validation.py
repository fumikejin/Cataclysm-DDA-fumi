"""
测试数据管理 - 数据验证
"""

import pytest
from src.data.validation import DataValidator


def test_validate_item():
    """测试物品数据验证"""
    validator = DataValidator()
    
    # 有效的物品数据
    valid_item = {
        "id": "test_item",
        "type": "GENERIC",
        "name": "测试物品",
        "weight": 100,
        "volume": 250
    }
    assert validator.validate_item(valid_item) is True
    assert len(validator.get_errors()) == 0
    
    # 缺少必需字段
    invalid_item = {
        "type": "GENERIC"
    }
    assert validator.validate_item(invalid_item) is False
    assert len(validator.get_errors()) > 0


def test_validate_monster():
    """测试怪物数据验证"""
    validator = DataValidator()
    
    # 有效的怪物数据
    valid_monster = {
        "id": "test_monster",
        "type": "MONSTER",
        "name": "测试怪物",
        "hp": 100
    }
    assert validator.validate_monster(valid_monster) is True
    
    # 无效的生命值
    invalid_monster = {
        "id": "test_monster",
        "type": "MONSTER",
        "name": "测试怪物",
        "hp": -10
    }
    assert validator.validate_monster(invalid_monster) is False


def test_validate_terrain():
    """测试地形数据验证"""
    validator = DataValidator()
    
    # 有效的地形数据
    valid_terrain = {
        "id": "test_terrain",
        "type": "terrain",
        "name": "测试地形",
        "move_cost": 100
    }
    assert validator.validate_terrain(valid_terrain) is True
