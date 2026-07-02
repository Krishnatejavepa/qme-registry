#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Krishna Teja Vepa
"""Verdict generator for external_audit_001.

Reads ONLY inputs/curation_log.json (quote-anchored transcription of the
subject paper's values plus the committed Tier-A anchors) and applies the
decision rules registered in PREREGISTRATION.md (commit ec8a2d5) BEFORE any
comparison was computed. Deterministic: no network, no environment reads,
stable rounding, sorted keys.

Registered rules encoded here:
  primary metric  MAE = mean |V_predicted - V_exp_anchor| over included dps
  PASS  MAE < 0.15 V | GRAY_ZONE 0.15 <= MAE < 0.30 V | FAIL MAE >= 0.30 V
  min n >= 2 else excluded_reproduction_inconclusive
  uncertainty rule: if shifting every included value by +/- u_v can change
  the verdict class, verdict = GRAY_ZONE (uncertainty-dominated)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
PASS_BAR = 0.15
FAIL_BAR = 0.30
MIN_N = 2


def verdict_class(mae: float) -> str:
    if mae < PASS_BAR:
        return "PASS"
    if mae < FAIL_BAR:
        return "GRAY_ZONE"
    return "FAIL"


def main() -> None:
    log = json.loads((HERE / "inputs" / "curation_log.json").read_text())
    anchors = {a["datapoint_id"]: a for a in log["anchors_V"]}
    excl = log["exclusion_determinations"]

    rows = []
    for v in log["transcribed_values_V"]:
        if not v["anchored"]:
            continue
        a = anchors[v["datapoint_id"]]
        delta = round(v["prediction"] - a["v_exp"], 6)
        rows.append({
            "datapoint_id": v["datapoint_id"],
            "compound": v["compound"],
            "couple": a["couple"],
            "v_predicted": v["prediction"],
            "v_exp_anchor": a["v_exp"],
            "anchor_source": a["source"],
            "delta_v": delta,
            "abs_delta_v": round(abs(delta), 6),
            "u_v": v["u_v"],
            "status": "included",
        })
    rows.sort(key=lambda r: r["datapoint_id"])

    n = len(rows)
    if n < MIN_N:
        verdict = "excluded_reproduction_inconclusive"
        mae = None
        rule = f"included n = {n} < minimum {MIN_N}"
        uncertainty_check = None
        mean_signed = None
    else:
        # Classification runs on RAW (unrounded) values so the registered
        # boundary semantics (PASS: MAE < 0.15) hold exactly; rounding is
        # applied only to the reported fields.
        mae_raw = sum(r["abs_delta_v"] for r in rows) / n
        mean_signed = round(sum(r["delta_v"] for r in rows) / n, 4)
        base = verdict_class(mae_raw)
        # Uncertainty envelope: each transcribed value may sit anywhere in
        # [v - u, v + u], so per-point |delta| ranges over
        # [max(0, |d|-u), |d|+u]; the conservative lower clamp errs toward
        # GRAY_ZONE when u_i > |delta_i|. Endpoint check suffices because
        # the class function is monotone in MAE.
        hi_raw = sum(r["abs_delta_v"] + r["u_v"] for r in rows) / n
        lo_raw = sum(max(0.0, r["abs_delta_v"] - r["u_v"]) for r in rows) / n
        straddles = len({verdict_class(lo_raw), verdict_class(hi_raw)}) > 1
        verdict = "GRAY_ZONE" if straddles else base
        mae = round(mae_raw, 4)
        mae_lo, mae_hi = round(lo_raw, 4), round(hi_raw, 4)
        rule = (
            f"MAE = {mae} V; class boundaries PASS<{PASS_BAR:.2f}, "
            f"FAIL>={FAIL_BAR:.2f}; "
            + ("uncertainty-dominated: class changes within transcription "
               "uncertainty" if straddles else
               f"uncertainty envelope [{mae_lo}, {mae_hi}] V stays in one class")
        )
        uncertainty_check = {
            "mae_low": mae_lo, "mae_high": mae_hi,
            "uncertainty_dominated": straddles,
        }

    artifact = {
        "instance_id": "external_audit_001",
        "kind": "external_audit",
        "subject": log["subject"],
        "audited_claim_quote": log["audited_claim_quote"]["text"],
        "preregistration": {
            "document": "PREREGISTRATION.md",
            "registered_utc": "2026-07-02T21:24:54Z",
            "commit": "ec8a2d5",
            "registered_before_any_comparison": True,
        },
        "primary_metric": {
            "definition": "MAE = mean |V_predicted(paper) - V_exp(Tier-A anchor)| over included datapoints",
            "value_V": mae,
            "mean_signed_offset_V": mean_signed,
            "n_included": n,
        },
        "verdict": verdict,
        "verdict_scope": "anchored subset only (n=3 of 7 Figure-6a compounds; see caveats_that_travel[0])",
        "rule_applied": rule,
        "uncertainty_check": uncertainty_check,
        "datapoints": rows,
        "exclusions": {
            "excluded_datapoints": [],
            "x1_range_mismatch": excl["x1_range_mismatch"],
            "x2_unreadable_value": excl["x2_unreadable_value"],
            "sensitivity_analysis": "no datapoint excluded, so verdict-with-and-without does not apply",
        },
        "secondary": {
            "unanchored_compounds_reported_not_judged": [
                {"compound": v["compound"], "v_predicted": v["prediction"],
                 "paper_experiment_label": v["paper_experiment_label"]}
                for v in log["transcribed_values_V"] if not v["anchored"]
            ],
            "paper_experiment_labels_vs_anchors_note":
                log["secondary_context"]["paper_experiment_labels_vs_tier_a_anchors"],
            "mp_reference_decomposition":
                "not retrieved: the generator performs no network access by design, "
                "and no retrieval is recorded in the curation log; the registered "
                "fallback (omission with disclosure) applies. The decomposition is "
                "secondary and never verdict-deciding (registered section 3)",
        },
        "caveats_that_travel": [
            "This verdict concerns absolute average voltages on three anchored couples only; the model's in-frame (reference-scale) performance and its other predictions are NOT tested here.",
            "QME's own local DFT bench FAILED its pre-registered single-offset calibration gate (sd 0.31 V, n=4; source: d1_corrected_offsets.json in github.com/Krishnatejavepa/qme-paper-validation, regenerable) and contributes nothing to this audit; the comparison is paper-vs-experimental-anchor only, and QME voltage language remains ranking-only.",
            "On the compounds where model, database reference, and experiment could previously be compared (QME's Na-cathode study, arXiv:2606.23725), Materials Project PBE+U reference voltages sat about 0.54 V below experiment; this audit's subject trained on MP Battery Explorer labels, and the anchored-subset result here neither confirms nor refutes that systematic for its full training domain.",
            "The LiCoO2 anchor carries the pre-flagged range-match caveat: the paper does not define its (de)lithiation range, so a definitional mismatch can neither be demonstrated nor ruled out from its text.",
            "The three transcribed predictions are printed figure labels (u_v = 0.005 V); the paper's SI Table S7 was not retrievable by automated means, and author-provided values supersede these transcriptions under the registered uncertainty rule.",
        ],
        "negative_assertions": [
            "No claim that the model is refuted as a model class.",
            "No claim of author misconduct or error; validating against computed references is field-standard practice.",
            "No absolute-voltage claims by QME's own bench.",
            "No novelty claims.",
            "A FAIL would be published with the same standing as a PASS; this verdict is published under the registered verdict policy either way.",
        ],
    }

    out = HERE / "artifact" / "verdict.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
