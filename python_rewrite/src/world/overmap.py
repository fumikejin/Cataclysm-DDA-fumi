"""
游戏世界 - 大地图系统 (Overmap)

实现 CDDA 的大地图系统，管理世界地图、特殊位置、城市、道路等
Overmap 坐标单位为 OMT (Overmap Tile)，每个 OMT 包含 2x2 个子地图
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from ..utils.point import Tripoint, Point
from ..utils.logger import logger


# 大地图常量
OMT_SIZE = 2  # 每个 OMT 包含 2x2 个子地图
OVERMAP_SIZE = 180  # 大地图大小 (180x180 OMT)
SUBMAP_SIZE = 12  # 子地图大小 (12x12 格子)


class OmTerType(Enum):
    """大地图地形类型"""
    # 自然地形
    FIELD = "field"  # 原野
    FOREST = "forest"  # 森林
    FOREST_THICK = "forest_thick"  # 密林
    FOREST_WATER = "forest_water"  # 沼泽森林
    SWAMP = "swamp"  # 沼泽
    
    # 道路和城市
    ROAD = "road"  # 道路
    BRIDGE = "bridge"  # 桥梁
    ROAD_HIGHWAY = "road_highway"  # 高速公路
    
    # 城市区域
    CITY_HOUSE = "house"  # 民居
    CITY_SHOP = "shop"  # 商店
    CITY_PARK = "park"  # 公园
    CITY_PARKING_LOT = "parking_lot"  # 停车场
    
    # 特殊建筑
    HOSPITAL = "hospital"  # 医院
    POLICE_STATION = "police_station"  # 警察局
    FIRE_STATION = "fire_station"  # 消防局
    SCHOOL = "school"  # 学校
    LIBRARY = "library"  # 图书馆
    BANK = "bank"  # 银行
    GAS_STATION = "gas_station"  # 加油站
    SUPERMARKET = "supermarket"  # 超市
    
    # 工业和军事
    FACTORY = "factory"  # 工厂
    WAREHOUSE = "warehouse"  # 仓库
    BUNKER = "bunker"  # 地堡
    MILITARY_OUTPOST = "military_outpost"  # 军事前哨
    
    # 水域
    RIVER = "river"  # 河流
    LAKE = "lake"  # 湖泊
    OCEAN = "ocean"  # 海洋


@dataclass
class OmTerrainData:
    """大地图地形数据"""
    id: str
    name: str
    symbol: str  # ASCII 符号
    color: str  # 颜色（用于渲染）
    allows_camp: bool = False  # 是否允许建营地
    spawns_monster: bool = True  # 是否生成怪物
    is_water: bool = False  # 是否为水域
    is_road: bool = False  # 是否为道路
    
    
class OmTerrainManager:
    """大地图地形管理器"""
    
    def __init__(self):
        """初始化地形管理器"""
        self.terrains: Dict[str, OmTerrainData] = {}
        self._init_default_terrains()
    
    def _init_default_terrains(self):
        """初始化默认地形类型"""
        terrains = [
            OmTerrainData("field", "原野", ".", "green", True, True),
            OmTerrainData("forest", "森林", "F", "dark_green", False, True),
            OmTerrainData("forest_thick", "密林", "f", "dark_green", False, True),
            OmTerrainData("swamp", "沼泽", "~", "cyan", False, True),
            
            OmTerrainData("road", "道路", "#", "gray", False, False, False, True),
            OmTerrainData("bridge", "桥梁", "B", "brown", False, False, False, True),
            OmTerrainData("road_highway", "高速公路", "=", "gray", False, False, False, True),
            
            OmTerrainData("house", "民居", "H", "white", False, True),
            OmTerrainData("shop", "商店", "S", "yellow", False, True),
            OmTerrainData("park", "公园", "P", "light_green", True, False),
            OmTerrainData("parking_lot", "停车场", "p", "gray", False, False),
            
            OmTerrainData("hospital", "医院", "+", "red", False, True),
            OmTerrainData("police_station", "警察局", "☆", "blue", False, True),
            OmTerrainData("fire_station", "消防局", "☆", "red", False, True),
            OmTerrainData("school", "学校", "○", "yellow", False, True),
            OmTerrainData("library", "图书馆", "L", "cyan", False, False),
            OmTerrainData("bank", "银行", "$", "gold", False, True),
            OmTerrainData("gas_station", "加油站", "G", "yellow", False, True),
            OmTerrainData("supermarket", "超市", "M", "blue", False, True),
            
            OmTerrainData("factory", "工厂", "■", "gray", False, True),
            OmTerrainData("warehouse", "仓库", "W", "gray", False, True),
            OmTerrainData("bunker", "地堡", "B", "dark_gray", False, True),
            OmTerrainData("military_outpost", "军事前哨", "M", "green", False, True),
            
            OmTerrainData("river", "河流", "~", "blue", False, False, True),
            OmTerrainData("lake", "湖泊", "≈", "blue", False, False, True),
            OmTerrainData("ocean", "海洋", "≈", "dark_blue", False, False, True),
        ]
        
        for terrain in terrains:
            self.terrains[terrain.id] = terrain
        
        logger.info(f"大地图地形管理器已初始化，加载了 {len(self.terrains)} 种地形")
    
    def get_terrain(self, terrain_id: str) -> Optional[OmTerrainData]:
        """获取地形数据"""
        return self.terrains.get(terrain_id)
    
    def register_terrain(self, terrain: OmTerrainData):
        """注册新地形类型"""
        self.terrains[terrain.id] = terrain


@dataclass
class OmNote:
    """大地图笔记"""
    text: str
    symbol: str = "N"
    color: str = "yellow"


@dataclass
class OmSpecial:
    """大地图特殊位置标记"""
    id: str  # 位置类型ID (如 "hospital_entrance", "quest_target")
    name: str  # 显示名称
    description: str = ""  # 描述
    seen: bool = False  # 是否已发现


class OmTile:
    """大地图格子 (Overmap Tile)"""
    
    def __init__(self, terrain_id: str = "field"):
        """
        初始化大地图格子
        
        Args:
            terrain_id: 地形类型ID
        """
        self.terrain_id = terrain_id
        self.seen = False  # 是否已探索
        self.explored = False  # 是否已详细探索
        self.note: Optional[OmNote] = None  # 玩家笔记
        self.specials: List[OmSpecial] = []  # 特殊位置标记
    
    def add_special(self, special: OmSpecial):
        """添加特殊位置标记"""
        self.specials.append(special)
    
    def remove_special(self, special_id: str):
        """移除特殊位置标记"""
        self.specials = [s for s in self.specials if s.id != special_id]
    
    def has_special(self, special_id: str) -> bool:
        """检查是否有特定的特殊位置"""
        return any(s.id == special_id for s in self.specials)


class Overmap:
    """大地图 - 管理世界地图、特殊位置、城市等"""
    
    def __init__(self, position: Tripoint = None):
        """
        初始化大地图
        
        Args:
            position: 大地图的世界坐标 (默认 (0,0,0))
        """
        self.position = position if position else Tripoint(0, 0, 0)
        
        # 大地图格子: [z][y][x]
        self.tiles: List[List[List[OmTile]]] = []
        
        # 初始化大地图格子
        for z in range(-1, 2):  # 支持 -1, 0, 1 三个Z层
            z_layer = []
            for y in range(OVERMAP_SIZE):
                row = []
                for x in range(OVERMAP_SIZE):
                    row.append(OmTile())
                z_layer.append(row)
            self.tiles.append(z_layer)
        
        # 地形管理器
        self.terrain_manager = OmTerrainManager()
        
        # 已发现的特殊位置集合
        self.discovered_locations: Set[str] = set()
        
        logger.info(f"大地图已创建，位置: {self.position}, 大小: {OVERMAP_SIZE}x{OVERMAP_SIZE}")
    
    def _get_z_index(self, z: int) -> int:
        """将Z坐标转换为数组索引"""
        return z + 1  # -1 -> 0, 0 -> 1, 1 -> 2
    
    def is_valid_pos(self, pos: Tripoint) -> bool:
        """检查位置是否有效"""
        return (0 <= pos.x < OVERMAP_SIZE and
                0 <= pos.y < OVERMAP_SIZE and
                -1 <= pos.z <= 1)
    
    def get_tile(self, pos: Tripoint) -> Optional[OmTile]:
        """
        获取指定位置的大地图格子
        
        Args:
            pos: OMT 坐标（相对于大地图）
            
        Returns:
            大地图格子，坐标无效则返回 None
        """
        if not self.is_valid_pos(pos):
            return None
        
        z_idx = self._get_z_index(pos.z)
        return self.tiles[z_idx][pos.y][pos.x]
    
    def set_terrain(self, pos: Tripoint, terrain_id: str):
        """
        设置指定位置的地形
        
        Args:
            pos: OMT 坐标
            terrain_id: 地形类型ID
        """
        tile = self.get_tile(pos)
        if tile:
            tile.terrain_id = terrain_id
            logger.debug(f"设置大地图地形: {pos} -> {terrain_id}")
    
    def get_terrain(self, pos: Tripoint) -> Optional[str]:
        """获取指定位置的地形ID"""
        tile = self.get_tile(pos)
        return tile.terrain_id if tile else None
    
    def reveal(self, pos: Tripoint, radius: int = 0):
        """
        揭示指定位置及其周围区域
        
        Args:
            pos: 中心位置
            radius: 揭示半径
        """
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                reveal_pos = Tripoint(pos.x + dx, pos.y + dy, pos.z)
                tile = self.get_tile(reveal_pos)
                if tile:
                    tile.seen = True
    
    def explore(self, pos: Tripoint):
        """标记位置为已详细探索"""
        tile = self.get_tile(pos)
        if tile:
            tile.seen = True
            tile.explored = True
    
    def is_explored(self, pos: Tripoint) -> bool:
        """检查位置是否已探索"""
        tile = self.get_tile(pos)
        return tile.explored if tile else False
    
    def is_seen(self, pos: Tripoint) -> bool:
        """检查位置是否已发现"""
        tile = self.get_tile(pos)
        return tile.seen if tile else False
    
    def add_note(self, pos: Tripoint, text: str, symbol: str = "N", color: str = "yellow"):
        """
        在指定位置添加笔记
        
        Args:
            pos: 位置
            text: 笔记内容
            symbol: 显示符号
            color: 颜色
        """
        tile = self.get_tile(pos)
        if tile:
            tile.note = OmNote(text, symbol, color)
            logger.info(f"添加大地图笔记: {pos} - {text}")
    
    def remove_note(self, pos: Tripoint):
        """移除指定位置的笔记"""
        tile = self.get_tile(pos)
        if tile:
            tile.note = None
    
    def get_note(self, pos: Tripoint) -> Optional[OmNote]:
        """获取指定位置的笔记"""
        tile = self.get_tile(pos)
        return tile.note if tile else None
    
    def add_special(self, pos: Tripoint, special: OmSpecial):
        """添加特殊位置标记"""
        tile = self.get_tile(pos)
        if tile:
            tile.add_special(special)
            self.discovered_locations.add(special.id)
            logger.info(f"添加特殊位置: {pos} - {special.name}")
    
    def find_special(self, special_id: str) -> Optional[Tripoint]:
        """
        查找特定类型的特殊位置
        
        Args:
            special_id: 特殊位置ID
            
        Returns:
            位置坐标，未找到则返回 None
        """
        for z_idx in range(len(self.tiles)):
            z = z_idx - 1  # 转换回真实Z坐标
            for y in range(OVERMAP_SIZE):
                for x in range(OVERMAP_SIZE):
                    tile = self.tiles[z_idx][y][x]
                    if tile.has_special(special_id):
                        return Tripoint(x, y, z)
        return None
    
    def find_terrain(self, terrain_id: str, start_pos: Tripoint, 
                    max_dist: int = 100) -> Optional[Tripoint]:
        """
        从起始位置查找最近的指定地形
        
        Args:
            terrain_id: 地形类型ID
            start_pos: 起始位置
            max_dist: 最大搜索距离
            
        Returns:
            最近的位置坐标，未找到则返回 None
        """
        min_dist = float('inf')
        result = None
        
        for dy in range(-max_dist, max_dist + 1):
            for dx in range(-max_dist, max_dist + 1):
                pos = Tripoint(start_pos.x + dx, start_pos.y + dy, start_pos.z)
                if not self.is_valid_pos(pos):
                    continue
                
                tile = self.get_tile(pos)
                if tile and tile.terrain_id == terrain_id:
                    dist = abs(dx) + abs(dy)  # 曼哈顿距离
                    if dist < min_dist:
                        min_dist = dist
                        result = pos
        
        return result
    
    def generate_simple(self):
        """生成简单的测试地图"""
        logger.info("生成简单测试大地图...")
        
        # 填充原野
        for z_idx in range(len(self.tiles)):
            for y in range(OVERMAP_SIZE):
                for x in range(OVERMAP_SIZE):
                    self.tiles[z_idx][y][x].terrain_id = "field"
        
        # 中心区域创建城市
        center = OVERMAP_SIZE // 2
        city_size = 20
        
        # 城市道路网格
        for i in range(-city_size, city_size):
            # 横向道路
            if i % 4 == 0:
                for x in range(center - city_size, center + city_size):
                    pos = Tripoint(x, center + i, 0)
                    if self.is_valid_pos(pos):
                        self.set_terrain(pos, "road")
            
            # 纵向道路
            if i % 4 == 0:
                for y in range(center - city_size, center + city_size):
                    pos = Tripoint(center + i, y, 0)
                    if self.is_valid_pos(pos):
                        self.set_terrain(pos, "road")
        
        # 放置建筑
        buildings = [
            ("hospital", center - 10, center - 10),
            ("police_station", center + 10, center - 10),
            ("supermarket", center - 10, center + 10),
            ("gas_station", center + 10, center + 10),
            ("library", center, center - 15),
            ("bank", center, center + 15),
        ]
        
        for building_type, x, y in buildings:
            pos = Tripoint(x, y, 0)
            if self.is_valid_pos(pos):
                self.set_terrain(pos, building_type)
                self.add_special(pos, OmSpecial(
                    id=f"{building_type}_{x}_{y}",
                    name=self.terrain_manager.get_terrain(building_type).name
                ))
        
        # 周围添加森林
        for y in range(OVERMAP_SIZE):
            for x in range(OVERMAP_SIZE):
                pos = Tripoint(x, y, 0)
                # 距离中心较远的地方
                dist = abs(x - center) + abs(y - center)
                if dist > city_size + 10:
                    if (x + y) % 3 == 0:
                        self.set_terrain(pos, "forest")
                    elif (x + y) % 7 == 0:
                        self.set_terrain(pos, "forest_thick")
        
        # 添加河流
        river_y = center + 30
        for x in range(OVERMAP_SIZE):
            pos = Tripoint(x, river_y, 0)
            if self.is_valid_pos(pos):
                self.set_terrain(pos, "river")
        
        logger.info("简单测试大地图生成完成")
    
    def to_dict(self) -> dict:
        """序列化为字典（用于保存）"""
        tiles_data = []
        
        # 只保存非默认状态的格子
        for z_idx in range(len(self.tiles)):
            z = z_idx - 1
            for y in range(OVERMAP_SIZE):
                for x in range(OVERMAP_SIZE):
                    tile = self.tiles[z_idx][y][x]
                    
                    # 如果格子有非默认状态，保存它
                    if (tile.terrain_id != "field" or tile.seen or 
                        tile.explored or tile.note or tile.specials):
                        
                        tile_data = {
                            "pos": [x, y, z],
                            "terrain": tile.terrain_id,
                            "seen": tile.seen,
                            "explored": tile.explored,
                        }
                        
                        if tile.note:
                            tile_data["note"] = {
                                "text": tile.note.text,
                                "symbol": tile.note.symbol,
                                "color": tile.note.color,
                            }
                        
                        if tile.specials:
                            tile_data["specials"] = [
                                {
                                    "id": s.id,
                                    "name": s.name,
                                    "description": s.description,
                                    "seen": s.seen,
                                }
                                for s in tile.specials
                            ]
                        
                        tiles_data.append(tile_data)
        
        return {
            "position": [self.position.x, self.position.y, self.position.z],
            "tiles": tiles_data,
            "discovered_locations": list(self.discovered_locations),
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Overmap':
        """从字典反序列化"""
        pos_data = data.get("position", [0, 0, 0])
        overmap = Overmap(Tripoint(pos_data[0], pos_data[1], pos_data[2]))
        
        # 恢复格子数据
        for tile_data in data.get("tiles", []):
            pos = tile_data["pos"]
            tile_pos = Tripoint(pos[0], pos[1], pos[2])
            tile = overmap.get_tile(tile_pos)
            
            if tile:
                tile.terrain_id = tile_data.get("terrain", "field")
                tile.seen = tile_data.get("seen", False)
                tile.explored = tile_data.get("explored", False)
                
                if "note" in tile_data:
                    note_data = tile_data["note"]
                    tile.note = OmNote(
                        text=note_data["text"],
                        symbol=note_data.get("symbol", "N"),
                        color=note_data.get("color", "yellow")
                    )
                
                if "specials" in tile_data:
                    for special_data in tile_data["specials"]:
                        special = OmSpecial(
                            id=special_data["id"],
                            name=special_data["name"],
                            description=special_data.get("description", ""),
                            seen=special_data.get("seen", False)
                        )
                        tile.add_special(special)
        
        # 恢复已发现位置列表
        overmap.discovered_locations = set(data.get("discovered_locations", []))
        
        return overmap


# 坐标转换工具函数
def tile_to_omt(tile_pos: Tripoint) -> Tripoint:
    """
    将格子坐标转换为 OMT 坐标
    
    Args:
        tile_pos: 格子全局坐标
        
    Returns:
        OMT 坐标
    """
    from .coordinates import SUBMAP_SIZE
    tiles_per_omt = OMT_SIZE * SUBMAP_SIZE  # 2 * 12 = 24
    
    return Tripoint(
        tile_pos.x // tiles_per_omt,
        tile_pos.y // tiles_per_omt,
        tile_pos.z
    )


def omt_to_tile(omt_pos: Tripoint) -> Tripoint:
    """
    将 OMT 坐标转换为格子坐标（OMT 左上角）
    
    Args:
        omt_pos: OMT 坐标
        
    Returns:
        格子全局坐标
    """
    from .coordinates import SUBMAP_SIZE
    tiles_per_omt = OMT_SIZE * SUBMAP_SIZE
    
    return Tripoint(
        omt_pos.x * tiles_per_omt,
        omt_pos.y * tiles_per_omt,
        omt_pos.z
    )


def submap_to_omt(submap_pos: Tripoint) -> Tripoint:
    """
    将子地图坐标转换为 OMT 坐标
    
    Args:
        submap_pos: 子地图坐标
        
    Returns:
        OMT 坐标
    """
    return Tripoint(
        submap_pos.x // OMT_SIZE,
        submap_pos.y // OMT_SIZE,
        submap_pos.z
    )
