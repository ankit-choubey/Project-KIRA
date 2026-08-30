"""Unit tests for research comparison table generation and statistical flags."""

from mcdl.research.comparison import apply_statistical_flags, generate_wave1_summary_table


def test_apply_statistical_flags():
    flags = apply_statistical_flags(n_samples=50, n_positive=10, ci_width=0.20)
    assert "UNDERPOWERED" in flags
    assert "LOW_SAMPLE" in flags
    assert "HIGH_VARIANCE" in flags


def test_generate_wave1_summary_table():
    s00 = {"status": "COMPLETE"}
    s01 = {"status": "COMPLETE"}
    l3 = {"status": "COMPLETE", "sample_count_synthetic": 500, "p1_interarrival": {"ratio": 1.2}}
    c2st = {"status": "COMPLETE", "c2st_auc": 0.65, "sample_counts": {"n_total": 400}}
    tstr = {"status": "COMPLETE", "tstr": {"pr_auc": 0.72, "n_test_real": 200, "n_test_real_fraud": 15}}
    graph = {"audit_passed": True, "status": "PASS"}

    table = generate_wave1_summary_table(s00, s01, l3, c2st, tstr, graph)
    assert table["baseline_run_id"] == "run_tiny_s20260827_193f7897_40997ab"
    assert len(table["entries"]) == 4
    assert table["entries"][3]["preliminary_decision"] == "ELIGIBLE_FOR_GPU_G01"
