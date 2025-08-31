import logging
from typing import Optional, Union


from dagshub_annotation_converter.formats.common import (
    ImageType,
    determine_image_dimensions,
)
from dagshub_annotation_converter.formats.yolo.categories import determine_category
from dagshub_annotation_converter.formats.yolo.context import YoloContext
from dagshub_annotation_converter.ir.image import CoordinateStyle
from dagshub_annotation_converter.ir.image.annotations.bbox import IRBBoxImageAnnotation

logger = logging.getLogger(__name__)


def import_bbox(
    category: Union[int, str],
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    context: YoloContext,
    image_width: Optional[int] = None,
    image_height: Optional[int] = None,
    image: Optional[ImageType] = None,
) -> IRBBoxImageAnnotation:
    image_width, image_height = determine_image_dimensions(
        image_width=image_width, image_height=image_height, image=image
    )
    parsed_category = determine_category(category, context.categories)
    return IRBBoxImageAnnotation(
        categories={parsed_category.name: 1.0},
        top=center_y - height / 2,
        left=center_x - width / 2,
        width=width,
        height=height,
        image_width=image_width,
        image_height=image_height,
        coordinate_style=CoordinateStyle.NORMALIZED,
    )


def import_bbox_from_string(
    annotation: str,
    context: YoloContext,
    image_width: Optional[int] = None,
    image_height: Optional[int] = None,
    image: Optional[ImageType] = None,
) -> IRBBoxImageAnnotation:
    if len(annotation.split("\n")) > 1:
        raise ValueError("Please pass one annotation at a time")
    parts = annotation.strip().split(" ")
    category = int(parts[0])
    center_x = float(parts[1])
    center_y = float(parts[2])
    width = float(parts[3])
    height = float(parts[4])

    return import_bbox(
        category=category,
        center_x=center_x,
        center_y=center_y,
        width=width,
        height=height,
        context=context,
        image_width=image_width,
        image_height=image_height,
        image=image,
    )


def export_bbox(
    annotation: IRBBoxImageAnnotation,
    context: YoloContext,
) -> str:
    if annotation.rotation != 0.0:
        logger.warning(
            f"Bounding box for file {annotation.filename} has a not-zero rotation. "
            f"This is not supported by YOLO format."
        )
    category = annotation.ensure_has_one_category()
    center_x = annotation.left + annotation.width / 2
    center_y = annotation.top + annotation.height / 2
    cat_id = context.categories[category].id
    return f"{cat_id} {center_x} {center_y} {annotation.width} {annotation.height}"
