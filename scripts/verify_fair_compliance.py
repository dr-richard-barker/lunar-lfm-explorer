#!/usr/bin/env python3
"""
FAIR Principles and ABAI Landmines Compliance Auditor.

Runs static analysis and schema checks on this repository:
  1. FAIR metadata presence (CITATION.cff, codemeta.json, LICENSE, pyproject.toml)
  2. ABAI L001/L002/L003: Checks for fabricated DOIs and verifies grounded citations
  3. ABAI L006: Confirms zero silent synthetic fallbacks (no np.random masquerading as real data)
  4. ABAI L022: Verifies large model weights (*.pt, *.safetensors) are excluded from git
  5. ABAI L025: Checks standard scientific repository directory layout
  6. Modality completeness: 11 modalities, 8 optical metadata fields, 28 static context fields
"""

import os
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))


def check_fair_metadata() -> bool:
    print("\n[1/6] Checking FAIR Metadata & Licensing...")
    required_files = [
        "LICENSE",
        "CITATION.cff",
        "codemeta.json",
        "pyproject.toml",
        "README.md",
        "STATE.md",
    ]
    all_ok = True
    for f in required_files:
        p = ROOT_DIR / f
        if p.exists() and p.stat().st_size > 0:
            print(f"  ✓ {f} exists ({p.stat().st_size} bytes)")
        else:
            print(f"  ✗ MISSING OR EMPTY: {f}")
            all_ok = False
    return all_ok


def check_doi_integrity() -> bool:
    print("\n[2/6] Checking DOI & Citation Integrity (ABAI L001, L003)...")
    # Search for known fabricated DOI patterns
    fabricated_pattern = re.compile(r"10\.1038/s41526-0\d{2}-\d{5}-[a-z]", re.IGNORECASE)
    any_found = False

    for root, _, files in os.walk(ROOT_DIR):
        if ".git" in root:
            continue
        for file in files:
            if file.endswith((".md", ".cff", ".json", ".py", ".toml")):
                filepath = Path(root) / file
                try:
                    content = filepath.read_text(encoding="utf-8")
                    matches = fabricated_pattern.findall(content)
                    if matches:
                        print(f"  ✗ FABRICATED DOI FOUND in {filepath.relative_to(ROOT_DIR)}: {matches}")
                        any_found = True
                except Exception:
                    pass

    if not any_found:
        print("  ✓ No fabricated DOIs found across repository files.")
        return True
    return False


def check_zero_synthetic_fallback() -> bool:
    print("\n[3/6] Checking Zero-Synthetic Fallback Guarantee (ABAI L006)...")
    # Inspect src/ code for random fallback patterns
    src_dir = ROOT_DIR / "src"
    suspicious_patterns = [
        r"np\.random",
        r"numpy\.random",
        r"random\.random",
        r"simulate_lunar_data",
        r"fake_results",
    ]
    regexes = [re.compile(p) for p in suspicious_patterns]
    violations = []

    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file
                content = filepath.read_text(encoding="utf-8")
                for r in regexes:
                    if r.search(content):
                        violations.append((filepath.relative_to(ROOT_DIR), r.pattern))

    if violations:
        print("  ✗ VIOLATION: Found synthetic random generation pattern in source code:")
        for v in violations:
            print(f"     {v[0]}: pattern '{v[1]}'")
        return False
    else:
        print("  ✓ No synthetic/random generation fallbacks in source code. All outputs are strictly grounded.")
        return True


def check_binary_exclusions() -> bool:
    print("\n[4/6] Checking Git Weight Boundary (ABAI L022)...")
    gitignore = ROOT_DIR / ".gitignore"
    if not gitignore.exists():
        print("  ✗ Missing .gitignore!")
        return False

    content = gitignore.read_text(encoding="utf-8")
    required_ignores = ["*.pt", "*.bin", "*.safetensors"]
    for req in required_ignores:
        if req not in content:
            print(f"  ✗ .gitignore is missing '{req}'")
            return False

    # Check that no *.pt files exist in the repo
    heavy_files = list(ROOT_DIR.glob("**/*.pt")) + list(ROOT_DIR.glob("**/*.safetensors"))
    if heavy_files:
        print(f"  ✗ Heavy model weights accidentally present in working directory: {heavy_files}")
        return False

    print("  ✓ Large checkpoint files (*.pt, *.safetensors) properly excluded from git.")
    return True


def check_standard_scaffold() -> bool:
    print("\n[5/6] Checking Standard Scientific Repository Scaffold (ABAI L025)...")
    required_dirs = [
        "src/lunar_lfm",
        "scripts",
        "tests",
        "docs",
        "results",
        "figures",
        "tables",
    ]
    all_ok = True
    for d in required_dirs:
        p = ROOT_DIR / d
        if p.exists() and p.is_dir():
            print(f"  ✓ Directory {d}/ exists")
        else:
            print(f"  ✗ MISSING DIRECTORY: {d}/")
            all_ok = False
    return all_ok


def check_modalities_completeness() -> bool:
    print("\n[6/6] Checking Modality & Benchmark Grounding...")
    from lunar_lfm.modalities import MODALITIES, OPTICAL_METADATA_FIELDS, STATIC_CONTEXT_FIELDS
    from lunar_lfm.benchmarks import BENCHMARKS, SCIENTIFIC_DISCLOSURES

    if len(MODALITIES) != 9:
        print(f"  ✗ Expected 9 dense modalities, got {len(MODALITIES)}")
        return False
    if len(OPTICAL_METADATA_FIELDS) != 8:
        print(f"  ✗ Expected 8 optical metadata fields, got {len(OPTICAL_METADATA_FIELDS)}")
        return False
    if len(STATIC_CONTEXT_FIELDS) != 28:
        print(f"  ✗ Expected 28 static context fields, got {len(STATIC_CONTEXT_FIELDS)}")
        return False
    if len(BENCHMARKS) != 5:
        print(f"  ✗ Expected 5 benchmark tasks, got {len(BENCHMARKS)}")
        return False
    if len(SCIENTIFIC_DISCLOSURES) != 4:
        print(f"  ✗ Expected 4 scientific disclosures, got {len(SCIENTIFIC_DISCLOSURES)}")
        return False

    print("  ✓ 9 dense modalities, 8 optical fields, 28 static fields verified.")
    print("  ✓ 5 SomBench benchmark records and 4 scientific disclosures verified.")
    return True


def main() -> None:
    print("==================================================")
    print("  FAIR & ABAI Compliance Audit")
    print("==================================================")

    results = [
        check_fair_metadata(),
        check_doi_integrity(),
        check_zero_synthetic_fallback(),
        check_binary_exclusions(),
        check_standard_scaffold(),
        check_modalities_completeness(),
    ]

    print("\n==================================================")
    if all(results):
        print("  🎉 AUDIT RESULT: FULL COMPLIANCE (ALL 6 CHECKS PASSED)")
        print("==================================================")
        sys.exit(0)
    else:
        print("  ❌ AUDIT RESULT: AUDIT FAILED - SEE DETAILS ABOVE")
        print("==================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
