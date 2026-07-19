"""
推理测试脚本
============
从验证集中随机抽取图片进行推理，输出检测结果和可视化效果。
"""

import random
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.inference.predictor import DiseasePredictor


def main():
    val_images = list(Path("data/yolo/images/val").glob("*.jpg")) + \
                 list(Path("data/yolo/images/val").glob("*.png")) + \
                 list(Path("data/yolo/images/val").glob("*.jpeg"))

    if not val_images:
        val_images = list(Path("data/yolo/images/train").glob("*.jpg"))[:5]

    sample = random.sample(val_images, min(3, len(val_images)))

    predictor = DiseasePredictor()
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    for img_path in sample:
        print(f"\n--- {img_path.name} ---")
        detections = predictor.predict(str(img_path))
        print(f"检测到 {len(detections)} 个目标:")
        for d in detections:
            print(f"  [{d['class_name']}] 置信度: {d['confidence']:.3f}  位置: {d['bbox']}")

        annotated = predictor.detect_and_draw(str(img_path))
        out_path = output_dir / f"result_{img_path.name}"
        cv2.imwrite(str(out_path), annotated)
        print(f"结果已保存: {out_path}")


if __name__ == "__main__":
    main()
