"""
数据管理 - 数据管理器

集中管理所有游戏数据
"""

from pathlib import Path
from typing import Any, Dict, Optional

from .json_loader import JSONLoader
from ..utils.logger import logger


class DataManager:
    """游戏数据管理器"""

    def __init__(self):
        """初始化数据管理器"""
        self.loader: Optional[JSONLoader] = None

        # 各类游戏数据
        self.items: Dict[str, Dict[str, Any]] = {}
        self.monsters: Dict[str, Dict[str, Any]] = {}
        self.terrain: Dict[str, Dict[str, Any]] = {}
        self.furniture: Dict[str, Dict[str, Any]] = {}
        self.professions: Dict[str, Dict[str, Any]] = {}
        self.scenarios: Dict[str, Dict[str, Any]] = {}
        self.skills: Dict[str, Dict[str, Any]] = {}
        self.mutations: Dict[str, Dict[str, Any]] = {}
        self.bionics: Dict[str, Dict[str, Any]] = {}
        self.recipes: Dict[str, Dict[str, Any]] = {}

        logger.info("数据管理器已初始化")

    def load_all_data(self, data_path: str):
        """
        加载所有游戏数据

        Args:
            data_path: 数据文件根目录
        """
        logger.info(f"开始加载游戏数据: {data_path}")
        self.loader = JSONLoader(data_path)

        data_root = Path(data_path)

        # 加载各类数据
        self._load_items(data_root)
        self._load_monsters(data_root)
        self._load_terrain(data_root)
        self._load_furniture(data_root)

        logger.info("游戏数据加载完成")
        self._print_statistics()

    def _load_items(self, data_root: Path):
        """加载物品数据"""
        items_path = data_root / "json" / "items"
        if not items_path.exists():
            logger.warning(f"物品数据目录不存在: {items_path}")
            return

        data_list = self.loader.load_recursive(items_path)
        for item_data in data_list:
            if "type" in item_data and item_data["type"] == "GENERIC":
                item_id = item_data.get("id")
                if item_id:
                    self.items[item_id] = item_data

        logger.info(f"已加载 {len(self.items)} 个物品")

    def _load_monsters(self, data_root: Path):
        """加载怪物数据"""
        monsters_path = data_root / "json" / "monsters"
        if not monsters_path.exists():
            logger.warning(f"怪物数据目录不存在: {monsters_path}")
            return

        data_list = self.loader.load_recursive(monsters_path)
        for monster_data in data_list:
            if "type" in monster_data and monster_data["type"] == "MONSTER":
                monster_id = monster_data.get("id")
                if monster_id:
                    self.monsters[monster_id] = monster_data

        logger.info(f"已加载 {len(self.monsters)} 个怪物")

    def _load_terrain(self, data_root: Path):
        """加载地形数据"""
        terrain_file = data_root / "json" / "terrain.json"
        if not terrain_file.exists():
            logger.warning(f"地形数据文件不存在: {terrain_file}")
            return

        data_list = self.loader.load_file(terrain_file)
        if data_list:
            for terrain_data in data_list:
                if "type" in terrain_data and terrain_data["type"] == "terrain":
                    terrain_id = terrain_data.get("id")
                    if terrain_id:
                        self.terrain[terrain_id] = terrain_data

        logger.info(f"已加载 {len(self.terrain)} 个地形")

    def _load_furniture(self, data_root: Path):
        """加载家具数据"""
        furniture_file = data_root / "json" / "furniture.json"
        if not furniture_file.exists():
            logger.warning(f"家具数据文件不存在: {furniture_file}")
            return

        data_list = self.loader.load_file(furniture_file)
        if data_list:
            for furniture_data in data_list:
                if "type" in furniture_data and furniture_data["type"] == "furniture":
                    furniture_id = furniture_data.get("id")
                    if furniture_id:
                        self.furniture[furniture_id] = furniture_data

        logger.info(f"已加载 {len(self.furniture)} 个家具")

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """获取物品数据"""
        return self.items.get(item_id)

    def get_monster(self, monster_id: str) -> Optional[Dict[str, Any]]:
        """获取怪物数据"""
        return self.monsters.get(monster_id)

    def get_terrain(self, terrain_id: str) -> Optional[Dict[str, Any]]:
        """获取地形数据"""
        return self.terrain.get(terrain_id)

    def get_furniture(self, furniture_id: str) -> Optional[Dict[str, Any]]:
        """获取家具数据"""
        return self.furniture.get(furniture_id)

    def _print_statistics(self):
        """打印数据统计信息"""
        logger.info("=" * 50)
        logger.info("数据统计:")
        logger.info(f"  物品: {len(self.items)}")
        logger.info(f"  怪物: {len(self.monsters)}")
        logger.info(f"  地形: {len(self.terrain)}")
        logger.info(f"  家具: {len(self.furniture)}")
        logger.info(f"  职业: {len(self.professions)}")
        logger.info(f"  场景: {len(self.scenarios)}")
        logger.info(f"  技能: {len(self.skills)}")
        logger.info(f"  突变: {len(self.mutations)}")
        logger.info(f"  生化插件: {len(self.bionics)}")
        logger.info(f"  配方: {len(self.recipes)}")
        logger.info("=" * 50)


# 全局数据管理器实例
data_manager = DataManager()
