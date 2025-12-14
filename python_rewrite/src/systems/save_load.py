"""
游戏系统 - 保存/加载

游戏状态的序列化和反序列化
"""

import os
import json
import gzip
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from ..utils.logger import logger
from ..utils.point import Point, Tripoint


class SaveLoadSystem:
    """保存/加载系统"""

    def __init__(self, save_dir: str = "saves"):
        """
        初始化保存/加载系统

        Args:
            save_dir: 存档目录
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"保存/加载系统已初始化，存档目录: {self.save_dir}")

    def get_save_path(self, world_name: str) -> Path:
        """
        获取存档路径

        Args:
            world_name: 世界名称

        Returns:
            存档文件路径
        """
        return self.save_dir / f"{world_name}.json.gz"

    def list_saves(self) -> list:
        """
        列出所有存档

        Returns:
            存档列表，每个存档是一个字典
        """
        saves = []
        for save_file in self.save_dir.glob("*.json.gz"):
            try:
                # 读取存档元数据
                with gzip.open(save_file, "rt", encoding="utf-8") as f:
                    data = json.load(f)
                    metadata = data.get("metadata", {})
                    saves.append(
                        {
                            "name": save_file.stem.replace(".json", ""),
                            "player_name": metadata.get("player_name", "未知"),
                            "save_time": metadata.get("save_time", "未知"),
                            "turns": metadata.get("turns", 0),
                            "version": metadata.get("version", "未知"),
                        }
                    )
            except Exception as e:
                logger.error(f"读取存档 {save_file} 失败: {e}")

        return sorted(saves, key=lambda x: x["save_time"], reverse=True)

    def save_game(self, game, world_name: str) -> bool:
        """
        保存游戏

        Args:
            game: 游戏实例
            world_name: 世界名称

        Returns:
            是否保存成功
        """
        try:
            save_path = self.get_save_path(world_name)
            logger.info(f"开始保存游戏到: {save_path}")

            # 构建保存数据
            save_data = {
                "metadata": self._save_metadata(game),
                "player": self._save_player(game.player) if game.player else None,
                "world": self._save_world(game.world) if game.world else None,
                "turn_manager": self._save_turn_manager(game.turn_manager),
            }

            # 写入压缩JSON文件
            with gzip.open(save_path, "wt", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            logger.info("游戏保存成功")
            return True

        except Exception as e:
            logger.error(f"保存游戏失败: {e}")
            return False

    def load_game(self, game, world_name: str) -> bool:
        """
        加载游戏

        Args:
            game: 游戏实例
            world_name: 世界名称

        Returns:
            是否加载成功
        """
        try:
            save_path = self.get_save_path(world_name)
            if not save_path.exists():
                logger.error(f"存档文件不存在: {save_path}")
                return False

            logger.info(f"开始加载游戏: {save_path}")

            # 读取压缩JSON文件
            with gzip.open(save_path, "rt", encoding="utf-8") as f:
                save_data = json.load(f)

            # 检查版本兼容性
            metadata = save_data.get("metadata", {})
            save_version = metadata.get("version", "未知")
            logger.info(f"存档版本: {save_version}")

            # 加载玩家
            if save_data.get("player"):
                game.player = self._load_player(save_data["player"])

            # 加载世界
            if save_data.get("world"):
                game.world = self._load_world(save_data["world"])

            # 加载回合管理器
            if save_data.get("turn_manager"):
                self._load_turn_manager(game.turn_manager, save_data["turn_manager"])

            logger.info("游戏加载成功")
            return True

        except Exception as e:
            logger.error(f"加载游戏失败: {e}")
            return False

    def delete_save(self, world_name: str) -> bool:
        """
        删除存档

        Args:
            world_name: 世界名称

        Returns:
            是否删除成功
        """
        try:
            save_path = self.get_save_path(world_name)
            if save_path.exists():
                save_path.unlink()
                logger.info(f"存档已删除: {world_name}")
                return True
            else:
                logger.warning(f"存档不存在: {world_name}")
                return False

        except Exception as e:
            logger.error(f"删除存档失败: {e}")
            return False

    # === 私有方法：序列化 ===

    def _save_metadata(self, game) -> Dict[str, Any]:
        """保存元数据"""
        return {
            "version": "0.1.0",
            "save_time": datetime.now().isoformat(),
            "player_name": game.player.name if game.player else "未知",
            "turns": game.turn_manager.turn if hasattr(game.turn_manager, "turn") else 0,
        }

    def _save_player(self, player) -> Dict[str, Any]:
        """
        保存玩家数据

        Args:
            player: 玩家对象

        Returns:
            玩家数据字典
        """
        return {
            "name": player.name,
            "position": {
                "x": player.position.x,
                "y": player.position.y,
                "z": player.position.z,
            },
            "attributes": {
                "str": player.str,
                "dex": player.dex,
                "int": player.int,
                "per": player.per,
            },
            "hp": {"max": player.hp_max, "cur": player.hp_cur},
            "stamina": {"max": player.stamina_max, "cur": player.stamina_cur},
            "needs": {
                "pain": player.pain,
                "thirst": player.thirst,
                "hunger": player.hunger,
                "fatigue": player.fatigue,
            },
            "skills": player.skills.copy(),
            "traits": player.traits.copy(),
            "mutations": player.mutations.copy(),
            "bionics": player.bionics.copy(),
            "profession": player.profession,
            "scenario": player.scenario,
            "kills": player.kills,
            "turns_survived": player.turns_survived,
            "inventory": self._save_inventory(player.inventory),
            "wielded_item": (
                self._save_item(player.wielded_item) if player.wielded_item else None
            ),
            "worn_items": [self._save_item(item) for item in player.worn_items],
            "moves": player.moves,
        }

    def _save_inventory(self, inventory) -> Dict[str, Any]:
        """保存库存数据"""
        return {
            "volume_capacity": inventory.volume_capacity,
            "weight_capacity": inventory.weight_capacity,
            "items": [self._save_item(item) for item in inventory.items],
        }

    def _save_item(self, item) -> Dict[str, Any]:
        """保存物品数据"""
        return {
            "type_id": item.type_id,
            "uid": item.uid,
            "charges": item.charges,
            "damage_level": item.damage_level,
            "temperature": item.temperature,
            "active": item.active,
            "contents": [self._save_item(content) for content in item.contents],
            "custom_name": item.custom_name,
            "custom_description": item.custom_description,
        }

    def _save_world(self, world) -> Dict[str, Any]:
        """
        保存世界数据

        Args:
            world: 世界对象（地图）

        Returns:
            世界数据字典
        """
        if not hasattr(world, "submaps"):
            return {}

        submaps_data = {}
        for (x, y, z), submap in world.submaps.items():
            key = f"{x},{y},{z}"
            submaps_data[key] = self._save_submap(submap)

        return {
            "center": {"x": world.center.x, "y": world.center.y, "z": world.center.z},
            "submaps": submaps_data,
        }

    def _save_submap(self, submap) -> Dict[str, Any]:
        """保存子地图数据"""
        tiles_data = []
        for y in range(len(submap.tiles)):
            for x in range(len(submap.tiles[y])):
                tile = submap.tiles[y][x]
                if tile.terrain_id != "t_grass" or tile.furniture_id or tile.items:
                    # 只保存非默认状态的格子
                    tiles_data.append(
                        {
                            "x": x,
                            "y": y,
                            "terrain": tile.terrain_id,
                            "furniture": tile.furniture_id,
                            "items": [self._save_item(item) for item in tile.items],
                        }
                    )

        return {
            "x": submap.x,
            "y": submap.y,
            "z": submap.z,
            "tiles": tiles_data,
        }

    def _save_turn_manager(self, turn_manager) -> Dict[str, Any]:
        """保存回合管理器数据"""
        data = {}
        if hasattr(turn_manager, "turn"):
            data["turn"] = turn_manager.turn
        if hasattr(turn_manager, "calendar"):
            data["calendar"] = turn_manager.calendar
        return data

    # === 私有方法：反序列化 ===

    def _load_player(self, data: Dict[str, Any]):
        """
        加载玩家数据

        Args:
            data: 玩家数据字典

        Returns:
            玩家对象
        """
        from ..entities.player import Player

        player = Player(data["name"])

        # 位置
        pos_data = data["position"]
        player.position = Tripoint(pos_data["x"], pos_data["y"], pos_data["z"])

        # 属性
        attrs = data["attributes"]
        player.str = attrs["str"]
        player.dex = attrs["dex"]
        player.int = attrs["int"]
        player.per = attrs["per"]

        # 生命值和体力
        hp = data["hp"]
        player.hp_max = hp["max"]
        player.hp_cur = hp["cur"]

        stamina = data["stamina"]
        player.stamina_max = stamina["max"]
        player.stamina_cur = stamina["cur"]

        # 需求
        needs = data["needs"]
        player.pain = needs["pain"]
        player.thirst = needs["thirst"]
        player.hunger = needs["hunger"]
        player.fatigue = needs["fatigue"]

        # 技能、特征、突变、生化
        player.skills = data["skills"].copy()
        player.traits = data["traits"].copy()
        player.mutations = data["mutations"].copy()
        player.bionics = data["bionics"].copy()

        # 玩家专属数据
        player.profession = data.get("profession")
        player.scenario = data.get("scenario")
        player.kills = data.get("kills", 0)
        player.turns_survived = data.get("turns_survived", 0)

        # 库存
        player.inventory = self._load_inventory(data["inventory"])

        # 手持和穿戴物品
        if data["wielded_item"]:
            player.wielded_item = self._load_item(data["wielded_item"])

        player.worn_items = [self._load_item(item_data) for item_data in data["worn_items"]]

        # 行动点数
        player.moves = data.get("moves", 100)

        return player

    def _load_inventory(self, data: Dict[str, Any]):
        """加载库存数据"""
        from ..entities.inventory import Inventory

        inventory = Inventory(data["volume_capacity"], data["weight_capacity"])
        for item_data in data["items"]:
            item = self._load_item(item_data)
            inventory.add_item(item)

        return inventory

    def _load_item(self, data: Dict[str, Any]):
        """加载物品数据"""
        from ..entities.item import Item

        item = Item(data["type_id"])
        item.uid = data.get("uid", item.uid)
        item.charges = data.get("charges", 0)
        item.damage_level = data.get("damage_level", 0)
        item.temperature = data.get("temperature", 0)
        item.active = data.get("active", False)
        item.custom_name = data.get("custom_name")
        item.custom_description = data.get("custom_description")

        # 加载容器内容物
        for content_data in data.get("contents", []):
            content = self._load_item(content_data)
            item.contents.append(content)

        return item

    def _load_world(self, data: Dict[str, Any]):
        """
        加载世界数据

        Args:
            data: 世界数据字典

        Returns:
            地图对象
        """
        from ..world.map import Map

        world = Map()

        # 加载中心位置
        center_data = data["center"]
        world.center = Tripoint(center_data["x"], center_data["y"], center_data["z"])

        # 加载子地图
        submaps_data = data.get("submaps", {})
        for key, submap_data in submaps_data.items():
            x, y, z = map(int, key.split(","))
            submap = self._load_submap(submap_data)
            world.submaps[(x, y, z)] = submap

        return world

    def _load_submap(self, data: Dict[str, Any]):
        """加载子地图数据"""
        from ..world.submap import Submap

        submap = Submap(data["x"], data["y"], data["z"])

        # 加载非默认状态的格子
        for tile_data in data["tiles"]:
            x = tile_data["x"]
            y = tile_data["y"]
            tile = submap.tiles[y][x]

            tile.terrain_id = tile_data["terrain"]
            tile.furniture_id = tile_data.get("furniture")

            # 加载物品
            for item_data in tile_data.get("items", []):
                item = self._load_item(item_data)
                tile.items.append(item)

        return submap

    def _load_turn_manager(self, turn_manager, data: Dict[str, Any]):
        """加载回合管理器数据"""
        if "turn" in data:
            turn_manager.turn = data["turn"]
        if "calendar" in data:
            turn_manager.calendar = data["calendar"]
