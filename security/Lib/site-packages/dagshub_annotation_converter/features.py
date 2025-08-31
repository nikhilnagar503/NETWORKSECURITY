import os
from functools import lru_cache


FEATURE_CVAT_POSE_GROUPING_KEY = "DAGSHUB_ANNOTATION_EXPERIMENTAL_CVAT_POSE_GROUPING_BY_GROUP_ID_ENABLED"


def _is_enabled(key):
    return os.environ.get(key, "f").lower() in ("true", "1", "t")


class ConverterFeatures:
    @staticmethod
    @lru_cache
    def cvat_pose_grouping_by_group_id_enabled() -> bool:
        """
        When importing CVAT annotations, groups together pose + bbox, as long as they have the same group_id.

        Limitations:
        - Only one bbox and one of either points or skeletons annotation per group_id is allowed.
          If this is not satisfied, then the annotations in the group will be left as is.
        - bbox and pose need to have the same label

        Side Effects:
        - Might change the order of annotations in the output.
        """
        # return True
        return _is_enabled(FEATURE_CVAT_POSE_GROUPING_KEY)
