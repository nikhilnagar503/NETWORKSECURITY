from typing import List


from dagshub_annotation_converter.ir.image.annotations.base import IRImageAnnotationBase
from dagshub_annotation_converter.util.pydantic_util import ParentModel


class IRSegmentationPoint(ParentModel):
    x: float
    y: float


class IRSegmentationImageAnnotation(IRImageAnnotationBase):
    points: List[IRSegmentationPoint] = []

    def _normalize(self):
        self.points = [IRSegmentationPoint(x=p.x / self.image_width, y=p.y / self.image_height) for p in self.points]

    def _denormalize(self):
        self.points = [IRSegmentationPoint(x=p.x * self.image_width, y=p.y * self.image_height) for p in self.points]

    def add_point(self, x: float, y: float):
        self.points.append(IRSegmentationPoint(x=x, y=y))
