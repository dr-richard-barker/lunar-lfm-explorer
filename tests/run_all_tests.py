#!/usr/bin/env python3
"""
Test discovery and runner for lunar-lfm-explorer.

Supports execution with standard Python (zero dependencies) or via pytest.
Runs every test module imported in run_tests() below, including:
  - test_modalities.py
  - test_model_specs.py
  - test_benchmarks.py
  - test_hub_client.py
  - test_abai_compliance.py
"""

import inspect
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))
sys.path.insert(0, str(ROOT_DIR))


class MiniMonkeyPatch:
    """setattr("pkg.module.attr", value) with undo(), like pytest's monkeypatch fixture."""

    def __init__(self):
        self._undo = []

    def setattr(self, target, value):
        import importlib
        module_path, attr = target.rsplit(".", 1)
        obj = importlib.import_module(module_path)
        self._undo.append((obj, attr, getattr(obj, attr)))
        setattr(obj, attr, value)

    def undo(self):
        for obj, attr, old in reversed(self._undo):
            setattr(obj, attr, old)
        self._undo.clear()


def run_tests() -> bool:
    import tests.test_modalities as t_mod
    import tests.test_model_specs as t_spec
    import tests.test_benchmarks as t_bench
    import tests.test_hub_client as t_hub
    import tests.test_abai_compliance as t_abai
    import tests.test_inference as t_infer
    import tests.test_shackleton_analysis as t_shack
    import tests.test_blender_pipeline as t_blend
    import tests.test_3d_solar_lab as t_lab

    modules = [t_mod, t_spec, t_bench, t_hub, t_abai, t_infer, t_shack, t_blend, t_lab]
    total = 0
    passed = 0
    failed = 0

    print("=" * 60)
    print("  Running NASA-IBM LFM Explorer Test Suite")
    print("=" * 60)
    start_time = time.time()

    import tempfile

    for mod in modules:
        mod_name = mod.__name__.split(".")[-1]
        print(f"\n[{mod_name}]")
        for attr in dir(mod):
            if attr.startswith("test_"):
                fn = getattr(mod, attr)
                if callable(fn):
                    total += 1
                    try:
                        # Check parameters
                        sig = inspect.signature(fn)
                        if "tmp_path" in sig.parameters and "monkeypatch" in sig.parameters:
                            # Minimal working monkeypatch (an earlier stub did nothing, so
                            # patched tests silently ran against the real network).
                            mp = MiniMonkeyPatch()
                            try:
                                with tempfile.TemporaryDirectory() as td:
                                    fn(Path(td), mp)
                            finally:
                                mp.undo()
                        elif "tmp_path" in sig.parameters:
                            with tempfile.TemporaryDirectory() as td:
                                fn(Path(td))
                        else:
                            fn()
                        print(f"  ✓ {attr}")
                        passed += 1
                    except Exception as e:
                        print(f"  ✗ {attr} FAILED: {e}")
                        failed += 1

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"  Test Results: {passed}/{total} passed in {elapsed:.3f}s")
    if failed == 0:
        print("  🎉 ALL TESTS PASSED SUCCESSFULLY")
        print("=" * 60)
        return True
    else:
        print(f"  ❌ {failed} TEST(S) FAILED")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
