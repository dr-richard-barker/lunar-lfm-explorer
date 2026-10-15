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

    # The client uses urllib.request.urlopen; make it fail as an outage would.
    # (An earlier version patched requests.get, which the client never calls, so the
    # test reached the live API and failed whenever the network was up.)
    import urllib.error

    def mock_urlopen(*args, **kwargs):
        raise urllib.error.URLError("Simulated network outage")

    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)

    meta = client.get_remote_metadata()
    assert meta["_source"] == "offline_no_cache"
    assert "offline_guidance" in meta
    assert "error" in meta
