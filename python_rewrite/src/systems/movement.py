"""
游戏机制系统 - 移动系统

处理角色移动和位置变化
"""

from typing import Optional

from ..utils.point import Point, Tripoint
from ..utils.logger import logger
from ..entities.character import Character
from ..world.map import Map
from ..world.terrain import terrain_manager
from ..world.furniture import furniture_manager


class MovementSystem:
    """移动系统"""

    def __init__(self, game_map: Map):
        """
        初始化移动系统

        Args:
            game_map: 游戏地图
        """
        self.game_map = game_map
        logger.info("移动系统已初始化")

    def can_move_to(self, character: Character, target_pos: Tripoint) -> bool:
        """
        检查是否可以移动到目标位置

        Args:
            character: 角色
            target_pos: 目标位置

        Returns:
            是否可以移动
        """
        # 获取目标位置的格子
        tile = self.game_map.get_tile(target_pos)
        if not tile:
            return False

        # 检查地形移动成本
        terrain = terrain_manager.get_terrain(tile.terrain_id)
        if terrain and terrain.move_cost == 0:
            logger.debug(f"{character.name} 无法移动到 {target_pos}：地形不可通行")
            return False

        # 检查是否有家具阻挡
        if tile.furniture_id:
            furniture = furniture_manager.get_furniture(tile.furniture_id)
            if furniture and furniture.move_cost == 0:
                logger.debug(f"{character.name} 无法移动到 {target_pos}：家具阻挡")
                return False

        # TODO: 检查是否有其他角色占据
        # TODO: 检查是否有怪物占据

        return True

    def get_move_cost(self, character: Character, target_pos: Tripoint) -> int:
        """
        获取移动到目标位置的行动点花费

        Args:
            character: 角色
            target_pos: 目标位置

        Returns:
            行动点花费
        """
        tile = self.game_map.get_tile(target_pos)
        if not tile:
            return 100

        move_cost = 100  # 默认花费

        # 获取地形移动成本
        terrain = terrain_manager.get_terrain(tile.terrain_id)
        if terrain:
            move_cost = terrain.move_cost

        # 如果有家具，使用家具的移动成本（如果更高）
        if tile.furniture_id:
            furniture = furniture_manager.get_furniture(tile.furniture_id)
            if furniture and furniture.move_cost > 0:
                move_cost = max(move_cost, furniture.move_cost)

        return move_cost

    def move_character(self, character: Character, direction: Point) -> bool:
        """
        移动角色

        Args:
            character: 角色
            direction: 移动方向

        Returns:
            是否成功移动
        """
        # 计算新位置
        new_pos = Tripoint(
            character.position.x + direction.x,
            character.position.y + direction.y,
            character.position.z
        )

        # 检查是否可以移动
        if not self.can_move_to(character, new_pos):
            return False

        # 获取移动成本
        move_cost = self.get_move_cost(character, new_pos)

        # 检查是否有足够的行动点
        if character.moves < move_cost:
            logger.debug(f"{character.name} 行动点不足，无法移动")
            return False

        # 执行移动
        old_pos = character.position
        character.move_to(new_pos)

        # 扣除行动点
        character.moves -= move_cost

        logger.debug(f"{character.name} 从 {old_pos} 移动到 {new_pos}，花费 {move_cost} 行动点")

        return True

    def move_character_to(self, character: Character, target_pos: Tripoint) -> bool:
        """
        直接移动角色到目标位置（不检查路径）

        Args:
            character: 角色
            target_pos: 目标位置

        Returns:
            是否成功移动
        """
        if self.can_move_to(character, target_pos):
            character.move_to(target_pos)
            logger.info(f"{character.name} 移动到 {target_pos}")
            return True
        return False

    def calculate_path(self, start: Tripoint, end: Tripoint) -> list:
        """
        计算从起点到终点的路径（简单实现）

        Args:
            start: 起点
            end: 终点

        Returns:
            路径点列表
        """
        # TODO: 实现A*寻路算法
        # 当前仅返回直线路径
        path = []

        current = start
        while current != end:
            # 计算方向
            dx = 0 if current.x == end.x else (1 if end.x > current.x else -1)
            dy = 0 if current.y == end.y else (1 if end.y > current.y else -1)

            # 移动一步
            current = Tripoint(current.x + dx, current.y + dy, current.z)
            path.append(current)

        return path
