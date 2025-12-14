"""
AI系统 - 怪物 AI

实现怪物的智能行为和决策
"""

from typing import Optional, List
from enum import Enum
import random

from ..utils.point import Tripoint
from ..utils.logger import logger
from ..entities.monster import Monster
from ..entities.character import Character
from ..world.map import Map
from .pathfinding import Pathfinding


class MonsterGoal(Enum):
    """怪物目标类型"""
    IDLE = "idle"  # 空闲
    CHASE = "chase"  # 追逐目标
    ATTACK = "attack"  # 攻击
    FLEE = "flee"  # 逃跑
    WANDER = "wander"  # 徘徊
    RETURN_HOME = "return_home"  # 返回家园


class MonsterAI:
    """怪物 AI系统"""
    
    def __init__(self, game_map: Map):
        """
        初始化怪物 AI系统
        
        Args:
            game_map: 游戏地图
        """
        self.game_map = game_map
        self.pathfinding = Pathfinding(game_map)
        logger.info("怪物 AI系统已初始化")
    
    def decide_goal(self, monster: Monster, 
                   nearby_characters: Optional[List[Character]] = None) -> MonsterGoal:
        """
        决定怪物的当前目标
        
        Args:
            monster: 怪物实例
            nearby_characters: 附近的角色列表
            
        Returns:
            怪物目标类型
        """
        # 如果怪物是友好的，空闲或徘徊
        if monster.friendly:
            return MonsterGoal.IDLE
        
        # 检查生命值
        monster_type = monster.get_type()
        if monster_type:
            hp_percent = monster.hp_cur / monster.hp_max
            
            # 生命值过低，考虑逃跑
            if hp_percent < 0.3 and monster_type.morale < 0:
                logger.debug(f"怪物 {monster.get_name()} 生命值低，考虑逃跑")
                return MonsterGoal.FLEE
        
        # 查找最近的目标
        if nearby_characters and len(nearby_characters) > 0:
            # 找到最近的敌对角色
            closest_target = None
            closest_distance = float('inf')
            
            for char in nearby_characters:
                distance = self._calculate_distance(monster.position, char.position)
                
                # 如果在视野范围内
                vision_range = monster_type.vision if monster_type else 10
                if distance <= vision_range:
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_target = char
            
            if closest_target:
                # 如果非常接近，攻击
                if closest_distance <= 1:
                    logger.debug(f"怪物 {monster.get_name()} 准备攻击")
                    return MonsterGoal.ATTACK
                
                # 否则追逐
                logger.debug(f"怪物 {monster.get_name()} 追逐目标，距离: {closest_distance}")
                monster.target_position = closest_target.position
                return MonsterGoal.CHASE
        
        # 如果有愤怒值但没有目标，徘徊寻找目标
        if monster.anger > 0:
            return MonsterGoal.WANDER
        
        # 默认空闲
        return MonsterGoal.IDLE
    
    def execute_goal(self, monster: Monster, goal: MonsterGoal, 
                    nearby_characters: Optional[List[Character]] = None) -> bool:
        """
        执行怪物目标
        
        Args:
            monster: 怪物实例
            goal: 目标类型
            nearby_characters: 附近的角色列表
            
        Returns:
            是否成功执行
        """
        if not monster.get_type():
            return False
        
        if goal == MonsterGoal.IDLE:
            return self._execute_idle(monster)
        elif goal == MonsterGoal.CHASE:
            return self._execute_chase(monster)
        elif goal == MonsterGoal.ATTACK:
            return self._execute_attack(monster, nearby_characters)
        elif goal == MonsterGoal.FLEE:
            return self._execute_flee(monster, nearby_characters)
        elif goal == MonsterGoal.WANDER:
            return self._execute_wander(monster)
        elif goal == MonsterGoal.RETURN_HOME:
            return self._execute_return_home(monster)
        
        return False
    
    def update(self, monster: Monster, 
              nearby_characters: Optional[List[Character]] = None) -> bool:
        """
        更新怪物AI（每回合调用）
        
        Args:
            monster: 怪物实例
            nearby_characters: 附近的角色列表
            
        Returns:
            是否执行了行动
        """
        # 决定目标
        goal = self.decide_goal(monster, nearby_characters)
        
        # 执行目标
        return self.execute_goal(monster, goal, nearby_characters)
    
    def _execute_idle(self, monster: Monster) -> bool:
        """
        执行空闲行为
        
        Args:
            monster: 怪物实例
            
        Returns:
            是否成功
        """
        # 空闲状态，什么也不做
        logger.debug(f"怪物 {monster.get_name()} 空闲")
        return True
    
    def _execute_chase(self, monster: Monster) -> bool:
        """
        执行追逐行为
        
        Args:
            monster: 怪物实例
            
        Returns:
            是否成功移动
        """
        if not monster.target_position:
            return False
        
        # 使用寻路算法找到路径
        path = self.pathfinding.astar(
            monster.position, 
            monster.target_position,
            max_distance=50
        )
        
        if path and len(path) > 1:
            # 移动到路径的下一个位置
            next_pos = path[1]
            
            # 检查是否可以移动
            if self._can_move_to(next_pos):
                logger.debug(f"怪物 {monster.get_name()} 移动到 {next_pos}")
                monster.position = next_pos
                return True
        
        return False
    
    def _execute_attack(self, monster: Monster, 
                       nearby_characters: Optional[List[Character]] = None) -> bool:
        """
        执行攻击行为
        
        Args:
            monster: 怪物实例
            nearby_characters: 附近的角色列表
            
        Returns:
            是否执行了攻击
        """
        if not nearby_characters:
            return False
        
        # 找到相邻的目标
        for char in nearby_characters:
            distance = self._calculate_distance(monster.position, char.position)
            if distance <= 1:
                # 执行攻击
                monster_type = monster.get_type()
                damage = monster_type.melee_damage if monster_type else 5
                
                logger.info(f"怪物 {monster.get_name()} 攻击 {char.name}，造成 {damage} 伤害")
                
                # 实际伤害应该通过战斗系统处理
                # 这里只是标记攻击意图
                return True
        
        return False
    
    def _execute_flee(self, monster: Monster, 
                     nearby_characters: Optional[List[Character]] = None) -> bool:
        """
        执行逃跑行为
        
        Args:
            monster: 怪物实例
            nearby_characters: 附近的角色列表
            
        Returns:
            是否成功逃跑
        """
        if not nearby_characters or len(nearby_characters) == 0:
            return False
        
        # 找到最近的威胁
        closest_threat = min(
            nearby_characters,
            key=lambda c: self._calculate_distance(monster.position, c.position)
        )
        
        # 计算远离威胁的方向
        dx = monster.position.x - closest_threat.position.x
        dy = monster.position.y - closest_threat.position.y
        
        # 归一化方向
        if dx != 0:
            dx = dx // abs(dx)
        if dy != 0:
            dy = dy // abs(dy)
        
        # 尝试向远离威胁的方向移动
        flee_pos = Tripoint(
            monster.position.x + dx * 2,
            monster.position.y + dy * 2,
            monster.position.z
        )
        
        # 使用寻路找到可行路径
        path = self.pathfinding.astar(
            monster.position,
            flee_pos,
            max_distance=10
        )
        
        if path and len(path) > 1:
            next_pos = path[1]
            if self._can_move_to(next_pos):
                logger.debug(f"怪物 {monster.get_name()} 逃跑到 {next_pos}")
                monster.position = next_pos
                return True
        
        return False
    
    def _execute_wander(self, monster: Monster) -> bool:
        """
        执行徘徊行为
        
        Args:
            monster: 怪物实例
            
        Returns:
            是否成功移动
        """
        # 随机选择一个方向
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        
        if dx == 0 and dy == 0:
            return False
        
        new_pos = Tripoint(
            monster.position.x + dx,
            monster.position.y + dy,
            monster.position.z
        )
        
        if self._can_move_to(new_pos):
            logger.debug(f"怪物 {monster.get_name()} 徘徊到 {new_pos}")
            monster.position = new_pos
            return True
        
        return False
    
    def _execute_return_home(self, monster: Monster) -> bool:
        """
        执行返回家园行为
        
        Args:
            monster: 怪物实例
            
        Returns:
            是否成功移动
        """
        # 如果怪物有spawn位置，返回那里
        # 这需要在Monster类中添加spawn_position属性
        # 暂时返回False
        return False
    
    def _can_move_to(self, position: Tripoint) -> bool:
        """
        检查是否可以移动到指定位置
        
        Args:
            position: 目标位置
            
        Returns:
            是否可以移动
        """
        tile = self.game_map.get_tile(position)
        if not tile:
            return False
        
        terrain = tile.get_terrain()
        if not terrain:
            return False
        
        return terrain.passable
    
    def _calculate_distance(self, pos1: Tripoint, pos2: Tripoint) -> float:
        """
        计算两点之间的距离
        
        Args:
            pos1: 位置1
            pos2: 位置2
            
        Returns:
            距离
        """
        dx = pos1.x - pos2.x
        dy = pos1.y - pos2.y
        dz = pos1.z - pos2.z
        return (dx * dx + dy * dy + dz * dz) ** 0.5
