"""
车辆系统（简化版）

该模块实现了基础的车辆系统，包括：
- 车辆类型和属性
- 车辆部件管理
- 燃料系统
- 车辆移动
- 车辆状态检查
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import json
from ..utils.point import Tripoint
from ..utils.logger import Logger

logger = Logger()


class VehicleType(Enum):
    """车辆类型"""
    MOTORCYCLE = "motorcycle"  # 摩托车
    CAR = "car"  # 汽车
    TRUCK = "truck"  # 卡车
    SUV = "suv"  # SUV
    BUS = "bus"  # 巴士
    ARMORED = "armored"  # 装甲车
    TANK = "tank"  # 坦克
    BICYCLE = "bicycle"  # 自行车


class FuelType(Enum):
    """燃料类型"""
    GASOLINE = "gasoline"  # 汽油
    DIESEL = "diesel"  # 柴油
    ELECTRIC = "electric"  # 电力
    NONE = "none"  # 无需燃料


class PartType(Enum):
    """部件类型"""
    ENGINE = "engine"  # 引擎
    WHEEL = "wheel"  # 车轮
    SEAT = "seat"  # 座位
    FUEL_TANK = "fuel_tank"  # 油箱
    BATTERY = "battery"  # 电池
    DOOR = "door"  # 车门
    WINDOW = "window"  # 车窗
    FRAME = "frame"  # 车架
    CARGO = "cargo"  # 货架
    HEADLIGHT = "headlight"  # 前灯
    ARMOR = "armor"  # 装甲
    TURRET = "turret"  # 炮塔
    CONTROLS = "controls"  # 控制装置
    ALTERNATOR = "alternator"  # 发电机
    SOLAR_PANEL = "solar_panel"  # 太阳能板
    WINDSHIELD = "windshield"  # 挡风玻璃
    DASHBOARD = "dashboard"  # 仪表盘
    STEREO = "stereo"  # 音响
    MUFFLER = "muffler"  # 消音器
    TRUNK = "trunk"  # 后备箱
    HOOD = "hood"  # 引擎盖
    ROOF = "roof"  # 车顶
    QUARTERPANEL = "quarterpanel"  # 侧板
    FENDER = "fender"  # 挡泥板
    MIRROR = "mirror"  # 后视镜


@dataclass
class VehiclePart:
    """车辆部件"""
    part_type: PartType
    name: str
    hp: int
    max_hp: int
    position: Tuple[int, int] = (0, 0)  # 相对车辆中心的位置
    
    def is_broken(self) -> bool:
        """部件是否损坏"""
        return self.hp <= 0
    
    def damage(self, amount: int) -> None:
        """损坏部件"""
        self.hp = max(0, self.hp - amount)
        if self.is_broken():
            logger.info(f"部件 {self.name} 已损坏")
    
    def repair(self, amount: int) -> None:
        """修复部件"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "part_type": self.part_type.value,
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "position": list(self.position)
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'VehiclePart':
        """从字典反序列化"""
        return VehiclePart(
            part_type=PartType(data["part_type"]),
            name=data["name"],
            hp=data["hp"],
            max_hp=data["max_hp"],
            position=tuple(data.get("position", [0, 0]))
        )


class Vehicle:
    """车辆类"""
    
    def __init__(
        self,
        vehicle_type: VehicleType,
        name: str,
        fuel_type: FuelType = FuelType.GASOLINE
    ):
        self.vehicle_type = vehicle_type
        self.name = name
        self.fuel_type = fuel_type
        
        # 车辆属性
        self.position: Optional[Tripoint] = None
        self.velocity: float = 0.0  # 当前速度 (km/h)
        self.max_velocity: float = self._get_max_velocity()
        self.fuel: float = 0.0  # 当前燃料
        self.max_fuel: float = 100.0  # 最大燃料
        self.facing: int = 0  # 朝向 (0-360度)
        
        # 部件列表
        self.parts: List[VehiclePart] = []
        
        # 初始化基础部件
        self._initialize_parts()
    
    def _get_max_velocity(self) -> float:
        """获取最大速度"""
        speed_map = {
            VehicleType.BICYCLE: 25.0,
            VehicleType.MOTORCYCLE: 120.0,
            VehicleType.CAR: 160.0,
            VehicleType.TRUCK: 100.0,
            VehicleType.SUV: 140.0,
            VehicleType.BUS: 90.0,
            VehicleType.ARMORED: 80.0,
            VehicleType.TANK: 60.0
        }
        return speed_map.get(self.vehicle_type, 100.0)
    
    def _initialize_parts(self) -> None:
        """初始化基础部件"""
        # 根据车辆类型添加基础部件
        if self.vehicle_type == VehicleType.BICYCLE:
            self.add_part(VehiclePart(PartType.FRAME, "车架", 50, 50, (0, 0)))
            self.add_part(VehiclePart(PartType.WHEEL, "前轮", 30, 30, (0, 1)))
            self.add_part(VehiclePart(PartType.WHEEL, "后轮", 30, 30, (0, -1)))
            self.add_part(VehiclePart(PartType.SEAT, "座位", 20, 20, (0, 0)))
        else:
            # 引擎（自行车除外）
            if self.vehicle_type != VehicleType.BICYCLE:
                self.add_part(VehiclePart(PartType.ENGINE, "引擎", 100, 100, (0, 1)))
            
            # 车轮
            self.add_part(VehiclePart(PartType.WHEEL, "前左轮", 40, 40, (-1, 1)))
            self.add_part(VehiclePart(PartType.WHEEL, "前右轮", 40, 40, (1, 1)))
            self.add_part(VehiclePart(PartType.WHEEL, "后左轮", 40, 40, (-1, -1)))
            self.add_part(VehiclePart(PartType.WHEEL, "后右轮", 40, 40, (1, -1)))
            
            # 座位
            self.add_part(VehiclePart(PartType.SEAT, "驾驶座", 30, 30, (0, 0)))
            
            # 油箱或电池
            if self.fuel_type == FuelType.ELECTRIC:
                self.add_part(VehiclePart(PartType.BATTERY, "电池", 80, 80, (0, -1)))
            elif self.fuel_type != FuelType.NONE:
                self.add_part(VehiclePart(PartType.FUEL_TANK, "油箱", 60, 60, (0, -1)))
            
            # 控制装置
            self.add_part(VehiclePart(PartType.CONTROLS, "控制装置", 50, 50, (0, 0)))
            
            # 车门和车窗
            if self.vehicle_type in [VehicleType.CAR, VehicleType.SUV, VehicleType.TRUCK]:
                self.add_part(VehiclePart(PartType.DOOR, "左门", 40, 40, (-1, 0)))
                self.add_part(VehiclePart(PartType.DOOR, "右门", 40, 40, (1, 0)))
                self.add_part(VehiclePart(PartType.WINDOW, "挡风玻璃", 20, 20, (0, 1)))
    
    def add_part(self, part: VehiclePart) -> None:
        """添加部件"""
        self.parts.append(part)
        logger.debug(f"车辆 {self.name} 添加部件: {part.name}")
    
    def remove_part(self, part: VehiclePart) -> bool:
        """移除部件"""
        if part in self.parts:
            self.parts.remove(part)
            logger.info(f"车辆 {self.name} 移除部件: {part.name}")
            return True
        return False
    
    def get_parts_by_type(self, part_type: PartType) -> List[VehiclePart]:
        """获取指定类型的所有部件"""
        return [p for p in self.parts if p.part_type == part_type]
    
    def has_functional_engine(self) -> bool:
        """是否有可用的引擎"""
        if self.vehicle_type == VehicleType.BICYCLE:
            return True  # 自行车不需要引擎
        engines = self.get_parts_by_type(PartType.ENGINE)
        return any(not e.is_broken() for e in engines)
    
    def has_functional_wheels(self) -> bool:
        """是否有足够的可用车轮"""
        wheels = self.get_parts_by_type(PartType.WHEEL)
        functional_wheels = [w for w in wheels if not w.is_broken()]
        # 至少需要2个可用车轮
        return len(functional_wheels) >= 2
    
    def can_move(self) -> bool:
        """是否可以移动"""
        if not self.has_functional_engine():
            return False
        if not self.has_functional_wheels():
            return False
        if self.fuel_type != FuelType.NONE and self.fuel <= 0:
            return False
        return True
    
    def accelerate(self, amount: float) -> None:
        """加速"""
        if not self.can_move():
            logger.warning(f"车辆 {self.name} 无法移动")
            return
        
        self.velocity = min(self.max_velocity, self.velocity + amount)
        logger.debug(f"车辆 {self.name} 加速至 {self.velocity:.1f} km/h")
        
        # 消耗燃料
        if self.fuel_type != FuelType.NONE:
            fuel_consumption = amount * 0.01  # 简化的燃料消耗
            self.consume_fuel(fuel_consumption)
    
    def decelerate(self, amount: float) -> None:
        """减速"""
        self.velocity = max(0, self.velocity - amount)
        logger.debug(f"车辆 {self.name} 减速至 {self.velocity:.1f} km/h")
    
    def stop(self) -> None:
        """停车"""
        self.velocity = 0.0
        logger.info(f"车辆 {self.name} 已停车")
    
    def turn(self, degrees: int) -> None:
        """转向"""
        if self.velocity > 0:
            self.facing = (self.facing + degrees) % 360
            logger.debug(f"车辆 {self.name} 转向至 {self.facing} 度")
    
    def refuel(self, amount: float) -> None:
        """加燃料"""
        if self.fuel_type == FuelType.NONE:
            logger.warning(f"车辆 {self.name} 不需要燃料")
            return
        
        old_fuel = self.fuel
        self.fuel = min(self.max_fuel, self.fuel + amount)
        added = self.fuel - old_fuel
        logger.info(f"车辆 {self.name} 加燃料 {added:.1f} 单位")
    
    def consume_fuel(self, amount: float) -> None:
        """消耗燃料"""
        self.fuel = max(0, self.fuel - amount)
        if self.fuel <= 0:
            logger.warning(f"车辆 {self.name} 燃料耗尽")
    
    def get_total_cargo_capacity(self) -> int:
        """获取总货物容量"""
        cargo_parts = self.get_parts_by_type(PartType.CARGO)
        trunk_parts = self.get_parts_by_type(PartType.TRUNK)
        # 每个货架/后备箱提供100单位容量
        return (len(cargo_parts) + len(trunk_parts)) * 100
    
    def get_status(self) -> Dict[str, Any]:
        """获取车辆状态"""
        return {
            "name": self.name,
            "type": self.vehicle_type.value,
            "velocity": self.velocity,
            "max_velocity": self.max_velocity,
            "fuel": self.fuel,
            "max_fuel": self.max_fuel,
            "fuel_percentage": (self.fuel / self.max_fuel * 100) if self.max_fuel > 0 else 0,
            "facing": self.facing,
            "can_move": self.can_move(),
            "total_parts": len(self.parts),
            "broken_parts": len([p for p in self.parts if p.is_broken()]),
            "cargo_capacity": self.get_total_cargo_capacity()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "vehicle_type": self.vehicle_type.value,
            "name": self.name,
            "fuel_type": self.fuel_type.value,
            "position": [self.position.x, self.position.y, self.position.z] if self.position else None,
            "velocity": self.velocity,
            "max_velocity": self.max_velocity,
            "fuel": self.fuel,
            "max_fuel": self.max_fuel,
            "facing": self.facing,
            "parts": [p.to_dict() for p in self.parts]
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Vehicle':
        """从字典反序列化"""
        vehicle = Vehicle(
            vehicle_type=VehicleType(data["vehicle_type"]),
            name=data["name"],
            fuel_type=FuelType(data["fuel_type"])
        )
        
        # 恢复属性
        if data.get("position"):
            pos = data["position"]
            vehicle.position = Tripoint(pos[0], pos[1], pos[2])
        
        vehicle.velocity = data["velocity"]
        vehicle.max_velocity = data["max_velocity"]
        vehicle.fuel = data["fuel"]
        vehicle.max_fuel = data["max_fuel"]
        vehicle.facing = data["facing"]
        
        # 恢复部件（清除初始化的部件，使用保存的部件）
        vehicle.parts = []
        for part_data in data["parts"]:
            vehicle.parts.append(VehiclePart.from_dict(part_data))
        
        return vehicle


class VehicleManager:
    """车辆管理器"""
    
    def __init__(self):
        self.vehicles: Dict[str, Vehicle] = {}
    
    def create_vehicle(
        self,
        vehicle_id: str,
        vehicle_type: VehicleType,
        name: str,
        fuel_type: FuelType = FuelType.GASOLINE
    ) -> Vehicle:
        """创建新车辆"""
        if vehicle_id in self.vehicles:
            logger.warning(f"车辆ID {vehicle_id} 已存在")
            return self.vehicles[vehicle_id]
        
        vehicle = Vehicle(vehicle_type, name, fuel_type)
        self.vehicles[vehicle_id] = vehicle
        logger.info(f"创建车辆: {name} (ID: {vehicle_id})")
        return vehicle
    
    def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        """获取车辆"""
        return self.vehicles.get(vehicle_id)
    
    def remove_vehicle(self, vehicle_id: str) -> bool:
        """移除车辆"""
        if vehicle_id in self.vehicles:
            vehicle = self.vehicles.pop(vehicle_id)
            logger.info(f"移除车辆: {vehicle.name} (ID: {vehicle_id})")
            return True
        return False
    
    def get_all_vehicles(self) -> List[Vehicle]:
        """获取所有车辆"""
        return list(self.vehicles.values())
    
    def get_vehicles_at_position(self, position: Tripoint) -> List[Vehicle]:
        """获取指定位置的所有车辆"""
        return [v for v in self.vehicles.values() if v.position == position]
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "vehicles": {
                vehicle_id: vehicle.to_dict()
                for vehicle_id, vehicle in self.vehicles.items()
            }
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'VehicleManager':
        """从字典反序列化"""
        manager = VehicleManager()
        for vehicle_id, vehicle_data in data.get("vehicles", {}).items():
            manager.vehicles[vehicle_id] = Vehicle.from_dict(vehicle_data)
        return manager
    
    def save_to_file(self, filepath: str) -> None:
        """保存到文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"车辆管理器已保存到 {filepath}")
        except Exception as e:
            logger.error(f"保存车辆管理器失败: {e}")
    
    @staticmethod
    def load_from_file(filepath: str) -> 'VehicleManager':
        """从文件加载"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            manager = VehicleManager.from_dict(data)
            logger.info(f"从 {filepath} 加载车辆管理器")
            return manager
        except Exception as e:
            logger.error(f"加载车辆管理器失败: {e}")
            return VehicleManager()


# 预定义车辆模板
VEHICLE_TEMPLATES = {
    "bicycle": {
        "type": VehicleType.BICYCLE,
        "name": "自行车",
        "fuel_type": FuelType.NONE
    },
    "motorcycle": {
        "type": VehicleType.MOTORCYCLE,
        "name": "摩托车",
        "fuel_type": FuelType.GASOLINE
    },
    "car": {
        "type": VehicleType.CAR,
        "name": "汽车",
        "fuel_type": FuelType.GASOLINE
    },
    "truck": {
        "type": VehicleType.TRUCK,
        "name": "卡车",
        "fuel_type": FuelType.DIESEL
    },
    "suv": {
        "type": VehicleType.SUV,
        "name": "SUV",
        "fuel_type": FuelType.GASOLINE
    },
    "bus": {
        "type": VehicleType.BUS,
        "name": "巴士",
        "fuel_type": FuelType.DIESEL
    },
    "armored": {
        "type": VehicleType.ARMORED,
        "name": "装甲车",
        "fuel_type": FuelType.DIESEL
    },
    "tank": {
        "type": VehicleType.TANK,
        "name": "坦克",
        "fuel_type": FuelType.DIESEL
    }
}
