# Copyright The Lightning team.
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
from functools import partial
from typing import Callable

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
import torch

from torchmetrics.aggregation import MaxMetric, MeanMetric, MinMetric, SumMetric
from torchmetrics.audio import (
    ScaleInvariantSignalDistortionRatio,
    ScaleInvariantSignalNoiseRatio,
    ShortTimeObjectiveIntelligibility,
    SignalDistortionRatio,
    SignalNoiseRatio,
)
from torchmetrics.audio.pesq import PerceptualEvaluationSpeechQuality
from torchmetrics.audio.pit import PermutationInvariantTraining
from torchmetrics.classification import (
    BinaryAccuracy,
    BinaryAUROC,
    BinaryAveragePrecision,
    BinaryCalibrationError,
    BinaryCohenKappa,
    BinaryConfusionMatrix,
    BinaryROC,
    MulticlassAccuracy,
    MulticlassAUROC,
    MulticlassAveragePrecision,
    MulticlassCalibrationError,
    MulticlassCohenKappa,
    MulticlassConfusionMatrix,
    MultilabelAveragePrecision,
    MultilabelConfusionMatrix,
)
from torchmetrics.functional.audio import scale_invariant_signal_noise_ratio
from torchmetrics.image import (
    ErrorRelativeGlobalDimensionlessSynthesis,
    MultiScaleStructuralSimilarityIndexMeasure,
    PeakSignalNoiseRatio,
    SpectralAngleMapper,
    SpectralDistortionIndex,
    StructuralSimilarityIndexMeasure,
    UniversalImageQualityIndex,
)
from torchmetrics.nominal import CramersV, PearsonsContingencyCoefficient, TheilsU, TschuprowsT
from torchmetrics.regression import MeanSquaredError

_rand_input = lambda: torch.rand(10)
_binary_randint_input = lambda: torch.randint(2, (10,))
_multiclass_randint_input = lambda: torch.randint(3, (10,))
_multiclass_randn_input = lambda: torch.randn(10, 3).softmax(dim=-1)
_multilabel_rand_input = lambda: torch.rand(10, 3)
_multilabel_randint_input = lambda: torch.randint(2, (10, 3))
_audio_input = lambda: torch.randn(8000)
_image_input = lambda: torch.rand([8, 3, 16, 16])
_nominal_input = lambda: torch.randint(0, 4, (100,))


@pytest.mark.parametrize(
    ("metric_class", "preds", "target"),
    [
        pytest.param(BinaryAccuracy, _rand_input, _binary_randint_input, id="binary accuracy"),
        pytest.param(
            partial(MulticlassAccuracy, num_classes=3),
            _multiclass_randint_input,
            _multiclass_randint_input,
            id="multiclass accuracy",
        ),
        pytest.param(
            partial(MulticlassAccuracy, num_classes=3, average=None),
            _multiclass_randint_input,
            _multiclass_randint_input,
            id="multiclass accuracy and average=None",
        ),
        # AUROC
        pytest.param(
            BinaryAUROC,
            _rand_input,
            _binary_randint_input,
            id="binary auroc",
        ),
        pytest.param(
            partial(MulticlassAUROC, num_classes=3),
            _multiclass_randn_input,
            _multiclass_randint_input,
            id="multiclass auroc",
        ),
        pytest.param(
            partial(MulticlassAUROC, num_classes=3, average=None),
            _multiclass_randn_input,
            _multiclass_randint_input,
            id="multiclass auroc and average=None",
        ),
        pytest.param(
            BinaryROC,
            _rand_input,
            _binary_randint_input,
            id="binary roc",
        ),
        pytest.param(
            partial(PearsonsContingencyCoefficient, num_classes=5),
            _nominal_input,
            _nominal_input,
            id="pearson contigency coef",
        ),
        pytest.param(partial(TheilsU, num_classes=5), _nominal_input, _nominal_input, id="theils U"),
        pytest.param(partial(TschuprowsT, num_classes=5), _nominal_input, _nominal_input, id="tschuprows T"),
        pytest.param(partial(CramersV, num_classes=5), _nominal_input, _nominal_input, id="cramers V"),
        pytest.param(
            SpectralDistortionIndex,
            _image_input,
            _image_input,
            id="spectral distortion index",
        ),
        pytest.param(
            ErrorRelativeGlobalDimensionlessSynthesis,
            _image_input,
            _image_input,
            id="error relative global dimensionless synthesis",
        ),
        pytest.param(
            PeakSignalNoiseRatio,
            lambda: torch.tensor([[0.0, 1.0], [2.0, 3.0]]),
            lambda: torch.tensor([[3.0, 2.0], [1.0, 0.0]]),
            id="peak signal noise ratio",
        ),
        pytest.param(
            SpectralAngleMapper,
            _image_input,
            _image_input,
            id="spectral angle mapper",
        ),
        pytest.param(
            StructuralSimilarityIndexMeasure,
            _image_input,
            _image_input,
            id="structural similarity index_measure",
        ),
        pytest.param(
            MultiScaleStructuralSimilarityIndexMeasure,
            lambda: torch.rand(3, 3, 180, 180),
            lambda: torch.rand(3, 3, 180, 180),
            id="multiscale structural similarity index measure",
        ),
        pytest.param(
            UniversalImageQualityIndex,
            _image_input,
            _image_input,
            id="universal image quality index",
        ),
        pytest.param(
            partial(PerceptualEvaluationSpeechQuality, fs=8000, mode="nb"),
            _audio_input,
            _audio_input,
            id="perceptual_evaluation_speech_quality",
        ),
        pytest.param(SignalDistortionRatio, _audio_input, _audio_input, id="signal_distortion_ratio"),
        pytest.param(
            ScaleInvariantSignalDistortionRatio, _rand_input, _rand_input, id="scale_invariant_signal_distortion_ratio"
        ),
        pytest.param(SignalNoiseRatio, _rand_input, _rand_input, id="signal_noise_ratio"),
        pytest.param(ScaleInvariantSignalNoiseRatio, _rand_input, _rand_input, id="scale_invariant_signal_noise_ratio"),
        pytest.param(
            partial(ShortTimeObjectiveIntelligibility, fs=8000, extended=False),
            _audio_input,
            _audio_input,
            id="short_time_objective_intelligibility",
        ),
        pytest.param(
            partial(PermutationInvariantTraining, metric_func=scale_invariant_signal_noise_ratio, eval_func="max"),
            lambda: torch.randn(3, 2, 5),
            lambda: torch.randn(3, 2, 5),
            id="permutation_invariant_training",
        ),
        pytest.param(MeanSquaredError, _rand_input, _rand_input, id="mean squared error"),
        pytest.param(SumMetric, _rand_input, None, id="sum metric"),
        pytest.param(MeanMetric, _rand_input, None, id="mean metric"),
        pytest.param(MinMetric, _rand_input, None, id="min metric"),
        pytest.param(MaxMetric, _rand_input, None, id="min metric"),
        pytest.param(BinaryAveragePrecision, _rand_input, _binary_randint_input, id="binary average precision"),
        pytest.param(
            partial(BinaryCalibrationError, n_bins=2, norm="l1"),
            _rand_input,
            _binary_randint_input,
            id="binary calibration error",
        ),
        pytest.param(BinaryCohenKappa, _rand_input, _binary_randint_input, id="binary cohen kappa"),
        pytest.param(
            partial(MulticlassAveragePrecision, num_classes=3),
            _multiclass_randn_input,
            _multiclass_randint_input,
            id="multiclass average precision",
        ),
        pytest.param(
            partial(MulticlassCalibrationError, num_classes=3, n_bins=3, norm="l1"),
            _multiclass_randn_input,
            _multiclass_randint_input,
            id="multiclass calibration error",
        ),
        pytest.param(
            partial(MulticlassCohenKappa, num_classes=3),
            _multiclass_randn_input,
            _multiclass_randint_input,
            id="multiclass cohen kappa",
        ),
        pytest.param(
            partial(MultilabelAveragePrecision, num_labels=3),
            _multilabel_rand_input,
            _multilabel_randint_input,
            id="multilabel average precision",
        ),
    ],
)
@pytest.mark.parametrize("num_vals", [1, 5])
def test_single_multi_val_plot_methods(metric_class: object, preds: Callable, target: Callable, num_vals: int):
    """Test the plot method of metrics that only output a single tensor scalar."""
    metric = metric_class()

    input = (lambda: (preds(),)) if target is None else lambda: (preds(), target())

    if num_vals == 1:
        metric.update(*input())
        fig, ax = metric.plot()
    else:
        vals = []
        for _ in range(num_vals):
            vals.append(metric(*input()))
        fig, ax = metric.plot(vals)

    assert isinstance(fig, plt.Figure)
    assert isinstance(ax, matplotlib.axes.Axes)


@pytest.mark.parametrize(
    ("metric_class", "preds", "target", "labels"),
    [
        pytest.param(
            BinaryConfusionMatrix,
            _rand_input,
            _binary_randint_input,
            ["cat", "dog"],
            id="binary confusion matrix",
        ),
        pytest.param(
            partial(MulticlassConfusionMatrix, num_classes=3),
            _multiclass_randint_input,
            _multiclass_randint_input,
            ["cat", "dog", "bird"],
            id="multiclass confusion matrix",
        ),
        pytest.param(
            partial(MultilabelConfusionMatrix, num_labels=3),
            _multilabel_randint_input,
            _multilabel_randint_input,
            ["cat", "dog", "bird"],
            id="multilabel confusion matrix",
        ),
    ],
)
@pytest.mark.parametrize("use_labels", [False, True])
def test_confusion_matrix_plotter(metric_class, preds, target, labels, use_labels):
    """Test confusion matrix that uses specialized plot function."""
    metric = metric_class()
    metric.update(preds(), target())
    labels = labels if use_labels else None
    fig, axs = metric.plot(add_text=True, labels=labels)
    assert isinstance(fig, plt.Figure)
    cond1 = isinstance(axs, matplotlib.axes.Axes)
    cond2 = isinstance(axs, np.ndarray) and all(isinstance(a, matplotlib.axes.Axes) for a in axs)
    assert cond1 or cond2
