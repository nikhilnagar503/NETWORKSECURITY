import math
from typing import Tuple

from lxml.etree import ElementBase

from dagshub_annotation_converter.formats.cvat.context import parse_image_tag, parse_metadata
from dagshub_annotation_converter.ir.image import IRBBoxImageAnnotation, CoordinateStyle

_keys = {"xtl", "ytl", "xbr", "ybr", "rotation", "label"}


def calculate_bbox(xtl, ytl, xbr, ybr, rotation: float) -> Tuple[int, int, int, int, float]:
    """
    Converts the CVAT rotation bounding box to the dagshub one.

    CVAT rotates counter-clockwise around the center point.
    We use LS format, which rotates clockwise around the top-left point

    :return: coordinates of the top-left point, width, height, rotation
    """
    if rotation == 0.0:
        return xtl, ytl, xbr - xtl, ybr - ytl, rotation

    # If rotation is set, then we need to:
    # - pivot from rotating from center, to rotating from top-left
    # - change rotation from counter-clockwise, to clock-wise
    # This can be done by rotating the top-left point relative to the center, the rotation will stay the same
    xc = xtl + (xbr - xtl) / 2
    yc = ytl + (ybr - ytl) / 2

    cos = math.cos(math.radians(rotation))
    sin = math.sin(math.radians(rotation))

    x1 = xc + cos * (xtl - xc) - sin * (ytl - yc)
    y1 = yc + sin * (xtl - xc) + cos * (ytl - yc)

    # The widths should stay the same
    width = xbr - xtl
    height = ybr - ytl

    # Rotation degrees also stay the same
    return round(x1), round(y1), width, height, rotation


def parse_box(elem: ElementBase, containing_image: ElementBase) -> IRBBoxImageAnnotation:
    top = float(elem.attrib["ytl"])
    bottom = float(elem.attrib["ybr"])
    left = float(elem.attrib["xtl"])
    right = float(elem.attrib["xbr"])

    rotation = float(elem.attrib.get("rotation", 0.0))

    left, top, width, height, rotation = calculate_bbox(left, top, right, bottom, rotation)

    image_info = parse_image_tag(containing_image)

    return IRBBoxImageAnnotation(
        categories={str(elem.attrib["label"]): 1.0},
        top=top,
        left=left,
        width=width,
        height=height,
        rotation=rotation,
        image_width=image_info.width,
        image_height=image_info.height,
        filename=image_info.name,
        coordinate_style=CoordinateStyle.DENORMALIZED,
        meta=parse_metadata(elem, _keys),
    )
