"""
YOLOv8 模型训练脚本
====================
使用 Ultralytics YOLOv8 在 PlantDoc 农业病害数据集上训练目标检测模型。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ultralytics import YOLO
from src.utils.config import config


def main():
    data_yaml = Path(__file__).parent.parent.parent / "data" / "yolo" / "dataset.yaml"
    project = Path(__file__).parent.parent.parent / "runs" / "train"
    name = "plantdoc_yolov8n"

    model = YOLO(config.training["model"])

    results = model.train(
        data=str(data_yaml),
        epochs=config.training["epochs"],
        batch=config.training["batch_size"],
        imgsz=config.training["imgsz"],
        lr0=config.training["lr0"],
        lrf=config.training["lrf"],
        momentum=config.training["momentum"],
        weight_decay=config.training["weight_decay"],
        warmup_epochs=config.training["warmup_epochs"],
        patience=config.training["patience"],
        device=config.training["device"],
        workers=config.training["workers"],
        augment=config.training["augment"],
        mosaic=config.training["mosaic"],
        mixup=config.training["mixup"],
        copy_paste=config.training["copy_paste"],
        project=str(project),
        name=name,
        pretrained=True,
        optimizer="auto",
        verbose=True,
        seed=42,
        exist_ok=True,
        val=True,
        save=True,
        save_period=10,
    )

    print(f"\n训练完成, 最佳模型: {results.save_dir}/weights/best.pt")


if __name__ == "__main__":
    main()
