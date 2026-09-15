#!/usr/bin/env python3
"""Attestation: a record that `/abai check` cleared a repo's publishable content.

The gate ([[L003]], [[L006]], [[L007]]) needs to distinguish "these docs were
verified" from "these docs were changed since they were verified". It does that by
hashing the *tracked blob ids* of everything publishable at HEAD. Blob ids come
from git itself, so the digest changes if and only if the content changes — it is
insensitive to mtimes, checkouts and clones, and needs no re-reading of files.

Used as a module by ``abai_gate.py`` and as a CLI by the ``/abai check`` mode.

Usage::

    python3 scripts/attest.py digest [repo]      # print the current digest
    python3 scripts/attest.py status [repo]      # is the attestation current?
    python3 scripts/attest.py write  [repo] --verdict clear --note "..."
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

# What counts as publishable: anything a reader could take a factual claim from.
GATED_SUFFIXES = (".md", ".tex", ".bib", ".cls", ".typ", ".ipynb")
GATED_DIRS = ("docs/", "manuscript/")
ATTEST_PATH = os.path.join(".abai", "attest.json")
ATTEST_DIR = ".abai/"


def is_gated(path: str) -> bool:
    if path.startswith(ATTEST_DIR):
        return False
    return path.endswith(GATED_SUFFIXES) or path.startswith(GATED_DIRS)


def git(repo: str, *args: str, timeout: int = 20) -> str:
    return subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True,
        text=True,
        check=True,
        timeout=timeout,
    ).stdout


def repo_root(start: str) -> str | None:
    try:
        return git(start, "rev-parse", "--show-toplevel").strip() or None
    except (subprocess.SubprocessError, OSError):
        return None


def gated_files(repo: str) -> list[tuple[str, str]]:
    """[(blob_id, path)] for every tracked publishable file at HEAD."""
    try:
        out = git(repo, "ls-tree", "-r", "HEAD")
    except (subprocess.SubprocessError, OSError):
        return []
    rows = []
    for line in out.splitlines():
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if len(parts) == 3 and parts[1] == "blob" and is_gated(path):
            rows.append((parts[2], path))
    rows.sort(key=lambda r: r[1])
    return rows


def digest(repo: str) -> tuple[str, int]:
    """(sha256 over blob-id + path pairs, file count). Empty repo -> ('', 0)."""
    rows = gated_files(repo)
    if not rows:
        return "", 0
    h = hashlib.sha256()
    for blob, path in rows:
        h.update(blob.encode())
        h.update(b"\0")
        h.update(path.encode())
        h.update(b"\n")
    return h.hexdigest(), len(rows)


def read_attestation(repo: str) -> dict | None:
    path = os.path.join(repo, ATTEST_PATH)
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def is_current(repo: str) -> tuple[bool, str]:
    """(current?, human-readable reason)."""
    current, count = digest(repo)
    if not current:
        return True, "no publishable files tracked at HEAD — nothing to attest"
    att = read_attestation(repo)
    if att is None:
        return False, f"no attestation ({count} publishable files at HEAD)"
    if att.get("digest") != current:
        return False, (
            f"attestation is stale — publishable content changed since "
            f"{att.get('checked_at', 'unknown')}"
        )
    if att.get("verdict") != "clear":
        return False, f"last verdict was '{att.get('verdict')}', not 'clear'"
    return True, f"attested {att.get('checked_at')} over {count} files"


def write_attestation(repo: str, verdict: str, note: str, session: str) -> dict:
    current, count = digest(repo)
    record = {
        "digest": current,
        "files": count,
        "verdict": verdict,
        "note": note,
        "session": session,
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "head": git(repo, "rev-parse", "HEAD").strip(),
    }
    out = os.path.join(repo, ATTEST_PATH)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2)
        fh.write("\n")
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["digest", "status", "write"])
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--verdict", default="clear", choices=["clear", "blocked"])
    ap.add_argument("--note", default="")
    ap.add_argument("--session", default=os.environ.get("CLAUDE_SESSION_ID", ""))
    args = ap.parse_args()

    root = repo_root(args.repo)
    if not root:
        print(f"not a git repository: {args.repo}", file=sys.stderr)
        return 2

    if args.action == "digest":
        d, n = digest(root)
        print(f"{d or '(none)'}  {n} files")
    elif args.action == "status":
        ok, reason = is_current(root)
        print(f"{'CURRENT' if ok else 'STALE'} — {reason}")
        return 0 if ok else 1
    else:
        rec = write_attestation(root, args.verdict, args.note, args.session)
        print(json.dumps(rec, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
