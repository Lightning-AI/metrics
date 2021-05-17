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

from typing import Tuple

import torch
from torch import Tensor

from torchmetrics.utilities.checks import _check_same_shape
from torchmetrics.utilities.data import METRIC_EPS


def _kld_update(preds: Tensor, target: Tensor) -> Tuple[Tensor, int]:
    _check_same_shape(preds, target)

    preds = preds / preds.sum(axis=-1)
    target = target / target.sum(axis=-1)

    preds = torch.clamp(preds, METRIC_EPS)
    target = torch.clamp(target, METRIC_EPS)

    total = preds.numel()

    measures = torch.sum(target * torch.log(target / preds), axis=-1)

    return measures, total


def _kld_compute(measures: Tensor, total: Tensor) -> Tensor:
    return measures / total


def kldivergence(preds: Tensor, target: Tensor) -> Tensor:
    measures, total = _kld_update(preds, target)
    return _kld_compute(measures, total)
