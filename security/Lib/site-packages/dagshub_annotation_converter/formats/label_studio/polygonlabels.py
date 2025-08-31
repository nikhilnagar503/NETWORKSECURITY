from typing import Sequence, List

from dagshub_annotation_converter.formats.label_studio.base import ImageAnnotationResultABC
from dagshub_annotation_converter.ir.image import IRSegmentationImageAnnotation, CoordinateStyle, IRImageAnnotationBase
from dagshub_annotation_converter.util.pydantic_util import ParentModel


class PolygonLabelsAnnotationValue(ParentModel):
    points: List[List[float]]
    polygonlabels: List[str]
    closed: bool = True


class PolygonLabelsAnnotation(ImageAnnotationResultABC):
    value: PolygonLabelsAnnotationValue
    type: str = "polygonlabels"

    def to_ir_annotation(self) -> List[IRSegmentationImageAnnotation]:
        res = IRSegmentationImageAnnotation(
            categories={self.value.polygonlabels[0]: 1.0},
            coordinate_style=CoordinateStyle.NORMALIZED,
            image_width=self.original_width,
            image_height=self.original_height,
            meta=self.meta or {},
        )
        for p in self.value.points:
            res.add_point(p[0] / 100, p[1] / 100)
        res.imported_id = self.id
        return [res]

    @staticmethod
    def from_ir_annotation(ir_annotation: IRImageAnnotationBase) -> Sequence["ImageAnnotationResultABC"]:
        assert isinstance(ir_annotation, IRSegmentationImageAnnotation)

        ir_annotation = ir_annotation.normalized()
        category = ir_annotation.ensure_has_one_category()

        return [
            PolygonLabelsAnnotation(
                original_width=ir_annotation.image_width,
                original_height=ir_annotation.image_height,
                value=PolygonLabelsAnnotationValue(
                    points=[[p.x * 100, p.y * 100] for p in ir_annotation.points],
                    polygonlabels=[category],
                ),
                meta=ir_annotation.meta or None,
            )
        ]
