"""
系统模块 - 身体部位系统

管理角色的身体部位、伤害、效果等
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..utils.logger import logger


class BodyPartType(Enum):
    """身体部位类型"""
    HEAD = "head"  # 头部
    TORSO = "torso"  # 躯干
    ARM_L = "arm_l"  # 左臂
    ARM_R = "arm_r"  # 右臂
    HAND_L = "hand_l"  # 左手
    HAND_R = "hand_r"  # 右手
    LEG_L = "leg_l"  # 左腿
    LEG_R = "leg_r"  # 右腿
    FOOT_L = "foot_l"  # 左脚
    FOOT_R = "foot_r"  # 右脚
    MOUTH = "mouth"  # 嘴巴
    EYES = "eyes"  # 眼睛


class BodyPartStatus(Enum):
    """身体部位状态"""
    HEALTHY = "healthy"  # 健康
    BRUISED = "bruised"  # 挫伤
    BLEEDING = "bleeding"  # 流血
    BROKEN = "broken"  # 骨折
    DISABLED = "disabled"  # 残废


@dataclass
class BodyPart:
    """身体部位"""
    
    part_type: BodyPartType  # 部位类型
    hp: int  # 当前生命值
    max_hp: int  # 最大生命值
    status: BodyPartStatus = BodyPartStatus.HEALTHY  # 状态
    encumbrance: int = 0  # 负重
    wetness: int = 0  # 湿度 (0-100)
    temperature: int = 37  # 温度 (摄氏度)
    
    def __post_init__(self):
        """初始化后处理"""
        if self.hp > self.max_hp:
            self.hp = self.max_hp
    
    @property
    def name(self) -> str:
        """获取部位名称"""
        names = {
            BodyPartType.HEAD: "头部",
            BodyPartType.TORSO: "躯干",
            BodyPartType.ARM_L: "左臂",
            BodyPartType.ARM_R: "右臂",
            BodyPartType.HAND_L: "左手",
            BodyPartType.HAND_R: "右手",
            BodyPartType.LEG_L: "左腿",
            BodyPartType.LEG_R: "右腿",
            BodyPartType.FOOT_L: "左脚",
            BodyPartType.FOOT_R: "右脚",
            BodyPartType.MOUTH: "嘴巴",
            BodyPartType.EYES: "眼睛",
        }
        return names.get(self.part_type, "未知部位")
    
    @property
    def is_limb(self) -> bool:
        """是否是肢体"""
        return self.part_type in [
            BodyPartType.ARM_L, BodyPartType.ARM_R,
            BodyPartType.LEG_L, BodyPartType.LEG_R,
        ]
    
    @property
    def is_vital(self) -> bool:
        """是否是重要部位"""
        return self.part_type in [BodyPartType.HEAD, BodyPartType.TORSO]
    
    @property
    def hp_ratio(self) -> float:
        """生命值比例"""
        if self.max_hp == 0:
            return 0.0
        return self.hp / self.max_hp
    
    def take_damage(self, damage: int) -> int:
        """
        承受伤害
        
        Args:
            damage: 伤害值
            
        Returns:
            实际造成的伤害
        """
        if damage <= 0:
            return 0
        
        actual_damage = min(damage, self.hp)
        self.hp -= actual_damage
        
        # 更新状态
        if self.hp <= 0:
            self.status = BodyPartStatus.DISABLED
        elif self.hp_ratio < 0.3:
            self.status = BodyPartStatus.BROKEN
        elif self.hp_ratio < 0.6:
            self.status = BodyPartStatus.BLEEDING
        elif self.hp_ratio < 0.9:
            self.status = BodyPartStatus.BRUISED
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """
        治疗
        
        Args:
            amount: 治疗量
            
        Returns:
            实际治疗的量
        """
        if amount <= 0 or self.hp >= self.max_hp:
            return 0
        
        actual_heal = min(amount, self.max_hp - self.hp)
        self.hp += actual_heal
        
        # 更新状态
        if self.hp >= self.max_hp:
            self.status = BodyPartStatus.HEALTHY
        elif self.hp_ratio >= 0.9:
            self.status = BodyPartStatus.BRUISED
        elif self.hp_ratio >= 0.6:
            self.status = BodyPartStatus.BLEEDING
        elif self.hp_ratio >= 0.3:
            self.status = BodyPartStatus.BROKEN
        
        return actual_heal
    
    def add_encumbrance(self, amount: int):
        """增加负重"""
        self.encumbrance = max(0, self.encumbrance + amount)
    
    def remove_encumbrance(self, amount: int):
        """减少负重"""
        self.encumbrance = max(0, self.encumbrance - amount)
    
    def set_wet(self, wetness: int):
        """设置湿度"""
        self.wetness = max(0, min(100, wetness))
    
    def set_temperature(self, temp: int):
        """设置温度"""
        self.temperature = max(-50, min(50, temp))
    
    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "part_type": self.part_type.value,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "status": self.status.value,
            "encumbrance": self.encumbrance,
            "wetness": self.wetness,
            "temperature": self.temperature,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BodyPart":
        """从字典反序列化"""
        return cls(
            part_type=BodyPartType(data["part_type"]),
            hp=data["hp"],
            max_hp=data["max_hp"],
            status=BodyPartStatus(data["status"]),
            encumbrance=data.get("encumbrance", 0),
            wetness=data.get("wetness", 0),
            temperature=data.get("temperature", 37),
        )


class BodySystem:
    """身体系统"""
    
    def __init__(self):
        """初始化身体系统"""
        self.parts: Dict[BodyPartType, BodyPart] = {}
        self._init_default_parts()
    
    def _init_default_parts(self):
        """初始化默认身体部位"""
        # 头部 - 最重要
        self.parts[BodyPartType.HEAD] = BodyPart(
            part_type=BodyPartType.HEAD,
            hp=60,
            max_hp=60
        )
        
        # 躯干 - 重要
        self.parts[BodyPartType.TORSO] = BodyPart(
            part_type=BodyPartType.TORSO,
            hp=80,
            max_hp=80
        )
        
        # 四肢
        for part_type in [BodyPartType.ARM_L, BodyPartType.ARM_R,
                         BodyPartType.LEG_L, BodyPartType.LEG_R]:
            self.parts[part_type] = BodyPart(
                part_type=part_type,
                hp=60,
                max_hp=60
            )
        
        # 手和脚
        for part_type in [BodyPartType.HAND_L, BodyPartType.HAND_R,
                         BodyPartType.FOOT_L, BodyPartType.FOOT_R]:
            self.parts[part_type] = BodyPart(
                part_type=part_type,
                hp=50,
                max_hp=50
            )
        
        # 特殊部位
        self.parts[BodyPartType.MOUTH] = BodyPart(
            part_type=BodyPartType.MOUTH,
            hp=30,
            max_hp=30
        )
        
        self.parts[BodyPartType.EYES] = BodyPart(
            part_type=BodyPartType.EYES,
            hp=30,
            max_hp=30
        )
    
    def get_part(self, part_type: BodyPartType) -> Optional[BodyPart]:
        """获取身体部位"""
        return self.parts.get(part_type)
    
    def get_all_parts(self) -> List[BodyPart]:
        """获取所有身体部位"""
        return list(self.parts.values())
    
    def get_damaged_parts(self) -> List[BodyPart]:
        """获取受伤的部位"""
        return [p for p in self.parts.values() if p.hp < p.max_hp]
    
    def get_disabled_parts(self) -> List[BodyPart]:
        """获取残废的部位"""
        return [p for p in self.parts.values() 
                if p.status == BodyPartStatus.DISABLED]
    
    def take_damage(self, part_type: BodyPartType, damage: int) -> int:
        """
        对指定部位造成伤害
        
        Args:
            part_type: 部位类型
            damage: 伤害值
            
        Returns:
            实际造成的伤害
        """
        part = self.get_part(part_type)
        if part is None:
            logger.warning(f"未找到身体部位: {part_type}")
            return 0
        
        actual_damage = part.take_damage(damage)
        logger.debug(f"{part.name}受到{actual_damage}点伤害")
        
        return actual_damage
    
    def heal_part(self, part_type: BodyPartType, amount: int) -> int:
        """
        治疗指定部位
        
        Args:
            part_type: 部位类型
            amount: 治疗量
            
        Returns:
            实际治疗的量
        """
        part = self.get_part(part_type)
        if part is None:
            logger.warning(f"未找到身体部位: {part_type}")
            return 0
        
        actual_heal = part.heal(amount)
        logger.debug(f"{part.name}治疗了{actual_heal}点生命")
        
        return actual_heal
    
    def heal_all(self, amount: int):
        """治疗所有部位"""
        for part in self.parts.values():
            part.heal(amount)
    
    @property
    def total_hp(self) -> int:
        """总生命值"""
        return sum(p.hp for p in self.parts.values())
    
    @property
    def total_max_hp(self) -> int:
        """总最大生命值"""
        return sum(p.max_hp for p in self.parts.values())
    
    @property
    def hp_ratio(self) -> float:
        """总生命值比例"""
        if self.total_max_hp == 0:
            return 0.0
        return self.total_hp / self.total_max_hp
    
    @property
    def is_alive(self) -> bool:
        """是否存活"""
        # 头部或躯干HP归零则死亡
        head = self.get_part(BodyPartType.HEAD)
        torso = self.get_part(BodyPartType.TORSO)
        
        if head and head.hp <= 0:
            return False
        if torso and torso.hp <= 0:
            return False
        
        return True
    
    @property
    def total_encumbrance(self) -> int:
        """总负重"""
        return sum(p.encumbrance for p in self.parts.values())
    
    def get_movement_penalty(self) -> float:
        """获取移动惩罚"""
        # 腿部受伤会影响移动
        leg_l = self.get_part(BodyPartType.LEG_L)
        leg_r = self.get_part(BodyPartType.LEG_R)
        
        penalty = 1.0
        if leg_l and leg_l.status == BodyPartStatus.DISABLED:
            penalty *= 0.5
        elif leg_l and leg_l.status == BodyPartStatus.BROKEN:
            penalty *= 0.7
        
        if leg_r and leg_r.status == BodyPartStatus.DISABLED:
            penalty *= 0.5
        elif leg_r and leg_r.status == BodyPartStatus.BROKEN:
            penalty *= 0.7
        
        return penalty
    
    def get_attack_penalty(self) -> float:
        """获取攻击惩罚"""
        # 手臂受伤会影响攻击
        arm_l = self.get_part(BodyPartType.ARM_L)
        arm_r = self.get_part(BodyPartType.ARM_R)
        
        penalty = 1.0
        if arm_l and arm_l.status == BodyPartStatus.DISABLED:
            penalty *= 0.7
        elif arm_l and arm_l.status == BodyPartStatus.BROKEN:
            penalty *= 0.85
        
        if arm_r and arm_r.status == BodyPartStatus.DISABLED:
            penalty *= 0.7
        elif arm_r and arm_r.status == BodyPartStatus.BROKEN:
            penalty *= 0.85
        
        return penalty
    
    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "parts": {
                part_type.value: part.to_dict()
                for part_type, part in self.parts.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BodySystem":
        """从字典反序列化"""
        body_system = cls()
        body_system.parts = {}
        
        for part_type_str, part_data in data.get("parts", {}).items():
            part_type = BodyPartType(part_type_str)
            body_system.parts[part_type] = BodyPart.from_dict(part_data)
        
        return body_system
