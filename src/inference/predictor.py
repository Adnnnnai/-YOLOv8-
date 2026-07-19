"""
YOLOv8 推理预测器
=================
封装模型加载、单图推理、批量推理、结果后处理。
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.utils.config import config


class DiseasePredictor:
    """农业病害检测预测器，封装 YOLOv8 模型推理流程。"""

    def __init__(self, model_path: str | None = None):
        if model_path is None:
            model_path = self._find_best_model()
        self.model = YOLO(str(model_path))
        self.class_names = self.model.names
        self.conf = config.inference["conf_threshold"]
        self.iou = config.inference["iou_threshold"]

    def _find_best_model(self) -> Path:
        candidates = [
            Path(__file__).parent.parent.parent / "runs" / "train" / "plantdoc_yolov8n" / "weights" / "best.pt",
            Path(__file__).parent.parent.parent / "models" / "weights" / "best.pt",
        ]
        for p in candidates:
            if p.exists():
                return p
        raise FileNotFoundError("未找到模型权重，请先训练或指定路径。")

    def predict(self, image: np.ndarray | str) -> list[dict]:
        """对单张图片执行推理，返回检测结果列表。"""
        if isinstance(image, str):
            image = cv2.imread(image)
            if image is None:
                raise FileNotFoundError(f"无法读取图片: {image}")
        results = self.model(image, conf=self.conf, iou=self.iou, verbose=False)
        return self._parse_results(results)

    def predict_batch(self, image_paths: list[str]) -> list[list[dict]]:
        """批量推理，返回每张图的检测结果。"""
        batch_results = []
        for path in image_paths:
            batch_results.append(self.predict(path))
        return batch_results

    def _parse_results(self, results) -> list[dict]:
        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            return []
        detections = []
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            detections.append({
                "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                "confidence": round(conf, 4),
                "class_id": cls_id,
                "class_name": self.class_names.get(cls_id, "unknown"),
            })
        return detections

    def detect_and_draw(self, image: np.ndarray | str) -> np.ndarray:
        """推理并绘制检测框，返回标注后的图片。"""
        from src.utils.visualize import draw_detections

        if isinstance(image, str):
            image = cv2.imread(image)
        detections = self.predict(image)
        return draw_detections(image, detections)
