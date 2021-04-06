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
from typing import Optional, Tuple

import torch
from torch import Tensor

from torchmetrics.utilities.checks import _check_same_shape


def _update_mean(old_mean: Tensor, old_nobs: Tensor, data: Tensor) -> Tensor:
    """ Update a mean estimate given new data
    Args:
        old_mean: current mean estimate
        old_nobs: number of observation until now
        data: data used for updating the estimate
    Returns:
        new_mean: updated mean estimate
    """
    data_size = data.shape[0]
    return (old_mean * old_nobs + data.mean(dim=0) * data_size) / (old_nobs + data_size)


def _update_cov(old_cov: Tensor, old_mean: Tensor, new_mean: Tensor, data: Tensor):
    """ Update a covariance estimate given new data
    Args:
        old_cov: current covariance estimate
        old_mean: current mean estimate
        new_mean: updated mean estimate
        data: data used for updating the estimate
    Returns:
        new_mean: updated covariance estimate
    """
    return old_cov + (data - new_mean).T @ (data - old_mean)


def _pearson_corrcoef_update(
    preds: Tensor,
    target: Tensor,
    old_mean: Optional[Tensor] = None,
    old_cov: Optional[Tensor] = None,
    old_nobs: Optional[Tensor] = None
) -> Tuple[Tensor, Tensor, Tensor, Tensor]:
    """ updates current estimates of the mean, cov and n_obs with new data for calculating
        pearsons correlation
    """
    # Data checking
    _check_same_shape(preds, target)
    preds = preds.squeeze()
    target = target.squeeze()
    if preds.ndim > 1 or target.ndim > 1:
        raise ValueError('Expected both predictions and target to be 1 dimensional tensors.')
    data = torch.stack([preds, target], dim=1)

    if old_mean is None:
        old_mean = 0
    if old_cov is None:
        old_cov = 0
    if old_nobs is None:
        old_nobs = 0

    new_mean = _update_mean(old_mean, old_nobs, data)
    new_cov = _update_cov(old_cov, old_mean, new_mean, data)
    new_size = old_nobs + preds.numel()

    return new_mean, new_cov, new_size


def _pearson_corrcoef_compute(c: Tensor, nobs: Tensor):
    """ computes the final pearson correlation based on covariance matrix and number of observatiosn """
    c /= (nobs - 1)
    x_var = c[0, 0]
    y_var = c[1, 1]
    cov = c[0, 1]
    corrcoef = cov / (x_var * y_var).sqrt()
    return torch.clamp(corrcoef, -1.0, 1.0)


def pearson_corrcoef(preds: Tensor, target: Tensor) -> Tensor:
    """
    Computes pearson correlation coefficient.

    Args:
        preds: estimated scores
        target: ground truth scores

    Example:
        >>> from torchmetrics.functional import pearson_corrcoef
        >>> target = torch.tensor([3, -0.5, 2, 7])
        >>> preds = torch.tensor([2.5, 0.0, 2, 8])
        >>> pearson_corrcoef(preds, target)
        tensor(0.9849)
    """
    _, c, nobs = _pearson_corrcoef_update(preds, target)
    return _pearson_corrcoef_compute(c, nobs)
