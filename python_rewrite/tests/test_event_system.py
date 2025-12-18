"""
测试游戏引擎 - 事件系统
"""

import pytest
from src.engine.event_system import EventSystem, Event, EventTypes


def test_event_creation():
    """测试事件创建"""
    event = Event(EventTypes.GAME_START, {"test": "data"})
    assert event.event_type == EventTypes.GAME_START
    assert event.data == {"test": "data"}


def test_subscribe_and_publish():
    """测试订阅和发布"""
    system = EventSystem()
    callback_called = []
    
    def callback(event):
        callback_called.append(event.event_type)
    
    # 订阅事件
    system.subscribe(EventTypes.GAME_START, callback)
    
    # 发布事件
    event = Event(EventTypes.GAME_START)
    system.publish(event)
    system.process_events()
    
    assert EventTypes.GAME_START in callback_called


def test_unsubscribe():
    """测试取消订阅"""
    system = EventSystem()
    callback_called = []
    
    def callback(event):
        callback_called.append(event.event_type)
    
    # 订阅后取消订阅
    system.subscribe(EventTypes.GAME_START, callback)
    system.unsubscribe(EventTypes.GAME_START, callback)
    
    # 发布事件
    event = Event(EventTypes.GAME_START)
    system.publish(event)
    system.process_events()
    
    assert len(callback_called) == 0


def test_multiple_listeners():
    """测试多个监听器"""
    system = EventSystem()
    callback_count = [0]
    
    def callback1(event):
        callback_count[0] += 1
    
    def callback2(event):
        callback_count[0] += 10
    
    # 订阅多个回调
    system.subscribe(EventTypes.GAME_START, callback1)
    system.subscribe(EventTypes.GAME_START, callback2)
    
    # 发布事件
    event = Event(EventTypes.GAME_START)
    system.publish(event)
    system.process_events()
    
    assert callback_count[0] == 11


def test_event_queue():
    """测试事件队列"""
    system = EventSystem()
    events_received = []
    
    def callback(event):
        events_received.append(event.event_type)
    
    system.subscribe(EventTypes.GAME_START, callback)
    system.subscribe(EventTypes.GAME_PAUSE, callback)
    
    # 发布多个事件
    system.publish(Event(EventTypes.GAME_START))
    system.publish(Event(EventTypes.GAME_PAUSE))
    
    # 处理队列
    system.process_events()
    
    assert len(events_received) == 2
    assert events_received[0] == EventTypes.GAME_START
    assert events_received[1] == EventTypes.GAME_PAUSE
