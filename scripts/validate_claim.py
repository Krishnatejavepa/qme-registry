#!/usr/bin/env python3
"""Validate a claim.json against the QME Validation Protocol, locally,
before you send it. This is the intake funnel's local half: run it, fix what
it names, and email a claim that passes.

    python3 scripts/validate_claim.py path/to/claim.json [--json]

Checks, in order:
  1. Schema: funnel/preregistration.schema.json (vendored byte-identical from
     the protocol's canonical copy in qme-paper-validation). Needs the
     'jsonschema' package: pip install jsonschema
  2. Admissibility: the same protocol checks QME's own intake runs
     (decision rules complete, anchors sourced for anchored claim types,
     spin states from literature physics, exclusions locked, negative
     assertions present).
  3. Funnel enforcement: every datapoint must be 'pending'. A claim arriving
     with its results already in hand is not a pre-registration; intake
     refuses it, so this script refuses it too, for the same reason.

Exit 0: sendable. Exit 1: fix the reported items. Exit 2: setup problem.

Nothing here launches compute, phones home, or writes anything.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "funnel" / "preregistration.schema.json"

# Claim types whose verdicts are judged against experimental anchors
# (mirrors qme_battery_loop/src/validation_protocol.py).
ANCHORED_CLAIM_TYPES = {"calibration", "accuracy"}


def schema_errors(doc: dict) -> list[str]:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("setup: the 'jsonschema' package is required for schema "
              "validation: pip install jsonschema", file=sys.stderr)
        sys.exit(2)
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text()))
    errors = []
    for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
        where = "/".join(str(p) for p in err.path) or "<root>"
        errors.append(f"{where}: {err.message}")
    return errors


def admissibility_check(doc: dict) -> dict:
    """Protocol admissibility beyond raw schema validity. Mirrors the checks
    in qme_battery_loop/src/validation_protocol.py (the mirror is behavior-
    tested on QME's side), with one funnel-specific hardening, documented and
    deliberate: datapoints_pre_result is a hard refusal here, not a warning,
    because everything arriving through this funnel is a fresh external
    intake. Every check below is required; there is no warning tier."""
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: str) -> None:
        checks.append({"id": check_id, "ok": bool(ok), "detail": detail})

    errs = schema_errors(doc)
    check("schema_valid", not errs,
          "; ".join(errs[:3]) if errs else "conforms to preregistration.schema.json")

    rules = {r.get("verdict") for r in doc.get("decision_rules", [])}
    check("decision_rules_complete", {"PASS", "FAIL"} <= rules,
          f"verdict rules present: {sorted(v for v in rules if v)}")

    claim_type = doc.get("claim", {}).get("claim_type")
    anchors = doc.get("anchors", [])
    if claim_type in ANCHORED_CLAIM_TYPES:
        anchored_ok = bool(anchors) and all(a.get("source") for a in anchors)
        check("anchors_experimental", anchored_ok,
              f"{len(anchors)} anchor(s), all with sources" if anchored_ok
              else "calibration/accuracy claims need experiment-anchored "
                   "references with sources")
    else:
        check("anchors_experimental", True,
              f"not required for claim_type={claim_type!r}")

    spin = doc.get("method", {}).get("spin_states", {})
    per_structure = spin.get("per_structure", [])
    spin_ok = (
        spin.get("source_policy") == "literature_physics_only"
        and bool(per_structure)
        and all("expected_total_magnetization_bohr" in s and s.get("literature_basis")
                for s in per_structure)
    )
    check("spin_states_documented", spin_ok,
          f"{len(per_structure)} structure(s) with literature manifolds")

    pol = doc.get("exclusion_policy", {})
    check("exclusions_locked",
          pol.get("sensitivity_analysis_required") is True
          and pol.get("silent_exclusion_forbidden") is True,
          "sensitivity analysis mandatory, silent exclusion forbidden")

    check("registered_before_results",
          doc.get("registration_evidence", {}).get("committed_before_results") is True,
          doc.get("registration_evidence", {}).get("canonical_document", ""))

    negs = doc.get("negative_assertions", [])
    check("negative_assertions_present", bool(negs),
          f"{len(negs)} registered")

    statuses = {d.get("status") for d in doc.get("datapoints", [])}
    all_pending = bool(statuses) and statuses <= {"pending"}
    check("datapoints_pre_result", all_pending,
          "all datapoints pending (true pre-result intake)" if all_pending
          else "non-pending or missing datapoints: registration must precede "
               "results; a claim with results in hand is exactly what the "
               "protocol referees, and this funnel refuses it")

    return {"admissible": all(c["ok"] for c in checks), "checks": checks}


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    as_json = "--json" in argv
    if len(args) != 1:
        print("usage: python3 scripts/validate_claim.py path/to/claim.json [--json]",
              file=sys.stderr)
        return 2
    path = Path(args[0])
    if not path.exists():
        print(f"setup: {path} does not exist", file=sys.stderr)
        return 2
    if not SCHEMA_PATH.exists():
        print(f"setup: vendored schema missing at {SCHEMA_PATH}", file=sys.stderr)
        return 2
    try:
        doc = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"claim is not valid JSON: {e}", file=sys.stderr)
        return 1

    result = admissibility_check(doc)
    if as_json:
        print(json.dumps({"claim": str(path), **result}, indent=2))
    else:
        print(f"claim: {path}")
        for c in result["checks"]:
            mark = "ok  " if c["ok"] else "FAIL"
            print(f"  [{mark}] {c['id']}: {c['detail']}")
        print("SENDABLE: validate passed; email this claim.json"
              if result["admissible"]
              else "NOT SENDABLE: fix the FAIL items above and re-run")
    return 0 if result["admissible"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
