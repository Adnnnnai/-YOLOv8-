"""
FastAPI 路由
=============
定义所有 API 端点：
- 健康检查（含 GPU / 模型 / 图片计数）
- 配置读写
- 单图 / 批量 / 标注检测
- 模型回滚
- 训练 WebSocket
"""

import io
import json
import sys
import time
import base64
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect

from backend.app.schemas.models import (
    DetectionResponse,
    DetectionBox,
    HealthResponse,
    ConfigResponse,
    ConfigUpdateRequest,
    RollbackResponse,
    AnnotatedResponse,
)
from backend.app.services.detector import DetectorService

router = APIRouter()
detector = DetectorService()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
SETTINGS_PATH = Path(__file__).parent.parent.parent.parent / "configs" / "settings.yaml"


# ============================================================
#  工具函数
# ============================================================

def _count_images() -> dict:
    """统计 data/yolo 目录下的训练/验证图片数量。"""
    base = Path(__file__).parent.parent.parent.parent / "data" / "yolo" / "images"
    train = len(list(base.glob("train/**/*.jpg"))) + len(list(base.glob("train/**/*.png")))
    val = len(list(base.glob("val/**/*.jpg"))) + len(list(base.glob("val/**/*.png")))
    return {"train": train, "val": val, "total": train + val}


def _find_latest_results() -> Path | None:
    """查找最近的训练结果 CSV。"""
    runs = Path(__file__).parent.parent.parent.parent / "runs" / "train"
    best = None
    best_mtime = 0
    for csv in runs.glob("**/results.csv"):
        mtime = csv.stat().st_mtime
        if mtime > best_mtime:
            best_mtime = mtime
            best = csv
    return best


def _read_settings() -> dict:
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _write_settings(data: dict) -> None:
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


# ============================================================
#  健康检查
# ============================================================

@router.get("/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    return HealthResponse(
        status="ok",
        model_loaded=detector.is_loaded(),
        num_classes=29,
        model_name=detector.model_name(),
        gpu_mem=detector.gpu_info(),
        latency_p50=round(detector.avg_latency(), 1),
        images=_count_images(),
    )


# ============================================================
#  配置读写
# ============================================================

@router.get("/config", response_model=ConfigResponse, tags=["配置"])
async def get_config():
    return ConfigResponse(config=_read_settings())


@router.put("/config", response_model=ConfigResponse, tags=["配置"])
async def update_config(body: ConfigUpdateRequest):
    current = _read_settings()
    for key in body.updates:
        if key in current:
            current[key] = body.updates[key]
    _write_settings(current)
    return ConfigResponse(config=current)


# ============================================================
#  单图检测
# ============================================================

@router.post("/detect", response_model=DetectionResponse, tags=["检测"])
async def detect_disease(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件名")
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}")

    try:
        contents = await file.read()
        image = detector.bytes_to_image(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"图片解析失败: {str(e)}")

    try:
        t0 = time.perf_counter()
        detections = detector.detect(image)
        elapsed = round((time.perf_counter() - t0) * 1000, 1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

    return DetectionResponse(
        filename=file.filename,
        num_detections=len(detections),
        detections=[DetectionBox(
            bbox=d["bbox"],
            confidence=d["confidence"],
            class_id=d["class_id"],
            class_name=d["class_name"],
        ) for d in detections],
        latency_ms=elapsed,
    )


# ============================================================
#  标注图检测（返回 base64 图片）
# ============================================================

@router.post("/detect/annotated", response_model=AnnotatedResponse, tags=["检测"])
async def detect_annotated(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件名")
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}")

    try:
        contents = await file.read()
        image = detector.bytes_to_image(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"图片解析失败: {str(e)}")

    try:
        t0 = time.perf_counter()
        annotated, detections = detector.detect_and_draw(image)
        elapsed = round((time.perf_counter() - t0) * 1000, 1)
        _, buf = detector.image_to_bytes(annotated)
        b64 = base64.b64encode(buf).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

    return AnnotatedResponse(
        filename=file.filename,
        num_detections=len(detections),
        detections=[DetectionBox(
            bbox=d["bbox"],
            confidence=d["confidence"],
            class_id=d["class_id"],
            class_name=d["class_name"],
        ) for d in detections],
        latency_ms=elapsed,
        image_base64=b64,
    )


# ============================================================
#  批量检测
# ============================================================

@router.post("/detect/batch", response_model=list[DetectionResponse], tags=["检测"])
async def detect_batch(files: list[UploadFile] = File(...)):
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="批量最多支持 20 张图片")
    results = []
    for file in files:
        if not file.filename:
            continue
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            results.append(DetectionResponse(filename=file.filename or "unknown", num_detections=0, detections=[], error=f"不支持格式: {ext}"))
            continue
        try:
            contents = await file.read()
            image = detector.bytes_to_image(contents)
            t0 = time.perf_counter()
            dets = detector.detect(image)
            elapsed = round((time.perf_counter() - t0) * 1000, 1)
            results.append(DetectionResponse(
                filename=file.filename,
                num_detections=len(dets),
                detections=[DetectionBox(bbox=d["bbox"], confidence=d["confidence"], class_id=d["class_id"], class_name=d["class_name"]) for d in dets],
                latency_ms=elapsed,
            ))
        except Exception as e:
            results.append(DetectionResponse(filename=file.filename or "unknown", num_detections=0, detections=[], error=str(e)))
    return results


# ============================================================
#  模型回滚
# ============================================================

@router.post("/model/rollback", response_model=RollbackResponse, tags=["模型"])
async def rollback_model(body: dict):
    weight_path = body.get("weight_path", "")
    if not weight_path:
        raise HTTPException(status_code=400, detail="请指定 weight_path")
    try:
        detector.reload(weight_path)
        return RollbackResponse(success=True, active_model=Path(weight_path).name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回滚失败: {str(e)}")


# ============================================================
#  训练历史数据
# ============================================================

@router.get("/train/results", tags=["训练"])
async def get_train_results():
    """读取最近一次训练的 results.csv，返回完整曲线数据。"""
    csv_path = _find_latest_results()
    if csv_path is None:
        raise HTTPException(status_code=404, detail="未找到训练结果 CSV")
    rows = []
    with open(csv_path, "r") as f:
        header = f.readline().strip().split(",")
        for line in f:
            line = line.strip()
            if not line:
                continue
            vals = line.split(",")
            row = {"epoch": int(vals[0].strip())}
            for h, v in zip(header[1:], vals[1:]):
                try:
                    row[h.strip()] = float(v.strip())
                except ValueError:
                    row[h.strip()] = v.strip()
            rows.append(row)
    train_name = csv_path.parent.name
    return {
        "train_name": train_name,
        "total_epochs": len(rows),
        "epochs": rows,
    }


# ============================================================
#  训练 WebSocket
# ============================================================

@router.websocket("/ws/train")
async def ws_train(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            action = msg.get("action", "")
            if action == "subscribe":
                await detector.broadcast_train(websocket)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass


# ============================================================
#  智能诊断 WebSocket
# ============================================================

@router.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket):
    from backend.app.services.chat import ChatService
    await websocket.accept()
    try:
        await ChatService().handle(websocket)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
