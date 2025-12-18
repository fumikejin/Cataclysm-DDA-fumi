"""
实体系统 - 怪物类型

定义怪物类型的数据结构
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from ..utils.logger import logger


@dataclass
class MonsterType:
    """怪物类型定义"""

    id: str  # 怪物ID
    name: str  # 显示名称
    description: str = ""  # 描述
    symbol: str = "m"  # ASCII 符号
    color: str = "red"  # 颜色
    size: str = "medium"  # 体型 (tiny, small, medium, large, huge)
    hp: int = 10  # 生命值
    speed: int = 100  # 速度
    melee_skill: int = 0  # 近战技能
    melee_dice: int = 1  # 近战骰子数
    melee_dice_sides: int = 4  # 近战骰子面数
    melee_cut: int = 0  # 近战切割伤害
    dodge: int = 0  # 闪避值
    armor_bash: int = 0  # 钝击护甲
    armor_cut: int = 0  # 切割护甲
    vision_day: int = 40  # 白天视野
    vision_night: int = 1  # 夜间视野
    aggression: int = 0  # 攻击性
    morale: int = 0  # 士气
    flags: List[str] = field(default_factory=list)  # 标志列表
    special_attacks: List[str] = field(default_factory=list)  # 特殊攻击


class MonsterTypeManager:
    """怪物类型管理器"""

    def __init__(self):
        """初始化怪物类型管理器"""
        self.monster_types: Dict[str, MonsterType] = {}
        self._load_default_monsters()
        logger.info("怪物类型管理器已初始化")

    def _load_default_monsters(self):
        """加载默认怪物类型"""
        # 僵尸
        self.register_monster(MonsterType(
            id="mon_zombie",
            name="僵尸",
            description="行动缓慢的活死人",
            symbol="Z",
            color="lightGreen",
            size="medium",
            hp=80,
            speed=70,
            melee_skill=4,
            melee_dice=1,
            melee_dice_sides=6,
            melee_cut=0,
            dodge=0,
            armor_bash=2,
            armor_cut=1,
            vision_day=40,
            vision_night=5,
            aggression=100,
            morale=100,
            flags=["SEES", "HEARS", "SMELLS", "STUMBLES", "WARM", "BASHES", "POISON"]
        ))

        # 巨型老鼠
        self.register_monster(MonsterType(
            id="mon_rat_giant",
            name="巨型老鼠",
            description="异常巨大的老鼠",
            symbol="r",
            color="darkGray",
            size="small",
            hp=20,
            speed=120,
            melee_skill=2,
            melee_dice=1,
            melee_dice_sides=4,
            melee_cut=2,
            dodge=4,
            armor_bash=0,
            armor_cut=0,
            vision_day=30,
            vision_night=30,
            aggression=50,
            morale=30,
            flags=["SEES", "HEARS", "SMELLS", "WARM", "ANIMAL"]
        ))

        # 野狗
        self.register_monster(MonsterType(
            id="mon_dog_wild",
            name="野狗",
            description="凶猛的野狗",
            symbol="d",
            color="brown",
            size="small",
            hp=30,
            speed=150,
            melee_skill=4,
            melee_dice=1,
            melee_dice_sides=6,
            melee_cut=4,
            dodge=4,
            armor_bash=0,
            armor_cut=0,
            vision_day=50,
            vision_night=20,
            aggression=80,
            morale=50,
            flags=["SEES", "HEARS", "SMELLS", "WARM", "ANIMAL", "KEENNOSE"]
        ))

    def register_monster(self, monster_type: MonsterType):
        """
        注册怪物类型

        Args:
            monster_type: 怪物类型
        """
        self.monster_types[monster_type.id] = monster_type

    def get_monster_type(self, monster_id: str) -> Optional[MonsterType]:
        """
        获取怪物类型

        Args:
            monster_id: 怪物ID

        Returns:
            怪物类型，不存在则返回 None
        """
        return self.monster_types.get(monster_id)

    def load_from_data(self, monster_data: dict):
        """
        从数据字典加载怪物类型

        Args:
            monster_data: 怪物数据
        """
        monster_type = MonsterType(
            id=monster_data.get("id", ""),
            name=monster_data.get("name", ""),
            description=monster_data.get("description", ""),
            symbol=monster_data.get("symbol", "m"),
            color=monster_data.get("color", "red"),
            size=monster_data.get("size", "medium"),
            hp=monster_data.get("hp", 10),
            speed=monster_data.get("speed", 100),
            melee_skill=monster_data.get("melee_skill", 0),
            melee_dice=monster_data.get("melee_dice", 1),
            melee_dice_sides=monster_data.get("melee_dice_sides", 4),
            melee_cut=monster_data.get("melee_cut", 0),
            dodge=monster_data.get("dodge", 0),
            armor_bash=monster_data.get("armor_bash", 0),
            armor_cut=monster_data.get("armor_cut", 0),
            vision_day=monster_data.get("vision_day", 40),
            vision_night=monster_data.get("vision_night", 1),
            aggression=monster_data.get("aggression", 0),
            morale=monster_data.get("morale", 0),
            flags=monster_data.get("flags", []),
            special_attacks=monster_data.get("special_attacks", [])
        )

        self.register_monster(monster_type)

    def get_monster_count(self) -> int:
        """获取已注册的怪物类型数量"""
        return len(self.monster_types)


# 全局怪物类型管理器实例
monster_type_manager = MonsterTypeManager()
