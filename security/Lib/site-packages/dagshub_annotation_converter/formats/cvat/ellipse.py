from lxml.etree import ElementBase

from dagshub_annotation_converter.formats.cvat.context import parse_image_tag, parse_metadata
from dagshub_annotation_converter.ir.image import IREllipseImageAnnotation, CoordinateStyle

_keys = {"cx", "cy", "rx", "ry", "rotation", "label"}


def parse_ellipse(elem: ElementBase, containing_image: ElementBase) -> IREllipseImageAnnotation:
    center_x = float(elem.attrib["cx"])
    center_y = float(elem.attrib["cy"])
    radius_x = float(elem.attrib["rx"])
    radius_y = float(elem.attrib["ry"])

    rotation = float(elem.attrib.get("rotation", 0.0))

    image_info = parse_image_tag(containing_image)

    return IREllipseImageAnnotation(
        categories={str(elem.attrib["label"]): 1.0},
        center_x=round(center_x),
        center_y=round(center_y),
        radius_x=radius_x,
        radius_y=radius_y,
        rotation=rotation,
        image_width=image_info.width,
        image_height=image_info.height,
        filename=image_info.name,
        coordinate_style=CoordinateStyle.DENORMALIZED,
        meta=parse_metadata(elem, _keys),
    )
