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


def _ciou_update(preds: torch.Tensor, target: torch.Tensor, iou_threshold: Optional[float]) -> torch.Tensor:
    iou = complete_box_iou(preds, target)
    if iou_threshold is not None:
        return iou[iou >= iou_threshold]
    return iou


def _ciou_compute(iou: torch.Tensor) -> torch.Tensor:
    return iou.diag().mean()


def complete_intersection_over_union(
    preds: torch.Tensor,
    target: torch.Tensor,
    iou_threshold: Optional[float] = None,
) -> torch.Tensor:
    r"""
    Computes `Complete Intersection over Union <https://arxiv.org/abs/2005.03572>`_ between two sets of boxes.
    Both sets of boxes are expected to be in (x1, y1, x2, y2) format with 0 <= x1 < x2 and 0 <= y1 < y2.
    Args:
        preds:
            The input tensor containing the predicted bounding boxes.
        target:
            The tensor containing the ground truth.
        iou_thresholds:
            Optional IoU thresholds for evaluation. If set to `None` the threshold is ignored.
    Example:
        >>> from torchmetrics.functional.detection import complete_intersection_over_union
        >>> preds = torch.Tensor([[100, 100, 200, 200]])
        >>> target = torch.Tensor([[110, 110, 210, 210]])
        >>> complete_intersection_over_union(preds, target)
        tensor([[0.6724]])
    """
    iou = _ciou_update(preds, target, iou_threshold)
    return _ciou_compute(iou)
