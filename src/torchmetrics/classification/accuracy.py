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
from typing import Any, Optional, Sequence, Union

import torch
from torch import Tensor
from typing_extensions import Literal

from torchmetrics.functional.classification.accuracy import _accuracy_reduce
from torchmetrics.metric import Metric
from torchmetrics.utilities.imports import _MATPLOTLIB_AVAILABLE
from torchmetrics.utilities.plot import _AX_TYPE, _PLOT_OUT_TYPE, plot_single_or_multi_val

if not _MATPLOTLIB_AVAILABLE:
    __doctest_skip__ = ["BinaryAccuracy.plot", "MulticlassAccuracy.plot"]

from torchmetrics.classification.stat_scores import (  # isort:skip
    BinaryStatScores,
    MulticlassStatScores,
    MultilabelStatScores,
)


class BinaryAccuracy(BinaryStatScores):
    r"""Computes `Accuracy`_ for binary tasks:

    .. math::
        \text{Accuracy} = \frac{1}{N}\sum_i^N 1(y_i = \hat{y}_i)

    Where :math:`y` is a tensor of target values, and :math:`\hat{y}` is a tensor of predictions.

    Accepts the following input tensors:

    - ``preds`` (int or float tensor): ``(N, ...)``. If preds is a floating point tensor with values outside
      [0,1] range we consider the input to be logits and will auto apply sigmoid per element. Addtionally,
      we convert to int tensor with thresholding using the value in ``threshold``.
    - ``target`` (int tensor): ``(N, ...)``

    The influence of the additional dimension ``...`` (if present) will be determined by the `multidim_average`
    argument.

    Args:
        threshold: Threshold for transforming probability to binary {0,1} predictions
        multidim_average:
            Defines how additionally dimensions ``...`` should be handled. Should be one of the following:

            - ``global``: Additional dimensions are flatted along the batch dimension
            - ``samplewise``: Statistic will be calculated independently for each sample on the ``N`` axis.
              The statistics in this case are calculated over the additional dimensions.

        ignore_index:
            Specifies a target value that is ignored and does not contribute to the metric calculation
        validate_args: bool indicating if input arguments and tensors should be validated for correctness.
            Set to ``False`` for faster computations.

    Returns:
        If ``multidim_average`` is set to ``global``, the metric returns a scalar value. If ``multidim_average``
        is set to ``samplewise``, the metric returns ``(N,)`` vector consisting of a scalar value per sample.

    Example (preds is int tensor):
        >>> from torchmetrics.classification import BinaryAccuracy
        >>> target = torch.tensor([0, 1, 0, 1, 0, 1])
        >>> preds = torch.tensor([0, 0, 1, 1, 0, 1])
        >>> metric = BinaryAccuracy()
        >>> metric(preds, target)
        tensor(0.6667)

    Example (preds is float tensor):
        >>> from torchmetrics.classification import BinaryAccuracy
        >>> target = torch.tensor([0, 1, 0, 1, 0, 1])
        >>> preds = torch.tensor([0.11, 0.22, 0.84, 0.73, 0.33, 0.92])
        >>> metric = BinaryAccuracy()
        >>> metric(preds, target)
        tensor(0.6667)

    Example (multidim tensors):
        >>> from torchmetrics.classification import BinaryAccuracy
        >>> target = torch.tensor([[[0, 1], [1, 0], [0, 1]], [[1, 1], [0, 0], [1, 0]]])
        >>> preds = torch.tensor(
        ...     [
        ...         [[0.59, 0.91], [0.91, 0.99], [0.63, 0.04]],
        ...         [[0.38, 0.04], [0.86, 0.780], [0.45, 0.37]],
        ...     ]
        ... )
        >>> metric = BinaryAccuracy(multidim_average='samplewise')
        >>> metric(preds, target)
        tensor([0.3333, 0.1667])
    """
    is_differentiable = False
    higher_is_better = True
    full_state_update: bool = False
    plot_options: dict = {"lower_bound": 0.0, "upper_bound": 1.0}

    def compute(self) -> Tensor:
        """Computes accuracy based on inputs passed in to ``update`` previously."""
        tp, fp, tn, fn = self._final_state()
        return _accuracy_reduce(tp, fp, tn, fn, average="binary", multidim_average=self.multidim_average)

    def plot(
        self, val: Optional[Union[Tensor, Sequence[Tensor]]] = None, ax: Optional[_AX_TYPE] = None
    ) -> _PLOT_OUT_TYPE:
        """Plot a single or multiple values from the metric.

        Args:
            val: Either a single result from calling `metric.forward` or `metric.compute` or a list of these results.
                If no value is provided, will automatically call `metric.compute` and plot that result.
            ax: An matplotlib axis object. If provided will add plot to that axis

        Returns:
            fig: Figure object
            ax: Axes object

        Raises:
            ModuleNotFoundError:
                If `matplotlib` is not installed

        Examples:

        .. plot::
            :scale: 75

            >>> # Example plotting a single value
            >>> import torch
            >>> from torchmetrics.classification import BinaryAccuracy
            >>> metric = BinaryAccuracy()
            >>> metric.update(torch.rand(10), torch.randint(2,(10,)))
            >>> metric.plot()

        .. plot::
            :scale: 75

            >>> # Example plotting multiple values
            >>> import torch
            >>> from torchmetrics.classification import BinaryAccuracy
            >>> metric = BinaryAccuracy()
            >>> values = [ ]
            >>> for _ in range(10):
            ...     values.append(metric(torch.rand(10), torch.randint(2,(10,))))
            >>> metric.plot(values)
        """
        val = val or self.compute()
        fig, ax = plot_single_or_multi_val(
            val, ax=ax, higher_is_better=self.higher_is_better, **self.plot_options, name=self.__class__.__name__
        )
        return fig, ax


class MulticlassAccuracy(MulticlassStatScores):
    r"""Computes `Accuracy`_ for multiclass tasks:

    .. math::
        \text{Accuracy} = \frac{1}{N}\sum_i^N 1(y_i = \hat{y}_i)

    Where :math:`y` is a tensor of target values, and :math:`\hat{y}` is a tensor of predictions.

    Accepts the following input tensors:

    - ``preds``: ``(N, ...)`` (int tensor) or ``(N, C, ..)`` (float tensor). If preds is a floating point
      we apply ``torch.argmax`` along the ``C`` dimension to automatically convert probabilities/logits into
      an int tensor.
    - ``target`` (int tensor): ``(N, ...)``

    The influence of the additional dimension ``...`` (if present) will be determined by the `multidim_average`
    argument.

    Args:
        num_classes: Integer specifing the number of classes
        average:
            Defines the reduction that is applied over labels. Should be one of the following:

            - ``micro``: Sum statistics over all labels
            - ``macro``: Calculate statistics for each label and average them
            - ``weighted``: Calculates statistics for each label and computes weighted average using their support
            - ``"none"`` or ``None``: Calculates statistic for each label and applies no reduction

        top_k:
            Number of highest probability or logit score predictions considered to find the correct label.
            Only works when ``preds`` contain probabilities/logits.
        multidim_average:
            Defines how additionally dimensions ``...`` should be handled. Should be one of the following:

            - ``global``: Additional dimensions are flatted along the batch dimension
            - ``samplewise``: Statistic will be calculated independently for each sample on the ``N`` axis.
              The statistics in this case are calculated over the additional dimensions.

        ignore_index:
            Specifies a target value that is ignored and does not contribute to the metric calculation
        validate_args: bool indicating if input arguments and tensors should be validated for correctness.
            Set to ``False`` for faster computations.

    Returns:
        The returned shape depends on the ``average`` and ``multidim_average`` arguments:

        - If ``multidim_average`` is set to ``global``:

          - If ``average='micro'/'macro'/'weighted'``, the output will be a scalar tensor
          - If ``average=None/'none'``, the shape will be ``(C,)``

        - If ``multidim_average`` is set to ``samplewise``:

          - If ``average='micro'/'macro'/'weighted'``, the shape will be ``(N,)``
          - If ``average=None/'none'``, the shape will be ``(N, C)``

    Example (preds is int tensor):
        >>> from torchmetrics.classification import MulticlassAccuracy
        >>> target = torch.tensor([2, 1, 0, 0])
        >>> preds = torch.tensor([2, 1, 0, 1])
        >>> metric = MulticlassAccuracy(num_classes=3)
        >>> metric(preds, target)
        tensor(0.8333)
        >>> metric = MulticlassAccuracy(num_classes=3, average=None)
        >>> metric(preds, target)
        tensor([0.5000, 1.0000, 1.0000])

    Example (preds is float tensor):
        >>> from torchmetrics.classification import MulticlassAccuracy
        >>> target = torch.tensor([2, 1, 0, 0])
        >>> preds = torch.tensor([
        ...   [0.16, 0.26, 0.58],
        ...   [0.22, 0.61, 0.17],
        ...   [0.71, 0.09, 0.20],
        ...   [0.05, 0.82, 0.13],
        ... ])
        >>> metric = MulticlassAccuracy(num_classes=3)
        >>> metric(preds, target)
        tensor(0.8333)
        >>> metric = MulticlassAccuracy(num_classes=3, average=None)
        >>> metric(preds, target)
        tensor([0.5000, 1.0000, 1.0000])

    Example (multidim tensors):
        >>> from torchmetrics.classification import MulticlassAccuracy
        >>> target = torch.tensor([[[0, 1], [2, 1], [0, 2]], [[1, 1], [2, 0], [1, 2]]])
        >>> preds = torch.tensor([[[0, 2], [2, 0], [0, 1]], [[2, 2], [2, 1], [1, 0]]])
        >>> metric = MulticlassAccuracy(num_classes=3, multidim_average='samplewise')
        >>> metric(preds, target)
        tensor([0.5000, 0.2778])
        >>> metric = MulticlassAccuracy(num_classes=3, multidim_average='samplewise', average=None)
        >>> metric(preds, target)
        tensor([[1.0000, 0.0000, 0.5000],
                [0.0000, 0.3333, 0.5000]])
    """
    is_differentiable = False
    higher_is_better = True
    full_state_update: bool = False
    plot_options = {"lower_bound": 0.0, "upper_bound": 1.0, "legend_name": "Class"}

    def compute(self) -> Tensor:
        """Computes accuracy based on inputs passed in to ``update`` previously."""
        tp, fp, tn, fn = self._final_state()
        return _accuracy_reduce(tp, fp, tn, fn, average=self.average, multidim_average=self.multidim_average)

    def plot(
        self, val: Optional[Union[Tensor, Sequence[Tensor]]] = None, ax: Optional[_AX_TYPE] = None
    ) -> _PLOT_OUT_TYPE:
        """Plot a single or multiple values from the metric.

        Args:
            val: Either a single result from calling `metric.forward` or `metric.compute` or a list of these results.
                If no value is provided, will automatically call `metric.compute` and plot that result.
            ax: An matplotlib axis object. If provided will add plot to that axis

        Returns:
            fig: Figure object
            ax: Axes object

        Raises:
            ModuleNotFoundError:
                If `matplotlib` is not installed

        Examples:

        .. plot::
            :scale: 75

            >>> # Example plotting a single value per class
            >>> import torch
            >>> from torchmetrics.classification import MulticlassAccuracy
            >>> metric = MulticlassAccuracy(num_classes=3, average=None)
            >>> metric.update(torch.randint(3, (20,)), torch.randint(3, (20,)))
            >>> metric.plot()

        .. plot::
            :scale: 75

            >>> # Example plotting a multiple values per class
            >>> import torch
            >>> from torchmetrics.classification import MulticlassAccuracy
            >>> metric = MulticlassAccuracy(num_classes=3, average=None)
            >>> values = []
            >>> for _ in range(20):
            ...     values.append(metric(torch.randint(3, (20,)), torch.randint(3, (20,))))
            >>> metric.plot(values)
        """
        val = val or self.compute()
        fig, ax = plot_single_or_multi_val(
            val, ax=ax, higher_is_better=self.higher_is_better, **self.plot_options, name=self.__class__.__name__
        )
        return fig, ax


class MultilabelAccuracy(MultilabelStatScores):
    r"""Computes `Accuracy`_ for multilabel tasks:

    .. math::
        \text{Accuracy} = \frac{1}{N}\sum_i^N 1(y_i = \hat{y}_i)

    Where :math:`y` is a tensor of target values, and :math:`\hat{y}` is a tensor of predictions.

    Accepts the following input tensors:

    - ``preds`` (int or float tensor): ``(N, C, ...)``. If preds is a floating point tensor with values outside
      [0,1] range we consider the input to be logits and will auto apply sigmoid per element. Addtionally,
      we convert to int tensor with thresholding using the value in ``threshold``.
    - ``target`` (int tensor): ``(N, C, ...)``

    The influence of the additional dimension ``...`` (if present) will be determined by the `multidim_average`
    argument.

    Args:
        num_labels: Integer specifing the number of labels
        threshold: Threshold for transforming probability to binary (0,1) predictions
        average:
            Defines the reduction that is applied over labels. Should be one of the following:

            - ``micro``: Sum statistics over all labels
            - ``macro``: Calculate statistics for each label and average them
            - ``weighted``: Calculates statistics for each label and computes weighted average using their support
            - ``"none"`` or ``None``: Calculates statistic for each label and applies no reduction

        multidim_average:
            Defines how additionally dimensions ``...`` should be handled. Should be one of the following:

            - ``global``: Additional dimensions are flatted along the batch dimension
            - ``samplewise``: Statistic will be calculated independently for each sample on the ``N`` axis.
              The statistics in this case are calculated over the additional dimensions.

        ignore_index:
            Specifies a target value that is ignored and does not contribute to the metric calculation
        validate_args: bool indicating if input arguments and tensors should be validated for correctness.
            Set to ``False`` for faster computations.

    Returns:
        The returned shape depends on the ``average`` and ``multidim_average`` arguments:

        - If ``multidim_average`` is set to ``global``:

          - If ``average='micro'/'macro'/'weighted'``, the output will be a scalar tensor
          - If ``average=None/'none'``, the shape will be ``(C,)``

        - If ``multidim_average`` is set to ``samplewise``:

          - If ``average='micro'/'macro'/'weighted'``, the shape will be ``(N,)``
          - If ``average=None/'none'``, the shape will be ``(N, C)``

    Example (preds is int tensor):
        >>> from torchmetrics.classification import MultilabelAccuracy
        >>> target = torch.tensor([[0, 1, 0], [1, 0, 1]])
        >>> preds = torch.tensor([[0, 0, 1], [1, 0, 1]])
        >>> metric = MultilabelAccuracy(num_labels=3)
        >>> metric(preds, target)
        tensor(0.6667)
        >>> metric = MultilabelAccuracy(num_labels=3, average=None)
        >>> metric(preds, target)
        tensor([1.0000, 0.5000, 0.5000])

    Example (preds is float tensor):
        >>> from torchmetrics.classification import MultilabelAccuracy
        >>> target = torch.tensor([[0, 1, 0], [1, 0, 1]])
        >>> preds = torch.tensor([[0.11, 0.22, 0.84], [0.73, 0.33, 0.92]])
        >>> metric = MultilabelAccuracy(num_labels=3)
        >>> metric(preds, target)
        tensor(0.6667)
        >>> metric = MultilabelAccuracy(num_labels=3, average=None)
        >>> metric(preds, target)
        tensor([1.0000, 0.5000, 0.5000])

    Example (multidim tensors):
        >>> from torchmetrics.classification import MultilabelAccuracy
        >>> target = torch.tensor([[[0, 1], [1, 0], [0, 1]], [[1, 1], [0, 0], [1, 0]]])
        >>> preds = torch.tensor(
        ...     [
        ...         [[0.59, 0.91], [0.91, 0.99], [0.63, 0.04]],
        ...         [[0.38, 0.04], [0.86, 0.780], [0.45, 0.37]],
        ...     ]
        ... )
        >>> metric = MultilabelAccuracy(num_labels=3, multidim_average='samplewise')
        >>> metric(preds, target)
        tensor([0.3333, 0.1667])
        >>> metric = MultilabelAccuracy(num_labels=3, multidim_average='samplewise', average=None)
        >>> metric(preds, target)
        tensor([[0.5000, 0.5000, 0.0000],
                [0.0000, 0.0000, 0.5000]])
    """
    is_differentiable = False
    higher_is_better = True
    full_state_update: bool = False
    plot_options: dict = {"lower_bound": 0.0, "upper_bound": 1.0, "legend_name": "Label"}

    def compute(self) -> Tensor:
        """Computes accuracy based on inputs passed in to ``update`` previously."""
        tp, fp, tn, fn = self._final_state()
        return _accuracy_reduce(
            tp, fp, tn, fn, average=self.average, multidim_average=self.multidim_average, multilabel=True
        )


class Accuracy:
    r"""Computes `Accuracy`_

    .. math::
        \text{Accuracy} = \frac{1}{N}\sum_i^N 1(y_i = \hat{y}_i)

    Where :math:`y` is a tensor of target values, and :math:`\hat{y}` is a tensor of predictions.

    This module is a simple wrapper to get the task specific versions of this metric, which is done by setting the
    ``task`` argument to either ``'binary'``, ``'multiclass'`` or ``multilabel``. See the documentation of
    :mod:`BinaryAccuracy`, :mod:`MulticlassAccuracy` and :mod:`MultilabelAccuracy` for the specific details of
    each argument influence and examples.

    Legacy Example:
        >>> import torch
        >>> target = torch.tensor([0, 1, 2, 3])
        >>> preds = torch.tensor([0, 2, 1, 3])
        >>> accuracy = Accuracy(task="multiclass", num_classes=4)
        >>> accuracy(preds, target)
        tensor(0.5000)

        >>> target = torch.tensor([0, 1, 2])
        >>> preds = torch.tensor([[0.1, 0.9, 0], [0.3, 0.1, 0.6], [0.2, 0.5, 0.3]])
        >>> accuracy = Accuracy(task="multiclass", num_classes=3, top_k=2)
        >>> accuracy(preds, target)
        tensor(0.6667)
    """

    def __new__(
        cls,
        task: Literal["binary", "multiclass", "multilabel"],
        threshold: float = 0.5,
        num_classes: Optional[int] = None,
        num_labels: Optional[int] = None,
        average: Optional[Literal["micro", "macro", "weighted", "none"]] = "micro",
        multidim_average: Literal["global", "samplewise"] = "global",
        top_k: Optional[int] = 1,
        ignore_index: Optional[int] = None,
        validate_args: bool = True,
        **kwargs: Any,
    ) -> Metric:
        kwargs.update(dict(multidim_average=multidim_average, ignore_index=ignore_index, validate_args=validate_args))
        if task == "binary":
            return BinaryAccuracy(threshold, **kwargs)
        if task == "multiclass":
            assert isinstance(num_classes, int)
            assert isinstance(top_k, int)
            return MulticlassAccuracy(num_classes, top_k, average, **kwargs)
        if task == "multilabel":
            assert isinstance(num_labels, int)
            return MultilabelAccuracy(num_labels, threshold, average, **kwargs)
        raise ValueError(
            f"Expected argument `task` to either be `'binary'`, `'multiclass'` or `'multilabel'` but got {task}"
        )
