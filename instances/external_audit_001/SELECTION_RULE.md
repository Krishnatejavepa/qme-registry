# Target selection rule for external audit 001

**Status:** committed BEFORE any candidate enumeration or anchor-agreement check.
**Day-0 clock:** this rule executes by 2026-07-09 (seven days from plan adoption).
**Why this document exists:** the operator knows the field's measured reference
systematic in advance, so a hand-picked audit target would be unrefereed
refereeing. This rule fixes the target selection mechanically, before looking,
and is committed so that the selection itself can be checked by anyone.

## 1. Enumeration procedure (fixed)

Candidates are enumerated by running exactly these queries and merging results:

- arXiv full-text/metadata search (cond-mat.mtrl-sci, cs.LG):
  Q1: "machine learning" cathode voltage prediction
  Q2: "graph neural network" battery voltage prediction
  Q3: ML predicted voltage olivine OR spinel OR "layered oxide" cathode
- Google Scholar (secondary, same three query strings).

**Window:** first public posting within 24 months before the execution date.
**Ordering:** reverse chronological by first public posting date, after
deduplication. Recency drives position; fame does not.
**Visibility bar:** indexed on arXiv or published in a peer-reviewed venue,
in English, with identifiable corresponding author contact.
**Cap:** the first 20 candidates in order; if fewer exist, all of them.

## 2. Bars, applied in enumeration order to each candidate

- **B1 Claim type.** The paper reports ML-predicted or data-driven average
  voltages for one or more specific Li-ion compounds in a Tier-A anchor family
  (olivine LiMPO4, layered LiMO2, spinel, pyrophosphate, tavorite fluoro/sulfate).
- **B2 Auditability, zero new compute.** At least one predicted compound has a
  clean Tier-A experimental anchor in the committed QME anchor set, and the
  audit can be executed entirely against committed artifacts (no new DFT; the
  local bench's campaigns are untouchable and its calibration status is itself
  FAILED for absolute claims, which the audit must disclose).
- **B3 Non-triviality.** The verdict must tell the authors something they do
  not already state: at minimum, a quantified inherited reference offset for
  their specific numbers (for example, validation against MP-class computed
  references transfers a measured systematic of about 0.54 V on the audited
  compounds), not a lookup-table echo of their own table or of QME's CSVs.

**Selection:** the FIRST candidate in enumeration order clearing B1, B2, and B3
is the audit target. No skipping, no preference, no second look.

## 3. Fallback, named now as the probable primary

Anchor coverage is five families and clean Tier-A anchors number about eight,
so the probability that a recent claim clears B2 is honestly low. If the
enumeration exhausts without a target, the audit re-scopes to a pre-registered
METHODS AUDIT: what the measured reference systematic implies for the
enumerated class of published claims, with no single named subject. This
fallback is declared before enumeration so it cannot be read as a retreat
after an inconvenient result.

## 4. Evidence trail

The full enumeration log (queries as run, dates, the ordered candidate list,
and each candidate's B1/B2/B3 outcome with one-line reasons) is committed to
this directory as `ENUMERATION_LOG.md` at execution time, whichever way the
selection lands.
