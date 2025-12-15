"""
车辆系统单元测试
"""

import pytest
import tempfile
import os
from src.systems.vehicle import (
    Vehicle, VehicleType, FuelType, PartType,
    VehiclePart, VehicleManager, VEHICLE_TEMPLATES
)
from src.utils.point import Tripoint


class TestVehiclePart:
    """测试车辆部件"""
    
    def test_create_part(self):
        """测试创建部件"""
        part = VehiclePart(PartType.ENGINE, "测试引擎", 100, 100)
        assert part.part_type == PartType.ENGINE
        assert part.name == "测试引擎"
        assert part.hp == 100
        assert part.max_hp == 100
        assert not part.is_broken()
    
    def test_damage_part(self):
        """测试损坏部件"""
        part = VehiclePart(PartType.WHEEL, "车轮", 50, 50)
        part.damage(30)
        assert part.hp == 20
        assert not part.is_broken()
        
        part.damage(25)
        assert part.hp == 0
        assert part.is_broken()
    
    def test_repair_part(self):
        """测试修复部件"""
        part = VehiclePart(PartType.DOOR, "车门", 20, 50)
        part.repair(15)
        assert part.hp == 35
        
        part.repair(30)
        assert part.hp == 50  # 不能超过最大值
    
    def test_part_serialization(self):
        """测试部件序列化"""
        part = VehiclePart(PartType.SEAT, "座位", 40, 60, (1, 2))
        data = part.to_dict()
        
        restored = VehiclePart.from_dict(data)
        assert restored.part_type == part.part_type
        assert restored.name == part.name
        assert restored.hp == part.hp
        assert restored.max_hp == part.max_hp
        assert restored.position == part.position


class TestVehicle:
    """测试车辆"""
    
    def test_create_vehicle(self):
        """测试创建车辆"""
        vehicle = Vehicle(VehicleType.CAR, "我的汽车")
        assert vehicle.vehicle_type == VehicleType.CAR
        assert vehicle.name == "我的汽车"
        assert vehicle.fuel_type == FuelType.GASOLINE
        assert vehicle.velocity == 0.0
        assert len(vehicle.parts) > 0  # 应该有初始化的部件
    
    def test_bicycle_no_engine(self):
        """测试自行车没有引擎"""
        bicycle = Vehicle(VehicleType.BICYCLE, "自行车", FuelType.NONE)
        engines = bicycle.get_parts_by_type(PartType.ENGINE)
        assert len(engines) == 0
        assert bicycle.has_functional_engine()  # 自行车不需要引擎也能移动
    
    def test_add_remove_part(self):
        """测试添加和移除部件"""
        vehicle = Vehicle(VehicleType.MOTORCYCLE, "摩托车")
        initial_count = len(vehicle.parts)
        
        new_part = VehiclePart(PartType.CARGO, "货架", 50, 50)
        vehicle.add_part(new_part)
        assert len(vehicle.parts) == initial_count + 1
        
        vehicle.remove_part(new_part)
        assert len(vehicle.parts) == initial_count
    
    def test_get_parts_by_type(self):
        """测试按类型获取部件"""
        vehicle = Vehicle(VehicleType.CAR, "汽车")
        wheels = vehicle.get_parts_by_type(PartType.WHEEL)
        assert len(wheels) == 4  # 汽车应该有4个轮子
        
        doors = vehicle.get_parts_by_type(PartType.DOOR)
        assert len(doors) >= 2  # 至少有2个门
    
    def test_has_functional_wheels(self):
        """测试车轮功能检查"""
        vehicle = Vehicle(VehicleType.CAR, "汽车")
        assert vehicle.has_functional_wheels()
        
        # 损坏3个轮子
        wheels = vehicle.get_parts_by_type(PartType.WHEEL)
        for i in range(3):
            wheels[i].damage(100)
        
        assert not vehicle.has_functional_wheels()  # 只剩1个轮子，不能移动
    
    def test_can_move(self):
        """测试是否可以移动"""
        vehicle = Vehicle(VehicleType.CAR, "汽车")
        vehicle.refuel(50)
        assert vehicle.can_move()
        
        # 耗尽燃料
        vehicle.fuel = 0
        assert not vehicle.can_move()
        
        # 加燃料但损坏引擎
        vehicle.refuel(50)
        engines = vehicle.get_parts_by_type(PartType.ENGINE)
        engines[0].damage(200)
        assert not vehicle.can_move()
    
    def test_accelerate_decelerate(self):
        """测试加速和减速"""
        vehicle = Vehicle(VehicleType.CAR, "汽车")
        vehicle.refuel(100)
        
        vehicle.accelerate(50)
        assert vehicle.velocity == 50.0
        
        vehicle.accelerate(50)
        assert vehicle.velocity == 100.0
        
        vehicle.decelerate(30)
        assert vehicle.velocity == 70.0
        
        vehicle.stop()
        assert vehicle.velocity == 0.0
    
    def test_max_velocity(self):
        """测试最大速度限制"""
        vehicle = Vehicle(VehicleType.BICYCLE, "自行车", FuelType.NONE)
        max_vel = vehicle.max_velocity
        
        vehicle.accelerate(1000)  # 尝试超速加速
        assert vehicle.velocity == max_vel  # 不能超过最大速度
    
    def test_turn(self):
        """测试转向"""
        vehicle = Vehicle(VehicleType.CAR, "汽车")
        vehicle.refuel(50)
        vehicle.accelerate(50)
        
        vehicle.turn(90)
        assert vehicle.facing == 90
        
        vehicle.turn(300)
        assert vehicle.facing == 30  # 390 % 360 = 30
    
    def test_refuel(self):
        """测试加燃料"""
        vehicle = Vehicle(VehicleType.CAR, "汽车")
        assert vehicle.fuel == 0.0
        
        vehicle.refuel(50)
        assert vehicle.fuel == 50.0
        
        vehicle.refuel(100)
        assert vehicle.fuel == vehicle.max_fuel  # 不能超过最大值
    
    def test_bicycle_no_fuel_needed(self):
        """测试自行车不需要燃料"""
        bicycle = Vehicle(VehicleType.BICYCLE, "自行车", FuelType.NONE)
        assert bicycle.can_move()  # 不需要燃料就能移动
        
        bicycle.accelerate(10)
        assert bicycle.velocity == 10.0  # 能加速
    
    def test_cargo_capacity(self):
        """测试货物容量"""
        vehicle = Vehicle(VehicleType.TRUCK, "卡车")
        initial_capacity = vehicle.get_total_cargo_capacity()
        
        vehicle.add_part(VehiclePart(PartType.CARGO, "额外货架", 50, 50))
        assert vehicle.get_total_cargo_capacity() == initial_capacity + 100
    
    def test_get_status(self):
        """测试获取车辆状态"""
        vehicle = Vehicle(VehicleType.CAR, "测试车")
        vehicle.refuel(75)
        vehicle.accelerate(60)
        
        status = vehicle.get_status()
        assert status["name"] == "测试车"
        assert status["velocity"] == 60.0
        assert status["fuel_percentage"] < 75.0  # 加速会消耗燃料
        assert status["fuel_percentage"] > 70.0
        assert status["can_move"] == True
    
    def test_vehicle_serialization(self):
        """测试车辆序列化"""
        vehicle = Vehicle(VehicleType.MOTORCYCLE, "摩托车")
        vehicle.position = Tripoint(10, 20, 0)
        vehicle.refuel(50)
        vehicle.accelerate(80)
        vehicle.facing = 180
        
        data = vehicle.to_dict()
        restored = Vehicle.from_dict(data)
        
        assert restored.vehicle_type == vehicle.vehicle_type
        assert restored.name == vehicle.name
        assert restored.fuel_type == vehicle.fuel_type
        assert restored.velocity == vehicle.velocity
        assert restored.fuel == vehicle.fuel
        assert restored.facing == vehicle.facing
        assert len(restored.parts) == len(vehicle.parts)


class TestVehicleManager:
    """测试车辆管理器"""
    
    def test_create_vehicle(self):
        """测试创建车辆"""
        manager = VehicleManager()
        vehicle = manager.create_vehicle(
            "car1",
            VehicleType.CAR,
            "我的汽车"
        )
        
        assert vehicle is not None
        assert manager.get_vehicle("car1") == vehicle
    
    def test_create_duplicate(self):
        """测试创建重复ID的车辆"""
        manager = VehicleManager()
        vehicle1 = manager.create_vehicle("car1", VehicleType.CAR, "汽车1")
        vehicle2 = manager.create_vehicle("car1", VehicleType.TRUCK, "卡车")
        
        assert vehicle1 == vehicle2  # 返回已存在的车辆
        assert manager.get_vehicle("car1").name == "汽车1"
    
    def test_get_vehicle(self):
        """测试获取车辆"""
        manager = VehicleManager()
        manager.create_vehicle("bike1", VehicleType.BICYCLE, "自行车")
        
        vehicle = manager.get_vehicle("bike1")
        assert vehicle is not None
        assert vehicle.name == "自行车"
        
        assert manager.get_vehicle("nonexistent") is None
    
    def test_remove_vehicle(self):
        """测试移除车辆"""
        manager = VehicleManager()
        manager.create_vehicle("car1", VehicleType.CAR, "汽车")
        
        assert manager.remove_vehicle("car1")
        assert manager.get_vehicle("car1") is None
        assert not manager.remove_vehicle("nonexistent")
    
    def test_get_all_vehicles(self):
        """测试获取所有车辆"""
        manager = VehicleManager()
        manager.create_vehicle("car1", VehicleType.CAR, "汽车1")
        manager.create_vehicle("bike1", VehicleType.BICYCLE, "自行车")
        manager.create_vehicle("truck1", VehicleType.TRUCK, "卡车")
        
        vehicles = manager.get_all_vehicles()
        assert len(vehicles) == 3
    
    def test_get_vehicles_at_position(self):
        """测试获取指定位置的车辆"""
        manager = VehicleManager()
        
        car1 = manager.create_vehicle("car1", VehicleType.CAR, "汽车1")
        car1.position = Tripoint(10, 20, 0)
        
        car2 = manager.create_vehicle("car2", VehicleType.CAR, "汽车2")
        car2.position = Tripoint(10, 20, 0)
        
        bike = manager.create_vehicle("bike1", VehicleType.BICYCLE, "自行车")
        bike.position = Tripoint(30, 40, 0)
        
        vehicles_at_pos = manager.get_vehicles_at_position(Tripoint(10, 20, 0))
        assert len(vehicles_at_pos) == 2
    
    def test_manager_serialization(self):
        """测试管理器序列化"""
        manager = VehicleManager()
        manager.create_vehicle("car1", VehicleType.CAR, "汽车1")
        manager.create_vehicle("bike1", VehicleType.BICYCLE, "自行车")
        
        data = manager.to_dict()
        restored = VehicleManager.from_dict(data)
        
        assert len(restored.get_all_vehicles()) == 2
        assert restored.get_vehicle("car1") is not None
        assert restored.get_vehicle("bike1") is not None
    
    def test_save_load_file(self):
        """测试保存和加载文件"""
        manager = VehicleManager()
        manager.create_vehicle("car1", VehicleType.CAR, "测试车")
        manager.create_vehicle("bike1", VehicleType.BICYCLE, "测试自行车")
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            manager.save_to_file(filepath)
            
            # 从文件加载
            loaded_manager = VehicleManager.load_from_file(filepath)
            assert len(loaded_manager.get_all_vehicles()) == 2
            assert loaded_manager.get_vehicle("car1") is not None
            assert loaded_manager.get_vehicle("bike1") is not None
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestVehicleTemplates:
    """测试车辆模板"""
    
    def test_templates_exist(self):
        """测试模板存在"""
        assert "bicycle" in VEHICLE_TEMPLATES
        assert "car" in VEHICLE_TEMPLATES
        assert "truck" in VEHICLE_TEMPLATES
        assert "motorcycle" in VEHICLE_TEMPLATES
    
    def test_create_from_template(self):
        """测试从模板创建车辆"""
        template = VEHICLE_TEMPLATES["car"]
        vehicle = Vehicle(
            template["type"],
            template["name"],
            template["fuel_type"]
        )
        
        assert vehicle.vehicle_type == VehicleType.CAR
        assert vehicle.fuel_type == FuelType.GASOLINE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
