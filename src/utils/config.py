"""
基于YOLOv8的智能农业病害检测系统
==================================
使用YOLOv8目标检测算法，实现农作物叶片病害区域的自动检测。
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    """全局配置管理类，加载 settings.yaml 并提供属性访问。"""

    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls, config_path: str | None = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: str | None = None):
        if self._config:
            return
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "configs" / "settings.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

    @property
    def paths(self) -> Dict[str, str]:
        return self._config.get("paths", {})

    @property
    def dataset(self) -> Dict[str, Any]:
        return self._config.get("dataset", {})

    @property
    def training(self) -> Dict[str, Any]:
        return self._config.get("training", {})

    @property
    def inference(self) -> Dict[str, Any]:
        return self._config.get("inference", {})

    @property
    def server(self) -> Dict[str, Any]:
        return self._config.get("server", {})

    @property
    def class_names(self) -> list:
        return self._config.get("class_names", [])

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def resolve_path(self, key: str) -> Path:
        """将配置中的相对路径解析为绝对路径。"""
        p = self.paths.get(key, key)
        if not Path(p).is_absolute():
            p = str(Path(__file__).parent.parent.parent / p)
        return Path(p)


# 全局单例
config = Config()
