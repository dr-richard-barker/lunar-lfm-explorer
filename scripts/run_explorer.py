#!/usr/bin/env python3
"""
Convenience launcher for the Lunar Foundation Model Explorer.

Usage:
  python3 scripts/run_explorer.py --serve [--port 8088]
  python3 scripts/run_explorer.py info
  python3 scripts/run_explorer.py inspect-modalities
  python3 scripts/run_explorer.py inspect-model
  python3 scripts/run_explorer.py benchmarks
"""

import sys
from pathlib import Path

# Add src to pythonpath
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--serve":
        port = 8088
        if "--port" in sys.argv:
            idx = sys.argv.index("--port")
            if idx + 1 < len(sys.argv):
                port = int(sys.argv[idx + 1])
        from lunar_lfm.dashboard.app import run_dashboard
        run_dashboard(port=port)
    else:
        from lunar_lfm.cli import main
        main()
