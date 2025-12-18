"""
测试 - 效果系统
"""

import pytest
from src.systems.effect import (
    Effect,
    EffectType,
    EffectSystem,
)


def test_effect_creation():
    """测试创建效果"""
    effect = Effect(
        effect_type=EffectType.POISONED,
        duration=10,
        intensity=2
    )
    
    assert effect.effect_type == EffectType.POISONED
    assert effect.duration == 10
    assert effect.intensity == 2
    assert effect.name == "中毒"
    assert effect.is_negative


def test_effect_positive_negative():
    """测试正负面效果判断"""
    positive = Effect(EffectType.STRONG, 5)
    negative = Effect(EffectType.POISONED, 5)
    
    assert positive.is_positive
    assert not positive.is_negative
    assert negative.is_negative
    assert not negative.is_positive


def test_effect_decay():
    """测试效果衰减"""
    effect = Effect(EffectType.FAST, 10)
    
    effect.decay(3)
    assert effect.duration == 7
    
    effect.decay(10)
    assert effect.duration == 0


def test_effect_serialization():
    """测试效果序列化"""
    effect = Effect(
        effect_type=EffectType.REGENERATION,
        duration=20,
        intensity=3
    )
    
    data = effect.to_dict()
    restored = Effect.from_dict(data)
    
    assert restored.effect_type == effect.effect_type
    assert restored.duration == effect.duration
    assert restored.intensity == effect.intensity


def test_effect_system_creation():
    """测试创建效果系统"""
    system = EffectSystem()
    
    assert len(system.get_all_effects()) == 0


def test_effect_system_add_effect():
    """测试添加效果"""
    system = EffectSystem()
    
    effect = Effect(EffectType.STRONG, 10, 1)
    system.add_effect(effect)
    
    assert system.has_effect(EffectType.STRONG)
    assert len(system.get_all_effects()) == 1


def test_effect_system_remove_effect():
    """测试移除效果"""
    system = EffectSystem()
    
    system.add_effect(Effect(EffectType.FAST, 5))
    assert system.has_effect(EffectType.FAST)
    
    removed = system.remove_effect(EffectType.FAST)
    assert removed
    assert not system.has_effect(EffectType.FAST)


def test_effect_system_stack_effects():
    """测试叠加效果"""
    system = EffectSystem()
    
    # 添加第一个效果
    system.add_effect(Effect(EffectType.POISONED, 10, 1))
    effect1 = system.get_effect(EffectType.POISONED)
    
    # 添加相同类型效果
    system.add_effect(Effect(EffectType.POISONED, 15, 1))
    effect2 = system.get_effect(EffectType.POISONED)
    
    # 强度叠加，持续时间取较大值
    assert effect2.intensity == 2
    assert effect2.duration == 15


def test_effect_system_get_positive_negative():
    """测试获取正负面效果"""
    system = EffectSystem()
    
    system.add_effect(Effect(EffectType.STRONG, 10))
    system.add_effect(Effect(EffectType.FAST, 10))
    system.add_effect(Effect(EffectType.POISONED, 10))
    system.add_effect(Effect(EffectType.SLOWED, 10))
    
    positive = system.get_positive_effects()
    negative = system.get_negative_effects()
    
    assert len(positive) == 2
    assert len(negative) == 2


def test_effect_system_update():
    """测试更新效果"""
    system = EffectSystem()
    
    system.add_effect(Effect(EffectType.FAST, 3))
    system.add_effect(Effect(EffectType.POISONED, 5))
    
    # 更新3回合
    system.update(3)
    
    # FAST效果应该过期
    assert not system.has_effect(EffectType.FAST)
    # POISONED效果还在
    assert system.has_effect(EffectType.POISONED)
    
    # 再更新3回合
    system.update(3)
    
    # 所有效果都应该过期
    assert len(system.get_all_effects()) == 0


def test_effect_system_modifiers():
    """测试效果修正值"""
    system = EffectSystem()
    
    # 初始无修正
    assert system.get_strength_modifier() == 1.0
    assert system.get_speed_modifier() == 1.0
    assert system.get_perception_modifier() == 1.0
    
    # 添加正面效果
    system.add_effect(Effect(EffectType.STRONG, 10, 2))
    assert system.get_strength_modifier() > 1.0
    
    # 添加负面效果
    system.add_effect(Effect(EffectType.SLOWED, 10, 1))
    assert system.get_speed_modifier() < 1.0


def test_effect_system_can_actions():
    """测试能力检查"""
    system = EffectSystem()
    
    # 初始可以行动
    assert system.can_act()
    assert system.can_see()
    assert system.can_hear()
    
    # 眩晕不能行动
    system.add_effect(Effect(EffectType.STUNNED, 3))
    assert not system.can_act()
    
    # 失明不能看
    system.add_effect(Effect(EffectType.BLINDED, 5))
    assert not system.can_see()
    
    # 耳聋不能听
    system.add_effect(Effect(EffectType.DEAF, 5))
    assert not system.can_hear()


def test_effect_system_serialization():
    """测试效果系统序列化"""
    system = EffectSystem()
    
    system.add_effect(Effect(EffectType.STRONG, 10, 2))
    system.add_effect(Effect(EffectType.POISONED, 15, 1))
    
    # 序列化和反序列化
    data = system.to_dict()
    restored = EffectSystem.from_dict(data)
    
    assert len(restored.get_all_effects()) == len(system.get_all_effects())
    assert restored.has_effect(EffectType.STRONG)
    assert restored.has_effect(EffectType.POISONED)
