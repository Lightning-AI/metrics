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
# referenced from
# Library Name: torchtext
# Authors: torchtext authors and @sluks
# Date: 2020-07-18
# Link: https://pytorch.org/text/_modules/torchtext/data/metrics.html#bleu_score
from collections import Counter
from typing import Callable, Sequence, Tuple, Union

import torch
from torch import Tensor, tensor


def _count_ngram(ngram_input_list: Sequence[str], n_gram: int) -> Counter:
    """Counting how many times each word appears in a given text with ngram.

    Args:
        ngram_input_list: A list of translated text or reference texts
        n_gram: gram value ranged 1 to 4

    Return:
        ngram_counter: a collections.Counter object of ngram
    """

    ngram_counter: Counter = Counter()

    for i in range(1, n_gram + 1):
        for j in range(len(ngram_input_list) - i + 1):
            ngram_key = tuple(ngram_input_list[j : (i + j)])
            ngram_counter[ngram_key] += 1

    return ngram_counter


def _tokenize_fn(sentence: str) -> Sequence[str]:
    """Tokenizes sentence into list of words.

    Args:
        sentence: A sentence separated by white space.

    Return:
        List of words
    """
    return sentence.split()


def _bleu_score_update(
    prediction_corpus: Sequence[str],
    target_corpus: Sequence[Sequence[str]],
    numerator: Tensor,
    denominator: Tensor,
    prediction_len: Tensor,
    target_len: Tensor,
    n_gram: int = 4,
    tokenizer: Callable[[str], Sequence[str]] = _tokenize_fn,
) -> Tuple[Tensor, Tensor]:
    """Updates and returns variables required to compute the BLEU score.

    Args:
        target_corpus: An iterable of iterables of reference corpus
        prediction_corpus: An iterable of machine translated corpus
        numerator: Numerator of precision score (true positives)
        denominator: Denominator of precision score (true positives + false positives)
        prediction_len: count of words in a candidate prediction
        target_len: count of words in a reference translation
        n_gram: gram value ranged 1 to 4
        tokenizer: A function that turns sentence into list of words
    """
    target_corpus_: Sequence[Sequence[Sequence[str]]] = [
        [tokenizer(line) if line else [] for line in target] for target in target_corpus
    ]
    prediction_corpus_: Sequence[Sequence[str]] = [tokenizer(line) if line else [] for line in prediction_corpus]

    for (prediction, targets) in zip(prediction_corpus_, target_corpus_):
        prediction_len += len(prediction)
        target_len_list = [len(ref) for ref in targets]
        target_len_diff = [abs(len(prediction) - x) for x in target_len_list]
        target_len += target_len_list[target_len_diff.index(min(target_len_diff))]
        prediction_counter: Counter = _count_ngram(prediction, n_gram)
        target_counter: Counter = Counter()

        for ref in targets:
            target_counter |= _count_ngram(ref, n_gram)

        ngram_counter_clip = prediction_counter & target_counter

        for counter_clip in ngram_counter_clip:
            numerator[len(counter_clip) - 1] += ngram_counter_clip[counter_clip]

        for counter in prediction_counter:
            denominator[len(counter) - 1] += prediction_counter[counter]

    return prediction_len, target_len


def _bleu_score_compute(
    prediction_len: Tensor,
    target_len: Tensor,
    numerator: Tensor,
    denominator: Tensor,
    n_gram: int = 4,
    smooth: bool = False,
) -> Tensor:
    """Computes the BLEU score.

    Args:
        prediction_len: count of words in a candidate prediction
        target_len: count of words in a reference translation
        numerator: Numerator of precision score (true positives)
        denominator: Denominator of precision score (true positives + false positives)
        n_gram: gram value ranged 1 to 4
        smooth: Whether or not to apply smoothing
    """
    device = numerator.device
    if min(numerator) == 0.0:
        return tensor(0.0, device=device)

    if smooth:
        precision_scores = torch.div(
            torch.add(numerator, torch.ones(n_gram, device=device)),
            torch.add(denominator, torch.ones(n_gram, device=device)),
        )
        precision_scores[0] = numerator[0] / denominator[0]
    else:
        precision_scores = numerator / denominator

    log_precision_scores = tensor([1.0 / n_gram] * n_gram, device=device) * torch.log(precision_scores)
    geometric_mean = torch.exp(torch.sum(log_precision_scores))
    brevity_penalty = (
        tensor(1.0, device=device) if prediction_len > target_len else torch.exp(1 - (target_len / prediction_len))
    )
    bleu = brevity_penalty * geometric_mean

    return bleu


def bleu_score(
    prediction_corpus: Union[str, Sequence[str]],
    target_corpus: Sequence[Union[str, Sequence[str]]],
    n_gram: int = 4,
    smooth: bool = False,
) -> Tensor:
    """Calculate `BLEU score`_ of machine translated text with one or more references.

    Args:
        prediction_corpus:
            An iterable of machine translated corpus
        target_corpus:
            An iterable of iterables of reference corpus
        n_gram:
            Gram value ranged from 1 to 4 (Default 4)
        smooth:
            Whether or not to apply smoothing – see [2]

    Return:
        Tensor with BLEU Score

    Example:
        >>> from torchmetrics.functional import bleu_score
        >>> prediction_corpus = ['the cat is on the mat']
        >>> target_corpus = [['there is a cat on the mat', 'a cat is on the mat']]
        >>> bleu_score(prediction_corpus, target_corpus)
        tensor(0.7598)

    References:
        [1] BLEU: a Method for Automatic Evaluation of Machine Translation by Papineni,
        Kishore, Salim Roukos, Todd Ward, and Wei-Jing Zhu `BLEU`_

        [2] Automatic Evaluation of Machine Translation Quality Using Longest Common Subsequence
        and Skip-Bigram Statistics by Chin-Yew Lin and Franz Josef Och `Machine Translation Evolution`_
    """
    prediction_corpus_ = [prediction_corpus] if isinstance(prediction_corpus, str) else prediction_corpus
    target_corpus_ = [[target_text] if isinstance(target_text, str) else target_text for target_text in target_corpus]

    if len(prediction_corpus_) != len(target_corpus_):
        raise ValueError(f"Corpus has different size {len(prediction_corpus_)} != {len(target_corpus_)}")

    numerator = torch.zeros(n_gram)
    denominator = torch.zeros(n_gram)
    prediction_len = tensor(0, dtype=torch.float)
    target_len = tensor(0, dtype=torch.float)

    prediction_len, target_len = _bleu_score_update(
        prediction_corpus_, target_corpus_, numerator, denominator, prediction_len, target_len, n_gram, _tokenize_fn
    )

    return _bleu_score_compute(prediction_len, target_len, numerator, denominator, n_gram, smooth)
