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

from functools import partial
from typing import Callable, Tuple, Union

import numpy as np
import pytest
import torch
from numpy import array
from torch import Tensor, tensor

from tests.helpers import seed_all
from tests.helpers.testers import Metric, MetricTester
from tests.retrieval.helpers import _default_metric_class_input_arguments, get_group_indexes
from tests.retrieval.test_precision import _precision_at_k
from tests.retrieval.test_recall import _recall_at_k
from torchmetrics import RetrievalRecallAtFixedPrecision

seed_all(42)


def _compute_recall_at_precision_metric(
    preds: Union[Tensor, array],
    target: Union[Tensor, array],
    indexes: Union[Tensor, array] = None,
    max_k: int = None,
    min_precision: float = 0.0,
    adaptive_k: bool = False,
    ignore_index: int = None,
    empty_target_action: str = "skip",
    reverse: bool = False,
) -> Tuple[Tensor, Tensor]:
    """Compute metric with multiple iterations over every query predictions set.

    Didn't find a reliable implementation of Precision in Information Retrieval, so, reimplementing here.
    A good explanation can be found here:
    `<https://nlp.stanford.edu/IR-book/pdf/08eval.pdf>_`. (part 8.4)
    """
    e_tol = 0.00001  # for torch.float64 comparision
    recalls, precisions = [], []

    if indexes is None:
        indexes = np.full_like(preds, fill_value=0, dtype=np.int64)
    if isinstance(indexes, Tensor):
        indexes = indexes.cpu().numpy()
    if isinstance(preds, Tensor):
        preds = preds.cpu().numpy()
    if isinstance(target, Tensor):
        target = target.cpu().numpy()

    assert isinstance(indexes, np.ndarray)
    assert isinstance(preds, np.ndarray)
    assert isinstance(target, np.ndarray)

    if ignore_index is not None:
        valid_positions = target != ignore_index
        indexes, preds, target = indexes[valid_positions], preds[valid_positions], target[valid_positions]

    indexes = indexes.flatten()
    preds = preds.flatten()
    target = target.flatten()
    groups = get_group_indexes(indexes)

    if max_k is None:
        max_k = max(map(len, groups))

    max_k_range = torch.arange(1, max_k + 1)

    for group in groups:
        trg, prd = target[group], preds[group]
        r, p = [], []

        if ((1 - trg) if reverse else trg).sum() == 0:
            if empty_target_action == "skip":
                pass
            elif empty_target_action == "pos":
                arr = [1.0] * max_k
                recalls.append(arr)
                precisions.append(arr)
            elif empty_target_action == "neg":
                arr = [0.0] * max_k
                recalls.append(arr)
                precisions.append(arr)

        else:
            for k in max_k_range:
                r.append(_recall_at_k(trg, prd, k=k.item()))
                p.append(_precision_at_k(trg, prd, k=k.item(), adaptive_k=adaptive_k))

            recalls.append(r)
            precisions.append(p)

    if not recalls:
        return tensor(0.0), tensor(max_k)

    recalls = tensor(recalls).mean(dim=0)
    precisions = tensor(precisions).mean(dim=0)

    recalls_at_k = [(r, k) for p, r, k in zip(precisions, recalls, max_k_range) if p > min_precision - e_tol]

    if not recalls_at_k:
        return tensor(0.0), tensor(max_k)

    return max(recalls_at_k)


def test_compute_recall_at_precision_metric():
    indexes = tensor([0, 0, 0, 0, 1, 1, 1])
    preds = tensor([0.4, 0.01, 0.5, 0.6, 0.2, 0.3, 0.5])
    target = tensor([True, False, False, True, True, False, True])
    max_k = 3
    min_precision = 0.8

    res = _compute_recall_at_precision_metric(
        preds,
        target,
        indexes,
        max_k,
        min_precision,
    )
    assert res == (tensor(0.5000), tensor(1))


class RetrievalRecallAtPrecisionMetricTester(MetricTester):
    def run_class_metric_test(
        self,
        ddp: bool,
        indexes: Tensor,
        preds: Tensor,
        target: Tensor,
        metric_class: Metric,
        sk_metric: Callable,
        dist_sync_on_step: bool,
        metric_args: dict,
        reverse: bool = False,
    ):
        _sk_metric_adapted = partial(sk_metric, reverse=reverse, **metric_args)

        super().run_class_metric_test(
            ddp=ddp,
            preds=preds,
            target=target,
            metric_class=metric_class,
            sk_metric=_sk_metric_adapted,
            dist_sync_on_step=dist_sync_on_step,
            metric_args=metric_args,
            fragment_kwargs=True,
            indexes=indexes,  # every additional argument will be passed to metric_class and _sk_metric_adapted
        )


@pytest.mark.parametrize("ddp", [False])
@pytest.mark.parametrize("dist_sync_on_step", [False])
@pytest.mark.parametrize("empty_target_action", ["neg", "skip", "pos"])
@pytest.mark.parametrize("ignore_index", [None, 1])  # avoid setting 0, otherwise test with all 0 targets will fail
@pytest.mark.parametrize("max_k", [None, 1, 2, 5, 10])
@pytest.mark.parametrize("min_precision", [0.0, 0.5, 0.9])
@pytest.mark.parametrize("adaptive_k", [False, True])
@pytest.mark.parametrize(**_default_metric_class_input_arguments)
class TestRetrievalRecallAtPrecision(RetrievalRecallAtPrecisionMetricTester):
    atol = 0.02

    def test_class_metric(
        self,
        indexes,
        preds,
        target,
        ddp,
        dist_sync_on_step,
        empty_target_action,
        ignore_index,
        max_k,
        min_precision,
        adaptive_k,
    ):
        metric_args = dict(
            max_k=max_k,
            min_precision=min_precision,
            adaptive_k=adaptive_k,
            empty_target_action=empty_target_action,
            ignore_index=ignore_index,
        )

        self.run_class_metric_test(
            ddp=ddp,
            indexes=indexes,
            preds=preds,
            target=target,
            metric_class=RetrievalRecallAtFixedPrecision,
            sk_metric=_compute_recall_at_precision_metric,
            dist_sync_on_step=dist_sync_on_step,
            metric_args=metric_args,
        )
