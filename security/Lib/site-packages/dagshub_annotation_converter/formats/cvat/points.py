from typing import List

from lxml.etree import ElementBase

from dagshub_annotation_converter.formats.cvat.context import parse_image_tag, parse_metadata
from dagshub_annotation_converter.ir.image import IRPoseImageAnnotation, IRPosePoint, CoordinateStyle

_keys = {"label", "points"}


def parse_points(elem: ElementBase, containing_image: ElementBase) -> IRPoseImageAnnotation:
    points: List[IRPosePoint] = []

    category = str(elem.attrib["label"])

    image_info = parse_image_tag(containing_image)

    for point_str in elem.attrib["points"].split(";"):
        x, y = point_str.split(",")
        points.append(IRPosePoint(x=float(x), y=float(y)))

    return IRPoseImageAnnotation.from_points(
        categories={category: 1.0},
        points=points,
        coordinate_style=CoordinateStyle.DENORMALIZED,
        image_width=image_info.width,
        image_height=image_info.height,
        filename=image_info.name,
        meta=parse_metadata(elem, _keys),
    )
