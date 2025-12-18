"""
AI系统 - 寻路算法

实现多种寻路算法，包括A*、Dijkstra等
"""

import heapq
from typing import List, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field

from ..utils.point import Tripoint
from ..utils.logger import logger
from ..world.map import Map


@dataclass(order=True)
class PathNode:
    """路径节点"""
    
    priority: float
    position: Tripoint = field(compare=False)
    g_score: float = field(compare=False, default=0.0)
    parent: Optional[Tripoint] = field(compare=False, default=None)


class Pathfinding:
    """寻路系统"""
    
    def __init__(self, game_map: Map):
        """
        初始化寻路系统
        
        Args:
            game_map: 游戏地图
        """
        self.game_map = game_map
        logger.info("寻路系统已初始化")
    
    def heuristic(self, start: Tripoint, goal: Tripoint) -> float:
        """
        启发函数 - 曼哈顿距离
        
        Args:
            start: 起点
            goal: 终点
            
        Returns:
            估计距离
        """
        return abs(start.x - goal.x) + abs(start.y - goal.y) + abs(start.z - goal.z)
    
    def get_neighbors(self, pos: Tripoint, 
                     passability_func: Optional[Callable[[Tripoint], bool]] = None) -> List[Tripoint]:
        """
        获取相邻可通行的位置
        
        Args:
            pos: 当前位置
            passability_func: 自定义可通行性判断函数
            
        Returns:
            相邻位置列表
        """
        neighbors = []
        # 8个方向 + 上下
        directions = [
            (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0),  # 东西南北
            (1, 1, 0), (-1, 1, 0), (1, -1, 0), (-1, -1, 0),  # 对角线
            (0, 0, 1), (0, 0, -1)  # 上下
        ]
        
        for dx, dy, dz in directions:
            neighbor = Tripoint(pos.x + dx, pos.y + dy, pos.z + dz)
            
            # 使用自定义判断函数或默认地图可通行性检查
            if passability_func:
                if passability_func(neighbor):
                    neighbors.append(neighbor)
            else:
                # 默认检查地形可通行性
                tile = self.game_map.get_tile(neighbor)
                if tile and self.game_map.is_passable(neighbor):
                    neighbors.append(neighbor)
        
        return neighbors
    
    def get_movement_cost(self, from_pos: Tripoint, to_pos: Tripoint) -> float:
        """
        获取从一个位置移动到另一个位置的成本
        
        Args:
            from_pos: 起点
            to_pos: 终点
            
        Returns:
            移动成本
        """
        tile = self.game_map.get_tile(to_pos)
        if not tile:
            return float('inf')
        
        # 基础成本
        cost = 1.0
        
        # 地形成本
        from ..world.terrain import terrain_manager
        terrain = terrain_manager.get_terrain(tile.terrain_id)
        if terrain:
            if terrain.move_cost == 0:
                return float('inf')
            cost *= terrain.move_cost
        
        # 家具成本
        if tile.furniture_id:
            from ..world.furniture import furniture_manager
            furniture = furniture_manager.get_furniture(tile.furniture_id)
            if furniture:
                if furniture.move_cost == 0:
                    return float('inf')
                cost *= furniture.move_cost
        
        # 对角线移动成本更高（约1.414倍）
        if abs(from_pos.x - to_pos.x) + abs(from_pos.y - to_pos.y) == 2:
            cost *= 1.414
        
        # Z层移动成本
        if from_pos.z != to_pos.z:
            cost *= 2.0
        
        return cost
    
    def find_path_astar(self, start: Tripoint, goal: Tripoint,
                       max_distance: Optional[int] = None,
                       passability_func: Optional[Callable[[Tripoint], bool]] = None) -> Optional[List[Tripoint]]:
        """
        A*寻路算法
        
        Args:
            start: 起点
            goal: 终点
            max_distance: 最大搜索距离（None表示无限制）
            passability_func: 自定义可通行性判断函数
            
        Returns:
            路径（包含起点和终点），如果找不到返回None
        """
        if start == goal:
            return [start]
        
        # 优先队列
        open_set = []
        heapq.heappush(open_set, PathNode(priority=0.0, position=start, g_score=0.0))
        
        # 记录已访问的节点
        came_from = {}
        g_score = {start: 0.0}
        f_score = {start: self.heuristic(start, goal)}
        
        # 已访问集合
        closed_set: Set[Tripoint] = set()
        
        while open_set:
            current_node = heapq.heappop(open_set)
            current = current_node.position
            
            # 找到目标
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                logger.debug(f"找到路径，长度: {len(path)}")
                return path
            
            # 已访问
            if current in closed_set:
                continue
            closed_set.add(current)
            
            # 检查最大距离限制
            if max_distance and len(closed_set) > max_distance * max_distance:
                logger.debug(f"超过最大搜索距离: {max_distance}")
                return None
            
            # 遍历相邻节点
            for neighbor in self.get_neighbors(current, passability_func):
                if neighbor in closed_set:
                    continue
                
                # 计算新的g分数
                tentative_g_score = g_score[current] + self.get_movement_cost(current, neighbor)
                
                # 如果找到更好的路径
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f = tentative_g_score + self.heuristic(neighbor, goal)
                    f_score[neighbor] = f
                    heapq.heappush(open_set, PathNode(priority=f, position=neighbor, g_score=tentative_g_score))
        
        logger.debug(f"找不到从 {start} 到 {goal} 的路径")
        return None
    
    def find_path_dijkstra(self, start: Tripoint, goal: Tripoint,
                          max_distance: Optional[int] = None) -> Optional[List[Tripoint]]:
        """
        Dijkstra寻路算法（不使用启发函数）
        
        Args:
            start: 起点
            goal: 终点
            max_distance: 最大搜索距离
            
        Returns:
            路径（包含起点和终点），如果找不到返回None
        """
        if start == goal:
            return [start]
        
        # 优先队列
        open_set = []
        heapq.heappush(open_set, PathNode(priority=0.0, position=start, g_score=0.0))
        
        came_from = {}
        g_score = {start: 0.0}
        closed_set: Set[Tripoint] = set()
        
        while open_set:
            current_node = heapq.heappop(open_set)
            current = current_node.position
            
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path
            
            if current in closed_set:
                continue
            closed_set.add(current)
            
            if max_distance and len(closed_set) > max_distance * max_distance:
                return None
            
            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                tentative_g_score = g_score[current] + self.get_movement_cost(current, neighbor)
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    heapq.heappush(open_set, PathNode(priority=tentative_g_score, position=neighbor, 
                                                     g_score=tentative_g_score))
        
        return None
    
    def find_path_to_any(self, start: Tripoint, goals: List[Tripoint],
                        max_distance: Optional[int] = None) -> Optional[Tuple[Tripoint, List[Tripoint]]]:
        """
        寻找到任意一个目标的路径（返回最近的目标）
        
        Args:
            start: 起点
            goals: 目标列表
            max_distance: 最大搜索距离
            
        Returns:
            (目标位置, 路径)，如果找不到返回None
        """
        if not goals:
            return None
        
        # 优先队列
        open_set = []
        heapq.heappush(open_set, PathNode(priority=0.0, position=start, g_score=0.0))
        
        came_from = {}
        g_score = {start: 0.0}
        closed_set: Set[Tripoint] = set()
        goal_set = set(goals)
        
        while open_set:
            current_node = heapq.heappop(open_set)
            current = current_node.position
            
            # 找到任意目标
            if current in goal_set:
                path = []
                target = current
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return (target, path)
            
            if current in closed_set:
                continue
            closed_set.add(current)
            
            if max_distance and len(closed_set) > max_distance * max_distance:
                return None
            
            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                tentative_g_score = g_score[current] + self.get_movement_cost(current, neighbor)
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    # 使用到最近目标的启发距离
                    min_h = min(self.heuristic(neighbor, goal) for goal in goals)
                    f = tentative_g_score + min_h
                    heapq.heappush(open_set, PathNode(priority=f, position=neighbor, g_score=tentative_g_score))
        
        return None
    
    def get_reachable_area(self, start: Tripoint, max_cost: float) -> Set[Tripoint]:
        """
        获取在指定成本内可到达的所有位置
        
        Args:
            start: 起点
            max_cost: 最大移动成本
            
        Returns:
            可到达位置的集合
        """
        reachable = {start}
        open_set = []
        heapq.heappush(open_set, PathNode(priority=0.0, position=start, g_score=0.0))
        g_score = {start: 0.0}
        
        while open_set:
            current_node = heapq.heappop(open_set)
            current = current_node.position
            current_cost = current_node.g_score
            
            if current_cost > max_cost:
                continue
            
            for neighbor in self.get_neighbors(current):
                move_cost = self.get_movement_cost(current, neighbor)
                new_cost = current_cost + move_cost
                
                if new_cost <= max_cost and (neighbor not in g_score or new_cost < g_score[neighbor]):
                    g_score[neighbor] = new_cost
                    reachable.add(neighbor)
                    heapq.heappush(open_set, PathNode(priority=new_cost, position=neighbor, g_score=new_cost))
        
        return reachable
