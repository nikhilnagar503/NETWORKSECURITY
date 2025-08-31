from dagshub_annotation_converter.ir.image.annotations.base import IRImageAnnotationBase


class IRBBoxImageAnnotation(IRImageAnnotationBase):
    top: float
    left: float
    width: float
    height: float
    rotation: float = 0.0
    """Rotation in degrees (pivot point - top-left)"""

    def _normalize(self):
        self.top = self.top / self.image_height
        self.left = self.left / self.image_width
        self.width = self.width / self.image_width
        self.height = self.height / self.image_height

    def _denormalize(self):
        self.top = self.top * self.image_height
        self.left = self.left * self.image_width
        self.width = self.width * self.image_width
        self.height = self.height * self.image_height
