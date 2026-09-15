"""
Unit tests for Hugging Face Hub client and offline handling.
"""

try:
    import pytest
except ImportError:
    pytest = None

from pathlib import Path
from lunar_lfm.hub import LunarHubClient


def test_hub_client_initialization(tmp_path):
    """Verify cache directory setup and URL generation."""
    client = LunarHubClient(cache_dir=tmp_path)
    assert client.cache_dir.exists()
    assert "NASA-IBM-Lunar-Foundation-Model" in client.api_url
    assert "raw/main" in client.raw_base_url


def test_offline_mode_behavior(tmp_path, monkeypatch):
    """Verify that when network is unreachable, it reports structured offline status without crashing."""
    client = LunarHubClient(cache_dir=tmp_path)

    # Monkeypatch requests.get to simulate connection error
    def mock_get(*args, **kwargs):
        raise ConnectionError("Simulated network outage")

    monkeypatch.setattr("requests.get", mock_get)

    meta = client.get_remote_metadata()
    assert meta["_source"] == "offline_no_cache"
    assert "offline_guidance" in meta
    assert "error" in meta
