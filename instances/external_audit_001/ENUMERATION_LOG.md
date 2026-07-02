# Enumeration log for external audit 001

**Executed:** 2026-07-02 (UTC), within the Day-0 clock (deadline 2026-07-09).
**Rule:** `SELECTION_RULE.md`, committed 2026-07-02 at `5d2af6b`, before this
enumeration ran.

## Queries as run

- Q1 (arXiv API, submittedDate desc, max 20):
  `all:"machine learning" AND all:cathode AND all:voltage AND all:prediction`
  returned 17 entries.
- Q2 (arXiv API, same form):
  `all:"graph neural network" AND all:battery AND all:voltage AND all:prediction`
  returned 0 entries as phrased. Logged as run; no re-phrasing.
- Q3 (arXiv API, same form):
  `all:voltage AND all:cathode AND (olivine OR spinel OR "layered oxide") AND ("machine learning" OR ML)`
  returned 1 entry.
- Secondary (web search, same query intents): surfaced one peer-reviewed
  candidate not on arXiv (JACS Au), merged per the rule's visibility bar,
  which admits peer-reviewed venues.

Limitation, disclosed: the secondary source was a general web search executed
on the same date rather than a Google Scholar session; result set recorded
below in full.

## Ordered candidates (24-month window: 2024-07-02 to 2026-07-02) and bar outcomes

| # | Paper (first posting) | B1 claim type | B2 auditable | B3 non-trivial |
|---|---|---|---|---|
| 1 | arXiv 2606.23725 (2026-06-19) | FAIL: not an ML voltage claim (it is the QME validation paper itself; also self, not external) | - | - |
| 2 | arXiv 2605.29029 (2026-05-27) | FAIL: Ca chemistry, migration barriers, not Li-ion Tier-A voltage | - | - |
| 3 | arXiv 2605.27229 (2026-05-26) | FAIL: Na-ion, outside Tier-A Li families | - | - |
| 4 | arXiv 2605.12067 (2026-05-12) | FAIL: Mg-ion | - | - |
| 5 | arXiv 2512.24816 (2025-12-31) | FAIL: Na-ion MLP upscaling, not a voltage claim | - | - |
| 6 | arXiv 2511.22504 (2025-11-27) | FAIL: post-lithium chemistries | - | - |
| 7 | **JACS Au, 2025-07-23: "A Universal Machine Learning Framework Driven by Artificial Intelligence for Ion Battery Cathode Material Design" (BatteryFormer; PMC12381736)** | **CLEAR: ML-predicted average voltages for named Li-ion compounds incl. LiFePO4 (olivine), LiCoO2 (layered), LiMn2O4 (spinel)** | **CLEAR: three predicted compounds sit on committed clean Tier-A anchors (3.45 / 4.0 / 4.05 V); audit executes against committed artifacts, zero new DFT** | **CLEAR: trained on Materials Project Battery Explorer, validated in-frame (test R2 0.82 vs computed references, no experimental comparison visible); a quantified inherited-offset analysis for their specific numbers is information the paper does not contain** |
| 8 | arXiv 2506.20605 (2025-06-25) | not reached (target selected at #7) | - | - |
| 9 | arXiv 2503.13067 (2025-03-17) | not reached; noted: would have been next (MP-trained DNN voltage prediction, but no named compounds visible at abstract level) | - | - |
| 10 | arXiv 2412.11032 (2024-12-15) | not reached (Mg-ion; would FAIL B1) | - | - |
| 11 | arXiv 2411.10125 (2024-11-15) | not reached | - | - |
| 12 | arXiv 2409.06921 (2024-09-11) | not reached | - | - |
| 13 | arXiv 2408.00301 (2024-08-01) | not reached (field emission; would FAIL B1) | - | - |

Entries older than 2024-07-02 (window boundary) were excluded: arXiv
2309.10014, 2304.04986, 2304.01650, 2104.00586, and pre-window journal papers
surfaced by the secondary search (npj Comput. Mater. 2022, ACS AMI 2019).

## Selection

**Target: the BatteryFormer paper (JACS Au, published 2025-07-23).** First
candidate in enumeration order clearing B1, B2, and B3. The pre-declared
methods-audit fallback was not needed.

## Caveats carried into the audit pre-registration (next step)

- The per-compound predicted voltages appear in the paper's Figure 6a; if the
  values are graphical only (no table), the audit pre-registration must fix a
  digitization procedure with disclosed uncertainty, or the values will be
  requested from the corresponding author before any verdict is computed.
  Transcription follows the quote-anchor rule regardless.
- Every voltage statement in the audit carries the registered caveats:
  ranking-only language, the local bench's FAILED single-offset calibration
  gate, and the reference-error systematics measured on the audited compounds.
- Nothing in this selection is a verdict. The audit's claim, metric,
  thresholds, and exclusion rules are registered in this directory before any
  comparison is computed.
