"""
系统模块 - 效果系统

管理角色身上的各种效果（buff/debuff）
"""

from enum import Enum
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import time

from ..utils.logger import logger


class EffectType(Enum):
    """效果类型"""
    # 正面效果
    STRONG = "strong"  # 强壮
    FAST = "fast"  # 快速
    REGENERATION = "regeneration"  # 再生
    NIGHT_VISION = "night_vision"  # 夜视
    POISON_RESIST = "poison_resist"  # 抗毒
    
    # 负面效果
    POISONED = "poisoned"  # 中毒
    BLEEDING = "bleeding"  # 流血
    INFECTED = "infected"  # 感染
    STUNNED = "stunned"  # 眩晕
    BLINDED = "blinded"  # 失明
    DEAF = "deaf"  # 耳聋
    SLOWED = "slowed"  # 减速
    WEAKENED = "weakened"  # 虚弱
    PAIN = "pain"  # 疼痛
    
    # 状态效果
    WET = "wet"  # 湿透
    COLD = "cold"  # 寒冷
    HOT = "hot"  # 炎热
    HUNGRY = "hungry"  # 饥饿
    THIRSTY = "thirsty"  # 口渴
    TIRED = "tired"  # 疲劳


@dataclass
class Effect:
    """效果"""
    
    effect_type: EffectType  # 效果类型
    duration: int  # 持续时间（回合）
    intensity: int = 1  # 强度
    start_time: int = 0  # 开始时间
    
    def __post_init__(self):
        """初始化后处理"""
        if self.start_time == 0:
            self.start_time = int(time.time())
    
    @property
    def name(self) -> str:
        """获取效果名称"""
        names = {
            EffectType.STRONG: "强壮",
            EffectType.FAST: "快速",
            EffectType.REGENERATION: "再生",
            EffectType.NIGHT_VISION: "夜视",
            EffectType.POISON_RESIST: "抗毒",
            EffectType.POISONED: "中毒",
            EffectType.BLEEDING: "流血",
            EffectType.INFECTED: "感染",
            EffectType.STUNNED: "眩晕",
            EffectType.BLINDED: "失明",
            EffectType.DEAF: "耳聋",
            EffectType.SLOWED: "减速",
            EffectType.WEAKENED: "虚弱",
            EffectType.PAIN: "疼痛",
            EffectType.WET: "湿透",
            EffectType.COLD: "寒冷",
            EffectType.HOT: "炎热",
            EffectType.HUNGRY: "饥饿",
            EffectType.THIRSTY: "口渴",
            EffectType.TIRED: "疲劳",
        }
        return names.get(self.effect_type, "未知效果")
    
    @property
    def is_positive(self) -> bool:
        """是否是正面效果"""
        positive_effects = {
            EffectType.STRONG,
            EffectType.FAST,
            EffectType.REGENERATION,
            EffectType.NIGHT_VISION,
            EffectType.POISON_RESIST,
        }
        return self.effect_type in positive_effects
    
    @property
    def is_negative(self) -> bool:
        """是否是负面效果"""
        return not self.is_positive
    
    @property
    def remaining_duration(self) -> int:
        """剩余持续时间"""
        elapsed = int(time.time()) - self.start_time
        turns_elapsed = elapsed // 6  # 假设每回合6秒
        return max(0, self.duration - turns_elapsed)
    
    @property
    def is_expired(self) -> bool:
        """是否已过期"""
        return self.remaining_duration <= 0
    
    def decay(self, turns: int = 1):
        """
        衰减效果
        
        Args:
            turns: 经过的回合数
        """
        self.duration = max(0, self.duration - turns)
    
    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "effect_type": self.effect_type.value,
            "duration": self.duration,
            "intensity": self.intensity,
            "start_time": self.start_time,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Effect":
        """从字典反序列化"""
        return cls(
            effect_type=EffectType(data["effect_type"]),
            duration=data["duration"],
            intensity=data.get("intensity", 1),
            start_time=data.get("start_time", int(time.time())),
        )


class EffectSystem:
    """效果系统"""
    
    def __init__(self):
        """初始化效果系统"""
        self.effects: Dict[EffectType, Effect] = {}
        self.on_effect_added: Optional[Callable] = None
        self.on_effect_removed: Optional[Callable] = None
    
    def add_effect(self, effect: Effect):
        """
        添加效果
        
        Args:
            effect: 效果
        """
        # 如果已存在相同效果，叠加或替换
        existing = self.effects.get(effect.effect_type)
        if existing:
            # 取较长的持续时间，叠加强度
            effect.duration = max(effect.duration, existing.duration)
            effect.intensity += existing.intensity
        
        self.effects[effect.effect_type] = effect
        logger.debug(f"添加效果: {effect.name} (强度{effect.intensity}, 持续{effect.duration}回合)")
        
        if self.on_effect_added:
            self.on_effect_added(effect)
    
    def remove_effect(self, effect_type: EffectType) -> bool:
        """
        移除效果
        
        Args:
            effect_type: 效果类型
            
        Returns:
            是否成功移除
        """
        effect = self.effects.pop(effect_type, None)
        if effect:
            logger.debug(f"移除效果: {effect.name}")
            if self.on_effect_removed:
                self.on_effect_removed(effect)
            return True
        return False
    
    def has_effect(self, effect_type: EffectType) -> bool:
        """
        检查是否有指定效果
        
        Args:
            effect_type: 效果类型
            
        Returns:
            是否有该效果
        """
        return effect_type in self.effects
    
    def get_effect(self, effect_type: EffectType) -> Optional[Effect]:
        """
        获取效果
        
        Args:
            effect_type: 效果类型
            
        Returns:
            效果对象，如果不存在则返回None
        """
        return self.effects.get(effect_type)
    
    def get_all_effects(self) -> List[Effect]:
        """获取所有效果"""
        return list(self.effects.values())
    
    def get_positive_effects(self) -> List[Effect]:
        """获取所有正面效果"""
        return [e for e in self.effects.values() if e.is_positive]
    
    def get_negative_effects(self) -> List[Effect]:
        """获取所有负面效果"""
        return [e for e in self.effects.values() if e.is_negative]
    
    def clear_all_effects(self):
        """清除所有效果"""
        self.effects.clear()
        logger.debug("清除所有效果")
    
    def update(self, turns: int = 1):
        """
        更新效果（每回合调用）
        
        Args:
            turns: 经过的回合数
        """
        expired = []
        
        for effect_type, effect in self.effects.items():
            effect.decay(turns)
            
            # 检查效果是否过期
            if effect.is_expired:
                expired.append(effect_type)
            else:
                # 应用效果（可以在这里添加效果逻辑）
                self._apply_effect(effect)
        
        # 移除过期效果
        for effect_type in expired:
            self.remove_effect(effect_type)
    
    def _apply_effect(self, effect: Effect):
        """
        应用效果（每回合）
        
        Args:
            effect: 效果
        """
        # 这里可以实现具体的效果逻辑
        # 例如：中毒每回合扣血、再生每回合加血等
        pass
    
    def get_strength_modifier(self) -> float:
        """获取力量修正"""
        modifier = 1.0
        
        if self.has_effect(EffectType.STRONG):
            effect = self.get_effect(EffectType.STRONG)
            modifier *= (1.0 + 0.1 * effect.intensity)
        
        if self.has_effect(EffectType.WEAKENED):
            effect = self.get_effect(EffectType.WEAKENED)
            modifier *= (1.0 - 0.1 * effect.intensity)
        
        return modifier
    
    def get_speed_modifier(self) -> float:
        """获取速度修正"""
        modifier = 1.0
        
        if self.has_effect(EffectType.FAST):
            effect = self.get_effect(EffectType.FAST)
            modifier *= (1.0 + 0.1 * effect.intensity)
        
        if self.has_effect(EffectType.SLOWED):
            effect = self.get_effect(EffectType.SLOWED)
            modifier *= (1.0 - 0.15 * effect.intensity)
        
        if self.has_effect(EffectType.PAIN):
            effect = self.get_effect(EffectType.PAIN)
            modifier *= (1.0 - 0.05 * effect.intensity)
        
        return modifier
    
    def get_perception_modifier(self) -> float:
        """获取感知修正"""
        modifier = 1.0
        
        if self.has_effect(EffectType.BLINDED):
            modifier *= 0.1
        
        if self.has_effect(EffectType.DEAF):
            modifier *= 0.7
        
        if self.has_effect(EffectType.PAIN):
            effect = self.get_effect(EffectType.PAIN)
            modifier *= (1.0 - 0.05 * effect.intensity)
        
        return modifier
    
    def can_act(self) -> bool:
        """是否可以行动"""
        return not self.has_effect(EffectType.STUNNED)
    
    def can_see(self) -> bool:
        """是否可以看见"""
        return not self.has_effect(EffectType.BLINDED)
    
    def can_hear(self) -> bool:
        """是否可以听见"""
        return not self.has_effect(EffectType.DEAF)
    
    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "effects": [
                effect.to_dict()
                for effect in self.effects.values()
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EffectSystem":
        """从字典反序列化"""
        effect_system = cls()
        
        for effect_data in data.get("effects", []):
            effect = Effect.from_dict(effect_data)
            effect_system.effects[effect.effect_type] = effect
        
        return effect_system
