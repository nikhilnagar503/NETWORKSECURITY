from pathlib import Path
from typing import Union, Optional, Tuple

import PIL.Image

ImageType = Union[str, Path, PIL.Image.Image]


def determine_image_dimensions(
    image_width: Optional[int] = None,
    image_height: Optional[int] = None,
    image: Optional[ImageType] = None,
) -> Tuple[int, int]:
    if image_width is not None and image_height is not None:
        return image_width, image_height
    if image is None:
        raise ValueError("Either image or image_width and image_height should be provided")

    if not isinstance(image, PIL.Image.Image):
        image = PIL.Image.open(image)
    return image.size
