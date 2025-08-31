from abc import abstractmethod
from typing import Optional, Dict, Any

from pydantic import Field
from typing_extensions import Self

from dagshub_annotation_converter.ir.image import CoordinateStyle
from dagshub_annotation_converter.util.pydantic_util import ParentModel


class MultipleCategoriesError(Exception):
    def __init__(self, ann: "IRAnnotationBase"):
        super().__init__()
        self.ann = ann

    def __str__(self):
        return (
            f"Annotation of type {type(self.ann)}, file {self.ann.filename} has multiple categories.\n"
            f"This is not supported for converting to other annotation formats.\n"
            f"Annotation:\n"
            f"\t{self.ann}"
        )


class IRAnnotationBase(ParentModel):
    """
    Base class for all annotations and predictions
    """

    filename: Optional[str] = None

    categories: Dict[str, float]
    """Categories and their confidence. 1 means 100% confidence or ground truth."""
    coordinate_style: CoordinateStyle
    imported_id: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

    def with_filename(self, filename: str) -> Self:
        self.filename = filename
        return self

    def has_one_category(self) -> bool:
        return len(self.categories) == 1

    def ensure_has_one_category(self) -> str:
        """Makes sure that the annotation has one category and returns it."""
        if not self.has_one_category():
            raise MultipleCategoriesError(self)
        return next(iter(self.categories.keys()))

    def normalized(self) -> Self:
        """
        Returns a copy with all parameters in the annotation normalized
        """
        if self.coordinate_style == CoordinateStyle.NORMALIZED:
            return self.model_copy()
        normalized = self.model_copy()
        normalized._normalize()
        normalized.coordinate_style = CoordinateStyle.NORMALIZED
        return normalized

    @abstractmethod
    def _normalize(self):
        """
        Every annotation should implement this to normalize itself
        """
        ...

    def denormalized(self) -> Self:
        """
        Returns a copy with all parameters in the annotation denormalized
        """
        if self.coordinate_style == CoordinateStyle.DENORMALIZED:
            return self.model_copy()
        denormalized = self.model_copy()
        denormalized._denormalize()
        denormalized.coordinate_style = CoordinateStyle.DENORMALIZED
        return denormalized

    @abstractmethod
    def _denormalize(self):
        """
        Every annotation should implement this to denormalize itself
        """
        ...


class IRImageAnnotationBase(IRAnnotationBase):
    """
    Common class for all intermediary image annotations
    """

    image_width: int
    image_height: int

    @abstractmethod
    def _normalize(self):
        """
        Every annotation should implement this to normalize itself
        """
        ...

    @abstractmethod
    def _denormalize(self):
        """
        Every annotation should implement this to denormalize itself
        """
        ...
