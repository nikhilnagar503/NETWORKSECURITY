import datetime
import logging
import random
from typing import Any, Sequence, Type, Optional, Union, cast, List, Dict

from typing_extensions import Annotated

from pydantic import SerializeAsAny, Field, BeforeValidator

from dagshub_annotation_converter.formats.label_studio.base import AnnotationResultABC, ImageAnnotationResultABC
from dagshub_annotation_converter.formats.label_studio.ellipselabels import EllipseLabelsAnnotation
from dagshub_annotation_converter.formats.label_studio.keypointlabels import KeyPointLabelsAnnotation
from dagshub_annotation_converter.formats.label_studio.polygonlabels import PolygonLabelsAnnotation
from dagshub_annotation_converter.formats.label_studio.rectanglelabels import RectangleLabelsAnnotation
from dagshub_annotation_converter.ir.image import (
    IRImageAnnotationBase,
    IRPoseImageAnnotation,
    IRBBoxImageAnnotation,
    CoordinateStyle,
    IRPosePoint,
    IRSegmentationImageAnnotation,
    IREllipseImageAnnotation,
)
from dagshub_annotation_converter.util.pydantic_util import ParentModel

task_lookup: Dict[str, Type[AnnotationResultABC]] = {
    "polygonlabels": PolygonLabelsAnnotation,
    "rectanglelabels": RectangleLabelsAnnotation,
    "keypointlabels": KeyPointLabelsAnnotation,
    "ellipselabels": EllipseLabelsAnnotation,
}

ir_annotation_lookup: Dict[Type[IRImageAnnotationBase], Type[ImageAnnotationResultABC]] = {
    IRPoseImageAnnotation: KeyPointLabelsAnnotation,
    IRBBoxImageAnnotation: RectangleLabelsAnnotation,
    IRSegmentationImageAnnotation: PolygonLabelsAnnotation,
    IREllipseImageAnnotation: EllipseLabelsAnnotation,
}

logger = logging.getLogger(__name__)


def ls_annotation_validator(v: Any) -> List[AnnotationResultABC]:
    assert isinstance(v, list)

    annotations: List[AnnotationResultABC] = []

    for raw_annotation in v:
        assert isinstance(raw_annotation, dict)
        assert "type" in raw_annotation
        assert raw_annotation["type"] in task_lookup

        ann_class = task_lookup[raw_annotation["type"]]
        annotations.append(ann_class.model_validate(raw_annotation))

    return annotations


AnnotationsList = Annotated[List[SerializeAsAny[AnnotationResultABC]], BeforeValidator(ls_annotation_validator)]


class AnnotationsContainer(ParentModel):
    completed_by: Optional[Any] = None
    result: AnnotationsList = []
    ground_truth: bool = False


class PredictionsContainer(ParentModel):
    result: AnnotationsList = []


PosePointsLookupKey = "pose_points"
PoseBBoxLookupKey = "pose_boxes"


class LabelStudioTask(ParentModel):
    annotations: List[AnnotationsContainer] = Field(
        default_factory=lambda: [],
    )

    meta: Dict[str, Any] = {}
    data: Dict[str, Any] = {}
    project: Any = 0
    created_at: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)
    updated_at: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)
    id: Any = Field(default_factory=lambda: random.randint(0, 2**63 - 1))

    user_id: int = Field(exclude=True, default=1)

    def add_annotation(self, annotation: AnnotationResultABC):
        if len(self.annotations) == 0:
            self.annotations.append(AnnotationsContainer(completed_by=self.user_id))
        self.annotations[0].result.append(annotation)

    def add_annotations(self, annotations: Sequence[AnnotationResultABC]):
        for ann in annotations:
            self.add_annotation(ann)

    def log_pose_metadata(self, bbox: RectangleLabelsAnnotation, keypoints: List[KeyPointLabelsAnnotation]):
        """
        Log additional metadata for pose annotation, that can be used later to reconstruct the pose on import

        :param bbox: Bounding box of the pose
        :param keypoints: Pose points
        """
        if PosePointsLookupKey not in self.data:
            self.data[PosePointsLookupKey] = []
        if PoseBBoxLookupKey not in self.data:
            self.data[PoseBBoxLookupKey] = []

        self.data[PoseBBoxLookupKey].append(bbox.id)
        self.data[PosePointsLookupKey].append([point.id for point in keypoints])

    def to_ir_annotations(self, filename: Optional[str] = None) -> Sequence[IRImageAnnotationBase]:
        res: List[IRImageAnnotationBase] = []
        for anns in self.annotations:
            for ann in anns.result:
                to_add = ann.to_ir_annotation()
                for a in to_add:
                    # Carry over extra values from the annotation
                    if ann.__pydantic_extra__ is not None:
                        a.__pydantic_extra__ = ann.__pydantic_extra__.copy()
                    if filename is not None:
                        a.filename = filename
                res.extend(to_add)
        res = self._reimport_poses(res)
        return res

    def _reimport_poses(self, annotations: List[IRImageAnnotationBase]) -> List[IRImageAnnotationBase]:
        if PosePointsLookupKey not in self.data or PoseBBoxLookupKey not in self.data:
            return annotations

        # Build a dictionary of all annotation indexes in the task by id
        # Keep the indexes instead of annotations, so we can pop them for convenience
        annotation_lookup = {ann.imported_id: ann for ann in annotations if ann.imported_id is not None}
        pose_bboxes: List[str] = self.data[PoseBBoxLookupKey]
        pose_points: List[List[str]] = self.data[PosePointsLookupKey]

        annotations_to_remove: set[str] = set()
        poses: List[IRPoseImageAnnotation] = []

        for bbox_id, point_ids in zip(pose_bboxes, pose_points):
            # Fetch the bbox of the pose
            maybe_bbox = annotation_lookup.get(bbox_id)
            bbox: Optional[IRBBoxImageAnnotation] = None
            category: Optional[str] = None
            image_width: Optional[int] = None
            image_height: Optional[int] = None
            filename: Optional[str] = None
            if maybe_bbox is None:
                logger.warning(
                    f"Bounding box of pose with annotation ID {bbox_id} "
                    f"does not exist in the task but exists in metadata"
                )
            elif not isinstance(maybe_bbox, IRBBoxImageAnnotation):
                logger.warning(f"Bounding box of pose with annotation ID {bbox_id} is not a bounding box annotation")
            else:
                bbox = maybe_bbox
                category = bbox.ensure_has_one_category()
                image_height = bbox.image_height
                image_width = bbox.image_width
                filename = bbox.filename
                annotations_to_remove.add(bbox_id)
            # Fetch the points
            points: List[IRPosePoint] = []
            for point_id in point_ids:
                maybe_point = annotation_lookup.get(point_id)
                if maybe_point is None:
                    logger.warning(
                        f"Point of pose with annotation ID {bbox_id} does not exist in the task but exists in metadata"
                    )
                    continue
                elif not isinstance(maybe_point, IRPoseImageAnnotation):
                    logger.warning(f"Point of pose with annotation ID {point_id} is not a point annotation")
                    continue
                else:
                    if category is None:
                        category = maybe_point.ensure_has_one_category()
                    if image_width is None:
                        image_width = maybe_point.image_width
                    if image_height is None:
                        image_height = maybe_point.image_height
                    if filename is None:
                        filename = maybe_point.filename
                    points.extend(maybe_point.points)
                    annotations_to_remove.add(point_id)

            if len(points) == 0:
                logger.warning(f"No points found for the pose on LS Task {self.id}")
                return annotations

            assert category is not None
            assert image_width is not None
            assert image_height is not None

            sum_annotation = IRPoseImageAnnotation.from_points(
                categories={category: 1.0},
                points=points,
                coordinate_style=CoordinateStyle.NORMALIZED,
                image_width=image_width,
                image_height=image_height,
                filename=filename,
            )
            if bbox is not None:
                sum_annotation.width = bbox.width
                sum_annotation.height = bbox.height
                sum_annotation.top = bbox.top
                sum_annotation.left = bbox.left

            poses.append(sum_annotation)

        logger.debug(f"Consolidated {len(poses)} pose annotations for LS Task {self.id}")

        if len(poses) == 0:
            return annotations

        annotations = list(filter(lambda ann: ann.imported_id not in annotations_to_remove, annotations))
        annotations.extend(poses)
        return annotations

    def add_ir_annotation(self, ann: IRImageAnnotationBase):
        ls_ann_type = ir_annotation_lookup.get(type(ann))

        if ls_ann_type is None:
            raise ValueError(f"Unsupported IR annotation type: {type(ann)}")

        ls_anns = ls_ann_type.from_ir_annotation(ann)
        # carry over the extras
        if ann.__pydantic_extra__ is not None:
            for ls_ann in ls_anns:
                ls_ann.__pydantic_extra__ = ann.__pydantic_extra__.copy()
        self.add_annotations(ls_anns)

        # For pose: log additional metadata
        # If we got back just one annotation, then it's a single point, otherwise it's [bounding box, *points]
        if isinstance(ann, IRPoseImageAnnotation) and len(ls_anns) > 1:
            bbox = cast(RectangleLabelsAnnotation, ls_anns[0])
            keypoints = cast(List[KeyPointLabelsAnnotation], ls_anns[1:])
            self.log_pose_metadata(bbox, keypoints)

    def add_ir_annotations(self, anns: Sequence[IRImageAnnotationBase]):
        for ann in anns:
            self.add_ir_annotation(ann)

    @staticmethod
    def from_ir_annotations(anns: Sequence[IRImageAnnotationBase]) -> "LabelStudioTask":
        res = LabelStudioTask()
        res.add_ir_annotations(anns)
        return res


def parse_ls_task(task: Union[str, bytes]) -> LabelStudioTask:
    return LabelStudioTask.model_validate_json(task)
