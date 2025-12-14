"""
工具模块 - 配置管理器

提供游戏配置的读取、保存和管理功能
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .logger import logger


class Config:
    """配置管理器"""

    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.default_config = self._get_default_config()

        # 加载配置
        self.load()

    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置

        Returns:
            默认配置字典
        """
        return {
            "game": {
                "language": "zh_CN",
                "sound_enabled": True,
                "music_enabled": True,
                "autosave": True,
                "autosave_interval": 5,  # 分钟
            },
            "graphics": {
                "tileset": "ASCII",
                "tile_size": 16,
                "font_size": 14,
                "fullscreen": False,
                "window_width": 1024,
                "window_height": 768,
                "fps_limit": 60,
            },
            "controls": {
                "move_north": "k",
                "move_south": "j",
                "move_east": "l",
                "move_west": "h",
                "move_northeast": "u",
                "move_northwest": "y",
                "move_southeast": "n",
                "move_southwest": "b",
                "inventory": "i",
                "pickup": ",",
                "drop": "d",
                "examine": "e",
                "crafting": "&",
                "wait": ".",
            },
            "debug": {
                "enabled": False,
                "show_fps": False,
                "log_level": "INFO",
            },
        }

    def load(self):
        """从文件加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    self.config = self._merge_configs(self.default_config, loaded_config)
                logger.info(f"配置已从 {self.config_file} 加载")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
                self.config = self.default_config.copy()
        else:
            logger.info("配置文件不存在，使用默认配置")
            self.config = self.default_config.copy()
            self.save()  # 保存默认配置

    def save(self):
        """保存配置到文件"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info(f"配置已保存到 {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持点号分隔的路径，如 "graphics.window_width"
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        设置配置值

        Args:
            key: 配置键，支持点号分隔的路径
            value: 配置值
        """
        keys = key.split(".")
        config = self.config

        # 导航到最后一级的父字典
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        # 设置值
        config[keys[-1]] = value
        logger.debug(f"配置已更新: {key} = {value}")

    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """
        合并配置，以加载的配置为准，但保留默认配置中的缺失项

        Args:
            default: 默认配置
            loaded: 加载的配置

        Returns:
            合并后的配置
        """
        result = default.copy()

        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self.default_config.copy()
        self.save()
        logger.info("配置已重置为默认值")


# 全局配置实例
config = Config()
