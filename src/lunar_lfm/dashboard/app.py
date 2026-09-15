"""
Lightweight local HTTP server for the Lunar Foundation Model interactive dashboard.

Zero external web dependencies (uses standard library http.server) with JSON API
endpoints for model specs, modalities, benchmarks, and static file serving.
Optimized for both Desktop and iPad / touchscreen clients (ABAI L027).
"""

import http.server
import json
import socketserver
import urllib.parse
from pathlib import Path
from typing import Any, Dict

from lunar_lfm.config import HF_MODEL_ID, HF_DATASET_ID, MODEL_SPECS, ScaleFamily
from lunar_lfm.modalities import (
    MODALITIES,
    OPTICAL_METADATA_FIELDS,
    STATIC_CONTEXT_FIELDS,
    list_modalities,
)
from lunar_lfm.model_inspect import ModelArchitecture
from lunar_lfm.benchmarks import BENCHMARKS, SCIENTIFIC_DISCLOSURES
from lunar_lfm.hub import LunarHubClient


STATIC_DIR = Path(__file__).parent / "static"


class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler serving static files and API endpoints."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed_path = urllib.parse.urlparse(self.path)

        if parsed_path.path.startswith("/api/"):
            self.handle_api(parsed_path)
        else:
            super().do_GET()

    def handle_api(self, parsed_path: urllib.parse.ParseResult) -> None:
        """Route JSON API endpoints."""
        endpoint = parsed_path.path[len("/api/"):]
        query_params = urllib.parse.parse_qs(parsed_path.query)

        response_data: Dict[str, Any] = {}

        if endpoint == "overview":
            arch = ModelArchitecture()
            params = arch.estimate_parameter_breakdown()
            response_data = {
                "model_id": HF_MODEL_ID,
                "dataset_id": HF_DATASET_ID,
                "specs": {
                    "backbone": MODEL_SPECS.backbone_type,
                    "embed_dim": MODEL_SPECS.embed_dim,
                    "depth": MODEL_SPECS.depth,
                    "heads": MODEL_SPECS.num_heads,
                    "input_size": MODEL_SPECS.input_size,
                    "pretrain_patch_size": MODEL_SPECS.pretrain_patch_size,
                    "fsq_levels": MODEL_SPECS.fsq_levels,
                    "total_modalities": MODEL_SPECS.total_modalities_count,
                    "pretrain_steps": MODEL_SPECS.pretrain_steps,
                    "pretrain_hardware": MODEL_SPECS.pretrain_hardware,
                    "sombench_bundles": MODEL_SPECS.total_sombench_bundles,
                    "approx_params_m": params["approx_backbone_params_millions"],
                    "approx_weight_gb": params["estimated_bf16_weight_gb"],
                },
            }

        elif endpoint == "modalities":
            family_str = query_params.get("family", [None])[0]
            family = ScaleFamily(family_str) if family_str in ["WAC", "NAC"] else None
            mods = list_modalities(family)
            response_data = {
                "dense": [
                    {
                        "key": m.key,
                        "name": m.name,
                        "family": m.family.value,
                        "channels": m.channels,
                        "resolution_m": m.native_resolution_m,
                        "instrument": m.source_instrument,
                        "description": m.description,
                        "channel_names": m.channel_names,
                    }
                    for m in mods
                ],
                "optical_metadata": list(OPTICAL_METADATA_FIELDS),
                "static_context": list(STATIC_CONTEXT_FIELDS),
            }

        elif endpoint == "benchmarks":
            response_data = {
                "benchmarks": [
                    {
                        "id": b.task_id,
                        "name": b.name,
                        "target": b.target_object,
                        "scale": b.scale_family,
                        "metric": b.metric_name,
                        "direction": b.metric_direction,
                        "lfm_score": b.best_lfm_score,
                        "lfm_config": b.best_lfm_config,
                        "baseline_score": b.best_baseline_score,
                        "baseline_name": b.best_baseline_name,
                        "random_init": b.random_init_lfm_score,
                        "takeaway": b.key_takeaway,
                    }
                    for b in BENCHMARKS.values()
                ],
                "disclosures": SCIENTIFIC_DISCLOSURES,
            }

        elif endpoint == "hub-status":
            client = LunarHubClient()
            response_data = client.get_remote_metadata()

        elif endpoint == "calculate-sequence":
            patch = int(query_params.get("patch", [16])[0])
            dense_mods = int(query_params.get("dense_mods", [5])[0])
            arch = ModelArchitecture()
            grid_h, grid_w, total_patches = arch.compute_patch_grid((patch, patch))
            seq = arch.compute_sequence_length(num_dense_modalities=dense_mods, patch_size=(patch, patch))
            response_data = {
                "patch_size": patch,
                "grid": f"{grid_h}x{grid_w}",
                "patches_per_modality": total_patches,
                **seq,
            }

        else:
            self.send_error(404, f"API endpoint '{endpoint}' not found")
            return

        body = json.dumps(response_data, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


def run_dashboard(port: int = 8088, host: str = "0.0.0.0") -> None:
    """Launch local dashboard server."""
    with socketserver.TCPServer((host, port), DashboardRequestHandler) as httpd:
        print(f"==================================================")
        print(f"  NASA-IBM Lunar Foundation Model Dashboard")
        print(f"  Serving at: http://localhost:{port}")
        print(f"  Tablet/iPad Touch Optimized (ABAI L027)")
        print(f"  Press Ctrl+C to stop.")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down dashboard server.")
            httpd.server_close()
