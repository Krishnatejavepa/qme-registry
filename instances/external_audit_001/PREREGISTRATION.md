# Pre-registration: external audit 001

**Registrant:** QME (referee-initiated external audit; the audit itself is the
registered study). **Kind:** `external_audit`.
**Subject claim:** "A Universal Machine Learning Framework Driven by Artificial
Intelligence for Ion Battery Cathode Material Design" (BatteryFormer), JACS Au,
published 2025-07-23 (PMC12381736). Target selected by the committed rule in
`SELECTION_RULE.md` (commit `5d2af6b`); enumeration in `ENUMERATION_LOG.md`
(commit `3337d7d`).
**Registered BEFORE any comparison is computed.** At registration time the
registrant has seen the paper's compound list, training-data source, and R2
statistics, and has NOT seen, digitized, or transcribed any per-compound
predicted voltage. Thresholds below are committed blind to those values.
**Protocol:** QME Validation Protocol v1.0 (R1-R10). Machine-readable JSON
instance will be transcribed into this directory and says so on its face.

## 1. The audited claim

The paper presents BatteryFormer's average-voltage predictions for seven
representative Li-ion cathode compounds (its Figure 6a) as a demonstration of
predictive accuracy, with training data from the Materials Project Battery
Explorer and validation against computed references (reported test R2 = 0.82
for redox potential). The verbatim accuracy sentence will be pinned with a
quote anchor in the curation log before any verdict is computed; if the paper
text does not support the claim as characterized here, that is recorded as a
deviation and the audit re-scopes or stops.

**What this audit tests (the falsifiable statement):** on the anchored subset
of Figure 6a compounds, BatteryFormer's predicted average voltages agree with
experiment-anchored reference values at decision-grade accuracy.

## 2. Datapoints (all `pending` at registration)

The anchored subset: Figure-6a compounds having clean Tier-A experimental
anchors in QME's committed anchor set, with couple definitions fixed here:

| id | Compound | Anchor couple | V_exp anchor | Anchor source |
|---|---|---|---|---|
| dp1 | LiFePO4 | LiFePO4 -> FePO4 (olivine, Fe2+/3+) | 3.45 V | Padhi, Nanjundaswamy, Goodenough, J. Electrochem. Soc. 144, 1188 (1997) |
| dp2 | LiCoO2 | LiCoO2 -> Li0.5CoO2 (layered, Co3+/4+) | 4.0 V | standard 3.9-4.1 V plateau window; range-match caveat applies (see exclusion x1) |
| dp3 | LiMn2O4 | LiMn2O4 -> lambda-MnO2 (spinel, Mn3+/4+) | 4.05 V | Thackeray et al., Mater. Res. Bull. 18, 461 (1983); Ohzuku et al., JES 137, 769 (1990); average of the two plateaus |

The other four Figure-6a compounds (LiNiO2, Li1.2Mn0.8O2, NMC811, NCA) have no
clean Tier-A anchor in the committed set and are OUT of the verdict statistic;
they may appear in secondary reporting only, clearly labeled.

## 3. One primary metric and complete decision rules

**Primary metric:** MAE = mean over included datapoints of
|V_predicted(paper) - V_exp(anchor)|.

- **PASS:** MAE < 0.15 V. Decision-grade agreement on the anchored subset.
- **GRAY_ZONE:** 0.15 V <= MAE < 0.30 V. Reported honestly, with what would
  resolve it; operator decision documented at decision time.
- **FAIL:** MAE >= 0.30 V. Not decision-grade; consistent with an inherited
  reference systematic.
- **Minimum n:** a verdict requires >= 2 included datapoints; otherwise the
  outcome is `excluded_reproduction_inconclusive`.

These bars are the same 0.15 / 0.30 V gates QME committed for its own D1 bench
audit. The referee applies to others exactly the bar it applied to itself.

**Uncertainty rule (digitization):** each transcribed value carries an
uncertainty u_i (zero for tabulated or author-provided values). If shifting
every included value by its +/- u_i can change the verdict class, the verdict
is GRAY_ZONE (uncertainty-dominated), and author-provided values supersede
digitized ones if later obtained, with the artifact superseded, never edited.

**Secondary analyses (reported, never verdict-deciding):** per-compound signed
deltas; mean signed offset; a decomposition against Materials Project Battery
Explorer reference voltages for the same couples (retrieved at curation time
with retrieval date recorded; data lookup only) separating model-vs-reference
from reference-vs-experiment; the four unanchored compounds, labeled.

## 4. Method (fixed)

1. **Curation first, verdict second.** Every subject value enters via the
   quote-anchor curation log (`inputs/curation_log.json`): verbatim source
   location (figure/table/page), transcribed value, uncertainty, conditions.
   The verdict generator reads only the curation log and the committed anchor
   table, never the paper.
2. **Digitization procedure (if Figure 6a has no tabulated values):** extract
   marker centers from the published figure at native resolution using axis
   calibration from labeled ticks; u_i = half the marker extent in volts plus
   axis-calibration residual; procedure and per-point u_i recorded in the
   curation log.
3. **Zero new compute.** No DFT runs. QME's local bench numbers do NOT enter
   this audit (its own single-offset calibration gate FAILED and it certifies
   nothing absolute); the comparison is paper-vs-experimental-anchor only.
4. **Toolchain:** python3 generator committed in `generator/`; artifact
   regenerates byte-identically via `scripts/verify.sh` from the repo root.

## 5. Exclusion policy (pre-committed; silent exclusion forbidden)

- **x1 range/couple mismatch:** if the paper's predicted quantity for a
  compound is definitionally a different couple or (de)lithiation range than
  the anchor couple fixed in section 2 (determined from the paper's methods
  text BEFORE any value comparison), that datapoint is `excluded_range_
  mismatch`, logged with the quote that shows it. LiCoO2 is pre-flagged as the
  likely case (full-delithiation averages differ from the 3.9-4.1 V plateau).
- **x2 unreadable value:** if a value cannot be transcribed or digitized to
  u_i <= 0.10 V, it is held `pending_author_values`; if author values never
  arrive, `excluded_reproduction_inconclusive`.
- **Sensitivity analysis required** for every exclusion: verdict reported with
  and without the excluded point. **Silent exclusion forbidden.**

## 6. Negative assertions (hold regardless of outcome)

- No claim that the model is refuted as a model class: its in-frame
  (reference-scale) performance is NOT tested here and may be excellent.
- No claim of author misconduct or error: validating against computed
  references is field-standard practice; this audit measures what that
  practice transfers, nothing about intent or competence.
- No absolute-voltage claims by QME's own bench enter this audit or its
  outreach; QME voltage language remains ranking-only per its FAILED
  single-offset gate.
- No novelty claims of any kind.
- A FAIL is published with the same standing as a PASS, under the verdict
  policy of the governing design document (private disclosure with a 14-day
  response window before any named FAIL publishes; 72-hour heads-up on PASS).

## 7. Operator gates

1. Operator approves this registration before curation or any comparison.
2. Operator reviews the verdict artifact before the policy branch executes
   (disclosure emails, publication).
3. Engineering review of the generator code before the artifact merges to the
   registry's main branch.
