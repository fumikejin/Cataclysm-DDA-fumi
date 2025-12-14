"""
Mission system for CDDA Python rewrite.

任务系统 - 管理游戏中的任务和目标。
"""

from typing import Dict, List, Optional, Callable, Any
from enum import Enum, auto
import json
from pathlib import Path

from ..utils.logger import Logger
from ..utils.point import Tripoint


class MissionType(Enum):
    """任务类型枚举"""
    KILL = auto()           # 击杀目标
    REACH = auto()          # 到达位置
    FIND_ITEM = auto()      # 找到物品
    BRING_ITEM = auto()     # 带来物品
    KILL_MONSTER = auto()   # 击杀特定怪物
    ASSASSINATE = auto()    # 暗杀目标
    RESCUE = auto()         # 救援任务
    EXPLORE = auto()        # 探索区域
    BUILD = auto()          # 建造任务
    ESCORT = auto()         # 护送任务


class MissionStatus(Enum):
    """任务状态枚举"""
    INACTIVE = auto()       # 未激活
    ACTIVE = auto()         # 进行中
    SUCCESS = auto()        # 成功
    FAILURE = auto()        # 失败


class MissionOrigin(Enum):
    """任务来源枚举"""
    NULL = auto()
    NPC = auto()            # NPC给的任务
    GAME_START = auto()     # 游戏开始时的任务
    FACTION = auto()        # 派系任务
    COMPUTER = auto()       # 电脑任务
    RADIO = auto()          # 无线电任务


class Mission:
    """
    任务类 - 表示单个任务实例
    
    Attributes:
        mission_id: 任务实例ID
        type_id: 任务类型ID
        mission_type: 任务类型
        status: 任务状态
        origin: 任务来源
        title: 任务标题
        description: 任务描述
        target_count: 目标数量
        current_count: 当前进度
        target_pos: 目标位置
        target_item_id: 目标物品ID
        target_monster_type: 目标怪物类型
        npc_id: 发布任务的NPC ID
        faction_id: 相关派系ID
        deadline: 截止时间（回合数）
        reward_items: 奖励物品列表
        reward_money: 奖励金钱
        fail_on_npc_death: NPC死亡时任务失败
        on_complete: 完成时回调函数
        on_fail: 失败时回调函数
    """
    
    _next_id = 0
    
    def __init__(self, type_id: str, mission_type: MissionType):
        self.mission_id = Mission._next_id
        Mission._next_id += 1
        
        self.type_id = type_id
        self.mission_type = mission_type
        self.status = MissionStatus.INACTIVE
        self.origin = MissionOrigin.NULL
        
        # 任务信息
        self.title = ""
        self.description = ""
        
        # 目标信息
        self.target_count = 0
        self.current_count = 0
        self.target_pos: Optional[Tripoint] = None
        self.target_item_id: Optional[str] = None
        self.target_monster_type: Optional[str] = None
        
        # 关联信息
        self.npc_id: Optional[int] = None
        self.faction_id: Optional[str] = None
        
        # 时间限制
        self.deadline: Optional[int] = None
        
        # 奖励
        self.reward_items: List[str] = []
        self.reward_money = 0
        
        # 失败条件
        self.fail_on_npc_death = False
        
        # 回调函数
        self.on_complete: Optional[Callable] = None
        self.on_fail: Optional[Callable] = None
        
        self.logger = Logger()
    
    def activate(self):
        """激活任务"""
        if self.status == MissionStatus.INACTIVE:
            self.status = MissionStatus.ACTIVE
            self.logger.info(f"Mission {self.mission_id} '{self.title}' activated")
    
    def update_progress(self, amount: int = 1):
        """
        更新任务进度
        
        Args:
            amount: 增加的进度量
        """
        if self.status != MissionStatus.ACTIVE:
            return
        
        self.current_count += amount
        self.logger.debug(f"Mission {self.mission_id} progress: {self.current_count}/{self.target_count}")
        
        # 检查是否完成
        if self.current_count >= self.target_count:
            self.complete()
    
    def complete(self):
        """完成任务"""
        if self.status != MissionStatus.ACTIVE:
            return
        
        self.status = MissionStatus.SUCCESS
        self.logger.info(f"Mission {self.mission_id} '{self.title}' completed!")
        
        if self.on_complete:
            self.on_complete(self)
    
    def fail(self, reason: str = ""):
        """
        任务失败
        
        Args:
            reason: 失败原因
        """
        if self.status != MissionStatus.ACTIVE:
            return
        
        self.status = MissionStatus.FAILURE
        self.logger.info(f"Mission {self.mission_id} '{self.title}' failed! Reason: {reason}")
        
        if self.on_fail:
            self.on_fail(self)
    
    def is_complete(self) -> bool:
        """检查任务是否完成"""
        return self.status == MissionStatus.SUCCESS
    
    def is_failed(self) -> bool:
        """检查任务是否失败"""
        return self.status == MissionStatus.FAILURE
    
    def is_active(self) -> bool:
        """检查任务是否进行中"""
        return self.status == MissionStatus.ACTIVE
    
    def to_dict(self) -> Dict:
        """序列化为字典"""
        return {
            "mission_id": self.mission_id,
            "type_id": self.type_id,
            "mission_type": self.mission_type.name,
            "status": self.status.name,
            "origin": self.origin.name,
            "title": self.title,
            "description": self.description,
            "target_count": self.target_count,
            "current_count": self.current_count,
            "target_pos": [self.target_pos.x, self.target_pos.y, self.target_pos.z] if self.target_pos else None,
            "target_item_id": self.target_item_id,
            "target_monster_type": self.target_monster_type,
            "npc_id": self.npc_id,
            "faction_id": self.faction_id,
            "deadline": self.deadline,
            "reward_items": self.reward_items,
            "reward_money": self.reward_money,
            "fail_on_npc_death": self.fail_on_npc_death
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Mission':
        """从字典反序列化"""
        mission = Mission(data["type_id"], MissionType[data["mission_type"]])
        mission.mission_id = data["mission_id"]
        mission.status = MissionStatus[data["status"]]
        mission.origin = MissionOrigin[data["origin"]]
        mission.title = data["title"]
        mission.description = data["description"]
        mission.target_count = data["target_count"]
        mission.current_count = data["current_count"]
        
        if data["target_pos"]:
            mission.target_pos = Tripoint(data["target_pos"][0], data["target_pos"][1], data["target_pos"][2])
        
        mission.target_item_id = data.get("target_item_id")
        mission.target_monster_type = data.get("target_monster_type")
        mission.npc_id = data.get("npc_id")
        mission.faction_id = data.get("faction_id")
        mission.deadline = data.get("deadline")
        mission.reward_items = data.get("reward_items", [])
        mission.reward_money = data.get("reward_money", 0)
        mission.fail_on_npc_death = data.get("fail_on_npc_death", False)
        
        return mission


class MissionManager:
    """
    任务管理器 - 管理所有任务和任务定义
    
    Attributes:
        mission_definitions: 任务定义字典 {type_id: definition}
        active_missions: 激活的任务列表
        completed_missions: 完成的任务列表
        failed_missions: 失败的任务列表
    """
    
    def __init__(self):
        self.mission_definitions: Dict[str, Dict] = {}
        self.active_missions: List[Mission] = []
        self.completed_missions: List[Mission] = []
        self.failed_missions: List[Mission] = []
        self.logger = Logger()
    
    def load_mission_definitions(self, data_dir: Path):
        """
        从JSON文件加载任务定义
        
        Args:
            data_dir: 数据目录路径
        """
        missions_dir = data_dir / "missions"
        if not missions_dir.exists():
            self.logger.warning(f"Missions directory not found: {missions_dir}")
            return
        
        for json_file in missions_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if isinstance(data, list):
                        for mission_def in data:
                            self.add_mission_definition(mission_def)
                    elif isinstance(data, dict):
                        self.add_mission_definition(data)
                        
            except Exception as e:
                self.logger.error(f"Error loading mission file {json_file}: {e}")
    
    def add_mission_definition(self, definition: Dict):
        """添加任务定义"""
        type_id = definition.get("id", "")
        if type_id:
            self.mission_definitions[type_id] = definition
            self.logger.debug(f"Added mission definition: {type_id}")
    
    def create_mission(self, type_id: str, **kwargs) -> Optional[Mission]:
        """
        创建任务实例
        
        Args:
            type_id: 任务类型ID
            **kwargs: 额外参数（覆盖定义中的值）
        
        Returns:
            任务实例，如果类型不存在返回None
        """
        if type_id not in self.mission_definitions:
            self.logger.error(f"Mission type not found: {type_id}")
            return None
        
        definition = self.mission_definitions[type_id]
        
        # 获取任务类型
        mission_type_str = definition.get("type", "FIND_ITEM")
        mission_type = MissionType[mission_type_str]
        
        mission = Mission(type_id, mission_type)
        
        # 应用定义中的值
        mission.title = definition.get("title", "Unknown Mission")
        mission.description = definition.get("description", "")
        mission.target_count = definition.get("target_count", 1)
        mission.target_item_id = definition.get("target_item_id")
        mission.target_monster_type = definition.get("target_monster_type")
        mission.reward_items = definition.get("reward_items", [])
        mission.reward_money = definition.get("reward_money", 0)
        mission.fail_on_npc_death = definition.get("fail_on_npc_death", False)
        
        # 应用覆盖参数
        for key, value in kwargs.items():
            if hasattr(mission, key):
                setattr(mission, key, value)
        
        return mission
    
    def add_mission(self, mission: Mission):
        """添加任务到激活列表"""
        mission.activate()
        self.active_missions.append(mission)
        self.logger.info(f"Added mission to active list: {mission.title}")
    
    def remove_mission(self, mission: Mission):
        """从激活列表移除任务"""
        if mission in self.active_missions:
            self.active_missions.remove(mission)
            
            if mission.is_complete():
                self.completed_missions.append(mission)
            elif mission.is_failed():
                self.failed_missions.append(mission)
    
    def get_active_missions(self) -> List[Mission]:
        """获取所有激活的任务"""
        return self.active_missions.copy()
    
    def get_mission_by_id(self, mission_id: int) -> Optional[Mission]:
        """通过ID获取任务"""
        for mission in self.active_missions:
            if mission.mission_id == mission_id:
                return mission
        return None
    
    def update_kill_mission(self, monster_type: str):
        """
        更新击杀任务进度
        
        Args:
            monster_type: 被击杀的怪物类型
        """
        for mission in self.active_missions:
            if mission.mission_type == MissionType.KILL_MONSTER:
                if mission.target_monster_type == monster_type:
                    mission.update_progress()
    
    def update_item_mission(self, item_id: str):
        """
        更新物品任务进度
        
        Args:
            item_id: 获得的物品ID
        """
        for mission in self.active_missions:
            if mission.mission_type in [MissionType.FIND_ITEM, MissionType.BRING_ITEM]:
                if mission.target_item_id == item_id:
                    mission.update_progress()
    
    def check_position_missions(self, pos: Tripoint):
        """
        检查位置相关任务
        
        Args:
            pos: 当前位置
        """
        for mission in self.active_missions:
            if mission.mission_type == MissionType.REACH:
                if mission.target_pos and pos.distance_to(mission.target_pos) <= 1:
                    mission.complete()
    
    def to_dict(self) -> Dict:
        """序列化为字典"""
        return {
            "active_missions": [m.to_dict() for m in self.active_missions],
            "completed_missions": [m.to_dict() for m in self.completed_missions],
            "failed_missions": [m.to_dict() for m in self.failed_missions]
        }
    
    def from_dict(self, data: Dict):
        """从字典反序列化"""
        self.active_missions = [Mission.from_dict(m) for m in data.get("active_missions", [])]
        self.completed_missions = [Mission.from_dict(m) for m in data.get("completed_missions", [])]
        self.failed_missions = [Mission.from_dict(m) for m in data.get("failed_missions", [])]
