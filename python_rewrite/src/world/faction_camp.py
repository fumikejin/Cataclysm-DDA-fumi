"""
游戏世界 - 派系营地

派系营地管理和资源系统
"""

from typing import Dict, List, Optional
from enum import Enum

from ..utils.logger import logger
from ..utils.point import Point


class CampResource(Enum):
    """营地资源类型"""
    FOOD = "food"                # 食物
    WATER = "water"              # 水
    WOOD = "wood"                # 木材
    METAL = "metal"              # 金属
    MEDICINE = "medicine"        # 药品
    AMMUNITION = "ammunition"    # 弹药
    FUEL = "fuel"                # 燃料
    TOOLS = "tools"              # 工具


class CampBuilding(Enum):
    """营地建筑类型"""
    TENT = "tent"                    # 帐篷
    WOODEN_WALL = "wooden_wall"      # 木墙
    WATCHTOWER = "watchtower"        # 瞭望塔
    WORKSHOP = "workshop"            # 工作间
    STORAGE = "storage"              # 仓库
    FARM = "farm"                    # 农场
    WELL = "well"                    # 水井
    KITCHEN = "kitchen"              # 厨房
    INFIRMARY = "infirmary"          # 医务室


class CampMission:
    """营地任务"""
    
    def __init__(self, mission_id: str, name: str, mission_type: str):
        """
        初始化营地任务
        
        Args:
            mission_id: 任务ID
            name: 任务名称
            mission_type: 任务类型
        """
        self.id = mission_id
        self.name = name
        self.type = mission_type  # "gather", "build", "recruit", "scout", "trade"
        self.description = ""
        
        # 任务要求
        self.required_resources: Dict[str, int] = {}  # 所需资源
        self.required_time = 1  # 所需时间（天数）
        self.required_workers = 1  # 所需工人数量
        
        # 任务奖励
        self.reward_resources: Dict[str, int] = {}  # 奖励资源
        self.reward_reputation = 0  # 奖励声望
        
        # 任务状态
        self.in_progress = False  # 是否进行中
        self.progress = 0.0  # 进度（0.0-1.0）
        self.assigned_workers = 0  # 已分配工人数量
    
    def start(self, workers: int) -> bool:
        """
        开始任务
        
        Args:
            workers: 分配的工人数量
            
        Returns:
            是否成功开始
        """
        if self.in_progress:
            logger.warning(f"营地任务 {self.name} 已在进行中")
            return False
        
        if workers < self.required_workers:
            logger.warning(f"营地任务 {self.name} 需要 {self.required_workers} 个工人")
            return False
        
        self.in_progress = True
        self.assigned_workers = workers
        self.progress = 0.0
        logger.info(f"营地任务 {self.name} 已开始，分配工人: {workers}")
        return True
    
    def update(self, time_passed: float):
        """
        更新任务进度
        
        Args:
            time_passed: 经过的时间（天数）
        """
        if not self.in_progress:
            return
        
        # 根据工人数量和时间更新进度
        progress_per_day = 1.0 / self.required_time
        self.progress += progress_per_day * time_passed
        
        # 检查是否完成
        if self.progress >= 1.0:
            self.complete()
    
    def complete(self):
        """完成任务"""
        self.in_progress = False
        self.progress = 1.0
        logger.info(f"营地任务 {self.name} 已完成")
    
    def cancel(self):
        """取消任务"""
        self.in_progress = False
        self.progress = 0.0
        self.assigned_workers = 0
        logger.info(f"营地任务 {self.name} 已取消")
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "required_resources": self.required_resources,
            "required_time": self.required_time,
            "required_workers": self.required_workers,
            "reward_resources": self.reward_resources,
            "reward_reputation": self.reward_reputation,
            "in_progress": self.in_progress,
            "progress": self.progress,
            "assigned_workers": self.assigned_workers,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CampMission":
        """反序列化"""
        mission = cls(data["id"], data["name"], data["type"])
        mission.description = data.get("description", "")
        mission.required_resources = data.get("required_resources", {})
        mission.required_time = data.get("required_time", 1)
        mission.required_workers = data.get("required_workers", 1)
        mission.reward_resources = data.get("reward_resources", {})
        mission.reward_reputation = data.get("reward_reputation", 0)
        mission.in_progress = data.get("in_progress", False)
        mission.progress = data.get("progress", 0.0)
        mission.assigned_workers = data.get("assigned_workers", 0)
        return mission


class FactionCamp:
    """派系营地"""
    
    def __init__(self, camp_id: str, name: str, position: Point, faction_id: str):
        """
        初始化派系营地
        
        Args:
            camp_id: 营地ID
            name: 营地名称
            position: 营地位置
            faction_id: 所属派系ID
        """
        self.id = camp_id
        self.name = name
        self.position = position
        self.faction_id = faction_id
        
        # 营地状态
        self.level = 1  # 营地等级（1-5）
        self.population = 0  # 人口数量
        self.available_workers = 0  # 可用工人数量
        
        # 营地资源
        self.resources: Dict[str, int] = {
            CampResource.FOOD.value: 0,
            CampResource.WATER.value: 0,
            CampResource.WOOD.value: 0,
            CampResource.METAL.value: 0,
            CampResource.MEDICINE.value: 0,
            CampResource.AMMUNITION.value: 0,
            CampResource.FUEL.value: 0,
            CampResource.TOOLS.value: 0,
        }
        
        # 营地建筑
        self.buildings: Dict[str, int] = {}  # 建筑类型 -> 数量
        
        # 营地任务
        self.available_missions: List[CampMission] = []  # 可用任务
        self.active_missions: List[CampMission] = []  # 进行中的任务
        self.completed_missions: List[CampMission] = []  # 已完成的任务
        
        # 营地防御
        self.defense_rating = 0  # 防御等级
        
        logger.info(f"派系营地 '{name}' 在 {position} 创建，归属 {faction_id}")
    
    def add_resource(self, resource_type: str, amount: int):
        """
        添加资源
        
        Args:
            resource_type: 资源类型
            amount: 数量
        """
        if resource_type in self.resources:
            self.resources[resource_type] += amount
            logger.debug(f"营地 {self.name}: 添加 {resource_type} x{amount}")
    
    def remove_resource(self, resource_type: str, amount: int) -> bool:
        """
        移除资源
        
        Args:
            resource_type: 资源类型
            amount: 数量
            
        Returns:
            是否成功移除
        """
        if resource_type not in self.resources:
            return False
        
        if self.resources[resource_type] < amount:
            logger.warning(f"营地 {self.name}: {resource_type} 不足")
            return False
        
        self.resources[resource_type] -= amount
        logger.debug(f"营地 {self.name}: 移除 {resource_type} x{amount}")
        return True
    
    def has_resource(self, resource_type: str, amount: int) -> bool:
        """
        检查是否有足够的资源
        
        Args:
            resource_type: 资源类型
            amount: 数量
            
        Returns:
            是否有足够资源
        """
        return self.resources.get(resource_type, 0) >= amount
    
    def add_building(self, building_type: str):
        """
        添加建筑
        
        Args:
            building_type: 建筑类型
        """
        if building_type not in self.buildings:
            self.buildings[building_type] = 0
        self.buildings[building_type] += 1
        
        # 更新营地状态
        self.update_defense_rating()
        logger.info(f"营地 {self.name}: 建造 {building_type}")
    
    def has_building(self, building_type: str) -> bool:
        """
        检查是否有指定建筑
        
        Args:
            building_type: 建筑类型
            
        Returns:
            是否有该建筑
        """
        return self.buildings.get(building_type, 0) > 0
    
    def update_defense_rating(self):
        """更新防御等级"""
        self.defense_rating = 0
        
        # 根据建筑计算防御
        self.defense_rating += self.buildings.get(CampBuilding.WOODEN_WALL.value, 0) * 5
        self.defense_rating += self.buildings.get(CampBuilding.WATCHTOWER.value, 0) * 10
        
        logger.debug(f"营地 {self.name} 防御等级: {self.defense_rating}")
    
    def add_population(self, amount: int):
        """
        增加人口
        
        Args:
            amount: 增加数量
        """
        self.population += amount
        self.available_workers = int(self.population * 0.7)  # 70%可作为工人
        logger.info(f"营地 {self.name} 人口: {self.population}, 工人: {self.available_workers}")
    
    def start_mission(self, mission: CampMission, workers: int) -> bool:
        """
        开始任务
        
        Args:
            mission: 任务
            workers: 分配的工人数量
            
        Returns:
            是否成功开始
        """
        # 检查资源
        for resource, amount in mission.required_resources.items():
            if not self.has_resource(resource, amount):
                logger.warning(f"营地 {self.name}: 资源不足以开始任务 {mission.name}")
                return False
        
        # 检查工人
        if workers > self.available_workers:
            logger.warning(f"营地 {self.name}: 可用工人不足")
            return False
        
        # 消耗资源
        for resource, amount in mission.required_resources.items():
            self.remove_resource(resource, amount)
        
        # 开始任务
        if mission.start(workers):
            self.active_missions.append(mission)
            self.available_workers -= workers
            return True
        
        return False
    
    def update_missions(self, time_passed: float):
        """
        更新所有任务
        
        Args:
            time_passed: 经过的时间（天数）
        """
        completed = []
        
        for mission in self.active_missions:
            mission.update(time_passed)
            
            if mission.progress >= 1.0:
                # 任务完成，获得奖励
                for resource, amount in mission.reward_resources.items():
                    self.add_resource(resource, amount)
                
                # 释放工人
                self.available_workers += mission.assigned_workers
                
                completed.append(mission)
                self.completed_missions.append(mission)
        
        # 移除已完成的任务
        for mission in completed:
            self.active_missions.remove(mission)
    
    def upgrade_level(self):
        """升级营地"""
        if self.level < 5:
            self.level += 1
            logger.info(f"营地 {self.name} 升级到 {self.level} 级")
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "id": self.id,
            "name": self.name,
            "position": [self.position.x, self.position.y],
            "faction_id": self.faction_id,
            "level": self.level,
            "population": self.population,
            "available_workers": self.available_workers,
            "resources": self.resources,
            "buildings": self.buildings,
            "available_missions": [m.to_dict() for m in self.available_missions],
            "active_missions": [m.to_dict() for m in self.active_missions],
            "completed_missions": [m.to_dict() for m in self.completed_missions],
            "defense_rating": self.defense_rating,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FactionCamp":
        """反序列化"""
        position = Point(data["position"][0], data["position"][1])
        camp = cls(data["id"], data["name"], position, data["faction_id"])
        
        camp.level = data.get("level", 1)
        camp.population = data.get("population", 0)
        camp.available_workers = data.get("available_workers", 0)
        camp.resources = data.get("resources", camp.resources)
        camp.buildings = data.get("buildings", {})
        
        # 恢复任务
        camp.available_missions = [CampMission.from_dict(m) 
                                   for m in data.get("available_missions", [])]
        camp.active_missions = [CampMission.from_dict(m) 
                               for m in data.get("active_missions", [])]
        camp.completed_missions = [CampMission.from_dict(m) 
                                   for m in data.get("completed_missions", [])]
        
        camp.defense_rating = data.get("defense_rating", 0)
        
        return camp


class CampManager:
    """营地管理器"""
    
    def __init__(self):
        """初始化营地管理器"""
        self.camps: Dict[str, FactionCamp] = {}  # 所有营地
        logger.info("营地管理器已初始化")
    
    def create_camp(self, camp_id: str, name: str, position: Point, 
                   faction_id: str) -> FactionCamp:
        """
        创建营地
        
        Args:
            camp_id: 营地ID
            name: 营地名称
            position: 位置
            faction_id: 派系ID
            
        Returns:
            新创建的营地
        """
        if camp_id in self.camps:
            logger.warning(f"营地 {camp_id} 已存在")
            return self.camps[camp_id]
        
        camp = FactionCamp(camp_id, name, position, faction_id)
        self.camps[camp_id] = camp
        return camp
    
    def get_camp(self, camp_id: str) -> Optional[FactionCamp]:
        """
        获取营地
        
        Args:
            camp_id: 营地ID
            
        Returns:
            营地实例
        """
        return self.camps.get(camp_id)
    
    def remove_camp(self, camp_id: str):
        """
        移除营地
        
        Args:
            camp_id: 营地ID
        """
        if camp_id in self.camps:
            del self.camps[camp_id]
            logger.info(f"营地 {camp_id} 已移除")
    
    def get_faction_camps(self, faction_id: str) -> List[FactionCamp]:
        """
        获取指定派系的所有营地
        
        Args:
            faction_id: 派系ID
            
        Returns:
            营地列表
        """
        return [camp for camp in self.camps.values() 
                if camp.faction_id == faction_id]
    
    def update_all_camps(self, time_passed: float):
        """
        更新所有营地
        
        Args:
            time_passed: 经过的时间（天数）
        """
        for camp in self.camps.values():
            camp.update_missions(time_passed)
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "camps": {camp_id: camp.to_dict() 
                     for camp_id, camp in self.camps.items()}
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CampManager":
        """反序列化"""
        manager = cls()
        
        for camp_id, camp_data in data.get("camps", {}).items():
            manager.camps[camp_id] = FactionCamp.from_dict(camp_data)
        
        return manager
