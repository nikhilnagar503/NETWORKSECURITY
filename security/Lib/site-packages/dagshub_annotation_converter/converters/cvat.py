import logging
from collections import defaultdict
from os import PathLike
from typing import Sequence, List, Dict, Union, Optional
from zipfile import ZipFile

import lxml.etree

from dagshub_annotation_converter.formats.cvat import annotation_parsers
from dagshub_annotation_converter.formats.cvat.context import parse_image_tag
from dagshub_annotation_converter.ir.image import IRImageAnnotationBase, IRBBoxImageAnnotation, IRPoseImageAnnotation
from dagshub_annotation_converter.features import ConverterFeatures

logger = logging.getLogger(__name__)


def parse_image_annotations(img: lxml.etree.ElementBase) -> Sequence[IRImageAnnotationBase]:
    annotations: List[IRImageAnnotationBase] = []
    for annotation_elem in img:
        annotation_type = annotation_elem.tag
        if annotation_type not in annotation_parsers:
            logger.warning(f"Unknown CVAT annotation type {annotation_type}")
            continue
        annotations.append(annotation_parsers[annotation_type](annotation_elem, img))

    annotations = _maybe_group_poses(annotations)

    return annotations


def _maybe_group_poses(annotations: List[IRImageAnnotationBase]) -> List[IRImageAnnotationBase]:
    if not ConverterFeatures.cvat_pose_grouping_by_group_id_enabled():
        return annotations
    res = []
    annotation_groups: Dict[str, List[IRImageAnnotationBase]] = defaultdict(list)
    for annotation in annotations:
        group_id = annotation.meta.get("group_id")
        if group_id is None:
            res.append(annotation)
        else:
            annotation_groups[group_id].append(annotation)

    for group_id, group_annotations in annotation_groups.items():
        if len(group_annotations) == 1:
            res.extend(group_annotations)
            continue

        bbox_count = sum((isinstance(ann, IRBBoxImageAnnotation) for ann in group_annotations))
        point_count = sum((isinstance(ann, IRPoseImageAnnotation) for ann in group_annotations))

        # If we have more than one bbox or point annotation in the group, don't bother trying to group
        if bbox_count != 1 or point_count != 1:
            res.extend(group_annotations)
            continue

        group_res = []
        bbox_ann: Optional[IRBBoxImageAnnotation] = None
        pose_ann: Optional[IRPoseImageAnnotation] = None

        for ann in group_annotations:
            if isinstance(ann, IRBBoxImageAnnotation):
                bbox_ann = ann
            elif isinstance(ann, IRPoseImageAnnotation):
                pose_ann = ann
            else:
                group_res.append(ann)

        assert bbox_ann is not None and pose_ann is not None

        # If there's somehow multiple labels (shouldn't be happening in CVAT), don't group
        if not (bbox_ann.has_one_category() and pose_ann.has_one_category()):
            res.extend(group_annotations)
            continue

        # Different categories - don't group
        if bbox_ann.ensure_has_one_category() != pose_ann.ensure_has_one_category():
            res.extend(group_annotations)
            continue

        pose_ann.width = bbox_ann.width
        pose_ann.height = bbox_ann.height
        pose_ann.top = bbox_ann.top
        pose_ann.left = bbox_ann.left

        group_res.append(pose_ann)
        res.extend(group_res)

    return res


def load_cvat_from_xml_string(
    xml_text: bytes,
) -> Dict[str, Sequence[IRImageAnnotationBase]]:
    annotations = {}
    root_elem = lxml.etree.XML(xml_text)

    for image_node in root_elem.xpath("//image"):
        image_info = parse_image_tag(image_node)
        annotations[image_info.name] = parse_image_annotations(image_node)

    return annotations


def load_cvat_from_xml_file(xml_file: Union[str, PathLike]) -> Dict[str, Sequence[IRImageAnnotationBase]]:
    with open(xml_file, "rb") as f:
        return load_cvat_from_xml_string(f.read())


def load_cvat_from_zip(zip_path: Union[str, PathLike]) -> Dict[str, Sequence[IRImageAnnotationBase]]:
    with ZipFile(zip_path) as proj_zip:
        with proj_zip.open("annotations.xml") as f:
            return load_cvat_from_xml_string(f.read())
