from typing import Tuple, List

from lxml.etree import ElementBase

from dagshub_annotation_converter.formats.cvat.context import parse_image_tag, parse_metadata
from dagshub_annotation_converter.ir.image import IRPoseImageAnnotation, IRPosePoint, CoordinateStyle

_keys = {"label", "points", "occluded"}


def parse_skeleton(elem: ElementBase, containing_image: ElementBase) -> IRPoseImageAnnotation:
    # Points also contain the labels, for consistent ordering in LS, they are later sorted
    points: List[Tuple[str, IRPosePoint]] = []

    category = str(elem.attrib["label"])

    image_info = parse_image_tag(containing_image)

    for point_elem in elem:
        x, y = point_elem.attrib["points"].split(",")
        points.append(
            (
                point_elem.attrib["label"],
                IRPosePoint(x=float(x), y=float(y), visible=point_elem.attrib["occluded"] == "0"),
            )
        )

    all_labels_ints = all(map(lambda tup: tup[0].isdigit(), points))

    # sort points by the label
    if all_labels_ints:
        points = sorted(points, key=lambda tup: int(tup[0]))
    else:
        points = sorted(points, key=lambda tup: tup[0])

    res_points = list(map(lambda tup: tup[1], points))

    return IRPoseImageAnnotation.from_points(
        categories={category: 1.0},
        points=res_points,
        coordinate_style=CoordinateStyle.DENORMALIZED,
        image_width=image_info.width,
        image_height=image_info.height,
        filename=image_info.name,
        meta=parse_metadata(elem, _keys),
    )
