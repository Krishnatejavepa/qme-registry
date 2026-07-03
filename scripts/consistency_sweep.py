"""Registry consistency sweep: the front page must agree with the artifacts,
and no retired-claim phrasing may appear in registry prose.

Ported from the QME paper repos' consistency_check.py pattern (positive
checks derive expected strings from committed artifacts; negative guards ban
phrasings tied to retired claims). Exits nonzero on any miss.

What is swept:
  - prose: every .md file in the repo except instance inputs (curation logs
    and quote anchors hold verbatim SUBJECT quotes by the transcription rule;
    those are data, not QME prose, and live in JSON anyway).
  - front page vs reality: the README's "Registered instances: N" must equal
    the number of instance directories; every instance must be named on the
    front page, and the line naming it must carry the artifact's verdict, so
    the front page can never misstate an outcome.

Stdlib only; runs in CI on every push (see .github/workflows/verify.yml).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qme_negative_guards import GUARDS_VERSION, RETIRED, sweep

ROOT = Path(__file__).resolve().parents[1]
INSTANCES = ROOT / "instances"


def _blocks(text):
    """Split markdown into blocks: a bullet plus its wrapped continuation
    lines, or a blank-line-delimited paragraph."""
    out, cur = [], []
    for ln in text.splitlines():
        if not ln.strip():
            if cur:
                out.append("\n".join(cur))
                cur = []
        elif re.match(r"^\s*[-*] ", ln):
            if cur:
                out.append("\n".join(cur))
            cur = [ln]
        else:
            cur.append(ln)
    if cur:
        out.append("\n".join(cur))
    return out


failures = []

# ---------------------------------------------------------------- prose sweep
prose_files = sorted(
    p for p in ROOT.rglob("*.md")
    if ".git" not in p.parts and "inputs" not in p.parts
)
if not prose_files:
    failures.append("sweep found no prose files; path assumptions are broken")
swept = 0
for p in prose_files:
    hits = sweep(p.read_text())
    swept += 1
    for why, s in hits:
        failures.append(f"RETIRED-CLAIM REGRESSION in {p.relative_to(ROOT)}: "
                        f"{s!r} ({why})")

# --------------------------------------------------- front page vs artifacts
readme = (ROOT / "README.md").read_text()
instance_dirs = sorted(
    d for d in INSTANCES.iterdir()
    if d.is_dir() and (d / "instance.json").exists()
) if INSTANCES.exists() else []

m = re.search(r"Registered instances:\s*\**(\d+)", readme)
if not m:
    failures.append("README.md has no parseable 'Registered instances: N' line")
elif int(m.group(1)) != len(instance_dirs):
    failures.append(
        f"README.md claims {m.group(1)} registered instance(s); "
        f"instances/ holds {len(instance_dirs)}"
    )

for d in instance_dirs:
    decl = json.loads((d / "instance.json").read_text())
    iid = decl["instance_id"]
    artifact_path = d / decl["artifact"]
    verdict = None
    if artifact_path.exists():
        verdict = json.loads(artifact_path.read_text()).get("verdict")
    # block granularity: markdown wraps lines freely and packs list items one
    # newline apart, so the unit is a block (a bullet with its continuation
    # lines, or a paragraph). A block that names an instance must also state
    # its verdict, so the front page can never name an outcome-bearing
    # instance without its outcome, and a neighboring bullet's text cannot
    # satisfy the check by accident.
    naming_blocks = [b for b in _blocks(readme) if iid in b]
    if not naming_blocks:
        failures.append(f"instance {iid} is registered but not named in README.md")
    elif verdict and not any(verdict in b for b in naming_blocks):
        failures.append(
            f"README.md names {iid} but no block naming it carries its "
            f"artifact verdict {verdict!r}"
        )

# -------------------------------------------------------------------- report
print(f"consistency sweep: {swept} prose file(s), {len(instance_dirs)} "
      f"instance(s), guards v{GUARDS_VERSION} ({len(RETIRED)} phrasings)")
for f in failures:
    print(f"  FAIL: {f}", file=sys.stderr)
print("PASS" if not failures else f"{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
