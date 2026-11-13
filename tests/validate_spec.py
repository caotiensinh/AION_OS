#!/usr/bin/env python3
"""Static validation of the AION OS Spec Kit acceptance baseline.

This tests consistency of documentation only. It is not an OS acceptance test.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "specs" / "001-ai-native-platform"
REQUIRED = [
    ROOT / "README.md",
    ROOT / "docs/PRODUCT_VISION.md",
    ROOT / "docs/ARCHITECTURE.md",
    ROOT / "docs/VARIANTS.md",
    ROOT / ".specify/memory/constitution.md",
    BASE / "spec.md",
    BASE / "plan.md",
    BASE / "tasks.md",
    BASE / "research.md",
    BASE / "data-model.md",
    BASE / "quickstart.md",
    BASE / "contracts/policy-v0.md",
    BASE / "checklists/acceptance.md",
]
errors = []
for path in REQUIRED:
    if not path.is_file() or not path.read_text(encoding="utf-8").strip():
        errors.append(f"Missing or empty: {path.relative_to(ROOT)}")

acceptance_path = BASE / "checklists/acceptance.md"
if acceptance_path.is_file():
    lines = acceptance_path.read_text(encoding="utf-8").splitlines()
    listed = []
    for line in lines:
        m = re.match(r"^\| (AT-\d{2}) \|", line)
        if m:
            listed.append(m.group(1))
            if not line.rstrip().endswith("| TODO |"):
                errors.append(f"Acceptance row not explicitly TODO: {m.group(1)}")
    expected = [f"AT-{i:02d}" for i in range(1, 29)]
    if listed != expected:
        errors.append(f"Expected ordered 28 acceptance cases, found: {listed}")

spec_path = BASE / "spec.md"
if spec_path.is_file():
    spec = spec_path.read_text(encoding="utf-8")
    for number in range(1, 17):
        if f"FR-{number:03d}" not in spec:
            errors.append(f"Missing FR-{number:03d}")
    for number in range(1, 8):
        if f"NFR-{number:03d}" not in spec:
            errors.append(f"Missing NFR-{number:03d}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print("Spec structural validation PASS: required files, 16 FR, 7 NFR, 28 TODO acceptance cases")
