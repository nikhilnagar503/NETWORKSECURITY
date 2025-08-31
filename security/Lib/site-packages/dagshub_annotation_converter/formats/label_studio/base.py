import uuid
from abc import abstractmethod
from typing import Sequence, Optional, Any

from pydantic import Field

from dagshub_annotation_converter.ir.image import IRImageAnnotationBase
from dagshub_annotation_converter.ir.image.annotations.base import IRAnnotationBase
from dagshub_annotation_converter.util.pydantic_util import ParentModel


class AnnotationResultABC(ParentModel):
    @abstractmethod
    def to_ir_annotation(self) -> Sequence[IRAnnotationBase]:
        """
        Convert LabelStudio annotation to 0..n DAGsHub IR annotations.

        Note: This method has a potential side effect of adding new categories.
        """
        ...

    @staticmethod
    @abstractmethod
    def from_ir_annotation(ir_annotation: IRImageAnnotationBase) -> Sequence["AnnotationResultABC"]:
        """
        Convert DagsHub IR annotation to 1..n LabelStudio annotations.
        """
        ...


class ImageAnnotationResultABC(AnnotationResultABC):
    original_width: int
    original_height: int
    image_rotation: float = 0.0
    type: str
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:10])
    origin: str = "manual"
    to_name: str = "image"
    from_name: str = "label"
    score: Optional[float] = None
    """For predictions, the score of the prediction."""
    meta: Optional[dict[str, Any]] = None

    @abstractmethod
    def to_ir_annotation(self) -> Sequence[IRImageAnnotationBase]:
        """
        Convert LabelStudio annotation to 1..n DagsHub IR annotations.
        """
        ...

    @staticmethod
    @abstractmethod
    def from_ir_annotation(ir_annotation: IRImageAnnotationBase) -> Sequence["ImageAnnotationResultABC"]:
        """
        Convert DagsHub IR annotation to 1..n LabelStudio annotations.
        """
        ...
