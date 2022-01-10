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
from functools import partial

import pytest
import torch
from pytorch_msssim import ms_ssim

from tests.helpers import seed_all
from tests.helpers.testers import NUM_BATCHES, MetricTester
from torchmetrics.functional.image.ms_ssim import multiscale_structural_similarity_index_measure
from torchmetrics.image.ssim import MultiScaleStructuralSimilarityIndexMeasure

seed_all(42)

Input = namedtuple("Input", ["preds", "target"])
BATCH_SIZE = 1

_inputs = []
for size, coef in [(128, 0.9), (128, 0.7)]:
    preds = torch.rand(NUM_BATCHES, BATCH_SIZE, 1, size, size)
    _inputs.append(
        Input(
            preds=preds,
            target=preds * coef,
        )
    )


def pytorch_ms_ssim(preds, target, data_range, kernel_size):
    return ms_ssim(preds, target, data_range=data_range, win_size=kernel_size)


@pytest.mark.parametrize(
    "preds, target",
    [(i.preds, i.target) for i in _inputs],
)
@pytest.mark.parametrize("kernel_size", [5, 7])
class TestMultiScaleStructuralSimilarityIndexMeasure(MetricTester):
    atol = 6e-3

    @pytest.mark.parametrize("ddp", [False, True])
    @pytest.mark.parametrize("dist_sync_on_step", [False, True])
    def test_ms_ssim(self, preds, target, kernel_size, ddp, dist_sync_on_step):
        self.run_class_metric_test(
            ddp,
            preds,
            target,
            MultiScaleStructuralSimilarityIndexMeasure,
            partial(pytorch_ms_ssim, data_range=1.0, kernel_size=kernel_size),
            metric_args={"data_range": 1.0, "kernel_size": (kernel_size, kernel_size)},
            dist_sync_on_step=dist_sync_on_step,
        )

    def test_ms_ssim_functional(self, preds, target, kernel_size):
        self.run_functional_metric_test(
            preds,
            target,
            multiscale_structural_similarity_index_measure,
            partial(pytorch_ms_ssim, data_range=1.0, kernel_size=kernel_size),
            metric_args={"data_range": 1.0, "kernel_size": (kernel_size, kernel_size)},
        )

    def test_ms_ssim_differentiability(self, preds, target, kernel_size):
        # We need to minimize this example to make the test tractable
        single_beta = (1.0,)
        _preds = preds[:, :, :, :16, :16]
        _target = target[:, :, :, :16, :16]

        self.run_differentiability_test(
            _preds.type(torch.float64),
            _target.type(torch.float64),
            metric_functional=multiscale_structural_similarity_index_measure,
            metric_module=MultiScaleStructuralSimilarityIndexMeasure,
            metric_args={
                "data_range": 1.0,
                "kernel_size": (kernel_size, kernel_size),
                "betas": single_beta,
            },
        )
