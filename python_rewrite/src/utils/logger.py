"""
工具模块 - 日志系统

提供统一的日志接口
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class Logger:
    """游戏日志管理器"""

    _instance: Optional["Logger"] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self):
        """设置日志器"""
        self._logger = logging.getLogger("CDDA-Python")
        self._logger.setLevel(logging.DEBUG)

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
        )
        console_handler.setFormatter(console_format)
        self._logger.addHandler(console_handler)

        # 文件处理器
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "game.log", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_format)
        self._logger.addHandler(file_handler)

    def debug(self, message: str):
        """调试信息"""
        if self._logger:
            self._logger.debug(message)

    def info(self, message: str):
        """普通信息"""
        if self._logger:
            self._logger.info(message)

    def warning(self, message: str):
        """警告信息"""
        if self._logger:
            self._logger.warning(message)

    def error(self, message: str):
        """错误信息"""
        if self._logger:
            self._logger.error(message)

    def critical(self, message: str):
        """严重错误"""
        if self._logger:
            self._logger.critical(message)


# 全局日志实例
logger = Logger()


# 便捷函数
def debug(message: str):
    logger.debug(message)


def info(message: str):
    logger.info(message)


def warning(message: str):
    logger.warning(message)


def error(message: str):
    logger.error(message)


def critical(message: str):
    logger.critical(message)
