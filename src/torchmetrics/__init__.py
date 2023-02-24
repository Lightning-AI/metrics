r"""Root package info."""
import logging as __logging
import os

from torchmetrics.__about__ import *  # noqa: F401, F403

_logger = __logging.getLogger("torchmetrics")
_logger.addHandler(__logging.StreamHandler())
_logger.setLevel(__logging.INFO)

_PACKAGE_ROOT = os.path.dirname(__file__)
_PROJECT_ROOT = os.path.dirname(_PACKAGE_ROOT)

from torchmetrics import functional  # noqa: E402
from torchmetrics.aggregation import CatMetric, MaxMetric, MeanMetric, MinMetric, SumMetric  # noqa: E402
from torchmetrics.audio import PermutationInvariantTraining  # noqa: E402
from torchmetrics.audio import (  # noqa: E402
    ScaleInvariantSignalDistortionRatio,
    ScaleInvariantSignalNoiseRatio,
    SignalDistortionRatio,
    SignalNoiseRatio,
)
from torchmetrics.classification import (  # noqa: E402
    AUROC,
    ROC,
    Accuracy,
    AveragePrecision,
    CalibrationError,
    CohenKappa,
    ConfusionMatrix,
    Dice,
    ExactMatch,
    F1Score,
    FBetaScore,
    HammingDistance,
    HingeLoss,
    JaccardIndex,
    MatthewsCorrCoef,
    Precision,
    PrecisionRecallCurve,
    Recall,
    Specificity,
    StatScores,
)
from torchmetrics.collections import MetricCollection  # noqa: E402
from torchmetrics.detection import PanopticQuality  # noqa: E402
from torchmetrics.image import (  # noqa: E402
    ErrorRelativeGlobalDimensionlessSynthesis,
    MultiScaleStructuralSimilarityIndexMeasure,
    PeakSignalNoiseRatio,
    SpectralAngleMapper,
    SpectralDistortionIndex,
    StructuralSimilarityIndexMeasure,
    TotalVariation,
    UniversalImageQualityIndex,
)
from torchmetrics.metric import Metric  # noqa: E402
from torchmetrics.nominal import CramersV  # noqa: E402
from torchmetrics.nominal import PearsonsContingencyCoefficient, TheilsU, TschuprowsT  # noqa: E402
from torchmetrics.regression import ConcordanceCorrCoef  # noqa: E402
from torchmetrics.regression import (  # noqa: E402
    CosineSimilarity,
    ExplainedVariance,
    KendallRankCorrCoef,
    KLDivergence,
    LogCoshError,
    MeanAbsoluteError,
    MeanAbsolutePercentageError,
    MeanSquaredError,
    MeanSquaredLogError,
    PearsonCorrCoef,
    R2Score,
    SpearmanCorrCoef,
    SymmetricMeanAbsolutePercentageError,
    TweedieDevianceScore,
    WeightedMeanAbsolutePercentageError,
)
from torchmetrics.retrieval import RetrievalFallOut  # noqa: E402
from torchmetrics.retrieval import (  # noqa: E402
    RetrievalHitRate,
    RetrievalMAP,
    RetrievalMRR,
    RetrievalNormalizedDCG,
    RetrievalPrecision,
    RetrievalPrecisionRecallCurve,
    RetrievalRecall,
    RetrievalRecallAtFixedPrecision,
    RetrievalRPrecision,
)
from torchmetrics.text import (  # noqa: E402
    BLEUScore,
    CharErrorRate,
    CHRFScore,
    ExtendedEditDistance,
    MatchErrorRate,
    Perplexity,
    SacreBLEUScore,
    SQuAD,
    TranslationEditRate,
    WordErrorRate,
    WordInfoLost,
    WordInfoPreserved,
)
from torchmetrics.wrappers import BootStrapper  # noqa: E402
from torchmetrics.wrappers import ClasswiseWrapper, MetricTracker, MinMaxMetric, MultioutputWrapper  # noqa: E402

__all__ = [
    "functional",
    "Accuracy",
    "AUROC",
    "AveragePrecision",
    "BLEUScore",
    "BootStrapper",
    "CalibrationError",
    "CatMetric",
    "ClasswiseWrapper",
    "CharErrorRate",
    "CHRFScore",
    "ConcordanceCorrCoef",
    "CohenKappa",
    "ConfusionMatrix",
    "CosineSimilarity",
    "CramersV",
    "Dice",
    "TweedieDevianceScore",
    "ErrorRelativeGlobalDimensionlessSynthesis",
    "ExactMatch",
    "ExplainedVariance",
    "ExtendedEditDistance",
    "F1Score",
    "FBetaScore",
    "HammingDistance",
    "HingeLoss",
    "JaccardIndex",
    "KendallRankCorrCoef",
    "KLDivergence",
    "LogCoshError",
    "MatchErrorRate",
    "MatthewsCorrCoef",
    "MaxMetric",
    "MeanAbsoluteError",
    "MeanAbsolutePercentageError",
    "MeanMetric",
    "MeanSquaredError",
    "MeanSquaredLogError",
    "Metric",
    "MetricCollection",
    "MetricTracker",
    "MinMaxMetric",
    "MinMetric",
    "MultioutputWrapper",
    "MultiScaleStructuralSimilarityIndexMeasure",
    "PanopticQuality",
    "PearsonCorrCoef",
    "PearsonsContingencyCoefficient",
    "PermutationInvariantTraining",
    "Perplexity",
    "Precision",
    "PrecisionRecallCurve",
    "PeakSignalNoiseRatio",
    "R2Score",
    "Recall",
    "RetrievalFallOut",
    "RetrievalHitRate",
    "RetrievalMAP",
    "RetrievalMRR",
    "RetrievalNormalizedDCG",
    "RetrievalPrecision",
    "RetrievalRecall",
    "RetrievalRPrecision",
    "RetrievalPrecisionRecallCurve",
    "RetrievalRecallAtFixedPrecision",
    "ROC",
    "SacreBLEUScore",
    "SignalDistortionRatio",
    "ScaleInvariantSignalDistortionRatio",
    "ScaleInvariantSignalNoiseRatio",
    "SignalNoiseRatio",
    "SpearmanCorrCoef",
    "Specificity",
    "SpectralAngleMapper",
    "SpectralDistortionIndex",
    "SQuAD",
    "StructuralSimilarityIndexMeasure",
    "StatScores",
    "SumMetric",
    "SymmetricMeanAbsolutePercentageError",
    "TheilsU",
    "TotalVariation",
    "TranslationEditRate",
    "TschuprowsT",
    "UniversalImageQualityIndex",
    "WeightedMeanAbsolutePercentageError",
    "WordErrorRate",
    "WordInfoLost",
    "WordInfoPreserved",
]
