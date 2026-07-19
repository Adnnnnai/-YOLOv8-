"""
检测服务模块
=============
封装 YOLOv8 预测器，提供统一的检测接口。
"""

import io
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.inference.predictor import DiseasePredictor


class DetectorService:
    """单例检测服务，确保模型只加载一次。"""

    _instance = None
    _predictor: DiseasePredictor | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def predictor(self) -> DiseasePredictor:
        if self._predictor is None:
            self._predictor = DiseasePredictor()
        return self._predictor

    def detect(self, image: np.ndarray) -> list[dict]:
        return self.predictor.predict(image)

    @staticmethod
    def bytes_to_image(file_bytes: bytes) -> np.ndarray:
        """上传字节流转为 numpy 数组 (BGR)。"""
        img = Image.open(io.BytesIO(file_bytes))
        img = np.array(img.convert("RGB"))
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
