#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Fixture generator: a pure function of inputs/values.csv, used only to prove
# that the registry's regeneration machinery reproduces artifacts
# byte-identically. Not a scientific computation.
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
values = [float(line) for line in
          (HERE / "inputs" / "values.csv").read_text().split() if line.strip()]
values.sort()
summary = {
    "kind": "machinery_self_test",
    "n": len(values),
    "min": f"{values[0]:.6f}",
    "max": f"{values[-1]:.6f}",
    "mean": f"{sum(values) / len(values):.6f}",
}
out = HERE / "artifact" / "summary.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(f"wrote {out}")
