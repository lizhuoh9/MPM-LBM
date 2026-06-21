from __future__ import annotations

import json
from pathlib import Path

from src.mpm_lbm.evidence.canonical_driver_output_guard import build_canonical_driver_output_guard
from src.mpm_lbm.evidence.canonical_driver_smoke_audit import build_canonical_driver_smoke_audit
from src.mpm_lbm.evidence.geo_path_naming_audit import build_geo_path_naming_audit


def build_step60_step59_regression_guard(root: Path) -> tuple[list[dict], dict]:
    root = Path(root)
    smoke_matrix = read_json(root / "outputs/step59_canonical_driver_smoke_matrix/smoke_matrix.json")["summary"]
    smoke_rows, smoke_quality = build_canonical_driver_smoke_audit(root)
    _, geo_summary = build_geo_path_naming_audit(root)
    _, output_summary = build_canonical_driver_output_guard(root)
    step58_summary = read_json(root / "outputs/step59_step58_regression_guard/step58_regression_guard.json")["summary"]
    artifact_summary = read_json(root / "outputs/step59_artifact_manifest/artifact_summary.json")
    rows = [
        row("step59_smoke_matrix", smoke_matrix["canonical_driver_smoke_matrix_pass"], smoke_matrix),
        row("step59_smoke_quality", smoke_quality["canonical_driver_smoke_audit_pass"], smoke_quality),
        row("step59_geo_path_naming", geo_summary["geo_path_naming_audit_pass"], geo_summary),
        row("step59_output_guard", output_summary["output_guard_pass"], output_summary),
        row("step59_step58_regression_guard", step58_summary["step58_regression_guard_pass"], step58_summary),
        row("step59_artifact_manifest", artifact_summary["artifact_budget_pass"], artifact_summary),
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for item in rows if item["pass"]),
        "step59_required_row_count": int(smoke_quality["required_row_count"]),
        "step59_smoke_quality_row_count": len(smoke_rows),
        "step59_missing_required_rows": smoke_quality["missing_required_rows"],
        "step59_canonical_module_count": int(smoke_quality["canonical_module_count"]),
        "step59_legacy_driver_module_used_count": int(smoke_quality["legacy_driver_module_used_count"]),
        "step59_regression_guard_pass": False,
    }
    summary["step59_regression_guard_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and summary["step59_missing_required_rows"] == []
        and summary["step59_canonical_module_count"] == summary["step59_required_row_count"]
        and summary["step59_legacy_driver_module_used_count"] == 0
    )
    return rows, summary


def row(check: str, passed: bool, details) -> dict:
    return {"check": check, "pass": bool(passed), "details": details}


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
