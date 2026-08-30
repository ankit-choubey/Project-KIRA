"""Unit tests for BudgetContext, GlobalBudget, and kill-switch controls."""

import time
import pytest
from mcdl.research.budget import BudgetContext, GlobalBudget, StageTimeoutError, check_kill_switch, KillSwitchTriggered


def test_budget_context_normal_completion():
    with BudgetContext("TEST-01", limit_seconds=5.0) as ctx:
        time.sleep(0.01)
    assert ctx.status == "COMPLETE"
    assert ctx.elapsed_seconds > 0.0
    assert ctx.truncation_reason is None


def test_budget_context_timeout(tmp_path):
    ctx = BudgetContext("TEST-TIMEOUT", limit_seconds=0.01)
    with ctx:
        time.sleep(0.02)
        ctx.check_budget()  # Should raise and be caught by __exit__
    assert ctx.status == "INCOMPLETE"
    assert "timed out" in (ctx.truncation_reason or "")


def test_kill_switch_trigger(tmp_path):
    stop_file = tmp_path / "STOP"
    stop_file.write_text("STOP", encoding="utf-8")
    
    with pytest.raises(KillSwitchTriggered):
        check_kill_switch(stop_file)
        
    abort_file = tmp_path / "ABORT_REASON.txt"
    assert abort_file.exists()
    assert "Kill switch activated" in abort_file.read_text(encoding="utf-8")


def test_global_budget():
    gb = GlobalBudget(max_seconds=5.0)
    gb.check()
    assert gb.elapsed_seconds >= 0.0
