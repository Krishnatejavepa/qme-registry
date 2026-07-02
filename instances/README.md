# Registered instances

One directory per instance. This registry is new: **no instances are registered
yet**; the first external audit is in preparation. This file describes the
layout every instance follows.

```
instances/<instance_id>/
├── instance.json     # declaration: id, kind, artifact, generator, inputs, prereg
├── manifest.json     # provenance: sha256 of every committed file above
├── inputs/           # committed inputs the generator reads
├── generator/        # the script that produces the artifact
└── artifact/         # the committed verdict artifact
```

Rules, inherited from the QME Validation Protocol:

- Registration precedes results. The instance's pre-registration (thresholds,
  decision rules, exclusion policy, negative assertions) is committed before
  the analysis it governs exists.
- `bash scripts/verify.sh` must regenerate every committed artifact
  byte-identically in a sandbox. An instance that cannot be regenerated is not
  registered.
- FAIL verdicts publish at the same standing as PASS.
- External audits (`kind: external_audit`) are themselves pre-registered:
  the audit's metric, thresholds, and target-selection rule are committed
  before the analysis runs, so the referee's choices are refereeable too.
