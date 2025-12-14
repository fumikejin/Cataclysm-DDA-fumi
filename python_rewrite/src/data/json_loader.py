"""
数据管理 - JSON 加载器

负责加载和解析 JSON 数据文件
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.logger import logger


class JSONLoader:
    """JSON 文件加载器"""

    def __init__(self, data_path: str = "../data"):
        """
        初始化加载器

        Args:
            data_path: 数据文件根目录路径
        """
        self.data_path = Path(data_path)
        if not self.data_path.exists():
            logger.warning(f"数据路径不存在: {self.data_path}")

    def load_file(self, file_path: Path) -> Optional[List[Dict[str, Any]]]:
        """
        加载单个 JSON 文件

        Args:
            file_path: JSON 文件路径

        Returns:
            加载的数据列表，失败返回 None
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 如果是单个对象，转换为列表
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                logger.error(f"不支持的 JSON 格式: {file_path}")
                return None

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析错误 {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"加载文件失败 {file_path}: {e}")
            return None

    def load_directory(self, dir_path: Path, pattern: str = "*.json") -> List[Dict[str, Any]]:
        """
        加载目录下所有匹配的 JSON 文件

        Args:
            dir_path: 目录路径
            pattern: 文件匹配模式

        Returns:
            所有加载的数据列表
        """
        all_data = []

        if not dir_path.exists():
            logger.warning(f"目录不存在: {dir_path}")
            return all_data

        json_files = list(dir_path.glob(pattern))
        logger.info(f"在 {dir_path} 中找到 {len(json_files)} 个 JSON 文件")

        for json_file in json_files:
            data = self.load_file(json_file)
            if data:
                all_data.extend(data)

        return all_data

    def load_recursive(
        self, dir_path: Path, pattern: str = "**/*.json"
    ) -> List[Dict[str, Any]]:
        """
        递归加载目录及子目录下的所有 JSON 文件

        Args:
            dir_path: 目录路径
            pattern: 文件匹配模式

        Returns:
            所有加载的数据列表
        """
        all_data = []

        if not dir_path.exists():
            logger.warning(f"目录不存在: {dir_path}")
            return all_data

        json_files = list(dir_path.glob(pattern))
        logger.info(f"递归搜索 {dir_path}，找到 {len(json_files)} 个 JSON 文件")

        for json_file in json_files:
            data = self.load_file(json_file)
            if data:
                all_data.extend(data)

        return all_data
