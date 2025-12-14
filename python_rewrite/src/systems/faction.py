"""
游戏系统 - 派系系统

派系管理和关系系统
"""

from typing import Dict, List, Optional, Set
from enum import Enum
import json

from ..utils.logger import logger
from ..utils.point import Point


class FactionRelation(Enum):
    """派系关系类型"""
    NEUTRAL = "neutral"      # 中立
    ALLY = "ally"           # 盟友
    ENEMY = "enemy"         # 敌人
    WAR = "war"             # 战争
    PEACE = "peace"         # 和平


class FactionPower(Enum):
    """派系影响力级别"""
    TINY = 1       # 微小（<10人）
    SMALL = 2      # 小型（10-50人）
    MEDIUM = 3     # 中型（50-200人）
    LARGE = 4      # 大型（200-500人）
    HUGE = 5       # 巨大（>500人）


class Faction:
    """派系类"""
    
    def __init__(self, faction_id: str, name: str):
        """
        初始化派系
        
        Args:
            faction_id: 派系ID
            name: 派系名称
        """
        self.id = faction_id
        self.name = name
        self.description = ""  # 描述
        
        # 派系属性
        self.power = FactionPower.SMALL  # 影响力
        self.wealth = 0  # 财富（货币）
        self.size = 10  # 成员数量
        self.respect = 0  # 声望（-100到100）
        
        # 派系关系
        self.relations: Dict[str, FactionRelation] = {}  # 与其他派系的关系
        self.liked_factions: Set[str] = set()  # 友好派系
        self.disliked_factions: Set[str] = set()  # 敌对派系
        
        # 派系成员
        self.members: Set[str] = set()  # NPC ID列表
        self.leader_id: Optional[str] = None  # 领袖NPC ID
        
        # 派系领土
        self.base_positions: List[Point] = []  # 基地位置
        self.controlled_area: List[Point] = []  # 控制区域
        
        # 派系价值观
        self.values = {
            "lawful": 0,    # 守序性 (-10到10)
            "moral": 0,     # 道德性 (-10到10)
            "strength": 5,  # 重视力量 (0到10)
            "wealth": 5,    # 重视财富 (0到10)
        }
        
        # 玩家关系
        self.player_attitude = 0  # 对玩家的态度 (-100到100)
        self.known_by_player = False  # 是否被玩家知晓
        
        logger.info(f"派系 '{name}' (ID: {faction_id}) 已创建")
    
    def add_member(self, npc_id: str):
        """
        添加成员
        
        Args:
            npc_id: NPC ID
        """
        self.members.add(npc_id)
        self.size = len(self.members)
        logger.debug(f"派系 {self.name}: 添加成员 {npc_id}")
    
    def remove_member(self, npc_id: str):
        """
        移除成员
        
        Args:
            npc_id: NPC ID
        """
        if npc_id in self.members:
            self.members.remove(npc_id)
            self.size = len(self.members)
            if npc_id == self.leader_id:
                self.leader_id = None
            logger.debug(f"派系 {self.name}: 移除成员 {npc_id}")
    
    def set_leader(self, npc_id: str):
        """
        设置领袖
        
        Args:
            npc_id: NPC ID
        """
        if npc_id in self.members:
            self.leader_id = npc_id
            logger.info(f"派系 {self.name}: {npc_id} 成为新领袖")
    
    def adjust_player_attitude(self, amount: int):
        """
        调整对玩家的态度
        
        Args:
            amount: 调整量
        """
        self.player_attitude += amount
        self.player_attitude = max(-100, min(100, self.player_attitude))
        logger.debug(f"派系 {self.name} 对玩家态度: {self.player_attitude}")
    
    def set_relation(self, other_faction_id: str, relation: FactionRelation):
        """
        设置与其他派系的关系
        
        Args:
            other_faction_id: 其他派系ID
            relation: 关系类型
        """
        self.relations[other_faction_id] = relation
        
        # 更新喜欢/不喜欢列表
        if relation in [FactionRelation.ALLY, FactionRelation.PEACE]:
            self.liked_factions.add(other_faction_id)
            self.disliked_factions.discard(other_faction_id)
        elif relation in [FactionRelation.ENEMY, FactionRelation.WAR]:
            self.disliked_factions.add(other_faction_id)
            self.liked_factions.discard(other_faction_id)
        else:
            self.liked_factions.discard(other_faction_id)
            self.disliked_factions.discard(other_faction_id)
        
        logger.info(f"派系 {self.name} 与 {other_faction_id} 关系设为: {relation.value}")
    
    def get_relation(self, other_faction_id: str) -> FactionRelation:
        """
        获取与其他派系的关系
        
        Args:
            other_faction_id: 其他派系ID
            
        Returns:
            关系类型
        """
        return self.relations.get(other_faction_id, FactionRelation.NEUTRAL)
    
    def is_ally(self, other_faction_id: str) -> bool:
        """检查是否为盟友"""
        return self.get_relation(other_faction_id) == FactionRelation.ALLY
    
    def is_enemy(self, other_faction_id: str) -> bool:
        """检查是否为敌人"""
        relation = self.get_relation(other_faction_id)
        return relation in [FactionRelation.ENEMY, FactionRelation.WAR]
    
    def add_base(self, position: Point):
        """
        添加基地位置
        
        Args:
            position: 位置
        """
        self.base_positions.append(position)
        logger.info(f"派系 {self.name} 在 {position} 建立基地")
    
    def adjust_wealth(self, amount: int):
        """
        调整财富
        
        Args:
            amount: 调整量
        """
        self.wealth += amount
        self.wealth = max(0, self.wealth)
        logger.debug(f"派系 {self.name} 财富: {self.wealth}")
    
    def adjust_respect(self, amount: int):
        """
        调整声望
        
        Args:
            amount: 调整量
        """
        self.respect += amount
        self.respect = max(-100, min(100, self.respect))
        logger.debug(f"派系 {self.name} 声望: {self.respect}")
    
    def update_power(self):
        """根据成员数量更新影响力级别"""
        if self.size < 10:
            self.power = FactionPower.TINY
        elif self.size < 50:
            self.power = FactionPower.SMALL
        elif self.size < 200:
            self.power = FactionPower.MEDIUM
        elif self.size < 500:
            self.power = FactionPower.LARGE
        else:
            self.power = FactionPower.HUGE
    
    def to_dict(self) -> dict:
        """
        序列化为字典
        
        Returns:
            字典数据
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "power": self.power.value,
            "wealth": self.wealth,
            "size": self.size,
            "respect": self.respect,
            "relations": {k: v.value for k, v in self.relations.items()},
            "members": list(self.members),
            "leader_id": self.leader_id,
            "base_positions": [[p.x, p.y] for p in self.base_positions],
            "values": self.values,
            "player_attitude": self.player_attitude,
            "known_by_player": self.known_by_player,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Faction":
        """
        从字典反序列化
        
        Args:
            data: 字典数据
            
        Returns:
            Faction实例
        """
        faction = cls(data["id"], data["name"])
        faction.description = data.get("description", "")
        faction.power = FactionPower(data.get("power", 2))
        faction.wealth = data.get("wealth", 0)
        faction.size = data.get("size", 10)
        faction.respect = data.get("respect", 0)
        
        # 恢复关系
        for faction_id, relation_str in data.get("relations", {}).items():
            faction.relations[faction_id] = FactionRelation(relation_str)
        
        faction.members = set(data.get("members", []))
        faction.leader_id = data.get("leader_id")
        
        # 恢复基地位置
        for pos in data.get("base_positions", []):
            faction.base_positions.append(Point(pos[0], pos[1]))
        
        faction.values = data.get("values", faction.values)
        faction.player_attitude = data.get("player_attitude", 0)
        faction.known_by_player = data.get("known_by_player", False)
        
        return faction


class FactionManager:
    """派系管理器"""
    
    def __init__(self):
        """初始化派系管理器"""
        self.factions: Dict[str, Faction] = {}  # 所有派系
        self.player_faction_id: Optional[str] = None  # 玩家所属派系
        
        logger.info("派系管理器已初始化")
    
    def create_faction(self, faction_id: str, name: str) -> Faction:
        """
        创建新派系
        
        Args:
            faction_id: 派系ID
            name: 派系名称
            
        Returns:
            新创建的派系
        """
        if faction_id in self.factions:
            logger.warning(f"派系 {faction_id} 已存在")
            return self.factions[faction_id]
        
        faction = Faction(faction_id, name)
        self.factions[faction_id] = faction
        return faction
    
    def get_faction(self, faction_id: str) -> Optional[Faction]:
        """
        获取派系
        
        Args:
            faction_id: 派系ID
            
        Returns:
            派系实例，如果不存在则返回None
        """
        return self.factions.get(faction_id)
    
    def remove_faction(self, faction_id: str):
        """
        移除派系
        
        Args:
            faction_id: 派系ID
        """
        if faction_id in self.factions:
            del self.factions[faction_id]
            logger.info(f"派系 {faction_id} 已移除")
    
    def get_all_factions(self) -> List[Faction]:
        """
        获取所有派系
        
        Returns:
            派系列表
        """
        return list(self.factions.values())
    
    def get_player_faction(self) -> Optional[Faction]:
        """
        获取玩家所属派系
        
        Returns:
            玩家派系，如果没有则返回None
        """
        if self.player_faction_id:
            return self.get_faction(self.player_faction_id)
        return None
    
    def set_player_faction(self, faction_id: str):
        """
        设置玩家所属派系
        
        Args:
            faction_id: 派系ID
        """
        if faction_id in self.factions:
            self.player_faction_id = faction_id
            logger.info(f"玩家加入派系: {faction_id}")
    
    def get_relations(self, faction_id1: str, faction_id2: str) -> FactionRelation:
        """
        获取两个派系之间的关系
        
        Args:
            faction_id1: 派系1 ID
            faction_id2: 派系2 ID
            
        Returns:
            关系类型
        """
        faction1 = self.get_faction(faction_id1)
        if faction1:
            return faction1.get_relation(faction_id2)
        return FactionRelation.NEUTRAL
    
    def set_relations(self, faction_id1: str, faction_id2: str, relation: FactionRelation):
        """
        设置两个派系之间的关系（双向）
        
        Args:
            faction_id1: 派系1 ID
            faction_id2: 派系2 ID
            relation: 关系类型
        """
        faction1 = self.get_faction(faction_id1)
        faction2 = self.get_faction(faction_id2)
        
        if faction1:
            faction1.set_relation(faction_id2, relation)
        if faction2:
            faction2.set_relation(faction_id1, relation)
    
    def load_faction_definitions(self, filepath: str):
        """
        从JSON文件加载派系定义
        
        Args:
            filepath: JSON文件路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for faction_data in data.get("factions", []):
                faction_id = faction_data["id"]
                name = faction_data["name"]
                
                faction = self.create_faction(faction_id, name)
                faction.description = faction_data.get("description", "")
                faction.values = faction_data.get("values", faction.values)
                
                # 加载初始关系
                for other_id, relation_str in faction_data.get("relations", {}).items():
                    faction.set_relation(other_id, FactionRelation(relation_str))
            
            logger.info(f"从 {filepath} 加载了 {len(data.get('factions', []))} 个派系定义")
        
        except FileNotFoundError:
            logger.warning(f"派系定义文件未找到: {filepath}")
        except Exception as e:
            logger.error(f"加载派系定义时出错: {e}")
    
    def to_dict(self) -> dict:
        """
        序列化为字典
        
        Returns:
            字典数据
        """
        return {
            "factions": {faction_id: faction.to_dict() 
                        for faction_id, faction in self.factions.items()},
            "player_faction_id": self.player_faction_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FactionManager":
        """
        从字典反序列化
        
        Args:
            data: 字典数据
            
        Returns:
            FactionManager实例
        """
        manager = cls()
        
        # 恢复所有派系
        for faction_id, faction_data in data.get("factions", {}).items():
            manager.factions[faction_id] = Faction.from_dict(faction_data)
        
        manager.player_faction_id = data.get("player_faction_id")
        
        return manager
