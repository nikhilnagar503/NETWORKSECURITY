from typing import Callable, Dict

from lxml.etree import ElementBase

from .box import parse_box
from .ellipse import parse_ellipse
from .polygon import parse_polygon
from .points import parse_points
from .skeleton import parse_skeleton
from dagshub_annotation_converter.ir.image import IRImageAnnotationBase

CVATParserFunction = Callable[[ElementBase, ElementBase], IRImageAnnotationBase]

annotation_parsers: Dict[str, CVATParserFunction] = {
    "box": parse_box,
    "polygon": parse_polygon,
    "points": parse_points,
    "skeleton": parse_skeleton,
    "ellipse": parse_ellipse,
}
