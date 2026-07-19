"""
模型评估脚本
============
在验证集上评估训练好的模型，输出 mAP、Recall、Precision 等指标。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ultralytics import YOLO
from src.utils.config import config


def main():
    data_yaml = Path(__file__).parent.parent.parent / "data" / "yolo" / "dataset.yaml"

    # 默认使用训练输出中的 best.pt
    weights = config.paths.get("models_dir", "models/weights")
    model_path = Path(__file__).parent.parent.parent / weights / "best.pt"
    if not model_path.exists():
        # 回退到 runs 目录
        runs_best = (
            Path(__file__).parent.parent.parent
            / "runs"
            / "train"
            / "plantdoc_yolov8n"
            / "weights"
            / "best.pt"
        )
        if runs_best.exists():
            model_path = runs_best
        else:
            raise FileNotFoundError(
                f"未找到模型权重文件。请先运行训练，或指定路径。\n"
                f"  检查路径: {model_path}\n"
                f"  检查路径: {runs_best}"
            )

    print(f"加载模型: {model_path}")
    model = YOLO(str(model_path))

    results = model.val(
        data=str(data_yaml),
        split="val",
        device=config.inference["device"],
        imgsz=config.training["imgsz"],
        conf=config.inference["conf_threshold"],
        iou=config.inference["iou_threshold"],
    )

    print("\n" + "=" * 50)
    print("评估结果:")
    print(f"  mAP@0.5:       {results.box.map50:.4f}")
    print(f"  mAP@0.5:0.95:  {results.box.map:.4f}")
    print(f"  Precision:     {results.box.mp:.4f}")
    print(f"  Recall:        {results.box.mr:.4f}")
    print("=" * 50)


if __name__ == "__main__":
    main()
