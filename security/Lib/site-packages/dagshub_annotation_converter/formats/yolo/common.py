from typing import Mapping, Any, Callable, Type

from .context import YoloAnnotationTypes, YoloContext, YoloConverterFunction
from .bbox import export_bbox, import_bbox_from_string
from .segmentation import export_segmentation, import_segmentation_from_string
from .pose import export_pose, import_pose_from_string

from dagshub_annotation_converter.ir.image import (
    IRBBoxImageAnnotation,
    IRSegmentationImageAnnotation,
    IRPoseImageAnnotation,
)
from dagshub_annotation_converter.ir.image.annotations.base import IRAnnotationBase

# Type actually has to be IRAnnotationBase, but it messes up MyPy
YoloExportFunctionType = Callable[[Any, YoloContext], str]

export_lookup: Mapping[YoloAnnotationTypes, YoloExportFunctionType] = {
    "bbox": export_bbox,
    "segmentation": export_segmentation,
    "pose": export_pose,
}

allowed_annotation_types = {
    "bbox": IRBBoxImageAnnotation,
    "segmentation": IRSegmentationImageAnnotation,
    "pose": IRPoseImageAnnotation,
}

import_lookup: Mapping[YoloAnnotationTypes, YoloConverterFunction] = {
    "bbox": import_bbox_from_string,
    "segmentation": import_segmentation_from_string,
    "pose": import_pose_from_string,
}

ir_mapping: Mapping[Type[IRAnnotationBase], YoloAnnotationTypes] = {
    IRBBoxImageAnnotation: "bbox",
    IRSegmentationImageAnnotation: "segmentation",
    IRPoseImageAnnotation: "pose",
}
