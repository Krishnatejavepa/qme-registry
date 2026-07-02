#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Krishna Teja Vepa
"""Provenance manifest generator and checker for registry instances.

Every instance directory declares itself in an `instance.json`:

    {
      "instance_id": "...",
      "kind": "external_audit | preregistration | machinery_self_test",
      "artifact":  "artifact/<name>.json",     # paths relative to the
      "generator": "generator/<name>.py",      # instance directory
      "inputs":    ["inputs/..."],
      "preregistration": {...} | null
    }

The manifest (`manifest.json`, written next to `instance.json`) records the
sha256 of the instance declaration, the artifact, the generator, and every
input, plus the captured environment. Check mode re-hashes every referenced
file and exits nonzero on any mismatch; environment differences are reported
as information, never as failure (a stranger's Python patch version does not
invalidate a file-hash check).

Usage:
  python3 scripts/make_manifest.py --dir <instance-dir>          # write
  python3 scripts/make_manifest.py --dir <instance-dir> --check  # verify
  python3 scripts/make_manifest.py [--check]                     # all under instances/

Determinism: output is a pure function of the referenced file contents. A
timestamp is included only when SOURCE_DATE_EPOCH is set, so byte-identical
reruns are the default, not a special mode.
"""
import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def captured_environment() -> dict:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
    }


def load_spec(instance_dir: Path) -> dict:
    spec_path = instance_dir / "instance.json"
    if not spec_path.exists():
        raise FileNotFoundError(f"{spec_path} missing")
    spec = json.loads(spec_path.read_text())
    for key in ("instance_id", "artifact", "generator", "inputs"):
        if key not in spec:
            raise KeyError(f"{spec_path}: required key '{key}' missing")
    return spec


def referenced_files(spec: dict) -> list:
    return ["instance.json", spec["artifact"], spec["generator"], *spec["inputs"]]


def build_manifest(instance_dir: Path) -> dict:
    spec = load_spec(instance_dir)
    files = {}
    for rel in referenced_files(spec):
        f = instance_dir / rel
        if not f.exists():
            raise FileNotFoundError(f"{instance_dir}/{rel} referenced but missing")
        files[rel] = sha256_of(f)
    manifest = {
        "manifest_for": spec["instance_id"],
        "generator": spec["generator"],
        "regeneration_command": (
            f"cd <instance-dir> && python3 {spec['generator']}"
        ),
        "sha256": dict(sorted(files.items())),
        "preregistration": spec.get("preregistration"),
        "captured_environment": captured_environment(),
    }
    sde = os.environ.get("SOURCE_DATE_EPOCH")
    if sde:
        manifest["generated_utc"] = datetime.fromtimestamp(
            int(sde), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return manifest


def write_one(instance_dir: Path) -> int:
    out = instance_dir / "manifest.json"
    out.write_text(json.dumps(build_manifest(instance_dir), indent=2) + "\n")
    print(f"wrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
    return 0


def check_one(instance_dir: Path) -> int:
    mpath = instance_dir / "manifest.json"
    label = str(instance_dir.relative_to(ROOT) if instance_dir.is_relative_to(ROOT)
                else instance_dir)
    if not mpath.exists():
        print(f"FAIL {label}: manifest.json missing")
        return 1
    committed = json.loads(mpath.read_text())
    ok = True
    for rel, want in committed.get("sha256", {}).items():
        f = instance_dir / rel
        if not f.exists():
            print(f"  MISSING {rel}")
            ok = False
            continue
        got = sha256_of(f)
        if got != want:
            print(f"  HASH MISMATCH {rel}")
            print(f"    manifest: {want}")
            print(f"    on disk : {got}")
            ok = False
    env_now = captured_environment()
    env_then = committed.get("captured_environment", {})
    if env_now != env_then:
        print(f"  info: environment differs (manifest: {env_then}, "
              f"now: {env_now}); not a failure")
    n = len(committed.get("sha256", {}))
    print(f"{'PASS' if ok else 'FAIL'} {label}: {n} file hash(es) checked")
    return 0 if ok else 1


def instance_dirs() -> list:
    base = ROOT / "instances"
    if not base.exists():
        return []
    return sorted(d for d in base.iterdir()
                  if d.is_dir() and (d / "instance.json").exists())


def main(argv: list) -> int:
    check = "--check" in argv
    dirs = []
    if "--dir" in argv:
        dirs = [Path(argv[argv.index("--dir") + 1]).resolve()]
    else:
        dirs = instance_dirs()
        if not dirs:
            print("no registered instances under instances/ (registry is new)")
            return 0
    bad = 0
    for d in dirs:
        bad += (check_one(d) if check else write_one(d))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
