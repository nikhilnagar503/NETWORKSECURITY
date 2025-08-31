from typing import Sequence, List

from dagshub_annotation_converter.formats.label_studio.base import ImageAnnotationResultABC
from dagshub_annotation_converter.ir.image import IRBBoxImageAnnotation, CoordinateStyle, IRImageAnnotationBase
from dagshub_annotation_converter.util.pydantic_util import ParentModel


class RectangleLabelsAnnotationValue(ParentModel):
    x: float
    y: float
    width: float
    height: float
    rotation: float = 0.0
    rectanglelabels: List[str]


class RectangleLabelsAnnotation(ImageAnnotationResultABC):
    value: RectangleLabelsAnnotationValue
    type: str = "rectanglelabels"

    def to_ir_annotation(self) -> List[IRBBoxImageAnnotation]:
        res = IRBBoxImageAnnotation(
            categories={self.value.rectanglelabels[0]: 1.0},
            coordinate_style=CoordinateStyle.NORMALIZED,
            top=self.value.y / 100,
            left=self.value.x / 100,
            width=self.value.width / 100,
            height=self.value.height / 100,
            rotation=self.value.rotation,
            image_width=self.original_width,
            image_height=self.original_height,
            meta=self.meta or {},
        )
        res.imported_id = self.id
        return [res]

    @staticmethod
    def from_ir_annotation(ir_annotation: IRImageAnnotationBase) -> Sequence[ImageAnnotationResultABC]:
        assert isinstance(ir_annotation, IRBBoxImageAnnotation)

        ir_annotation = ir_annotation.normalized()
        category = ir_annotation.ensure_has_one_category()

        return [
            RectangleLabelsAnnotation(
                original_width=ir_annotation.image_width,
                original_height=ir_annotation.image_height,
                value=RectangleLabelsAnnotationValue(
                    x=ir_annotation.left * 100,
                    y=ir_annotation.top * 100,
                    width=ir_annotation.width * 100,
                    height=ir_annotation.height * 100,
                    rotation=ir_annotation.rotation,
                    rectanglelabels=[category],
                ),
                meta=ir_annotation.meta or None,
            )
        ]
