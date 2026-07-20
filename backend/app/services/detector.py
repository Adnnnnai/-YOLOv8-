"""
检测服务模块
=============
封装 YOLOv8 预测器，提供统一的检测接口。
支持模型重载、GPU 信息采集、训练 WebSocket 推送。
"""

import io
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.inference.predictor import DiseasePredictor
from src.utils.visualize import draw_detections


class DetectorService:
    """单例检测服务，确保模型只加载一次。"""

    _instance = None
    _predictor: DiseasePredictor | None = None
    _model_path: str | None = None
    _latencies: list[float] = []
    _gpu_mem: str = "—"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def predictor(self) -> DiseasePredictor:
        if self._predictor is None:
            self._predictor = DiseasePredictor()
            if self._model_path is None:
                self._model_path = str(self._predictor._find_best_model())
            self._read_gpu()
        return self._predictor

    # ================================================================
    #  检测
    # ================================================================

    def detect(self, image: np.ndarray) -> list[dict]:
        t0 = time.perf_counter()
        result = self.predictor.predict(image)
        self._latencies.append((time.perf_counter() - t0) * 1000)
        if len(self._latencies) > 100:
            self._latencies = self._latencies[-100:]
        return result

    def detect_and_draw(self, image: np.ndarray) -> tuple[np.ndarray, list[dict]]:
        detections = self.detect(image)
        annotated = draw_detections(image, detections)
        return annotated, detections

    @staticmethod
    def bytes_to_image(file_bytes: bytes) -> np.ndarray:
        img = Image.open(io.BytesIO(file_bytes))
        img = np.array(img.convert("RGB"))
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    @staticmethod
    def image_to_bytes(image: np.ndarray, fmt: str = ".jpg") -> tuple[str, bytes]:
        """numpy BGR 图像 → (mime, bytes)"""
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        buf = io.BytesIO()
        pil.save(buf, format="JPEG" if fmt in (".jpg", ".jpeg") else fmt.upper().lstrip("."))
        mime = f"image/{'jpeg' if fmt in ('.jpg','.jpeg') else fmt.lower().lstrip('.')}"
        return mime, buf.getvalue()

    # ================================================================
    #  状态查询
    # ================================================================

    def is_loaded(self) -> bool:
        return self._predictor is not None

    def model_name(self) -> str:
        if self._model_path:
            return Path(self._model_path).name
        return "—"

    def gpu_info(self) -> str:
        self._read_gpu()
        return self._gpu_mem

    def avg_latency(self) -> float:
        if not self._latencies:
            return 0
        return sum(self._latencies) / len(self._latencies)

    def _read_gpu(self):
        """尝试从 torch 读取 GPU 显存。"""
        try:
            import torch
            if torch.cuda.is_available():
                total = torch.cuda.get_device_properties(0).total_mem / (1024 ** 3)
                reserved = torch.cuda.memory_reserved(0) / (1024 ** 3)
                self._gpu_mem = f"{reserved:.1f}G / {total:.0f}G"
                return
        except Exception:
            pass
        self._gpu_mem = "— / —"

    # ================================================================
    #  模型重载
    # ================================================================

    def reload(self, weight_path: str) -> None:
        p = Path(weight_path)
        if not p.is_absolute():
            p = Path(__file__).parent.parent.parent.parent / p
        if not p.exists():
            # 尝试 runs/train 下查找
            runs = Path(__file__).parent.parent.parent.parent / "runs" / "train"
            for d in runs.glob("*/weights"):
                candidate = d / p.name
                if candidate.exists():
                    p = candidate
                    break
        if not p.exists():
            raise FileNotFoundError(f"权重文件不存在: {weight_path}")
        self._predictor = DiseasePredictor(str(p))
        self._model_path = str(p)
        self._latencies.clear()
        self._read_gpu()

    # ================================================================
    #  训练 WebSocket 推送（模拟）
    # ================================================================

    async def broadcast_train(self, websocket):
        """模拟训练进度推送。实际接入时改为读取训练日志。"""
        import asyncio
        import random

        epoch = 0
        total = 100
        loss = 2.5
        mAP = 0.0

        while epoch < total:
            epoch += 1
            loss *= random.uniform(0.94, 0.99)
            mAP = min(0.68, mAP + random.uniform(0.005, 0.02) if epoch > 10 else 0)
            await websocket.send_json({
                "epoch": epoch,
                "total": total,
                "pct": round(epoch / total, 3),
                "loss": round(loss, 4),
                "mAP": round(mAP, 4),
                "eta": f"{random.randint(0,2):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}",
                "gpu": self.gpu_info(),
                "log": random.choice([
                    f"box_loss={loss*0.9:.2f}  cls_loss={loss*1.1:.2f}  dfl_loss={loss:.2f}",
                    f"Validating...  mAP@0.5={mAP:.3f}  best={max(mAP+0.01,0.632):.3f}",
                    f"Saving checkpoint → weights/epoch{epoch}.pt",
                    f"GPU {self.gpu_info()} · batch=16 · imgsz=640",
                ]),
            })
            await asyncio.sleep(random.uniform(0.4, 1.2))
