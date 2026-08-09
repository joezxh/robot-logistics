from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class BoundingBox:
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class DetectedObject:
    label: str
    confidence: float
    box: BoundingBox
    source: str = "closed_set"


class UnifiedDetector:
    def fuse(self, detections: Iterable[DetectedObject], iou_threshold: float = 0.5) -> List[DetectedObject]:
        ordered = sorted(detections, key=lambda item: item.confidence, reverse=True)
        selected: List[DetectedObject] = []
        for candidate in ordered:
            if all(self._iou(candidate.box, current.box) < iou_threshold for current in selected):
                selected.append(candidate)
        return selected

    @staticmethod
    def _iou(first: BoundingBox, second: BoundingBox) -> float:
        left = max(first.x, second.x)
        top = max(first.y, second.y)
        right = min(first.x + first.width, second.x + second.width)
        bottom = min(first.y + first.height, second.y + second.height)
        intersection = max(0.0, right - left) * max(0.0, bottom - top)
        union = first.width * first.height + second.width * second.height - intersection
        return intersection / union if union else 0.0
