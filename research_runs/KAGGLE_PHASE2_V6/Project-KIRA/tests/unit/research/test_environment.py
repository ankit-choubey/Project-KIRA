"""Unit tests for environment profiling and resource detection."""

from mcdl.research.environment import detect_environment_profile


def test_detect_environment_profile():
    profile = detect_environment_profile()
    assert "cpu_count" in profile
    assert profile["cpu_count"] >= 1
    assert "python_version" in profile
    assert "gpu_available" in profile
    assert isinstance(profile["gpu_available"], bool)
