"""
游戏世界 - 世界工厂 (World Factory)

管理游戏世界的创建、加载、保存和删除
类似于原版CDDA的worldfactory系统
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import shutil

from ..utils.point import Tripoint
from ..utils.logger import logger
from .overmap_buffer import OvermapBuffer


@dataclass
class WorldMetadata:
    """世界元数据"""
    name: str  # 世界名称
    seed: int  # 世界种子
    created_time: str  # 创建时间
    last_played: str  # 最后游玩时间
    play_time: int = 0  # 游玩时间（秒）
    turn_count: int = 0  # 回合数
    version: str = "0.1.0"  # 版本号
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.name,
            "seed": self.seed,
            "created_time": self.created_time,
            "last_played": self.last_played,
            "play_time": self.play_time,
            "turn_count": self.turn_count,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WorldMetadata':
        """从字典创建"""
        return cls(
            name=data.get("name", "Unnamed World"),
            seed=data.get("seed", 0),
            created_time=data.get("created_time", ""),
            last_played=data.get("last_played", ""),
            play_time=data.get("play_time", 0),
            turn_count=data.get("turn_count", 0),
            version=data.get("version", "0.1.0")
        )


class World:
    """
    游戏世界
    
    代表一个独立的游戏世界，包含：
    - 世界元数据
    - 大地图缓冲区
    - 世界中心位置
    - 玩家数据（在其他系统中管理）
    """
    
    def __init__(self, name: str, seed: int = None, world_dir: str = None):
        """
        初始化游戏世界
        
        Args:
            name: 世界名称
            seed: 世界种子（如果为None则自动生成）
            world_dir: 世界保存目录
        """
        import time
        import random
        
        self.metadata = WorldMetadata(
            name=name,
            seed=seed if seed is not None else random.randint(0, 999999999),
            created_time=datetime.now().isoformat(),
            last_played=datetime.now().isoformat()
        )
        
        # 世界目录
        if world_dir is None:
            world_dir = os.path.join("saves", "worlds", self._sanitize_name(name))
        self.world_dir = world_dir
        
        # 大地图缓冲区
        overmap_dir = os.path.join(self.world_dir, "overmaps")
        self.overmap_buffer = OvermapBuffer(save_dir=overmap_dir)
        
        # 世界中心位置（OMT坐标）
        self.center_pos = Tripoint(0, 0, 0)
        
        # 确保世界目录存在
        os.makedirs(self.world_dir, exist_ok=True)
        
        logger.info(f"世界 '{name}' 已初始化，种子: {self.metadata.seed}")
    
    @staticmethod
    def _sanitize_name(name: str) -> str:
        """
        清理世界名称，使其适合作为文件名
        
        Args:
            name: 原始名称
            
        Returns:
            清理后的名称
        """
        # 移除或替换非法字符
        import re
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        sanitized = sanitized.strip()
        if not sanitized:
            sanitized = "world"
        return sanitized
    
    def get_metadata_path(self) -> str:
        """获取元数据文件路径"""
        return os.path.join(self.world_dir, "world_metadata.json")
    
    def save_metadata(self):
        """保存世界元数据"""
        try:
            # 更新最后游玩时间
            self.metadata.last_played = datetime.now().isoformat()
            
            data = self.metadata.to_dict()
            
            # 添加世界中心位置
            data["center_pos"] = {
                "x": self.center_pos.x,
                "y": self.center_pos.y,
                "z": self.center_pos.z
            }
            
            metadata_path = self.get_metadata_path()
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"世界元数据已保存: {metadata_path}")
        except Exception as e:
            logger.error(f"保存世界元数据失败: {e}")
    
    def load_metadata(self) -> bool:
        """
        加载世界元数据
        
        Returns:
            是否成功加载
        """
        metadata_path = self.get_metadata_path()
        
        if not os.path.exists(metadata_path):
            return False
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.metadata = WorldMetadata.from_dict(data)
            
            # 加载世界中心位置
            if "center_pos" in data:
                center = data["center_pos"]
                self.center_pos = Tripoint(center["x"], center["y"], center["z"])
            
            logger.info(f"世界元数据已加载: {self.metadata.name}")
            return True
        except Exception as e:
            logger.error(f"加载世界元数据失败: {e}")
            return False
    
    def save(self):
        """保存整个世界（元数据和所有大地图）"""
        self.save_metadata()
        self.overmap_buffer.save_all()
        logger.info(f"世界 '{self.metadata.name}' 已保存")
    
    def update_play_time(self, seconds: int):
        """
        更新游玩时间
        
        Args:
            seconds: 增加的秒数
        """
        self.metadata.play_time += seconds
    
    def increment_turn_count(self):
        """增加回合数"""
        self.metadata.turn_count += 1


class WorldFactory:
    """
    世界工厂
    
    负责：
    - 创建新世界
    - 加载现有世界
    - 删除世界
    - 列出所有世界
    - 管理当前活动世界
    """
    
    def __init__(self, saves_dir: str = "saves/worlds"):
        """
        初始化世界工厂
        
        Args:
            saves_dir: 世界保存的根目录
        """
        self.saves_dir = saves_dir
        self.current_world: Optional[World] = None
        
        # 确保保存目录存在
        os.makedirs(self.saves_dir, exist_ok=True)
        
        logger.info("世界工厂已初始化")
    
    def create_world(
        self, 
        name: str, 
        seed: int = None, 
        set_as_current: bool = True
    ) -> World:
        """
        创建新世界
        
        Args:
            name: 世界名称
            seed: 世界种子（可选）
            set_as_current: 是否设置为当前世界
            
        Returns:
            创建的世界实例
        """
        # 检查世界是否已存在
        if self.world_exists(name):
            logger.warning(f"世界 '{name}' 已存在")
            # 可以选择加载现有世界或抛出异常
            # 这里选择创建一个带后缀的新世界
            import time
            name = f"{name}_{int(time.time())}"
        
        world_dir = os.path.join(self.saves_dir, World._sanitize_name(name))
        world = World(name=name, seed=seed, world_dir=world_dir)
        
        # 保存世界元数据
        world.save_metadata()
        
        if set_as_current:
            self.current_world = world
        
        logger.info(f"创建新世界: '{name}' (种子: {world.metadata.seed})")
        return world
    
    def load_world(self, name: str, set_as_current: bool = True) -> Optional[World]:
        """
        加载现有世界
        
        Args:
            name: 世界名称
            set_as_current: 是否设置为当前世界
            
        Returns:
            加载的世界实例，如果失败则返回None
        """
        world_dir = os.path.join(self.saves_dir, World._sanitize_name(name))
        
        if not os.path.exists(world_dir):
            logger.error(f"世界目录不存在: {world_dir}")
            return None
        
        # 创建世界实例并加载元数据
        world = World(name=name, world_dir=world_dir)
        
        if not world.load_metadata():
            logger.error(f"加载世界 '{name}' 失败")
            return None
        
        if set_as_current:
            self.current_world = world
        
        logger.info(f"已加载世界: '{name}'")
        return world
    
    def delete_world(self, name: str) -> bool:
        """
        删除世界
        
        Args:
            name: 世界名称
            
        Returns:
            是否成功删除
        """
        world_dir = os.path.join(self.saves_dir, World._sanitize_name(name))
        
        if not os.path.exists(world_dir):
            logger.warning(f"世界目录不存在: {world_dir}")
            return False
        
        try:
            shutil.rmtree(world_dir)
            logger.info(f"已删除世界: '{name}'")
            
            # 如果删除的是当前世界，清空当前世界
            if self.current_world and self.current_world.metadata.name == name:
                self.current_world = None
            
            return True
        except Exception as e:
            logger.error(f"删除世界失败 '{name}': {e}")
            return False
    
    def world_exists(self, name: str) -> bool:
        """
        检查世界是否存在
        
        Args:
            name: 世界名称
            
        Returns:
            世界是否存在
        """
        world_dir = os.path.join(self.saves_dir, World._sanitize_name(name))
        return os.path.exists(world_dir)
    
    def list_worlds(self) -> List[WorldMetadata]:
        """
        列出所有可用的世界
        
        Returns:
            世界元数据列表
        """
        worlds = []
        
        if not os.path.exists(self.saves_dir):
            return worlds
        
        for entry in os.listdir(self.saves_dir):
            world_dir = os.path.join(self.saves_dir, entry)
            
            # 检查是否为目录
            if not os.path.isdir(world_dir):
                continue
            
            # 尝试加载元数据
            metadata_path = os.path.join(world_dir, "world_metadata.json")
            if not os.path.exists(metadata_path):
                continue
            
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                metadata = WorldMetadata.from_dict(data)
                worlds.append(metadata)
            except Exception as e:
                logger.warning(f"加载世界元数据失败 {entry}: {e}")
        
        # 按最后游玩时间排序
        worlds.sort(key=lambda w: w.last_played, reverse=True)
        
        return worlds
    
    def get_current_world(self) -> Optional[World]:
        """
        获取当前活动世界
        
        Returns:
            当前世界，如果没有则返回None
        """
        return self.current_world
    
    def save_current_world(self):
        """保存当前世界"""
        if self.current_world:
            self.current_world.save()
            logger.info("当前世界已保存")
        else:
            logger.warning("没有当前世界可以保存")
    
    def close_current_world(self):
        """关闭当前世界（保存并清理）"""
        if self.current_world:
            self.current_world.save()
            self.current_world.overmap_buffer.clear_cache()
            logger.info(f"世界 '{self.current_world.metadata.name}' 已关闭")
            self.current_world = None
