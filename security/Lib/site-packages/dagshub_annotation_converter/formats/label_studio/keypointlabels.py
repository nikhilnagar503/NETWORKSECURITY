from typing import Sequence, List

from dagshub_annotation_converter.formats.label_studio.base import ImageAnnotationResultABC
from dagshub_annotation_converter.formats.label_studio.rectanglelabels import (
    RectangleLabelsAnnotationValue,
    RectangleLabelsAnnotation,
)
from dagshub_annotation_converter.ir.image import (
    IRPoseImageAnnotation,
    IRPosePoint,
    CoordinateStyle,
    IRImageAnnotationBase,
)
from dagshub_annotation_converter.util.pydantic_util import ParentModel


class KeyPointLabelsAnnotationValue(ParentModel):
    x: float
    y: float
    width: float = 1.0
    keypointlabels: List[str]


class KeyPointLabelsAnnotation(ImageAnnotationResultABC):
    value: KeyPointLabelsAnnotationValue
    type: str = "keypointlabels"

    def to_ir_annotation(self) -> List[IRPoseImageAnnotation]:
        ann = IRPoseImageAnnotation.from_points(
            categories={self.value.keypointlabels[0]: 1.0},
            points=[IRPosePoint(x=self.value.x / 100, y=self.value.y / 100)],
            coordinate_style=CoordinateStyle.NORMALIZED,
            image_width=self.original_width,
            image_height=self.original_height,
            meta=self.meta or {},
        )
        ann.imported_id = self.id
        return [ann]

    @staticmethod
    def from_ir_annotation(ir_annotation: IRImageAnnotationBase) -> Sequence["ImageAnnotationResultABC"]:
        assert isinstance(ir_annotation, IRPoseImageAnnotation)

        ir_annotation = ir_annotation.normalized()
        category = ir_annotation.ensure_has_one_category()

        res: List[ImageAnnotationResultABC] = []

        # For poses (multiple points) - add a bounding box
        if len(ir_annotation.points) > 1:
            bbox = RectangleLabelsAnnotation(
                original_width=ir_annotation.image_width,
                original_height=ir_annotation.image_height,
                value=RectangleLabelsAnnotationValue(
                    x=ir_annotation.left * 100,
                    y=ir_annotation.top * 100,
                    width=ir_annotation.width * 100,
                    height=ir_annotation.height * 100,
                    rectanglelabels=[category],
                ),
                meta=ir_annotation.meta or None,
            )
            res.append(bbox)

        for point in ir_annotation.points:
            res.append(
                KeyPointLabelsAnnotation(
                    original_width=ir_annotation.image_width,
                    original_height=ir_annotation.image_height,
                    value=KeyPointLabelsAnnotationValue(
                        x=point.x * 100,
                        y=point.y * 100,
                        keypointlabels=[category],
                    ),
                    meta=ir_annotation.meta or None,
                )
            )

        return res
