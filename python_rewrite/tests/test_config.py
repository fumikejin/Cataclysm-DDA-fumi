"""
测试工具模块 - Config 类
"""

import pytest
import json
import tempfile
from pathlib import Path

from src.utils.config import Config


def test_config_creation():
    """测试配置创建"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        config = Config(config_file)
        assert config is not None
        assert isinstance(config.config, dict)
    finally:
        Path(config_file).unlink(missing_ok=True)


def test_config_get():
    """测试配置获取"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        config = Config(config_file)
        
        # 测试获取默认配置
        assert config.get("game.language") == "zh_CN"
        assert config.get("graphics.window_width") == 1024
        
        # 测试不存在的键
        assert config.get("non.existent.key") is None
        assert config.get("non.existent.key", "default") == "default"
    finally:
        Path(config_file).unlink(missing_ok=True)


def test_config_set():
    """测试配置设置"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        config = Config(config_file)
        
        # 设置配置值
        config.set("game.language", "en_US")
        assert config.get("game.language") == "en_US"
        
        # 设置新的配置项
        config.set("test.new.value", 123)
        assert config.get("test.new.value") == 123
    finally:
        Path(config_file).unlink(missing_ok=True)


def test_config_save_load():
    """测试配置保存和加载"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        # 创建配置并设置值
        config1 = Config(config_file)
        config1.set("test.value", "test123")
        config1.save()
        
        # 创建新配置实例并加载
        config2 = Config(config_file)
        assert config2.get("test.value") == "test123"
    finally:
        Path(config_file).unlink(missing_ok=True)
