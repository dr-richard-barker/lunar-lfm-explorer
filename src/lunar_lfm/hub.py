"""
Hugging Face Hub interface for the NASA-IBM Lunar Foundation Model.

Provides safe, verified metadata inspection, configuration retrieval, and optional
on-demand weight downloading with atomic resumable state (ABAI L022, L026).
Strictly adheres to ABAI L006: never silently fallback to synthetic random data on network error.
Uses standard library urllib.request for zero-dependency portability.
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Any

from lunar_lfm.config import HF_MODEL_ID, HF_DATASET_ID


DEFAULT_CACHE_DIR = Path.home() / ".cache" / "lunar_lfm"


class LunarHubClient:
    """Client for querying the NASA-IBM LFM Hugging Face repository."""

    def __init__(self, model_id: str = HF_MODEL_ID, cache_dir: Optional[Path] = None):
        self.model_id = model_id
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.api_url = f"https://huggingface.co/api/models/{self.model_id}"
        self.raw_base_url = f"https://huggingface.co/{self.model_id}/raw/main"

    def get_remote_metadata(self, timeout_sec: int = 10) -> Dict[str, Any]:
        """
        Fetch repository metadata from the Hugging Face API.
        If offline, reads from local cache if available, or returns structured offline status.
        Never generates synthetic placeholder numbers (ABAI L006).
        """
        cache_file = self.cache_dir / "hf_metadata_cache.json"

        try:
            req = urllib.request.Request(
                self.api_url,
                headers={"User-Agent": "lunar-lfm-explorer/0.1.0"},
            )
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                if resp.status == 200:
                    raw_data = resp.read().decode("utf-8")
                    data = json.loads(raw_data)
                    # Atomic cache write
                    temp_file = cache_file.with_suffix(".tmp")
                    with open(temp_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    temp_file.replace(cache_file)
                    data["_source"] = "live_api"
                    return data
                else:
                    return {
                        "_source": "error_response",
                        "error": f"Hugging Face API returned status HTTP {resp.status}",
                        "model_id": self.model_id,
                    }
        except Exception as exc:
            # Fallback to cached metadata if present
            if cache_file.exists():
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cached_data = json.load(f)
                    cached_data["_source"] = "disk_cache_offline"
                    cached_data["_offline_reason"] = str(exc)
                    return cached_data
                except Exception:
                    pass

            # Explicit failure - no silent random generation (ABAI L006)
            return {
                "_source": "offline_no_cache",
                "error": f"Could not connect to Hugging Face API: {exc}",
                "model_id": self.model_id,
                "offline_guidance": (
                    "Network unreachable and no local metadata cache found. "
                    "Connect to internet or inspect local built-in specs with 'lunar-lfm inspect-model'."
                ),
            }

    def list_sibling_files(self) -> List[Dict[str, Any]]:
        """List files registered in the Hugging Face repository."""
        meta = self.get_remote_metadata()
        if "siblings" in meta:
            return meta["siblings"]
        return []

    def get_backbone_config_text(self, timeout_sec: int = 10) -> Optional[str]:
        """Fetch the raw backbone YAML configuration without downloading full weights."""
        cache_file = self.cache_dir / "backbone_config.yaml"
        url = f"{self.raw_base_url}/backbone/config.yaml"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "lunar-lfm-explorer/0.1.0"},
            )
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                if resp.status == 200:
                    content = resp.read().decode("utf-8")
                    temp_file = cache_file.with_suffix(".tmp")
                    with open(temp_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    temp_file.replace(cache_file)
                    return content
        except Exception:
            pass

        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                return f.read()

        return None

    def download_checkpoint(
        self,
        target_dir: Optional[Path] = None,
        only_backbone: bool = True,
    ) -> Dict[str, Any]:
        """
        Download checkpoints via huggingface_hub on explicit user request.
        Saves into a local cache or designated directory outside Git.
        """
        try:
            from huggingface_hub import snapshot_download  # type: ignore
        except ImportError:
            return {
                "success": False,
                "error": "huggingface_hub package is required for checkpoint download. Run 'pip install huggingface_hub'.",
            }

        dest = Path(target_dir) if target_dir else (self.cache_dir / "weights")
        dest.mkdir(parents=True, exist_ok=True)

        patterns = ["backbone/*"] if only_backbone else None

        try:
            local_path = snapshot_download(
                repo_id=self.model_id,
                local_dir=str(dest),
                allow_patterns=patterns,
                resume_download=True,
            )
            return {
                "success": True,
                "local_dir": local_path,
                "only_backbone": only_backbone,
            }
        except Exception as exc:
            return {
                "success": False,
                "error": f"Failed to download checkpoint: {exc}",
            }
