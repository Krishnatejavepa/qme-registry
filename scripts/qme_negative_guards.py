"""QME negative-assertion guards: phrasings tied to RETIRED claims.

Single shared module, vendored byte-identically in three places:

  - QME workspace:  arXiv submit drafts/QME_arXiv_v2/qme_negative_guards.py
  - qme-paper-validation:  scripts/qme_negative_guards.py
  - qme-registry:  scripts/qme_negative_guards.py

Drift between the copies is test-enforced from the QME workspace
(qme_battery_loop/tests/test_3c_guard_drift.py), which can see all three
local clones. Each consuming repo's checker imports its local copy, so a
fresh clone stays self-contained.

Each entry names the claim it guards against; a substring hit in any prose
swept by a consuming checker is a regression and fails that sweep. These only
ever get ADDED to; weakening or removing a guard requires operator sign-off.

Scope note for consumers: sweep QME's own prose (papers, READMEs, reports).
Verbatim quotes of a SUBJECT's claims (curation logs, quote anchors in verdict
artifacts) are data, not QME prose, and are excluded by construction where the
transcription rule stores them in JSON.
"""

GUARDS_VERSION = "1.0.0"

RETIRED = [
    ("LiCoO2 4.120 V anchor framing (under-converged; retired by D1 side-finding)",
     "matches experiment"),
    ("same, variant phrasing", "matches the experiment"),
    ("same, variant phrasing", "matches the measured"),
    ("same, variant phrasing", "reproduces experiment"),
    ("same, variant phrasing", "agrees with experiment"),
    ("computed references called ground truth (thesis: only experiment is)",
     "ground truth"),
    ("computed references called ground truth, hyphenated", "ground-truth"),
    ("novelty claim (prior-art layer never cleared anything)", "novel material"),
    ("novelty claim, variant", "new material"),
    ("Na screen fitness claim (retired: F3 verdict, not screening-grade)",
     "is screening-grade"),
    ("absolute-voltage accuracy claim (retired by D1 FAIL)",
     "absolute-voltage accuracy"),
    ("calibrated-bench claim (retired by D1 FAIL: sd 0.31 V >= 0.30 V bar)",
     "calibrated bench"),
    ("calibrated-bench claim, variant", "bench is calibrated"),
    ("accuracy overclaim", "chemically accurate"),
]


def sweep(text):
    """Return [(why, phrase)] for every retired phrasing found in text."""
    hay = text.lower()
    return [(why, s) for why, s in RETIRED if s.lower() in hay]
