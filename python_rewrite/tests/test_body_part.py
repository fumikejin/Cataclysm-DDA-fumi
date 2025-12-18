"""
测试 - 身体部位系统
"""

import pytest
from src.systems.body_part import (
    BodyPart,
    BodyPartType,
    BodyPartStatus,
    BodySystem,
)


def test_body_part_creation():
    """测试创建身体部位"""
    part = BodyPart(
        part_type=BodyPartType.HEAD,
        hp=60,
        max_hp=60
    )
    
    assert part.part_type == BodyPartType.HEAD
    assert part.hp == 60
    assert part.max_hp == 60
    assert part.status == BodyPartStatus.HEALTHY
    assert part.name == "头部"


def test_body_part_take_damage():
    """测试身体部位受伤"""
    part = BodyPart(
        part_type=BodyPartType.ARM_L,
        hp=60,
        max_hp=60
    )
    
    # 轻伤
    damage = part.take_damage(10)
    assert damage == 10
    assert part.hp == 50
    assert part.status == BodyPartStatus.BRUISED
    
    # 中伤
    damage = part.take_damage(30)
    assert damage == 30
    assert part.hp == 20
    assert part.status == BodyPartStatus.BLEEDING
    
    # 重伤
    damage = part.take_damage(15)
    assert damage == 15
    assert part.hp == 5
    assert part.status == BodyPartStatus.BROKEN


def test_body_part_heal():
    """测试身体部位治疗"""
    part = BodyPart(
        part_type=BodyPartType.TORSO,
        hp=30,
        max_hp=80
    )
    
    healed = part.heal(20)
    assert healed == 20
    assert part.hp == 50
    
    # 不能超过最大值
    healed = part.heal(100)
    assert healed == 30
    assert part.hp == 80


def test_body_part_properties():
    """测试身体部位属性"""
    head = BodyPart(BodyPartType.HEAD, 60, 60)
    arm = BodyPart(BodyPartType.ARM_L, 60, 60)
    
    assert head.is_vital
    assert not head.is_limb
    assert not arm.is_vital
    assert arm.is_limb


def test_body_part_serialization():
    """测试身体部位序列化"""
    part = BodyPart(
        part_type=BodyPartType.LEG_R,
        hp=40,
        max_hp=60,
        status=BodyPartStatus.BRUISED,
        encumbrance=5,
        wetness=30,
        temperature=35
    )
    
    data = part.to_dict()
    restored = BodyPart.from_dict(data)
    
    assert restored.part_type == part.part_type
    assert restored.hp == part.hp
    assert restored.max_hp == part.max_hp
    assert restored.status == part.status
    assert restored.encumbrance == part.encumbrance
    assert restored.wetness == part.wetness
    assert restored.temperature == part.temperature


def test_body_system_creation():
    """测试创建身体系统"""
    body = BodySystem()
    
    # 检查所有部位都已初始化
    assert len(body.parts) == 12
    assert body.get_part(BodyPartType.HEAD) is not None
    assert body.get_part(BodyPartType.TORSO) is not None


def test_body_system_damage():
    """测试身体系统受伤"""
    body = BodySystem()
    
    initial_hp = body.total_hp
    damage = body.take_damage(BodyPartType.ARM_L, 20)
    
    assert damage == 20
    assert body.total_hp == initial_hp - 20
    assert len(body.get_damaged_parts()) == 1


def test_body_system_heal():
    """测试身体系统治疗"""
    body = BodySystem()
    
    # 先造成伤害
    body.take_damage(BodyPartType.LEG_R, 30)
    damaged = len(body.get_damaged_parts())
    
    # 治疗
    healed = body.heal_part(BodyPartType.LEG_R, 30)
    assert healed == 30
    assert len(body.get_damaged_parts()) == damaged - 1


def test_body_system_is_alive():
    """测试身体系统存活状态"""
    body = BodySystem()
    
    assert body.is_alive
    
    # 头部致命伤
    head = body.get_part(BodyPartType.HEAD)
    body.take_damage(BodyPartType.HEAD, head.max_hp)
    assert not body.is_alive


def test_body_system_penalties():
    """测试身体系统惩罚"""
    body = BodySystem()
    
    # 初始无惩罚
    assert body.get_movement_penalty() == 1.0
    assert body.get_attack_penalty() == 1.0
    
    # 腿部骨折
    leg = body.get_part(BodyPartType.LEG_L)
    body.take_damage(BodyPartType.LEG_L, int(leg.max_hp * 0.8))
    assert body.get_movement_penalty() < 1.0
    
    # 手臂骨折
    arm = body.get_part(BodyPartType.ARM_R)
    body.take_damage(BodyPartType.ARM_R, int(arm.max_hp * 0.8))
    assert body.get_attack_penalty() < 1.0


def test_body_system_serialization():
    """测试身体系统序列化"""
    body = BodySystem()
    
    # 造成一些伤害
    body.take_damage(BodyPartType.HEAD, 10)
    body.take_damage(BodyPartType.ARM_L, 20)
    
    # 序列化和反序列化
    data = body.to_dict()
    restored = BodySystem.from_dict(data)
    
    assert restored.total_hp == body.total_hp
    assert len(restored.get_damaged_parts()) == len(body.get_damaged_parts())
