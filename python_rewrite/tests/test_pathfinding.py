"""
测试 - 寻路算法
"""

import pytest
from src.utils.point import Tripoint
from src.world.map import Map
from src.world.terrain import terrain_manager
from src.ai.pathfinding import Pathfinding, PathNode


def test_pathnode_ordering():
    """测试路径节点排序"""
    node1 = PathNode(priority=1.0, position=Tripoint(0, 0, 0))
    node2 = PathNode(priority=2.0, position=Tripoint(1, 1, 0))
    node3 = PathNode(priority=0.5, position=Tripoint(2, 2, 0))
    
    nodes = [node1, node2, node3]
    nodes.sort()
    
    assert nodes[0].priority == 0.5
    assert nodes[1].priority == 1.0
    assert nodes[2].priority == 2.0


def test_pathfinding_init():
    """测试寻路系统初始化"""
    game_map = Map()
    pathfinding = Pathfinding(game_map)
    
    assert pathfinding.game_map == game_map


def test_heuristic():
    """测试启发函数"""
    game_map = Map()
    pathfinding = Pathfinding(game_map)
    
    start = Tripoint(0, 0, 0)
    goal = Tripoint(3, 4, 0)
    
    # 曼哈顿距离应为 3 + 4 = 7
    distance = pathfinding.heuristic(start, goal)
    assert distance == 7


def test_get_neighbors():
    """测试获取相邻位置"""
    game_map = Map()
    # 创建一个简单的地图
    center = Tripoint(5, 5, 0)
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            pos = Tripoint(5 + dx, 5 + dy, 0)
            game_map.get_tile(pos)  # 确保格子存在
    
    pathfinding = Pathfinding(game_map)
    neighbors = pathfinding.get_neighbors(center)
    
    # 应该有8个相邻位置（东西南北+4个对角线）+ 上下2个 = 10个
    # 但由于上下Z层可能没有格子，实际可能少于10个
    assert len(neighbors) >= 8  # 至少有平面8个方向
    assert len(neighbors) <= 10  # 最多10个（包括上下）


def test_find_path_astar_simple():
    """测试A*寻路 - 简单直线"""
    game_map = Map()
    
    # 创建一条直线路径
    start = Tripoint(0, 0, 0)
    goal = Tripoint(5, 0, 0)
    for x in range(6):
        pos = Tripoint(x, 0, 0)
        tile = game_map.get_tile(pos)
        tile.terrain_id = "t_floor"
    
    pathfinding = Pathfinding(game_map)
    path = pathfinding.find_path_astar(start, goal)
    
    assert path is not None
    assert path[0] == start
    assert path[-1] == goal
    assert len(path) == 6  # 0,1,2,3,4,5


def test_find_path_astar_with_obstacle():
    """测试A*寻路 - 有障碍物"""
    game_map = Map()
    
    # 创建一个带障碍的简单地图
    # . . . .
    # S # # G
    # . . . .
    
    for x in range(4):
        for y in range(3):
            pos = Tripoint(x, y, 0)
            tile = game_map.get_tile(pos)
            tile.terrain_id = "t_floor"
    
    # 添加障碍
    game_map.get_tile(Tripoint(1, 1, 0)).terrain_id = "t_wall"
    game_map.get_tile(Tripoint(2, 1, 0)).terrain_id = "t_wall"
    
    start = Tripoint(0, 1, 0)
    goal = Tripoint(3, 1, 0)
    
    pathfinding = Pathfinding(game_map)
    path = pathfinding.find_path_astar(start, goal)
    
    assert path is not None
    assert path[0] == start
    assert path[-1] == goal
    # 路径应该绕过障碍物


def test_find_path_astar_no_path():
    """测试A*寻路 - 无法到达"""
    game_map = Map()
    
    # 创建起点
    start = Tripoint(0, 0, 0)
    game_map.get_tile(start).terrain_id = "t_floor"
    
    # 创建终点（被墙包围）
    goal = Tripoint(5, 5, 0)
    game_map.get_tile(goal).terrain_id = "t_floor"
    
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                pos = Tripoint(5 + dx, 5 + dy, 0)
                tile = game_map.get_tile(pos)
                tile.terrain_id = "t_wall"
    
    pathfinding = Pathfinding(game_map)
    path = pathfinding.find_path_astar(start, goal, max_distance=20)
    
    # 应该找不到路径
    assert path is None


def test_find_path_dijkstra():
    """测试Dijkstra寻路"""
    game_map = Map()
    
    # 创建简单路径
    start = Tripoint(0, 0, 0)
    goal = Tripoint(3, 3, 0)
    
    for x in range(5):
        for y in range(5):
            pos = Tripoint(x, y, 0)
            game_map.get_tile(pos).terrain_id = "t_floor"
    
    pathfinding = Pathfinding(game_map)
    path = pathfinding.find_path_dijkstra(start, goal)
    
    assert path is not None
    assert path[0] == start
    assert path[-1] == goal


def test_find_path_to_any():
    """测试寻找最近的目标"""
    game_map = Map()
    
    # 创建地图
    for x in range(10):
        for y in range(10):
            pos = Tripoint(x, y, 0)
            game_map.get_tile(pos).terrain_id = "t_floor"
    
    start = Tripoint(0, 0, 0)
    goals = [
        Tripoint(2, 2, 0),
        Tripoint(5, 5, 0),
        Tripoint(8, 8, 0)
    ]
    
    pathfinding = Pathfinding(game_map)
    result = pathfinding.find_path_to_any(start, goals)
    
    assert result is not None
    target, path = result
    assert target in goals
    assert path[0] == start
    assert path[-1] == target
    # 应该找到最近的目标
    assert target == Tripoint(2, 2, 0)


def test_get_reachable_area():
    """测试获取可到达区域"""
    game_map = Map()
    
    # 创建一个区域
    for x in range(10):
        for y in range(10):
            pos = Tripoint(x, y, 0)
            game_map.get_tile(pos).terrain_id = "t_floor"
    
    start = Tripoint(5, 5, 0)
    max_cost = 5.0
    
    pathfinding = Pathfinding(game_map)
    reachable = pathfinding.get_reachable_area(start, max_cost)
    
    assert start in reachable
    assert len(reachable) > 1
    # 在成本5.0范围内应该能到达多个位置


def test_get_movement_cost():
    """测试移动成本计算"""
    game_map = Map()
    
    # 创建不同地形成本的格子
    pos1 = Tripoint(0, 0, 0)
    pos2 = Tripoint(1, 0, 0)
    pos3 = Tripoint(1, 1, 0)  # 对角线
    
    game_map.get_tile(pos1).terrain_id = "t_floor"
    game_map.get_tile(pos2).terrain_id = "t_floor"
    game_map.get_tile(pos3).terrain_id = "t_floor"
    
    pathfinding = Pathfinding(game_map)
    
    # 直线移动成本
    cost1 = pathfinding.get_movement_cost(pos1, pos2)
    # 对角线移动成本应该更高
    cost2 = pathfinding.get_movement_cost(pos1, pos3)
    
    assert cost2 > cost1


def test_custom_passability_function():
    """测试自定义可通行性函数"""
    game_map = Map()
    
    # 创建地图
    for x in range(5):
        for y in range(5):
            pos = Tripoint(x, y, 0)
            game_map.get_tile(pos).terrain_id = "t_floor"
    
    # 自定义函数：只允许 x < 3 的位置
    def custom_passable(pos: Tripoint) -> bool:
        return pos.x < 3
    
    center = Tripoint(2, 2, 0)
    pathfinding = Pathfinding(game_map)
    neighbors = pathfinding.get_neighbors(center, custom_passable)
    
    # 所有相邻位置的 x 应该 < 3
    for neighbor in neighbors:
        assert neighbor.x < 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
