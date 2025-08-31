from dagshub_annotation_converter.ir.image import IRImageAnnotationBase


class IREllipseImageAnnotation(IRImageAnnotationBase):
    center_x: float
    center_y: float
    radius_x: float
    radius_y: float
    rotation: float = 0.0
    """Rotation in degrees (pivot point - top-left)"""

    def _normalize(self):
        self.center_x = self.center_x / self.image_width
        self.center_y = self.center_y / self.image_height
        self.radius_x = self.radius_x / self.image_width
        self.radius_y = self.radius_y / self.image_height

    def _denormalize(self):
        self.center_x = self.center_x * self.image_width
        self.center_y = self.center_y * self.image_height
        self.radius_x = self.radius_x * self.image_width
        self.radius_y = self.radius_y * self.image_height
