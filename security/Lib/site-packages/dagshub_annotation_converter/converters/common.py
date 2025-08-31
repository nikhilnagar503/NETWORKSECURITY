from typing import Sequence, Mapping, List, Dict

from dagshub_annotation_converter.ir.image import IRImageAnnotationBase


def group_annotations_by_filename(
    annotations: Sequence[IRImageAnnotationBase],
) -> Mapping[str, Sequence[IRImageAnnotationBase]]:
    res: Dict[str, List[IRImageAnnotationBase]] = {}
    for ann in annotations:
        if ann.filename is None:
            raise ValueError(f"An annotation {ann} doesn't have a filename associated, aborting")
        if ann.filename not in res:
            res[ann.filename] = []
        res[ann.filename].append(ann)
    return res
