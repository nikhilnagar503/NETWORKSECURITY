from typing import Union, Optional, Tuple, Sequence

from dagshub_annotation_converter.formats.common import (
    ImageType,
    determine_image_dimensions,
)
from dagshub_annotation_converter.formats.yolo.categories import determine_category
from dagshub_annotation_converter.formats.yolo.context import YoloContext
from dagshub_annotation_converter.ir.image import CoordinateStyle
from dagshub_annotation_converter.ir.image.annotations.segmentation import (
    IRSegmentationImageAnnotation,
    IRSegmentationPoint,
)


def import_segmentation(
    category: Union[int, str],
    points: Sequence[Tuple[float, float]],
    context: YoloContext,
    image_width: Optional[int] = None,
    image_height: Optional[int] = None,
    image: Optional[ImageType] = None,
):
    image_width, image_height = determine_image_dimensions(
        image_width=image_width, image_height=image_height, image=image
    )
    parsed_category = determine_category(category, context.categories)

    return IRSegmentationImageAnnotation(
        categories={parsed_category.name: 1.0},
        image_width=image_width,
        image_height=image_height,
        coordinate_style=CoordinateStyle.NORMALIZED,
        points=[IRSegmentationPoint(x=x, y=y) for x, y in points],
    )


def import_segmentation_from_string(
    annotation: str,
    context: YoloContext,
    image_width: Optional[int] = None,
    image_height: Optional[int] = None,
    image: Optional[ImageType] = None,
) -> IRSegmentationImageAnnotation:
    if len(annotation.split("\n")) > 1:
        raise ValueError("Please pass one annotation at a time")
    parts = annotation.strip().split(" ")
    category = int(parts[0])
    points = [(float(parts[i]), float(parts[i + 1])) for i in range(1, len(parts), 2)]
    return import_segmentation(
        category=category,
        points=points,
        context=context,
        image_width=image_width,
        image_height=image_height,
        image=image,
    )


def export_segmentation(annotation: IRSegmentationImageAnnotation, context: YoloContext) -> str:
    category = annotation.ensure_has_one_category()
    cat_id = context.categories[category].id
    return " ".join(
        [
            str(cat_id),
            *[f"{point.x} {point.y}" for point in annotation.points],
        ]
    )
