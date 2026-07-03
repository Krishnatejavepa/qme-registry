# Intake funnel v0: submit a claim without reading a paper

The cost of saying yes should be filling in a form, not studying a protocol.
This directory is the form.

## The three-step path

1. **Copy the example.** `claim.example.json` is a complete, schema-valid
   claim. Replace its fields with yours: one falsifiable claim statement, one
   primary metric, PASS and FAIL rules, a locked exclusion policy, negative
   assertions (what may NOT be concluded even from a PASS), and per-structure
   spin states with a literature basis. Every datapoint stays `"pending"`:
   a claim that arrives with its results already in hand is not a
   pre-registration, and intake refuses it.

2. **Validate locally** (nothing is sent anywhere):

   ```
   pip install jsonschema
   python3 scripts/validate_claim.py my_claim.json
   ```

   It prints the same admissibility report QME's own intake runs and ends
   with SENDABLE or NOT SENDABLE plus exactly what to fix.

3. **Send it.** Reply to any email you received from QME with the validated
   `claim.json` attached, or open a GitHub issue on this repository and
   attach it. You will get back an admissibility report; if the claim is
   admissible and accepted at the operator gate, it is registered immutably
   in `protocol/instances/` (companion repository) before any verifying
   computation is staged, and what eventually comes back is a Validation
   Certificate with the verdict stated plainly, FAIL at the same standing
   as PASS.

## What the schema pins down (and why)

- `preregistration.schema.json` here is a byte-identical vendored copy of the
  canonical schema in
  [qme-paper-validation](https://github.com/Krishnatejavepa/qme-paper-validation/tree/main/protocol/schema);
  drift between the copies is test-enforced on QME's side.
- The registered claim, not the eventual result, fixes the decision rules.
  That is the whole point: nobody, including QME, gets to move a threshold
  after seeing a number.
- Compute is operator-gated. Validating and emailing a claim costs you
  nothing and commits QME to nothing beyond an honest admissibility report;
  capacity is stated plainly at 2 to 4 claims per month.

## What you get back

A Validation Certificate: structured JSON plus a human-readable report,
integrity-hashed, HMAC-signed, and Ed25519-signed so you can verify issuance
yourself against the published key in [`KEYS.md`](../KEYS.md), with no secret
needed. It states what was tested, against which experiment-anchored
references, under which registered rules, with which verdict, and what may
and may not be concluded. Every certificate carries the known reference
offsets on its face, including the roughly 0.54 V Materials Project PBE+U
systematic and the FAILED single-offset gate of QME's own bench, and it
certifies voltages in ranking-only language.
