"""
FastAPI 数据模型
=================
定义请求和响应的 Pydantic Schema。
"""

from pydantic import BaseModel, Field


class DetectionBox(BaseModel):
    """单个检测框结果"""
    bbox: list[float] = Field(..., description="边界框 [x1, y1, x2, y2]", example=[100.0, 150.0, 300.0, 400.0])
    confidence: float = Field(..., description="置信度", ge=0.0, le=1.0, example=0.856)
    class_id: int = Field(..., description="类别ID", example=3)
    class_name: str = Field(..., description="类别名称", example="Apple rust leaf")


class DetectionResponse(BaseModel):
    """单张图片的检测响应"""
    filename: str = Field(..., description="图片文件名")
    num_detections: int = Field(..., description="检测到的目标数量")
    detections: list[DetectionBox] = Field(default_factory=list, description="检测结果列表")
    error: str | None = Field(default=None, description="错误信息(如有)")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(default="ok")
    model_loaded: bool = True
    num_classes: int = 29
