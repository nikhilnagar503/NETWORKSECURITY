import logging
from pathlib import Path
from typing import Dict, List, Union, Optional, Literal, Callable

import yaml


from dagshub_annotation_converter.formats.common import ImageType
from dagshub_annotation_converter.formats.yolo.categories import Categories
from dagshub_annotation_converter.ir.image import IRImageAnnotationBase
from dagshub_annotation_converter.ir.image.annotations.pose import IRPoseImageAnnotation
from dagshub_annotation_converter.util.pydantic_util import ParentModel

YoloConverterFunction = Callable[
    [str, "YoloContext", Optional[int], Optional[int], Optional[ImageType]], IRImageAnnotationBase
]

YoloAnnotationTypes = Literal["bbox", "segmentation", "pose"]

logger = logging.getLogger(__name__)


class YoloContext(ParentModel):
    annotation_type: YoloAnnotationTypes
    """Type of annotations associated with this Yolo Context"""
    categories: Categories = Categories()
    """List of categories"""
    label_dir_name: str = "labels"
    """Name of the directory containing label files"""
    image_dir_name: str = "images"
    """Name of the directory containing image files"""
    keypoint_dim: Literal[2, 3] = 3
    """[For pose annotations]
    Dimension of the annotation: 2 - x, y; 3 - x, y, visibility"""
    keypoints_in_annotation: Optional[int] = None
    """[For pose annotations]
    Number of keypoints in each annotation"""
    label_extension: str = ".txt"
    """Extension of the annotation files"""
    path: Optional[Path] = None
    """Base path to the data"""
    train_path: Optional[Path] = Path(".")
    """Path to the train data, relative to the base path"""
    val_path: Optional[Path] = Path(".")
    """Path to the validation data, relative to the base path"""
    test_path: Optional[Path] = None
    """Path to the test data, relative to the base path (defaults to None, might be discovered)"""

    @staticmethod
    def from_yaml_file(file_path: Union[str, Path], annotation_type: YoloAnnotationTypes) -> "YoloContext":
        res = YoloContext(annotation_type=annotation_type)
        file_path = Path(file_path)
        with open(file_path) as f:
            meta_dict = yaml.safe_load(f)
        res.categories = YoloContext._parse_categories(meta_dict)

        if "kpt_shape" in meta_dict:
            res.keypoints_in_annotation = meta_dict["kpt_shape"][0]
            res.keypoint_dim = meta_dict["kpt_shape"][1]

        if "path" in meta_dict:
            res.path = Path(meta_dict["path"])

        if "train" in meta_dict:
            res.train_path = Path(meta_dict["train"])
        if "val" in meta_dict:
            res.val_path = Path(meta_dict["val"])
        if "test" in meta_dict:
            res.test_path = Path(meta_dict["test"])

        return res

    @staticmethod
    def _parse_categories(yolo_meta: Dict) -> Categories:
        categories = Categories()
        for cat_id, cat_name in yolo_meta["names"].items():
            categories.add(cat_name, cat_id)
        return categories

    def get_yaml_content(self, path_override: Optional[Path] = None) -> str:
        path: Optional[Path]
        if path_override is not None:
            path = path_override
        else:
            path = self.path
        if path is None:
            raise ValueError(
                "Output path is not set, either set it on the context, or provide `path_override` to get_yaml_content"
            )

        content = {
            "path": str(path.resolve()),
            "names": {cat.id: cat.name for cat in self.categories.categories},
            "nc": len(self.categories),
        }

        if self.train_path is not None:
            content["train"] = str(self.train_path)
        if self.val_path is not None:
            content["val"] = str(self.val_path)
        if self.test_path is not None:
            content["test"] = str(self.test_path)

        if self.annotation_type == "pose":
            if self.keypoints_in_annotation is None:
                raise ValueError(
                    "Please provide the number of keypoints in the annotation "
                    "by setting context.keypoint_in_annotations"
                )
            content["kpt_shape"] = [self.keypoints_in_annotation, self.keypoint_dim]

        return yaml.dump(content)

    def infer_keypoints_from_annotations(self, annotations: List[IRImageAnnotationBase]):
        if self.annotation_type != "pose":
            raise ValueError("Keypoints in annotation can only be inferred for pose annotations")
        self.keypoints_in_annotation = 0
        for ann in annotations:
            if isinstance(ann, IRPoseImageAnnotation):
                current_keypoints = len(ann.points)
                if current_keypoints > self.keypoints_in_annotation:
                    if self.keypoints_in_annotation > 0:
                        logger.warning(
                            f"Found annotation with {current_keypoints} keypoints, "
                            f"which is more than previously found maximum of {self.keypoints_in_annotation}.\n"
                            "Your annotations might be inconsistent."
                        )
                    self.keypoints_in_annotation = current_keypoints
