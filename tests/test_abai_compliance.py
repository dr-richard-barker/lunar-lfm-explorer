"""
Automated unit tests validating ABAI principles and landmine guards.
"""

import os
import re
from pathlib import Path
try:
    import pytest
except ImportError:
    pytest = None


ROOT_DIR = Path(__file__).resolve().parent.parent


def test_abai_l006_no_synthetic_results_fallback():
    """
    ABAI L006: Strictly prohibit silent synthetic fallback (e.g. np.random masquerading as real results).
    Inspect all Python files in src/ for random number generation.
    """
    src_dir = ROOT_DIR / "src"
    prohibited_patterns = [
        re.compile(r"np\.random"),
        re.compile(r"numpy\.random"),
        re.compile(r"random\.random\(\)"),
        re.compile(r"simulate_lunar_data"),
    ]

    for py_file in src_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        for pat in prohibited_patterns:
            matches = pat.findall(content)
            assert not matches, (
                f"ABAI L006 VIOLATION: Found prohibited synthetic pattern '{pat.pattern}' "
                f"in {py_file.name}. Real scientific models must not fake results with random fallbacks."
            )


def test_abai_l003_no_fabricated_dois():
    """
    ABAI L003: Verify no template-fabricated DOIs exist in documentation, citation, or metadata files.
    """
    fabricated_doi_regex = re.compile(r"10\.1038/s41526-0\d{2}-\d{5}-[a-z]", re.IGNORECASE)

    for doc_file in ROOT_DIR.rglob("*"):
        if doc_file.is_file() and doc_file.suffix in [".md", ".cff", ".json", ".py", ".toml"]:
            if ".git" in doc_file.parts or ".pytest_cache" in doc_file.parts:
                continue
            content = doc_file.read_text(encoding="utf-8", errors="ignore")
            matches = fabricated_doi_regex.findall(content)
            assert not matches, (
                f"ABAI L003 VIOLATION: Fabricated DOI found in {doc_file.name}: {matches}"
            )


def test_abai_l022_large_binaries_excluded_from_git():
    """
    ABAI L022: Ensure .gitignore excludes multi-GB model weights (*.pt, *.safetensors)
    and that no weights are accidentally tracked.
    """
    gitignore = ROOT_DIR / ".gitignore"
    assert gitignore.exists()
    content = gitignore.read_text(encoding="utf-8")

    assert "*.pt" in content
    assert "*.safetensors" in content
    assert "*.bin" in content

    # Assert no .pt or .safetensors files currently exist in the repo
    weights = list(ROOT_DIR.glob("**/*.pt")) + list(ROOT_DIR.glob("**/*.safetensors"))
    assert len(weights) == 0, f"Heavy model weights committed in Git tree: {weights}"


def test_abai_l008_non_vacuous_assertion_behavior():
    """
    ABAI L008: Verify that checkers are non-vacuous.
    Ensure our validator fails when given an invalid schema.
    """
    from lunar_lfm.modalities import validate_bundle_schema

    # Deliberately broken bundle (wrong channel count)
    bogus_bundle = {
        "scale_family": "WAC",
        "modalities": {"vis": {"shape": [999, 256, 256]}},
        "optical_metadata": {},
    }
    is_valid, errors = validate_bundle_schema(bogus_bundle)
    assert is_valid is False, "Checker failed to reject invalid bundle (vacuous pass)!"
    assert len(errors) > 0
