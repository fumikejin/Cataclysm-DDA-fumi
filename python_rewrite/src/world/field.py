"""
游戏世界 - 场地效果

管理地图上的场地效果（火焰、烟雾、气体等）
"""

from dataclasses import dataclass
from typing import Dict, Optional

from ..utils.logger import logger


@dataclass
class FieldType:
    """场地类型"""

    id: str  # 场地ID
    name: str  # 名称
    symbol: str = "?"  # 显示符号
    color: str = "white"  # 颜色
    dangerous: bool = False  # 是否危险
    intensity_levels: int = 3  # 强度等级
    half_life: int = 0  # 半衰期（回合数），0表示永久


class FieldManager:
    """场地管理器"""

    def __init__(self):
        """初始化场地管理器"""
        self.field_types: Dict[str, FieldType] = {}
        self._load_default_fields()
        logger.info("场地管理器已初始化")

    def _load_default_fields(self):
        """加载默认场地类型"""
        # 火焰
        self.register_field(FieldType(
            id="fd_fire",
            name="火焰",
            symbol="^",
            color="red",
            dangerous=True,
            intensity_levels=3,
            half_life=2
        ))

        # 烟雾
        self.register_field(FieldType(
            id="fd_smoke",
            name="烟雾",
            symbol="8",
            color="gray",
            dangerous=False,
            intensity_levels=3,
            half_life=1
        ))

        # 毒气
        self.register_field(FieldType(
            id="fd_toxic_gas",
            name="毒气",
            symbol="8",
            color="green",
            dangerous=True,
            intensity_levels=3,
            half_life=3
        ))

        # 血液
        self.register_field(FieldType(
            id="fd_blood",
            name="血液",
            symbol="&",
            color="red",
            dangerous=False,
            intensity_levels=3,
            half_life=0  # 永久
        ))

        # 酸液
        self.register_field(FieldType(
            id="fd_acid",
            name="酸液",
            symbol="&",
            color="yellow",
            dangerous=True,
            intensity_levels=3,
            half_life=2
        ))

        # 水坑
        self.register_field(FieldType(
            id="fd_puddle",
            name="水坑",
            symbol="~",
            color="cyan",
            dangerous=False,
            intensity_levels=1,
            half_life=10
        ))

    def register_field(self, field_type: FieldType):
        """
        注册场地类型

        Args:
            field_type: 场地类型
        """
        self.field_types[field_type.id] = field_type

    def get_field_type(self, field_id: str) -> Optional[FieldType]:
        """
        获取场地类型

        Args:
            field_id: 场地ID

        Returns:
            场地类型，不存在则返回 None
        """
        return self.field_types.get(field_id)

    def load_from_data(self, field_data: dict):
        """
        从数据字典加载场地类型

        Args:
            field_data: 场地数据
        """
        field_type = FieldType(
            id=field_data.get("id", ""),
            name=field_data.get("name", ""),
            symbol=field_data.get("symbol", "?"),
            color=field_data.get("color", "white"),
            dangerous=field_data.get("dangerous", False),
            intensity_levels=field_data.get("intensity_levels", 3),
            half_life=field_data.get("half_life", 0)
        )

        self.register_field(field_type)

    def get_field_count(self) -> int:
        """获取已注册的场地类型数量"""
        return len(self.field_types)


# 全局场地管理器实例
field_manager = FieldManager()
