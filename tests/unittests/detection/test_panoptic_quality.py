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
from collections import namedtuple

import numpy as np
import pytest
import torch

from torchmetrics.detection.panoptic_quality import PanopticQuality
from torchmetrics.functional.detection.panoptic_quality import panoptic_quality
from unittests.helpers import seed_all
from unittests.helpers.testers import MetricTester

seed_all(42)

Input = namedtuple("Input", ["preds", "target"])

_inputs = Input(
    preds=torch.tensor(
        [
            [
                [[6, 0], [0, 0], [6, 0], [6, 0], [0, 1]],
                [[0, 0], [0, 0], [6, 0], [0, 1], [0, 1]],
                [[0, 0], [0, 0], [6, 0], [0, 1], [1, 0]],
                [[0, 0], [7, 0], [6, 0], [1, 0], [1, 0]],
                [[0, 0], [7, 0], [7, 0], [7, 0], [7, 0]],
            ],
            [
                [[6, 0], [0, 0], [6, 0], [6, 0], [0, 1]],
                [[0, 0], [0, 0], [6, 0], [0, 1], [0, 1]],
                [[0, 0], [0, 0], [6, 0], [0, 1], [1, 0]],
                [[0, 0], [7, 0], [6, 0], [1, 0], [1, 0]],
                [[0, 0], [7, 0], [7, 0], [7, 0], [7, 0]],
            ],
        ]
    ),
    target=torch.tensor(
        [
            [
                [[6, 0], [6, 0], [6, 0], [6, 0], [0, 0]],
                [[0, 1], [0, 1], [6, 0], [0, 0], [0, 0]],
                [[0, 1], [0, 1], [6, 0], [1, 0], [1, 0]],
                [[0, 1], [7, 0], [7, 0], [1, 0], [1, 0]],
                [[0, 1], [7, 0], [7, 0], [7, 0], [7, 0]],
            ],
            [
                [[6, 0], [6, 0], [6, 0], [6, 0], [0, 0]],
                [[0, 1], [0, 1], [6, 0], [0, 0], [0, 0]],
                [[0, 1], [0, 1], [6, 0], [1, 0], [1, 0]],
                [[0, 1], [7, 0], [7, 0], [1, 0], [1, 0]],
                [[0, 1], [7, 0], [7, 0], [7, 0], [7, 0]],
            ],
        ]
    ),
)
_args = {"things": {0, 1}, "stuffs": {6, 7}}


def _compare_fn(preds, target) -> np.ndarray:
    """Reference implementation

    Improve this by calling https://github.com/cocodataset/panopticapi/blob/master/panopticapi/evaluation.py
    directly and compare at runtime on multiple examples
    """
    return np.array([0.7753])


class TestPanopticQuality(MetricTester):
    @pytest.mark.parametrize("ddp", [False, True])
    def test_panoptic_quality_class(self, ddp):
        self.run_class_metric_test(
            ddp=ddp,
            preds=_inputs.preds,
            target=_inputs.target,
            metric_class=PanopticQuality,
            reference_metric=_compare_fn,
            check_batch=False,
            metric_args=_args,
        )

    def test_panoptic_quality_fn(self):
        self.run_functional_metric_test(
            _inputs.preds,
            _inputs.target,
            metric_functional=panoptic_quality,
            reference_metric=_compare_fn,
            metric_args=_args,
        )


def test_empty_metric():
    """Test empty metric."""
    metric = PanopticQuality(things=set(), stuffs=set())
    metric.compute()


def test_error_on_wrong_input():
    """Test class input validation."""
    with pytest.raises(TypeError, match="Expected argument `things` to be of type.*"):
        PanopticQuality(things=[0], stuffs={1})

    with pytest.raises(TypeError, match="Expected argument `stuffs` to be of type.*"):
        PanopticQuality(things={0}, stuffs={"sky"})

    with pytest.raises(ValueError, match="Expected arguments `things` and `stuffs` to have distinct keys.*"):
        PanopticQuality(things={0}, stuffs={0})

    metric = PanopticQuality(things={0, 1, 3}, stuffs={6, 8}, allow_unknown_preds_category=True)
    valid_image = torch.randint(low=0, high=9, size=(400, 300, 2))
    metric.update(valid_image, valid_image)

    with pytest.raises(TypeError, match="Expected argument `preds` to be of type `torch.Tensor`.*"):
        metric.update([], valid_image)

    with pytest.raises(TypeError, match="Expected argument `target` to be of type `torch.Tensor`.*"):
        metric.update(valid_image, [])

    preds = torch.randint(low=0, high=9, size=(400, 300, 2))
    target = torch.randint(low=0, high=9, size=(30, 40, 2))
    with pytest.raises(ValueError, match="Expected argument `preds` and `target` to have the same shape.*"):
        metric.update(preds, target)

    preds = torch.randint(low=0, high=9, size=(400, 300))
    with pytest.raises(ValueError, match="Expected argument `preds` to have shape.*"):
        metric.update(preds, preds)
