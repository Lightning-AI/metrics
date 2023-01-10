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
from typing import Any, List, Optional, Tuple, Union

from torch import Tensor
from typing_extensions import Literal

from torchmetrics.classification.precision_recall_curve import (
    BinaryPrecisionRecallCurve,
    MulticlassPrecisionRecallCurve,
    MultilabelPrecisionRecallCurve,
)
from torchmetrics.functional.classification.specificity_at_sensitivity import (
    _binary_specificity_at_sensitivity_arg_validation,
    _binary_specificity_at_sensitivity_compute,
    _multiclass_specificity_at_sensitivity_arg_validation,
    _multiclass_specificity_at_sensitivity_compute,
    _multilabel_specificity_at_sensitivity_arg_validation,
    _multilabel_specificity_at_sensitivity_compute,
)
from torchmetrics.metric import Metric
from torchmetrics.utilities.data import dim_zero_cat


class BinarySpecificityAtSensitivity(BinaryPrecisionRecallCurve):
    r"""Computes the higest possible specificity value given the minimum sensitivity thresholds provided. This is
    done by first calculating the Receiver Operating Characteristic (ROC) curve for different thresholds and the
    find the specificity for a given sensitivity level.

    Accepts the following input tensors:

    - ``preds`` (float tensor): ``(N, ...)``. Preds should be a tensor containing probabilities or logits for each
      observation. If preds has values outside [0,1] range we consider the input to be logits and will auto apply
      sigmoid per element.
    - ``target`` (int tensor): ``(N, ...)``. Target should be a tensor containing ground truth labels, and therefore
      only contain {0,1} values (except if `ignore_index` is specified).

    Additional dimension ``...`` will be flattened into the batch dimension.

    The implementation both supports calculating the metric in a non-binned but accurate version and a binned version
    that is less accurate but more memory efficient. Setting the `thresholds` argument to `None` will activate the
    non-binned  version that uses memory of size :math:`\mathcal{O}(n_{samples})` whereas setting the `thresholds`
    argument to either an integer, list or a 1d tensor will use a binned version that uses memory of
    size :math:`\mathcal{O}(n_{thresholds})` (constant memory).

    Args:
        min_sensitivity: float value specifying minimum sensitivity threshold.
        thresholds:
            Can be one of:

            - If set to `None`, will use a non-binned approach where thresholds are dynamically calculated from
              all the data. Most accurate but also most memory consuming approach.
            - If set to an `int` (larger than 1), will use that number of thresholds linearly spaced from
              0 to 1 as bins for the calculation.
            - If set to an `list` of floats, will use the indicated thresholds in the list as bins for the calculation
            - If set to an 1d `tensor` of floats, will use the indicated thresholds in the tensor as
              bins for the calculation.

        validate_args: bool indicating if input arguments and tensors should be validated for correctness.
            Set to ``False`` for faster computations.
        kwargs: Additional keyword arguments, see :ref:`Metric kwargs` for more info.

    Returns:
        (tuple): a tuple of 2 tensors containing:

        - specificity: an scalar tensor with the maximum specificity for the given sensitivity level
        - threshold: an scalar tensor with the corresponding threshold level

    Example:
        >>> from torchmetrics.classification import BinarySpecificityAtSensitivity
        >>> import torch
        >>> preds = torch.tensor([0, 0.5, 0.4, 0.1])
        >>> target = torch.tensor([0, 1, 1, 1])
        >>> metric = BinarySpecificityAtSensitivity(min_sensitivity=0.5, thresholds=None)
        >>> metric(preds, target)
        (tensor(1.), tensor(0.1000))
        >>> metric = BinarySpecificityAtSensitivity(min_sensitivity=0.5, thresholds=5)
        >>> metric(preds, target)
        (tensor(1.), tensor(0.2500))
    """
    is_differentiable: bool = False
    higher_is_better: Optional[bool] = None
    full_state_update: bool = False

    def __init__(
        self,
        min_sensitivity: float,
        thresholds: Optional[Union[int, List[float], Tensor]] = None,
        ignore_index: Optional[int] = None,
        validate_args: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(thresholds, ignore_index, validate_args=False, **kwargs)
        if validate_args:
            _binary_specificity_at_sensitivity_arg_validation(min_sensitivity, thresholds, ignore_index)
        self.validate_args = validate_args
        self.min_sensitivity = min_sensitivity

    def compute(self) -> Tuple[Tensor, Tensor]:  # type: ignore[override]
        if self.thresholds is None:
            state = [dim_zero_cat(self.preds), dim_zero_cat(self.target)]  # type: ignore
        else:
            state = self.confmat
        return _binary_specificity_at_sensitivity_compute(state, self.thresholds, self.min_sensitivity)  # type: ignore


class MulticlassSpecificityAtSensitivity(MulticlassPrecisionRecallCurve):
    r"""Computes the higest possible specificity value given the minimum sensitivity thresholds provided. This is
    done by first calculating the Receiver Operating Characteristic (ROC) curve for different thresholds and the
    find the specificity for a given sensitivity level.

    Accepts the following input tensors:

    - ``preds`` (float tensor): ``(N, C, ...)``. Preds should be a tensor containing probabilities or logits for each
      observation. If preds has values outside [0,1] range we consider the input to be logits and will auto apply
      softmax per sample.
    - ``target`` (int tensor): ``(N, ...)``. Target should be a tensor containing ground truth labels, and therefore
      only contain values in the [0, n_classes-1] range (except if `ignore_index` is specified).

    Additional dimension ``...`` will be flattened into the batch dimension.

    The implementation both supports calculating the metric in a non-binned but accurate version and a binned version
    that is less accurate but more memory efficient. Setting the `thresholds` argument to `None` will activate the
    non-binned  version that uses memory of size :math:`\mathcal{O}(n_{samples})` whereas setting the `thresholds`
    argument to either an integer, list or a 1d tensor will use a binned version that uses memory of
    size :math:`\mathcal{O}(n_{thresholds} \times n_{classes})` (constant memory).

    Args:
        num_classes: Integer specifing the number of classes
        min_sensitivity: float value specifying minimum sensitivity threshold.
        thresholds:
            Can be one of:

            - If set to `None`, will use a non-binned approach where thresholds are dynamically calculated from
              all the data. Most accurate but also most memory consuming approach.
            - If set to an `int` (larger than 1), will use that number of thresholds linearly spaced from
              0 to 1 as bins for the calculation.
            - If set to an `list` of floats, will use the indicated thresholds in the list as bins for the calculation
            - If set to an 1d `tensor` of floats, will use the indicated thresholds in the tensor as
              bins for the calculation.

        validate_args: bool indicating if input arguments and tensors should be validated for correctness.
            Set to ``False`` for faster computations.
        kwargs: Additional keyword arguments, see :ref:`Metric kwargs` for more info.

    Returns:
        (tuple): a tuple of either 2 tensors or 2 lists containing

        - specificity: an 1d tensor of size (n_classes, ) with the maximum specificity for the given
        sensitivity level per class
        - thresholds: an 1d tensor of size (n_classes, ) with the corresponding threshold level per class


    Example:
        >>> from torchmetrics.classification import MulticlassSpecificityAtSensitivity
        >>> import torch
        >>> preds = torch.tensor([[0.75, 0.05, 0.05, 0.05, 0.05],
        ...                       [0.05, 0.75, 0.05, 0.05, 0.05],
        ...                       [0.05, 0.05, 0.75, 0.05, 0.05],
        ...                       [0.05, 0.05, 0.05, 0.75, 0.05]])
        >>> target = torch.tensor([0, 1, 3, 2])
        >>> metric = MulticlassSpecificityAtSensitivity(num_classes=5, min_sensitivity=0.5, thresholds=None)
        >>> metric(preds, target)
        (tensor([1., 1., 0., 0., 0.]), tensor([7.5000e-01, 7.5000e-01, 5.0000e-02, 5.0000e-02, 1.0000e+06]))
        >>> metric = MulticlassSpecificityAtSensitivity(num_classes=5, min_sensitivity=0.5, thresholds=5)
        >>> metric(preds, target)
        (tensor([1., 1., 0., 0., 0.]), tensor([7.5000e-01, 7.5000e-01, 0.0000e+00, 0.0000e+00, 1.0000e+06]))
    """
    is_differentiable: bool = False
    higher_is_better: Optional[bool] = None
    full_state_update: bool = False

    def __init__(
        self,
        num_classes: int,
        min_sensitivity: float,
        thresholds: Optional[Union[int, List[float], Tensor]] = None,
        ignore_index: Optional[int] = None,
        validate_args: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            num_classes=num_classes, thresholds=thresholds, ignore_index=ignore_index, validate_args=False, **kwargs
        )
        if validate_args:
            _multiclass_specificity_at_sensitivity_arg_validation(
                num_classes, min_sensitivity, thresholds, ignore_index
            )
        self.validate_args = validate_args
        self.min_sensitivity = min_sensitivity

    def compute(self) -> Tuple[Tensor, Tensor]:  # type: ignore
        if self.thresholds is None:
            state = [dim_zero_cat(self.preds), dim_zero_cat(self.target)]  # type: ignore
        else:
            state = self.confmat
        return _multiclass_specificity_at_sensitivity_compute(
            state, self.num_classes, self.thresholds, self.min_sensitivity  # type: ignore
        )


class MultilabelSpecificityAtSensitivity(MultilabelPrecisionRecallCurve):
    r"""Computes the higest possible specificity value given the minimum sensitivity thresholds provided. This is
    done by first calculating the Receiver Operating Characteristic (ROC) curve for different thresholds and the
    find the specificity for a given sensitivity level.

    Accepts the following input tensors:

    - ``preds`` (float tensor): ``(N, C, ...)``. Preds should be a tensor containing probabilities or logits for each
      observation. If preds has values outside [0,1] range we consider the input to be logits and will auto apply
      sigmoid per element.
    - ``target`` (int tensor): ``(N, C, ...)``. Target should be a tensor containing ground truth labels, and therefore
      only contain {0,1} values (except if `ignore_index` is specified).

    Additional dimension ``...`` will be flattened into the batch dimension.

    The implementation both supports calculating the metric in a non-binned but accurate version and a binned version
    that is less accurate but more memory efficient. Setting the `thresholds` argument to `None` will activate the
    non-binned  version that uses memory of size :math:`\mathcal{O}(n_{samples})` whereas setting the `thresholds`
    argument to either an integer, list or a 1d tensor will use a binned version that uses memory of
    size :math:`\mathcal{O}(n_{thresholds} \times n_{labels})` (constant memory).

    Args:
        num_labels: Integer specifing the number of labels
        min_sensitivity: float value specifying minimum sensitivity threshold.
        thresholds:
            Can be one of:

            - If set to `None`, will use a non-binned approach where thresholds are dynamically calculated from
              all the data. Most accurate but also most memory consuming approach.
            - If set to an `int` (larger than 1), will use that number of thresholds linearly spaced from
              0 to 1 as bins for the calculation.
            - If set to an `list` of floats, will use the indicated thresholds in the list as bins for the calculation
            - If set to an 1d `tensor` of floats, will use the indicated thresholds in the tensor as
              bins for the calculation.

        validate_args: bool indicating if input arguments and tensors should be validated for correctness.
            Set to ``False`` for faster computations.
        kwargs: Additional keyword arguments, see :ref:`Metric kwargs` for more info.

    Returns:
        (tuple): a tuple of either 2 tensors or 2 lists containing

        - specificity: an 1d tensor of size (n_classes, ) with the maximum specificity for the given
        sensitivity level per class
        - thresholds: an 1d tensor of size (n_classes, ) with the corresponding threshold level per class

    Example:
        >>> from torchmetrics.classification import MultilabelSpecificityAtSensitivity
        >>> import torch
        >>> preds = torch.tensor([[0.75, 0.05, 0.35],
        ...                       [0.45, 0.75, 0.05],
        ...                       [0.05, 0.55, 0.75],
        ...                       [0.05, 0.65, 0.05]])
        >>> target = torch.tensor([[1, 0, 1],
        ...                        [0, 0, 0],
        ...                        [0, 1, 1],
        ...                        [1, 1, 1]])
        >>> metric = MultilabelSpecificityAtSensitivity(num_labels=3, min_sensitivity=0.5, thresholds=None)
        >>> metric(preds, target)
        (tensor([1.0000, 0.5000, 1.0000]), tensor([0.7500, 0.5500, 0.3500]))
        >>> metric = MultilabelSpecificityAtSensitivity(num_labels=3, min_sensitivity=0.5, thresholds=5)
        >>> metric(preds, target)
        (tensor([1.0000, 0.5000, 1.0000]), tensor([0.7500, 0.5000, 0.2500]))
    """
    is_differentiable: bool = False
    higher_is_better: Optional[bool] = None
    full_state_update: bool = False

    def __init__(
        self,
        num_labels: int,
        min_sensitivity: float,
        thresholds: Optional[Union[int, List[float], Tensor]] = None,
        ignore_index: Optional[int] = None,
        validate_args: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            num_labels=num_labels, thresholds=thresholds, ignore_index=ignore_index, validate_args=False, **kwargs
        )
        if validate_args:
            _multilabel_specificity_at_sensitivity_arg_validation(num_labels, min_sensitivity, thresholds, ignore_index)
        self.validate_args = validate_args
        self.min_sensitivity = min_sensitivity

    def compute(self) -> Tuple[Tensor, Tensor]:  # type: ignore[override]
        if self.thresholds is None:
            state = [dim_zero_cat(self.preds), dim_zero_cat(self.target)]  # type: ignore
        else:
            state = self.confmat
        return _multilabel_specificity_at_sensitivity_compute(
            state, self.num_labels, self.thresholds, self.ignore_index, self.min_sensitivity  # type: ignore
        )


class SpecificityAtSensitivity:
    r"""Computes the higest possible specificity value given the minimum sensitivity thresholds provided. This is
    done by first calculating the Receiver Operating Characteristic (ROC) curve for different thresholds and the
    find the specificity for a given sensitivity level.

    This function is a simple wrapper to get the task specific versions of this metric, which is done by setting the
    ``task`` argument to either ``'binary'``, ``'multiclass'`` or ``multilabel``. See the documentation of
    :mod:`BinarySpecificityAtSensitivity`, :func:`MulticlassSpecificityAtSensitivity` and
    :func:`MultilabelSpecificityAtSensitivity` for the specific details of each argument influence and examples.
    """

    def __new__(
        cls,
        task: Literal["binary", "multiclass", "multilabel"],
        min_sensitivity: float,
        thresholds: Optional[Union[int, List[float], Tensor]] = None,
        num_classes: Optional[int] = None,
        num_labels: Optional[int] = None,
        ignore_index: Optional[int] = None,
        validate_args: bool = True,
        **kwargs: Any,
    ) -> Metric:  # type: ignore
        if task == "binary":
            return BinarySpecificityAtSensitivity(min_sensitivity, thresholds, ignore_index, validate_args, **kwargs)
        if task == "multiclass":
            assert isinstance(num_classes, int)
            return MulticlassSpecificityAtSensitivity(
                num_classes, min_sensitivity, thresholds, ignore_index, validate_args, **kwargs
            )
        if task == "multilabel":
            assert isinstance(num_labels, int)
            return MultilabelSpecificityAtSensitivity(
                num_labels, min_sensitivity, thresholds, ignore_index, validate_args, **kwargs
            )
        raise ValueError(
            f"Expected argument `task` to either be `'binary'`, `'multiclass'` or `'multilabel'` but got {task}"
        )
