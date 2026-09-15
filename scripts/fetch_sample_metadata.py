#!/usr/bin/env python3
"""
Pre-fetches and caches repository metadata and backbone config from Hugging Face.
Enables full offline explorer operation without downloading the 12.8 GB weight checkpoints.
Saves resumable state to disk (ABAI L026).
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from lunar_lfm.hub import LunarHubClient


def main() -> None:
    print("Pre-fetching Hugging Face metadata for offline resilience...")
    client = LunarHubClient()
    meta = client.get_remote_metadata()

    if "error" in meta and "_offline_reason" not in meta:
        print(f"Warning: Remote query returned: {meta.get('error')}")
        print("Using local built-in specifications.")
        return

    print(f"✓ Metadata cached for model: {meta.get('id', client.model_id)}")
    siblings = meta.get("siblings", [])
    print(f"✓ Found {len(siblings)} registered sibling files.")

    print("Fetching backbone configuration YAML...")
    config_yaml = client.get_backbone_config_text()
    if config_yaml:
        print(f"✓ Backbone configuration cached ({len(config_yaml)} bytes).")
    else:
        print("Note: Backbone config YAML could not be fetched (offline or not reachable).")

    print("\nPre-fetch complete. Explorer can now run in full offline mode.")


if __name__ == "__main__":
    main()
