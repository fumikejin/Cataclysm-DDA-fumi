"""
游戏世界 - 大地图缓冲区 (Overmap Buffer)

管理多个大地图实例，负责按需加载和卸载大地图，提供统一的访问接口
类似于原版CDDA的overmapbuffer系统
"""

from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
import json
import os

from ..utils.point import Tripoint, Point
from ..utils.logger import logger
from .overmap import Overmap, OmTile, OVERMAP_SIZE, OMT_SIZE


@dataclass
class OvermapMetadata:
    """大地图元数据"""
    position: Tripoint  # 大地图的世界坐标
    last_accessed: float = 0.0  # 最后访问时间（用于LRU缓存）
    modified: bool = False  # 是否已修改（需要保存）


class OvermapBuffer:
    """
    大地图缓冲区
    
    管理多个大地图实例，提供：
    - 按需加载/卸载大地图
    - 缓存最近使用的大地图
    - 统一的坐标转换和访问接口
    - 大地图保存/加载
    """
    
    def __init__(self, save_dir: str = "saves/overmaps", cache_size: int = 9):
        """
        初始化大地图缓冲区
        
        Args:
            save_dir: 保存大地图的目录
            cache_size: 缓存的大地图数量（默认9个，3x3区域）
        """
        self.save_dir = save_dir
        self.cache_size = cache_size
        
        # 缓存的大地图实例: {overmap_pos: Overmap}
        self.overmaps: Dict[Tuple[int, int, int], Overmap] = {}
        
        # 大地图元数据
        self.metadata: Dict[Tuple[int, int, int], OvermapMetadata] = {}
        
        # 确保保存目录存在
        os.makedirs(self.save_dir, exist_ok=True)
        
        logger.info(f"大地图缓冲区已初始化，缓存大小: {self.cache_size}")
    
    def _overmap_coords_from_om_pos(self, om_pos: Tripoint) -> Tuple[int, int, int]:
        """
        从大地图坐标获取大地图索引
        
        大地图是180x180 OMT，每个大地图覆盖一个区域
        
        Args:
            om_pos: OMT坐标
            
        Returns:
            (om_x, om_y, om_z) 大地图索引
        """
        om_x = om_pos.x // OVERMAP_SIZE
        om_y = om_pos.y // OVERMAP_SIZE
        om_z = om_pos.z
        return (om_x, om_y, om_z)
    
    def _local_om_coords(self, om_pos: Tripoint) -> Tripoint:
        """
        将全局OMT坐标转换为大地图内的本地坐标
        
        Args:
            om_pos: 全局OMT坐标
            
        Returns:
            大地图内的本地OMT坐标 (0-179)
        """
        local_x = om_pos.x % OVERMAP_SIZE
        local_y = om_pos.y % OVERMAP_SIZE
        local_z = om_pos.z
        
        # 处理负坐标
        if local_x < 0:
            local_x += OVERMAP_SIZE
        if local_y < 0:
            local_y += OVERMAP_SIZE
            
        return Tripoint(local_x, local_y, local_z)
    
    def get_overmap_at(self, om_pos: Tripoint) -> Optional[Overmap]:
        """
        获取包含指定OMT坐标的大地图
        
        Args:
            om_pos: OMT坐标
            
        Returns:
            大地图实例，如果不存在则创建
        """
        om_coords = self._overmap_coords_from_om_pos(om_pos)
        
        # 如果已在缓存中，直接返回
        if om_coords in self.overmaps:
            return self.overmaps[om_coords]
        
        # 尝试从磁盘加载
        overmap = self._load_overmap(om_coords)
        
        # 如果不存在，创建新的大地图
        if overmap is None:
            overmap_pos = Tripoint(om_coords[0], om_coords[1], om_coords[2])
            overmap = Overmap(overmap_pos)
            logger.info(f"创建新大地图: {om_coords}")
        else:
            logger.info(f"从磁盘加载大地图: {om_coords}")
        
        # 添加到缓存
        self._add_to_cache(om_coords, overmap)
        
        return overmap
    
    def _add_to_cache(self, om_coords: Tuple[int, int, int], overmap: Overmap):
        """
        添加大地图到缓存，如果缓存已满则移除最久未使用的
        
        Args:
            om_coords: 大地图坐标
            overmap: 大地图实例
        """
        import time
        
        # 如果缓存已满，移除最久未使用的大地图
        if len(self.overmaps) >= self.cache_size:
            self._evict_lru()
        
        # 添加到缓存
        self.overmaps[om_coords] = overmap
        self.metadata[om_coords] = OvermapMetadata(
            position=Tripoint(om_coords[0], om_coords[1], om_coords[2]),
            last_accessed=time.time(),
            modified=True
        )
    
    def _evict_lru(self):
        """移除最久未使用的大地图"""
        if not self.overmaps:
            return
        
        # 找到最久未使用的大地图
        lru_coords = min(
            self.metadata.keys(),
            key=lambda k: self.metadata[k].last_accessed
        )
        
        # 如果已修改，保存到磁盘
        if self.metadata[lru_coords].modified:
            self._save_overmap(lru_coords)
        
        # 从缓存中移除
        del self.overmaps[lru_coords]
        del self.metadata[lru_coords]
        
        logger.debug(f"从缓存中移除大地图: {lru_coords}")
    
    def get_tile(self, om_pos: Tripoint) -> Optional[OmTile]:
        """
        获取指定OMT坐标处的大地图格子
        
        Args:
            om_pos: OMT坐标
            
        Returns:
            大地图格子，如果不存在则返回None
        """
        overmap = self.get_overmap_at(om_pos)
        if overmap is None:
            return None
        
        local_pos = self._local_om_coords(om_pos)
        return overmap.get_tile(local_pos)
    
    def set_tile_terrain(self, om_pos: Tripoint, terrain_id: str):
        """
        设置指定OMT坐标处的地形
        
        Args:
            om_pos: OMT坐标
            terrain_id: 地形ID
        """
        overmap = self.get_overmap_at(om_pos)
        if overmap is None:
            return
        
        local_pos = self._local_om_coords(om_pos)
        overmap.set_terrain(local_pos, terrain_id)
        
        # 标记为已修改
        om_coords = self._overmap_coords_from_om_pos(om_pos)
        if om_coords in self.metadata:
            self.metadata[om_coords].modified = True
    
    def mark_seen(self, om_pos: Tripoint):
        """
        标记OMT坐标为已见过
        
        Args:
            om_pos: OMT坐标
        """
        tile = self.get_tile(om_pos)
        if tile:
            tile.seen = True
            
            # 标记为已修改
            om_coords = self._overmap_coords_from_om_pos(om_pos)
            if om_coords in self.metadata:
                self.metadata[om_coords].modified = True
    
    def is_explored(self, om_pos: Tripoint) -> bool:
        """
        检查OMT坐标是否已探索
        
        Args:
            om_pos: OMT坐标
            
        Returns:
            是否已探索
        """
        tile = self.get_tile(om_pos)
        return tile.explored if tile else False
    
    def _get_save_path(self, om_coords: Tuple[int, int, int]) -> str:
        """
        获取大地图的保存路径
        
        Args:
            om_coords: 大地图坐标 (om_x, om_y, om_z)
            
        Returns:
            保存文件路径
        """
        om_x, om_y, om_z = om_coords
        filename = f"overmap_{om_x}_{om_y}_{om_z}.json"
        return os.path.join(self.save_dir, filename)
    
    def _save_overmap(self, om_coords: Tuple[int, int, int]):
        """
        保存大地图到磁盘
        
        Args:
            om_coords: 大地图坐标
        """
        if om_coords not in self.overmaps:
            return
        
        overmap = self.overmaps[om_coords]
        save_path = self._get_save_path(om_coords)
        
        try:
            data = overmap.to_dict()
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 标记为未修改
            if om_coords in self.metadata:
                self.metadata[om_coords].modified = False
            
            logger.debug(f"大地图已保存: {save_path}")
        except Exception as e:
            logger.error(f"保存大地图失败 {om_coords}: {e}")
    
    def _load_overmap(self, om_coords: Tuple[int, int, int]) -> Optional[Overmap]:
        """
        从磁盘加载大地图
        
        Args:
            om_coords: 大地图坐标
            
        Returns:
            大地图实例，如果文件不存在则返回None
        """
        save_path = self._get_save_path(om_coords)
        
        if not os.path.exists(save_path):
            return None
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            overmap = Overmap.from_dict(data)
            return overmap
        except Exception as e:
            logger.error(f"加载大地图失败 {om_coords}: {e}")
            return None
    
    def save_all(self):
        """保存所有已修改的大地图"""
        saved_count = 0
        for om_coords, metadata in self.metadata.items():
            if metadata.modified:
                self._save_overmap(om_coords)
                saved_count += 1
        
        if saved_count > 0:
            logger.info(f"已保存 {saved_count} 个大地图")
    
    def clear_cache(self):
        """清空缓存（保存所有已修改的大地图）"""
        self.save_all()
        self.overmaps.clear()
        self.metadata.clear()
        logger.info("大地图缓存已清空")
    
    def get_cached_overmaps(self) -> List[Tuple[int, int, int]]:
        """
        获取当前缓存的大地图列表
        
        Returns:
            大地图坐标列表
        """
        return list(self.overmaps.keys())
    
    def preload_region(self, center_om_pos: Tripoint, radius: int = 1):
        """
        预加载指定区域的大地图
        
        Args:
            center_om_pos: 中心OMT坐标
            radius: 半径（以大地图为单位，默认1表示3x3区域）
        """
        center_om_coords = self._overmap_coords_from_om_pos(center_om_pos)
        cx, cy, cz = center_om_coords
        
        loaded_count = 0
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                om_coords = (cx + dx, cy + dy, cz)
                
                # 如果不在缓存中，加载它
                if om_coords not in self.overmaps:
                    om_pos = Tripoint(
                        om_coords[0] * OVERMAP_SIZE,
                        om_coords[1] * OVERMAP_SIZE,
                        om_coords[2]
                    )
                    self.get_overmap_at(om_pos)
                    loaded_count += 1
        
        if loaded_count > 0:
            logger.info(f"预加载了 {loaded_count} 个大地图")
    
    def get_terrain_at(self, om_pos: Tripoint) -> str:
        """
        获取指定OMT坐标的地形ID
        
        Args:
            om_pos: OMT坐标
            
        Returns:
            地形ID，如果不存在则返回"field"
        """
        tile = self.get_tile(om_pos)
        return tile.terrain_id if tile else "field"
    
    def find_nearest_terrain(
        self, 
        start_pos: Tripoint, 
        terrain_id: str, 
        max_distance: int = 100
    ) -> Optional[Tripoint]:
        """
        查找最近的指定地形
        
        Args:
            start_pos: 起始OMT坐标
            terrain_id: 要查找的地形ID
            max_distance: 最大搜索距离（OMT单位）
            
        Returns:
            最近的匹配地形的OMT坐标，如果未找到则返回None
        """
        # 简单的螺旋搜索
        for distance in range(max_distance + 1):
            for dx in range(-distance, distance + 1):
                for dy in range(-distance, distance + 1):
                    # 只检查当前距离的边界
                    if abs(dx) != distance and abs(dy) != distance:
                        continue
                    
                    pos = Tripoint(start_pos.x + dx, start_pos.y + dy, start_pos.z)
                    if self.get_terrain_at(pos) == terrain_id:
                        return pos
        
        return None
