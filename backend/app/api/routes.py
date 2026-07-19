"""
FastAPI 路由
=============
定义所有 API 端点。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, File, UploadFile, HTTPException

from backend.app.schemas.models import DetectionResponse, HealthResponse
from backend.app.services.detector import DetectorService

router = APIRouter()
detector = DetectorService()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


@router.get("/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    """健康检查：确认模型已加载，服务可用。"""
    return HealthResponse()


@router.post("/detect", response_model=DetectionResponse, tags=["检测"])
async def detect_disease(file: UploadFile = File(...)):
    """上传一张农作物叶片图片，返回病害检测结果。"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件名")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}，仅支持 {ALLOWED_EXTENSIONS}",
        )

    try:
        contents = await file.read()
        image = detector.bytes_to_image(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"图片解析失败: {str(e)}")

    try:
        detections = detector.detect(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

    return DetectionResponse(
        filename=file.filename,
        num_detections=len(detections),
        detections=[{
            "bbox": d["bbox"],
            "confidence": d["confidence"],
            "class_id": d["class_id"],
            "class_name": d["class_name"],
        } for d in detections],
    )
