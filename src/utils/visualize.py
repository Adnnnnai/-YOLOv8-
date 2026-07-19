"""
可视化工具
==========
在图片上绘制检测框、类别标签和置信度。
"""

import colorsys

import cv2
import numpy as np


def _generate_colors(n: int) -> list[tuple[int, int, int]]:
    """生成 n 个 HSV 均匀分布的颜色，返回 BGR 格式。"""
    colors = []
    for i in range(n):
        hue = i / n
        rgb = colorsys.hsv_to_rgb(hue, 0.9, 0.9)
        bgr = (int(rgb[2] * 255), int(rgb[1] * 255), int(rgb[0] * 255))
        colors.append(bgr)
    return colors


# 预生成 30 类颜色
CLASS_COLORS = _generate_colors(30)


def draw_detections(
    image: np.ndarray,
    detections: list[dict],
    show_conf: bool = True,
    line_thickness: int = 2,
    font_scale: float = 0.6,
) -> np.ndarray:
    """在图片上绘制检测结果，返回标注后的图片副本。"""
    img = image.copy()
    h, w = img.shape[:2]
    tl = line_thickness or round(0.002 * (w + h) / 2) + 1

    for det in detections:
        x1, y1, x2, y2 = map(int, det["bbox"])
        cls_id = det["class_id"]
        conf = det["confidence"]
        label = det["class_name"]
        color = CLASS_COLORS[cls_id % len(CLASS_COLORS)]

        cv2.rectangle(img, (x1, y1), (x2, y2), color, tl)

        text = f"{label} {conf:.2f}" if show_conf else label
        (tw, th), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, tl)
        cv2.rectangle(img, (x1, y1 - th - baseline - 4), (x1 + tw + 4, y1), color, -1)
        cv2.putText(img, text, (x1 + 2, y1 - baseline - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), tl, cv2.LINE_AA)

    return img
