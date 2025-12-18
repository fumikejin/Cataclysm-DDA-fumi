"""
数据管理 - 数据验证

验证从 JSON 加载的数据是否符合预期格式
"""

from typing import Any, Dict, List, Optional, Set

from ..utils.logger import logger


class ValidationError(Exception):
    """数据验证错误"""

    pass


class DataValidator:
    """数据验证器"""

    def __init__(self):
        """初始化验证器"""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_item(self, item_data: Dict[str, Any]) -> bool:
        """
        验证物品数据

        Args:
            item_data: 物品数据字典

        Returns:
            是否有效
        """
        self.errors.clear()
        self.warnings.clear()

        # 检查必需字段
        required_fields = ["id", "type", "name"]
        for field in required_fields:
            if field not in item_data:
                self.errors.append(f"缺少必需字段: {field}")

        # 检查类型
        if "type" in item_data:
            valid_types = ["GENERIC", "TOOL", "ARMOR", "WEAPON", "AMMO", "COMESTIBLE"]
            if item_data["type"] not in valid_types:
                self.warnings.append(f"未知物品类型: {item_data['type']}")

        # 检查数值字段
        if "weight" in item_data:
            if not isinstance(item_data["weight"], (int, float)) or item_data["weight"] < 0:
                self.errors.append("weight 必须是非负数")

        if "volume" in item_data:
            if not isinstance(item_data["volume"], (int, float, str)) or (
                isinstance(item_data["volume"], (int, float)) and item_data["volume"] < 0
            ):
                self.errors.append("volume 必须是非负数或字符串")

        return len(self.errors) == 0

    def validate_monster(self, monster_data: Dict[str, Any]) -> bool:
        """
        验证怪物数据

        Args:
            monster_data: 怪物数据字典

        Returns:
            是否有效
        """
        self.errors.clear()
        self.warnings.clear()

        # 检查必需字段
        required_fields = ["id", "type", "name"]
        for field in required_fields:
            if field not in monster_data:
                self.errors.append(f"缺少必需字段: {field}")

        # 检查类型
        if "type" in monster_data and monster_data["type"] != "MONSTER":
            self.errors.append(f"无效的怪物类型: {monster_data['type']}")

        # 检查生命值
        if "hp" in monster_data:
            if not isinstance(monster_data["hp"], (int, float)) or monster_data["hp"] <= 0:
                self.errors.append("hp 必须是正数")

        return len(self.errors) == 0

    def validate_terrain(self, terrain_data: Dict[str, Any]) -> bool:
        """
        验证地形数据

        Args:
            terrain_data: 地形数据字典

        Returns:
            是否有效
        """
        self.errors.clear()
        self.warnings.clear()

        # 检查必需字段
        required_fields = ["id", "type", "name"]
        for field in required_fields:
            if field not in terrain_data:
                self.errors.append(f"缺少必需字段: {field}")

        # 检查类型
        if "type" in terrain_data and terrain_data["type"] != "terrain":
            self.errors.append(f"无效的地形类型: {terrain_data['type']}")

        # 检查移动成本
        if "move_cost" in terrain_data:
            move_cost = terrain_data["move_cost"]
            if not isinstance(move_cost, int) or move_cost < 0:
                self.errors.append("move_cost 必须是非负整数")

        return len(self.errors) == 0

    def validate_furniture(self, furniture_data: Dict[str, Any]) -> bool:
        """
        验证家具数据

        Args:
            furniture_data: 家具数据字典

        Returns:
            是否有效
        """
        self.errors.clear()
        self.warnings.clear()

        # 检查必需字段
        required_fields = ["id", "type", "name"]
        for field in required_fields:
            if field not in furniture_data:
                self.errors.append(f"缺少必需字段: {field}")

        # 检查类型
        if "type" in furniture_data and furniture_data["type"] != "furniture":
            self.errors.append(f"无效的家具类型: {furniture_data['type']}")

        return len(self.errors) == 0

    def validate_recipe(self, recipe_data: Dict[str, Any]) -> bool:
        """
        验证配方数据

        Args:
            recipe_data: 配方数据字典

        Returns:
            是否有效
        """
        self.errors.clear()
        self.warnings.clear()

        # 检查必需字段
        required_fields = ["type", "result"]
        for field in required_fields:
            if field not in recipe_data:
                self.errors.append(f"缺少必需字段: {field}")

        # 检查类型
        if "type" in recipe_data and recipe_data["type"] != "recipe":
            self.errors.append(f"无效的配方类型: {recipe_data['type']}")

        return len(self.errors) == 0

    def check_references(
        self, data_type: str, data: Dict[str, Any], all_ids: Set[str]
    ) -> bool:
        """
        检查数据引用的完整性

        Args:
            data_type: 数据类型
            data: 数据字典
            all_ids: 所有有效的 ID 集合

        Returns:
            是否有效
        """
        self.errors.clear()
        self.warnings.clear()

        # 根据数据类型检查特定引用
        if data_type == "recipe":
            # 检查配方结果物品是否存在
            if "result" in data and data["result"] not in all_ids:
                self.warnings.append(f"配方结果物品不存在: {data['result']}")

            # 检查配方组件
            if "components" in data:
                for component_group in data["components"]:
                    for component in component_group:
                        if isinstance(component, list) and len(component) >= 1:
                            item_id = component[0]
                            if item_id not in all_ids:
                                self.warnings.append(f"配方组件不存在: {item_id}")

        return len(self.errors) == 0

    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors.copy()

    def get_warnings(self) -> List[str]:
        """获取警告列表"""
        return self.warnings.copy()

    def log_results(self, data_id: str):
        """
        记录验证结果到日志

        Args:
            data_id: 数据 ID
        """
        if self.errors:
            for error in self.errors:
                logger.error(f"[{data_id}] {error}")

        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"[{data_id}] {warning}")


# 全局验证器实例
validator = DataValidator()
