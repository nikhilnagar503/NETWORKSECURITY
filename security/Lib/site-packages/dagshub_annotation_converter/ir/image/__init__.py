from .common import CoordinateStyle
from .annotations.base import IRImageAnnotationBase
from .annotations.pose import IRPoseImageAnnotation, IRPosePoint
from .annotations.segmentation import IRSegmentationImageAnnotation, IRSegmentationPoint
from .annotations.bbox import IRBBoxImageAnnotation
from .annotations.ellipse import IREllipseImageAnnotation

__all__ = [
    "CoordinateStyle",
    "IRImageAnnotationBase",
    "IRPoseImageAnnotation",
    "IRPosePoint",
    "IRSegmentationImageAnnotation",
    "IRSegmentationPoint",
    "IRBBoxImageAnnotation",
    "IREllipseImageAnnotation",
]
