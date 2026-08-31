"""Blue Team Detection & Policy Module."""

from mcdl.blue.calibration import IsotonicCalibrator, compute_brier_score, compute_ece
from mcdl.blue.explainer import TreeSHAPExplainer
from mcdl.blue.intent import compute_intent_drift
from mcdl.blue.metrics import ModelEvaluationReport, evaluate_predictions
from mcdl.blue.model import BlueDetector
from mcdl.blue.policy import CostSensitiveRouter, PolicyCostConfig
from mcdl.blue.rule_baseline import RuleBaseline
from mcdl.blue.split import SplitSummary, TemporalSplit, temporal_split

__all__ = [
    "BlueDetector",
    "RuleBaseline",
    "CostSensitiveRouter",
    "PolicyCostConfig",
    "IsotonicCalibrator",
    "TreeSHAPExplainer",
    "compute_ece",
    "compute_brier_score",
    "compute_intent_drift",
    "ModelEvaluationReport",
    "evaluate_predictions",
    "TemporalSplit",
    "SplitSummary",
    "temporal_split",
]
