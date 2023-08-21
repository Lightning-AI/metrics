# Copyright The PyTorch Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Optional

import torch

from torchmetrics.utilities.imports import _TORCHVISION_AVAILABLE, _TORCHVISION_GREATER_EQUAL_0_13

if _TORCHVISION_AVAILABLE and _TORCHVISION_GREATER_EQUAL_0_13:
    from torchvision.ops import complete_box_iou
else:
    complete_box_iou = None
    __doctest_skip__ = ["complete_intersection_over_union"]

__doctest_requires__ = {("complete_intersection_over_union",): ["torchvision"]}


def _ciou_update(
    preds: torch.Tensor, target: torch.Tensor, iou_threshold: Optional[float], replacement_val: float = 0
) -> torch.Tensor:
    iou = complete_box_iou(preds, target)
    if iou_threshold is not None:
        iou[iou < iou_threshold] = replacement_val
    return iou.diag()


def _ciou_compute(iou: torch.Tensor, aggregate: bool = True) -> torch.Tensor:
    if not aggregate:
        return iou
    return iou.mean() if iou.numel() > 0 else torch.tensor(0.0, device=iou.device)


def complete_intersection_over_union(
    preds: torch.Tensor,
    target: torch.Tensor,
    iou_threshold: Optional[float] = None,
    replacement_val: float = 0,
    aggregate: bool = True,
) -> torch.Tensor:
    r"""Compute Complete Intersection over Union (`CIOU`_) between two sets of boxes.

    Both sets of boxes are expected to be in (x1, y1, x2, y2) format with 0 <= x1 < x2 and 0 <= y1 < y2.

    Args:
        preds:
            The input tensor containing the predicted bounding boxes.
        target:
            The tensor containing the ground truth.
        iou_threshold:
            Optional IoU thresholds for evaluation. If set to `None` the threshold is ignored.
        replacement_val:
            Value to replace values under the threshold with.
        aggregate:
            Return the average value instead of the per box pair IoU value.

    Example::
        By default iou is aggregated across all box pairs:

        >>> import torch
        >>> from torchmetrics.functional.detection import complete_intersection_over_union
        >>> preds = torch.tensor(
        ...     [
        ...         [296.55, 93.96, 314.97, 152.79],
        ...         [328.94, 97.05, 342.49, 122.98],
        ...         [356.62, 95.47, 372.33, 147.55],
        ...     ]
        ... )
        >>> target = torch.tensor(
        ...     [
        ...         [300.00, 100.00, 315.00, 150.00],
        ...         [330.00, 100.00, 350.00, 125.00],
        ...         [350.00, 100.00, 375.00, 150.00],
        ...     ]
        ... )
        >>> complete_intersection_over_union(preds, target)
        tensor(0.5790)

    Example::
        By setting `aggregate=False` the IoU score per prediction and target boxes is returned:

        >>> import torch
        >>> from torchmetrics.functional.detection import complete_intersection_over_union
        >>> preds = torch.tensor(
        ...     [
        ...         [296.55, 93.96, 314.97, 152.79],
        ...         [328.94, 97.05, 342.49, 122.98],
        ...         [356.62, 95.47, 372.33, 147.55],
        ...     ]
        ... )
        >>> target = torch.tensor(
        ...     [
        ...         [300.00, 100.00, 315.00, 150.00],
        ...         [330.00, 100.00, 350.00, 125.00],
        ...         [350.00, 100.00, 375.00, 150.00],
        ...     ]
        ... )
        >>> complete_intersection_over_union(preds, target, aggregate=False)
        tensor([0.6883, 0.4881, 0.5606])

    """
    if not _TORCHVISION_GREATER_EQUAL_0_13:
        raise ModuleNotFoundError(
            f"`{complete_intersection_over_union.__name__}` requires that `torchvision` version 0.13.0 or newer"
            " is installed."
            " Please install with `pip install torchvision>=0.13` or `pip install torchmetrics[detection]`."
        )
    iou = _ciou_update(preds, target, iou_threshold, replacement_val)
    return _ciou_compute(iou, aggregate)
