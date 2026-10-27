"""Replay the public formatting fixtures using only the Python standard library."""
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/anti-overdefensive-paper-writing/scripts/scan_defensive_prose.py"
spec = importlib.util.spec_from_file_location("defensive_scanner", SCRIPT)
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)
cases = json.loads((Path(__file__).parent / "probes.json").read_text(encoding="utf-8"))["cases"]
failed = []
for case in cases:
    findings = scanner.scan_text(case["input"], latex=case["latex"], **case.get("options", {}))
    if "expected_positions" in case:
        actual = [{key: finding[key] for key in ("line", "column", "matched")} for finding in findings]
        passed = actual == case["expected_positions"]
    elif "expected_count" in case:
        passed = len(findings) == case["expected_count"]
    else:
        passed = any(finding["kind"] == case["expected_kind"] for finding in findings)
    if not passed:
        failed.append({"id": case["id"], "findings": findings})
if failed:
    print(json.dumps({"failed": failed}, ensure_ascii=False, indent=2))
    raise SystemExit(1)
print(f"{len(cases)}/{len(cases)} formatting probes passed.")
