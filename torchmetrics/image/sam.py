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
from typing import Any, Dict, List, Optional

from torch import Tensor
from typing_extensions import Literal

from torchmetrics.functional.image.sam import _sam_compute, _sam_update
from torchmetrics.metric import Metric
from torchmetrics.utilities import rank_zero_warn
from torchmetrics.utilities.data import dim_zero_cat


class SpectralAngleMapper(Metric):
    """Spectral Angle Mapper determine thespectral similarity between image spectra and reference spectra by
    calculating the angle between thespectra, where small angles between the two spectrums indicate high similarity
    and high angles indicate low similarity

    Args:
        reduction: a method to reduce metric score over labels.
            - ``'elementwise_mean'``: takes the mean (default)
            - ``'sum'``: takes the sum
            - ``'none'``: no reduction will be applied
        compute_on_step:
            Forward only calls ``update()`` and returns None if this is set to False.

        kwargs:
            Additional keyword arguments, see :ref:`Metric kwargs` for more info.
    Return:
        Tensor with SpectralAngleMapper score

    Example:
        >>> import torch
        >>> from torchmetrics import SpectralAngleMapper
        >>> preds = torch.rand([16, 1, 16, 16])
        >>> target = torch.rand([16, 1, 16, 16])
        >>> sam = SpectralAngleMapper()
        >>> sam(preds, target)
        tensor(0.7542)
    """

    preds: List[Tensor]
    target: List[Tensor]
    higher_is_better: bool = False

    def __init__(
        self,
        reduction: Literal["elementwise_mean", "sum", "none"] = "elementwise_mean",
        compute_on_step: Optional[bool] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        super().__init__(compute_on_step=compute_on_step, **kwargs)
        rank_zero_warn(
            "Metric `SpectralAngleMapper` will save all targets and"
            " predictions in buffer. For large datasets this may lead"
            " to large memory footprint."
        )

        self.add_state("preds", default=[], dist_reduce_fx="cat")
        self.add_state("target", default=[], dist_reduce_fx="cat")
        self.reduction = reduction

    def _update(self, preds: Tensor, target: Tensor) -> None:
        """Update state with predictions and targets.

        Args:
            preds: Predictions from model
            target: Ground truth values
        """
        preds, target = _sam_update(preds, target)
        self.preds.append(preds)
        self.target.append(target)

    def _compute(self) -> Tensor:
        """Computes explained variance over state."""
        preds = dim_zero_cat(self.preds)
        target = dim_zero_cat(self.target)
        return _sam_compute(preds, target, self.reduction)


