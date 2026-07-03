"""Registry consistency sweep: the front page must agree with the artifacts,
and no retired-claim phrasing may appear in registry prose.

Ported from the QME paper repos' consistency_check.py pattern (positive
checks derive expected strings from committed artifacts; negative guards ban
phrasings tied to retired claims). Exits nonzero on any miss.

What is swept:
  - prose: every .md file in the repo except instance inputs (curation logs
    and quote anchors hold verbatim SUBJECT quotes by the transcription rule;
    those are data, not QME prose, and live in JSON anyway). Markdown
    blockquote lines (starting with '>') are stripped before the guard sweep:
    a verbatim subject quote in QME-authored instance prose MUST be
    blockquoted, which both renders it visibly as a quote and keeps the
    guards pointed at QME's own words.
  - front page vs reality: the README's "Registered instances: N" must equal
    the number of instance directories; every instance must be named on the
    front page, and the block naming it must carry the artifact's verdict as
    a whole word, so the front page can never misstate an outcome. An
    instance whose declared artifact file is missing is a failure outright.

Stdlib only; runs in CI on every push (see .github/workflows/verify.yml).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_manifest import instance_dirs, load_spec
from qme_negative_guards import GUARDS_VERSION, RETIRED, sweep

ROOT = Path(__file__).resolve().parents[1]


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


def _own_prose(text):
    """Drop markdown blockquote lines: verbatim subject quotes are data, not
    QME prose, and the convention is that instance .md files blockquote them."""
    return "\n".join(ln for ln in text.splitlines()
                     if not ln.lstrip().startswith(">"))


failures = []

# ---------------------------------------------------------------- prose sweep
prose_files = sorted(
    p for p in ROOT.rglob("*.md")
    if ".git" not in p.parts and "inputs" not in p.parts
)
if not prose_files:
    failures.append("sweep found no prose files; path assumptions are broken")
for p in prose_files:
    for why, s in sweep(_own_prose(p.read_text())):
        failures.append(f"RETIRED-CLAIM REGRESSION in {p.relative_to(ROOT)}: "
                        f"{s!r} ({why})")

# --------------------------------------------------- front page vs artifacts
readme = (ROOT / "README.md").read_text()
instances = instance_dirs()

m = re.search(r"Registered instances:\s*\**(\d+)", readme)
if not m:
    failures.append("README.md has no parseable 'Registered instances: N' line")
elif int(m.group(1)) != len(instances):
    failures.append(
        f"README.md claims {m.group(1)} registered instance(s); "
        f"instances/ holds {len(instances)}"
    )

for d in instances:
    decl = load_spec(d)
    iid = decl["instance_id"]
    artifact_path = d / decl["artifact"]
    if not artifact_path.exists():
        failures.append(f"instance {iid}: declared artifact "
                        f"{decl['artifact']} is missing")
        continue
    verdict = json.loads(artifact_path.read_text()).get("verdict")
    naming_blocks = [b for b in _blocks(readme) if iid in b]
    if not naming_blocks:
        failures.append(f"instance {iid} is registered but not named in README.md")
    elif verdict and not any(
        re.search(rf"\b{re.escape(verdict)}\b", b) for b in naming_blocks
    ):
        failures.append(
            f"README.md names {iid} but no block naming it carries its "
            f"artifact verdict {verdict!r} as a whole word"
        )

# -------------------------------------------------------------------- report
print(f"consistency sweep: {len(prose_files)} prose file(s), "
      f"{len(instances)} instance(s), guards v{GUARDS_VERSION} "
      f"({len(RETIRED)} phrasings)")
for f in failures:
    print(f"  FAIL: {f}", file=sys.stderr)
print("PASS" if not failures else f"{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
