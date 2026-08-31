"""MCDL Research Expansion Sub-Package (Phase 1).

Additive research tracks and CPU Wave 1 infrastructure.
"""

from mcdl.research.budget import BudgetContext, GlobalBudget, StageTimeoutError, check_kill_switch
from mcdl.research.c2st import run_c2st_evaluation
from mcdl.research.checkpoint import atomic_write_json, atomic_write_text, save_stage_checkpoint
from mcdl.research.comparison import generate_wave1_summary_table
from mcdl.research.environment import detect_environment_profile
from mcdl.research.graph import CausalGraphTopology, build_causal_graph_from_transactions
from mcdl.research.graph_leakage_audit import audit_graph_causal_integrity
from mcdl.research.l3_fidelity import evaluate_l3_behavioral_fidelity
from mcdl.research.provenance import Namespace, compute_file_sha256, create_dataset_provenance
from mcdl.research.tstr import evaluate_tstr_transfer

__all__ = [
    "BudgetContext",
    "GlobalBudget",
    "StageTimeoutError",
    "check_kill_switch",
    "atomic_write_json",
    "atomic_write_text",
    "save_stage_checkpoint",
    "Namespace",
    "compute_file_sha256",
    "create_dataset_provenance",
    "detect_environment_profile",
    "evaluate_l3_behavioral_fidelity",
    "run_c2st_evaluation",
    "evaluate_tstr_transfer",
    "CausalGraphTopology",
    "build_causal_graph_from_transactions",
    "audit_graph_causal_integrity",
    "generate_wave1_summary_table",
]
