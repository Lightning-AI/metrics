from typing import Callable, List, Union

import pytest

from tests.text.helpers import INPUT_ORDER, TextTester
from torchmetrics.utilities.imports import _JIWER_AVAILABLE

if _JIWER_AVAILABLE:
    from jiwer import compute_measures
else:
    compute_measures = Callable

from torchmetrics.functional.text.mer import match_error_rate
from torchmetrics.text.mer import MatchErrorRate

BATCHES_1 = {"preds": [["hello world"], ["what a day"]], "targets": [["hello world"], ["what a wonderful day"]]}

BATCHES_2 = {
    "preds": [
        ["i like python", "what you mean or swallow"],
        ["hello duck", "i like python"],
    ],
    "targets": [
        ["i like monthy python", "what do you mean, african or european swallow"],
        ["hello world", "i like monthy python"],
    ],
}


def _compute_mer_metric_jiwer(prediction: Union[str, List[str]], reference: Union[str, List[str]]):
    return compute_measures(reference, prediction)["mer"]


@pytest.mark.skipif(not _JIWER_AVAILABLE, reason="test requires jiwer")
@pytest.mark.parametrize(
    ["preds", "targets"],
    [
        pytest.param(BATCHES_1["preds"], BATCHES_1["targets"]),
        pytest.param(BATCHES_2["preds"], BATCHES_2["targets"]),
    ],
)
class TestMatchErrorRate(TextTester):
    @pytest.mark.parametrize("ddp", [False, True])
    @pytest.mark.parametrize("dist_sync_on_step", [False, True])
    def test_mer_class(self, ddp, dist_sync_on_step, preds, targets):

        self.run_class_metric_test(
            ddp=ddp,
            preds=preds,
            targets=targets,
            metric_class=MatchErrorRate,
            sk_metric=_compute_mer_metric_jiwer,
            dist_sync_on_step=dist_sync_on_step,
            input_order=INPUT_ORDER.PREDS_FIRST,
        )

    def test_mer_functional(self, preds, targets):

        self.run_functional_metric_test(
            preds,
            targets,
            metric_functional=match_error_rate,
            sk_metric=_compute_mer_metric_jiwer,
            input_order=INPUT_ORDER.PREDS_FIRST,
        )

    def test_mer_differentiability(self, preds, targets):

        self.run_differentiability_test(
            preds=preds,
            targets=targets,
            metric_module=MatchErrorRate,
            metric_functional=match_error_rate,
            input_order=INPUT_ORDER.PREDS_FIRST,
        )
