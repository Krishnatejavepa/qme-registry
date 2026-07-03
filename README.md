# qme-registry

The public registry of QME Validation Protocol instances: pre-registered audits
and claims about computational materials science, each shipping with a verdict
artifact a stranger can regenerate byte-identically from this repository.

## Verify (about two minutes)

```
git clone https://github.com/Krishnatejavepa/qme-registry.git
cd qme-registry
bash scripts/verify.sh              # every registered instance
bash scripts/verify.sh --self-test  # the machinery itself, incl. tamper detection
```

`verify.sh` checks each instance's provenance manifest (sha256 of every
committed file), regenerates the verdict artifact in a sandbox from the
committed inputs, and byte-compares it against the committed copy. It prints
PASS or a unified diff. Nothing here asks to be believed; everything offers to
be checked.

## Status, stated plainly

- **Registered instances: 1.**
  [`external_audit_001`](instances/external_audit_001/): a blind,
  pre-registered audit of an external published ML voltage claim
  (BatteryFormer, JACS Au 2025), verdict **PASS** on the anchored subset
  (MAE 0.1333 V, n = 3). The selection rule, enumeration log, and thresholds
  were committed before the analysis ran; the verdict regenerates
  byte-identically from the committed inputs.
- Nothing in this registry is an endorsement, a novelty claim, or an
  experimental result. Computed voltages, where they appear, are reported in
  ranking-only language, and every artifact carries its reference-error caveats.
  A PASS on an anchored subset is not a model-class judgment.

## What this registry is

Machine-learned materials screens are typically validated against computed
reference values that carry their own systematic error against experiment. The
QME Validation Protocol fixes what a real validation must contain before any
result exists: one falsifiable claim, one primary metric, complete decision
rules, a locked exclusion policy, and negative assertions that survive any
outcome. This registry is the public record of instances run under that
protocol: what was claimed, when, under which rules, and what happened, with
FAIL verdicts published at the same standing as PASS.

Each instance directory contains its declaration (`instance.json`), the
committed inputs, the generator, the verdict artifact, and a provenance
manifest binding them together (see `instances/README.md` for the layout).

## The credential

The referee that operates this registry published its own failures first. Two
pre-registered audits, both FAILED, both public and regenerable from a clean
clone: the paper ("Computational references are not experiments",
arXiv:2606.23725) and its validation repository,
[qme-paper-validation](https://github.com/Krishnatejavepa/qme-paper-validation),
which also hosts the protocol specification, its JSON schema, and the founding
instances. A referee that cannot fail its own side is not a referee.

## Submitting a claim

Three steps, no paper-reading required: copy
[`funnel/claim.example.json`](funnel/claim.example.json), validate it locally
with `python3 scripts/validate_claim.py my_claim.json`, and send it (reply to
any QME email with it attached, or open a GitHub issue here). All datapoints
stay `pending`: a claim that arrives with its results already in hand is not a
pre-registration, and intake refuses it. Full instructions:
[`funnel/README.md`](funnel/README.md).

Certificates issued for validated claims are Ed25519-signed; verify one
yourself against the published key in [`KEYS.md`](KEYS.md), no secret needed.

## License

Code under MIT (`LICENSE`). Instance artifacts and documents carry their own
notices where they differ.
