"""Root package info."""

__version__ = '0.0.0rc1'
__author__ = 'PyTorchLightning et al.'
__author_email__ = 'name@pytorchlightning.ai'
__license__ = 'TBD'
__copyright__ = 'Copyright (c) 2020-2020, %s.' % __author__
__homepage__ = 'https://github.com/PyTorchLightning/torchmetrics'
__docs__ = "PyTorch Lightning Sample project."
__long_doc__ = """
What is it?
-----------
...
"""
from torchmetrics.metric import Metric

from torchmetrics.classification import (
    Accuracy,
    Precision,
    Recall,
    ConfusionMatrix,
    PrecisionRecallCurve,
    AveragePrecision,
    ROC,
    FBeta,
    F1,
)

from torchmetrics.regression import (
    MeanSquaredError,
    MeanAbsoluteError,
    MeanSquaredLogError,
    ExplainedVariance,
    PSNR,
    SSIM,
)
