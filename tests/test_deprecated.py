import pytest
import torch

from torchmetrics import Accuracy, Metric


def test_compute_on_step():
    with pytest.warns(
        DeprecationWarning, match="Argument `compute_on_step` is deprecated in v0.8 and will be removed in v0.9"
    ):
        Accuracy(compute_on_step=False)  # any metric will raise the warning


def test_error_overriden_update():
    class OldMetricAPI(Metric):
        def __init__(self):
            super().__init__()
            self.add_state("x", torch.tensor(0))

        def update(self, *args, **kwargs):
            self.x += 1

        def _update(self, *args, **kwargs):
            self.x += 1

        def _compute(self):
            return self.x

    with pytest.raises(UserWarning, match=""):
        OldMetricAPI()


def test_error_overriden_compute():
    class OldMetricAPI(Metric):
        def __init__(self):
            super().__init__()
            self.add_state("x", torch.tensor(0))

        def compute(self):
            return self.x

        def _update(self, *args, **kwargs):
            self.x += 1

        def _compute(self):
            return self.x

    with pytest.raises(UserWarning, match=""):
        OldMetricAPI()
