from typing import TYPE_CHECKING, Sequence

from .context import YoloAnnotationTypes
from dagshub_annotation_converter.ir.image.annotations.base import IRAnnotationBase
from dagshub_annotation_converter.ir.image import (
    IRBBoxImageAnnotation,
    IRPoseImageAnnotation,
    IRSegmentationImageAnnotation,
    CoordinateStyle,
    IRSegmentationPoint,
    IRPosePoint,
)

if TYPE_CHECKING:
    import ultralytics.engine.results


def _import_result_bboxes(result: "ultralytics.engine.results.Results") -> Sequence[IRBBoxImageAnnotation]:
    res = []
    for i, cat_n in enumerate(result.boxes.cls):
        cat = result.names[cat_n.item()]
        center_x = result.boxes.xywh[i][0]
        center_y = result.boxes.xywh[i][1]

        width = result.boxes.xywh[i][2]
        height = result.boxes.xywh[i][3]

        x_tl = center_x - width / 2
        y_tl = center_y - height / 2

        res.append(
            IRBBoxImageAnnotation(
                categories={cat: result.boxes.conf[i]},
                coordinate_style=CoordinateStyle.DENORMALIZED,
                image_width=result.orig_shape[1],
                image_height=result.orig_shape[0],
                left=x_tl,
                top=y_tl,
                width=width,
                height=height,
            )
        )
    return res


def _import_result_segmentations(
    result: "ultralytics.engine.results.Results",
) -> Sequence[IRSegmentationImageAnnotation]:
    res = []
    for i, cat_n in enumerate(result.boxes.cls):
        cat = result.names[cat_n.item()]
        points = [IRSegmentationPoint(x=x, y=y) for x, y in result.masks.xy[i]]
        res.append(
            IRSegmentationImageAnnotation(
                categories={cat: result.boxes.conf[i]},
                points=points,
                coordinate_style=CoordinateStyle.DENORMALIZED,
                image_width=result.orig_shape[1],
                image_height=result.orig_shape[0],
            )
        )
    return res


def _import_result_poses(result: "ultralytics.engine.results.Results") -> Sequence[IRPoseImageAnnotation]:
    res = []
    for i, cat_n in enumerate(result.boxes.cls):
        cat = result.names[cat_n.item()]
        points = [IRPosePoint(x=x, y=y) for x, y in result.keypoints.xy[i]]

        center_x = result.boxes.xywh[i][0]
        center_y = result.boxes.xywh[i][1]

        width = result.boxes.xywh[i][2]
        height = result.boxes.xywh[i][3]

        x_tl = center_x - width / 2
        y_tl = center_y - height / 2

        res.append(
            IRPoseImageAnnotation(
                categories={cat: result.boxes.conf[i]},
                left=x_tl,
                top=y_tl,
                width=width,
                height=height,
                points=points,
                coordinate_style=CoordinateStyle.DENORMALIZED,
                image_width=result.orig_shape[1],
                image_height=result.orig_shape[0],
            )
        )
    return res


def import_yolo_result(
    annotation_type: YoloAnnotationTypes, result: "ultralytics.engine.results.Results"
) -> Sequence[IRAnnotationBase]:
    if annotation_type == "bbox":
        return _import_result_bboxes(result)
    elif annotation_type == "segmentation":
        return _import_result_segmentations(result)
    elif annotation_type == "pose":
        return _import_result_poses(result)
    else:
        raise ValueError(f"Unknown annotation type: {annotation_type}")
