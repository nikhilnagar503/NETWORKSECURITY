from typing import List, Optional, TYPE_CHECKING, Dict, Any

from dagshub_annotation_converter.ir.image.annotations.base import IRImageAnnotationBase
from dagshub_annotation_converter.util.pydantic_util import ParentModel

if TYPE_CHECKING:
    from dagshub_annotation_converter.ir.image import CoordinateStyle


class IRPosePoint(ParentModel):
    x: float
    y: float
    visible: Optional[bool] = None


class IRPoseImageAnnotation(IRImageAnnotationBase):
    # Parameters of the bounding box
    top: float
    left: float
    width: float
    height: float

    points: List[IRPosePoint] = []

    def _normalize(self):
        self.top = self.top / self.image_height
        self.left = self.left / self.image_width
        self.width = self.width / self.image_width
        self.height = self.height / self.image_height

        for point in self.points:
            point.x = point.x / self.image_width
            point.y = point.y / self.image_height

    def _denormalize(self):
        self.top = self.top * self.image_height
        self.left = self.left * self.image_width
        self.width = self.width * self.image_width
        self.height = self.height * self.image_height

        for point in self.points:
            point.x = point.x * self.image_width
            point.y = point.y * self.image_height

    def add_point(self, x: float, y: float, visible: Optional[bool] = None):
        self.points.append(IRPosePoint(x=x, y=y, visible=visible))

    @staticmethod
    def from_points(
        categories: Dict[str, float],
        points: List[IRPosePoint],
        coordinate_style: "CoordinateStyle",
        image_width: int,
        image_height: int,
        filename: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> "IRPoseImageAnnotation":
        point_xs = list(map(lambda p: p.x, points))
        point_ys = list(map(lambda p: p.y, points))

        min_x = min(point_xs)
        max_x = max(point_xs)
        min_y = min(point_ys)
        max_y = max(point_ys)

        return IRPoseImageAnnotation(
            categories=categories,
            filename=filename,
            top=min_y,
            left=min_x,
            width=max_x - min_x,
            height=max_y - min_y,
            points=points,
            coordinate_style=coordinate_style,
            image_height=image_height,
            image_width=image_width,
            meta=meta or {},
        )
