"""
AI系统 - NPC AI

实现NPC的智能行为和决策
"""

from typing import Optional, List
from enum import Enum

from ..utils.point import Tripoint
from ..utils.logger import logger
from ..entities.npc import NPC
from ..entities.player import Player
from ..entities.monster import Monster
from ..world.map import Map
from .pathfinding import Pathfinding


class NPCGoal(Enum):
    """NPC目标类型"""
    IDLE = "idle"  # 空闲
    FOLLOW_PLAYER = "follow_player"  # 跟随玩家
    GUARD_POSITION = "guard_position"  # 守卫位置
    FLEE = "flee"  # 逃跑
    ATTACK = "attack"  # 攻击
    WANDER = "wander"  # 徘徊
    SEARCH_ITEMS = "search_items"  # 搜索物品


class NPCAI:
    """NPC AI系统"""
    
    def __init__(self, game_map: Map):
        """
        初始化NPC AI系统
        
        Args:
            game_map: 游戏地图
        """
        self.game_map = game_map
        self.pathfinding = Pathfinding(game_map)
        logger.info("NPC AI系统已初始化")
    
    def decide_goal(self, npc: NPC, player: Optional[Player] = None, 
                   nearby_monsters: Optional[List[Monster]] = None) -> NPCGoal:
        """
        决定NPC的当前目标
        
        Args:
            npc: NPC实例
            player: 玩家（如果存在）
            nearby_monsters: 附近的怪物列表
            
        Returns:
            NPC目标
        """
        # 如果AI被禁用，保持空闲
        if not npc.ai_enabled:
            return NPCGoal.IDLE
        
        # 如果生命值过低，逃跑
        if npc.hp < npc.max_hp * 0.3:
            logger.debug(f"{npc.name} 生命值过低，决定逃跑")
            return NPCGoal.FLEE
        
        # 如果有附近的敌对怪物且NPC是战斗型
        if nearby_monsters and npc.personality == "aggressive":
            logger.debug(f"{npc.name} 发现敌对目标，决定攻击")
            return NPCGoal.ATTACK
        
        # 如果设置为跟随玩家
        if npc.follow_player and player:
            logger.debug(f"{npc.name} 跟随玩家")
            return NPCGoal.FOLLOW_PLAYER
        
        # 如果有守卫位置
        if npc.guard_position:
            logger.debug(f"{npc.name} 守卫位置")
            return NPCGoal.GUARD_POSITION
        
        # 如果性格是友好的，且有玩家，倾向于跟随
        if npc.personality == "friendly" and player and npc.attitude > 20:
            return NPCGoal.FOLLOW_PLAYER
        
        # 默认徘徊
        return NPCGoal.WANDER
    
    def execute_goal(self, npc: NPC, goal: NPCGoal, 
                    player: Optional[Player] = None,
                    target: Optional[Tripoint] = None) -> Optional[Tripoint]:
        """
        执行NPC的目标
        
        Args:
            npc: NPC实例
            goal: NPC目标
            player: 玩家（如果存在）
            target: 目标位置（用于某些目标）
            
        Returns:
            下一个移动位置，如果不需要移动返回None
        """
        if goal == NPCGoal.IDLE:
            return None
        
        elif goal == NPCGoal.FOLLOW_PLAYER:
            if player and player.position:
                return self._follow_target(npc, player.position)
        
        elif goal == NPCGoal.GUARD_POSITION:
            if npc.guard_position:
                return self._move_to_position(npc, npc.guard_position)
        
        elif goal == NPCGoal.FLEE:
            return self._flee(npc, target)
        
        elif goal == NPCGoal.ATTACK:
            if target:
                return self._approach_target(npc, target)
        
        elif goal == NPCGoal.WANDER:
            return self._wander(npc)
        
        elif goal == NPCGoal.SEARCH_ITEMS:
            # 简化实现：随机移动寻找物品
            return self._wander(npc)
        
        return None
    
    def _follow_target(self, npc: NPC, target_pos: Tripoint, 
                      follow_distance: int = 2) -> Optional[Tripoint]:
        """
        跟随目标位置
        
        Args:
            npc: NPC实例
            target_pos: 目标位置
            follow_distance: 跟随距离
            
        Returns:
            下一个移动位置
        """
        if not npc.position:
            return None
        
        # 计算当前距离
        distance = self._manhattan_distance(npc.position, target_pos)
        
        # 如果太远，靠近
        if distance > follow_distance + 3:
            path = self.pathfinding.find_path_astar(npc.position, target_pos, max_distance=50)
            if path and len(path) > 1:
                logger.debug(f"{npc.name} 跟随目标，移动到 {path[1]}")
                return path[1]
        
        # 如果太近，保持距离
        elif distance < follow_distance:
            # 向远离目标的方向移动
            return self._move_away_from(npc, target_pos)
        
        # 距离适中，不移动
        return None
    
    def _move_to_position(self, npc: NPC, target_pos: Tripoint) -> Optional[Tripoint]:
        """
        移动到指定位置
        
        Args:
            npc: NPC实例
            target_pos: 目标位置
            
        Returns:
            下一个移动位置
        """
        if not npc.position:
            return None
        
        # 如果已经在目标位置
        if npc.position == target_pos:
            return None
        
        # 寻找路径
        path = self.pathfinding.find_path_astar(npc.position, target_pos, max_distance=100)
        if path and len(path) > 1:
            logger.debug(f"{npc.name} 移动到守卫位置 {path[1]}")
            return path[1]
        
        return None
    
    def _approach_target(self, npc: NPC, target_pos: Tripoint, 
                        attack_range: int = 1) -> Optional[Tripoint]:
        """
        接近目标以进行攻击
        
        Args:
            npc: NPC实例
            target_pos: 目标位置
            attack_range: 攻击距离
            
        Returns:
            下一个移动位置
        """
        if not npc.position:
            return None
        
        distance = self._manhattan_distance(npc.position, target_pos)
        
        # 如果在攻击范围内，不移动
        if distance <= attack_range:
            logger.debug(f"{npc.name} 在攻击范围内")
            return None
        
        # 接近目标
        path = self.pathfinding.find_path_astar(npc.position, target_pos, max_distance=30)
        if path and len(path) > 1:
            logger.debug(f"{npc.name} 接近目标 {path[1]}")
            return path[1]
        
        return None
    
    def _flee(self, npc: NPC, threat_pos: Optional[Tripoint]) -> Optional[Tripoint]:
        """
        逃离威胁
        
        Args:
            npc: NPC实例
            threat_pos: 威胁位置
            
        Returns:
            下一个移动位置
        """
        if not npc.position:
            return None
        
        if threat_pos:
            # 向远离威胁的方向移动
            return self._move_away_from(npc, threat_pos)
        else:
            # 随机逃跑
            return self._wander(npc)
    
    def _wander(self, npc: NPC) -> Optional[Tripoint]:
        """
        随机徘徊
        
        Args:
            npc: NPC实例
            
        Returns:
            下一个移动位置
        """
        if not npc.position:
            return None
        
        import random
        
        # 获取相邻可通行位置
        neighbors = self.pathfinding.get_neighbors(npc.position)
        if neighbors:
            next_pos = random.choice(neighbors)
            logger.debug(f"{npc.name} 徘徊到 {next_pos}")
            return next_pos
        
        return None
    
    def _move_away_from(self, npc: NPC, threat_pos: Tripoint) -> Optional[Tripoint]:
        """
        远离指定位置
        
        Args:
            npc: NPC实例
            threat_pos: 威胁位置
            
        Returns:
            下一个移动位置
        """
        if not npc.position:
            return None
        
        # 获取相邻位置
        neighbors = self.pathfinding.get_neighbors(npc.position)
        if not neighbors:
            return None
        
        # 选择距离威胁最远的位置
        best_pos = None
        best_distance = -1
        
        for neighbor in neighbors:
            distance = self._manhattan_distance(neighbor, threat_pos)
            if distance > best_distance:
                best_distance = distance
                best_pos = neighbor
        
        if best_pos:
            logger.debug(f"{npc.name} 远离威胁，移动到 {best_pos}")
        
        return best_pos
    
    def _manhattan_distance(self, pos1: Tripoint, pos2: Tripoint) -> int:
        """
        计算曼哈顿距离
        
        Args:
            pos1: 位置1
            pos2: 位置2
            
        Returns:
            曼哈顿距离
        """
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y) + abs(pos1.z - pos2.z)
    
    def update_npc(self, npc: NPC, player: Optional[Player] = None,
                  nearby_monsters: Optional[List[Monster]] = None) -> Optional[Tripoint]:
        """
        更新NPC的AI（每回合调用）
        
        Args:
            npc: NPC实例
            player: 玩家
            nearby_monsters: 附近的怪物列表
            
        Returns:
            下一个移动位置，如果不需要移动返回None
        """
        # 决定目标
        goal = self.decide_goal(npc, player, nearby_monsters)
        
        # 确定目标位置
        target = None
        if nearby_monsters:
            # 选择最近的怪物作为目标
            if npc.position:
                closest_monster = min(nearby_monsters, 
                                    key=lambda m: self._manhattan_distance(npc.position, m.position))
                target = closest_monster.position
        
        # 执行目标
        next_pos = self.execute_goal(npc, goal, player, target)
        
        return next_pos
    
    def set_follow_player(self, npc: NPC, follow: bool):
        """
        设置NPC是否跟随玩家
        
        Args:
            npc: NPC实例
            follow: 是否跟随
        """
        npc.follow_player = follow
        logger.info(f"{npc.name} 跟随玩家: {follow}")
    
    def set_guard_position(self, npc: NPC, position: Optional[Tripoint]):
        """
        设置NPC守卫位置
        
        Args:
            npc: NPC实例
            position: 守卫位置（None表示取消守卫）
        """
        npc.guard_position = position
        if position:
            logger.info(f"{npc.name} 开始守卫位置: {position}")
        else:
            logger.info(f"{npc.name} 取消守卫位置")
    
    def enable_ai(self, npc: NPC, enabled: bool):
        """
        启用或禁用NPC的AI
        
        Args:
            npc: NPC实例
            enabled: 是否启用
        """
        npc.ai_enabled = enabled
        logger.info(f"{npc.name} AI {'启用' if enabled else '禁用'}")
