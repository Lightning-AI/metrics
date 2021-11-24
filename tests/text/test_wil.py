from typing import List, Union

import pytest
from jiwer import wil

from tests.text.helpers import INPUT_ORDER, TextTester
from torchmetrics.functional.text.wil import word_information_lost
from torchmetrics.text.wil import WordInfoLost
from torchmetrics.utilities.imports import _JIWER_AVAILABLE

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


def _compute_wil_metric_jiwer(prediction: Union[str, List[str]], reference: Union[str, List[str]]):
    return wil(reference, prediction)


@pytest.mark.skipif(not _JIWER_AVAILABLE, reason="test requires jiwer")
@pytest.mark.parametrize(
    ["preds", "targets"],
    [(BATCHES_1["preds"], BATCHES_1["targets"]), (BATCHES_2["preds"], BATCHES_2["targets"])],
)
class TestWordInfoLost(TextTester):
    @pytest.mark.parametrize("ddp", [False, True])
    @pytest.mark.parametrize("dist_sync_on_step", [False, True])
    def test_wil_class(self, ddp, dist_sync_on_step, preds, targets):

        self.run_class_metric_test(
            ddp=ddp,
            preds=preds,
            targets=targets,
            metric_class=WordInfoLost,
            sk_metric=_compute_wil_metric_jiwer,
            dist_sync_on_step=dist_sync_on_step,
            input_order=INPUT_ORDER.PREDS_FIRST,
        )

    def test_wil_functional(self, preds, targets):

        self.run_functional_metric_test(
            preds,
            targets,
            metric_functional=word_information_lost,
            sk_metric=_compute_wil_metric_jiwer,
            input_order=INPUT_ORDER.PREDS_FIRST,
        )

    def test_wil_differentiability(self, preds, targets):

        self.run_differentiability_test(
            preds=preds,
            targets=targets,
            metric_module=WordInfoLost,
            metric_functional=word_information_lost,
            input_order=INPUT_ORDER.PREDS_FIRST,
        )
