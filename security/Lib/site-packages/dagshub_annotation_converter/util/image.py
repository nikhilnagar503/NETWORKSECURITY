from pathlib import Path
from typing import Set

from dagshub_annotation_converter.util.path import get_extension

_supported_image_formats = None


def supported_image_formats() -> Set[str]:
    global _supported_image_formats
    if _supported_image_formats is None:
        from PIL import Image

        exts = Image.registered_extensions()
        supported = {ex for ex, f in exts.items() if f in Image.OPEN}
        _supported_image_formats = supported
    return _supported_image_formats


def is_image(path: Path) -> bool:
    return get_extension(path) in supported_image_formats()
