from __future__ import annotations

import re
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


PRIVATE_ABSOLUTE_RE = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+")


def build_step75_output_artifact_policy_audit(
    root: Path,
    policy_path: str = "configs/step75_output_artifact_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    related_files = step75_related_files(root)
    forbidden_dirs = [path for path in policy["forbidden_output_directories"] if (root / path).exists()]
    protected_external = [path for path in related_files if path.startswith("external/taichi_LBM3D/")]
    protected_real_geometry = [path for path in related_files if path.startswith("data/real_geometry_candidates/")]
    vtr_files = [path for path in related_files if path.lower().endswith(".vtr")]
    particle_npy_files = [path for path in related_files if path.lower().endswith(".npy") and "particle" in path.lower()]
    large_files = [
        path for path in related_files if (root / path).is_file() and (root / path).stat().st_size > int(policy["large_file_threshold_bytes"])
    ]
    private_paths = private_absolute_path_rows(root)
    report_missing = [path for path in policy["report_required_paths"] if not (root / path).is_file()]
    rows = []
    rows.extend(absence_row("forbidden_output_directory_absent", path) for path in forbidden_dirs)
    rows.extend(absence_row("no_step75_vtr", path) for path in vtr_files)
    rows.extend(absence_row("no_step75_particle_npy", path) for path in particle_npy_files)
    rows.extend(absence_row("no_protected_external_file", path) for path in protected_external)
    rows.extend(absence_row("no_protected_real_geometry_candidate_file", path) for path in protected_real_geometry)
    rows.extend(absence_row("no_large_step75_file", path) for path in large_files)
    rows.extend(absence_row("no_private_absolute_path", path) for path in private_paths)
    rows.extend(absence_row("required_report_file_present", path) for path in report_missing)
    rows.append(bool_row("required_report_file_count", len(report_missing), 0, "report_required_paths"))
    summary = {
        "large_file_count": len(large_files),
        "output_artifact_policy_audit_pass": False,
        "pass_count": sum(1 for row in rows if row["pass"]),
        "private_absolute_path_count": len(private_paths),
        "protected_external_edit_count": len(protected_external),
        "protected_real_geometry_candidate_edit_count": len(protected_real_geometry),
        "report_missing_count": len(report_missing),
        "row_count": len(rows),
        "step75_driver_run_output_dir_count": len(forbidden_dirs),
        "step75_particle_npy_count": len(particle_npy_files),
        "step75_vtr_count": len(vtr_files),
    }
    summary["output_artifact_policy_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["protected_external_edit_count"] == 0
        and summary["protected_real_geometry_candidate_edit_count"] == 0
        and summary["report_missing_count"] == 0
        and summary["step75_driver_run_output_dir_count"] == 0
        and summary["step75_vtr_count"] == 0
        and summary["step75_particle_npy_count"] == 0
    )
    return rows, summary


def bool_row(check: str, actual, expected, path: str) -> dict:
    return {"actual": actual, "check": check, "expected": expected, "pass": actual == expected, "path": path}


def absence_row(check: str, path: str) -> dict:
    return {"actual": True, "check": check, "expected": False, "pass": False, "path": path}


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for relative in step75_related_files(root):
        if not relative.startswith(("outputs/step75_", "logs/step75_")):
            continue
        path = root / relative
        if path.is_file() and PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(relative)
    return paths


def step75_related_files(root: Path) -> list[str]:
    explicit_paths = {
        "README.md",
        "docs/00_project_status.md",
        "docs/ACTIVATION_PRECONDITIONS.md",
        "docs/75_solver_complete_simulation_campaign_readiness_gate.md",
        "docs/SOLVER_COMPLETE_READINESS_GATE.md",
        "docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md",
        "STEP75_SOLVER_COMPLETE_SIMULATION_CAMPAIGN_READINESS_GATE_GOAL.md",
        "STEP75_SOLVER_COMPLETE_SIMULATION_CAMPAIGN_READINESS_GATE_REPORT.md",
    }
    rows = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        lower = rel.lower()
        if "step75" in lower or "solver_complete" in lower or rel in explicit_paths:
            rows.append(rel)
    return sorted(rows)
