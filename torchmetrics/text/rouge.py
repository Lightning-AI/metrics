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
from typing import Any, Callable, Dict, List, Optional, Tuple

from torch import Tensor

from torchmetrics import Metric
from torchmetrics.functional.text.rouge import RougeBatchAggregator, _rouge_score_compute, _rouge_score_update
from torchmetrics.utilities.imports import _NLTK_AVAILABLE, _ROUGE_SCORE_AVAILABLE

if _ROUGE_SCORE_AVAILABLE:
    from rouge_score import rouge_scorer


class ROUGEScore(Metric):
    """
    Calculate `ROUGE score <https://en.wikipedia.org/wiki/ROUGE_(metric)>`_, used for automatic summarization.

    Args:
        preds:
            An iterable of predicted sentences.
        targets:
            An iterable of target sentences.
        newline_sep:
            New line separate the inputs.
        use_stemmer:
            Use Porter stemmer to strip word suffixes to improve matching.
        rouge_keys:
            A list of rouge types to calculate.
        compute_on_step:
            Forward only calls ``update()`` and returns None if this is set to False. default: True
        dist_sync_on_step:
            Synchronize metric state across processes at each ``forward()``
            before returning the value at the step.
        process_group:
            Specify the process group on which synchronization is called. default: None (which selects the entire world)
        dist_sync_fn:
            Callback that performs the allgather operation on the metric state. When `None`, DDP
            will be used to perform the allgather.

    Example:

        >>> targets = "Is your name John".split()
        >>> preds = "My name is John".split()
        >>> rouge = ROUGEScore()   # doctest: +SKIP
        >>> from pprint import pprint
        >>> pprint(rouge(preds, targets))  # doctest: +NORMALIZE_WHITESPACE +SKIP
        {'rouge1_fmeasure': 0.25,
         'rouge1_precision': 0.25,
         'rouge1_recall': 0.25,
         'rouge2_fmeasure': 0.0,
         'rouge2_precision': 0.0,
         'rouge2_recall': 0.0,
         'rougeL_fmeasure': 0.25,
         'rougeL_precision': 0.25,
         'rougeL_recall': 0.25,
         'rougeLsum_fmeasure': 0.25,
         'rougeLsum_precision': 0.25,
         'rougeLsum_recall': 0.25}

    References:
        [1] ROUGE: A Package for Automatic Evaluation of Summaries by Chin-Yew Lin https://aclanthology.org/W04-1013/
    """

    def __init__(
        self,
        newline_sep: bool = False,
        use_stemmer: bool = False,
        rouge_keys: Tuple[str] = ("rouge1", "rouge2", "rougeL", "rougeLsum"),
        compute_on_step: bool = True,
        dist_sync_on_step: bool = False,
        process_group: Optional[Any] = None,
        dist_sync_fn: Optional[Callable] = None,
    ):
        super().__init__(
            compute_on_step=compute_on_step,
            dist_sync_on_step=dist_sync_on_step,
            process_group=process_group,
            dist_sync_fn=dist_sync_fn,
        )

        if not (_NLTK_AVAILABLE or _ROUGE_SCORE_AVAILABLE):
            raise ValueError(
                'ROUGE metric requires that both nltk and rouge-score is installed.'
                'Either as `pip install torchmetrics[text]`'
                ' or `pip install nltk rouge-score`'
            )

        self.newline_sep = newline_sep
        self.rouge_keys = rouge_keys
        self.use_stemmer = use_stemmer
        self.aggregator = RougeBatchAggregator()
        self.scorer = rouge_scorer.RougeScorer(rouge_keys, use_stemmer=self.use_stemmer)
        self.scores = {key: [] for key in rouge_keys}

    def update(self, preds: List[str], targets: List[str]) -> None:
        """
        Compute rouge scores.

        Args:
            preds: An iterable of predicted sentences.
            targets: An iterable of target sentences.
        """
        _rouge_score_update(preds, targets, scores=self.scores, scorer=self.scorer, newline_sep=self.newline_sep)

    def compute(self) -> Dict[str, Tensor]:
        """
        Calculate (Agregate and provide confidence intervals) ROUGE score

        Return:
            Python dictionary of rouge scores for each input rouge key.
        """
        return _rouge_score_compute(self.scores, aggregator=self.aggregator)

    def __hash__(self):
        # override to hash list objects.
        # this is a bug in the upstream pytorch release.
        hash_vals = [self.__class__.__name__]

        for key in self._defaults:
            value = getattr(self, key)
            if isinstance(value, list):
                value = tuple(value)
            hash_vals.append(value)

        return hash(tuple(hash_vals))
