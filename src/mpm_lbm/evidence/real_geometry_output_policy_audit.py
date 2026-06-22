from __future__ import annotations

import re
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


PRIVATE_ABSOLUTE_RE = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+")


def build_step74_real_geometry_output_policy_audit(
    root: Path,
    policy_path: str = "configs/step74_real_geometry_output_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    related_files = step74_related_files(root)
    forbidden_dirs = [path for path in policy["forbidden_output_directories"] if (root / path).exists()]
    protected_real_geometry = [path for path in related_files if path.startswith("data/real_geometry_candidates/")]
    protected_external = [path for path in related_files if path.startswith("external/taichi_LBM3D/")]
    vtr_files = [path for path in related_files if path.lower().endswith(".vtr")]
    particle_npy_files = [path for path in related_files if path.lower().endswith(".npy") and "particle" in path.lower()]
    raw_geometry_files = [
        path
        for path in related_files
        if Path(path).suffix.lower() in set(policy["raw_geometry_extensions"])
        and not is_allowed_synthetic_fixture(path, policy)
    ]
    synthetic_fixtures = [
        path
        for path in related_files
        if any(path.startswith(prefix) for prefix in policy["allowed_synthetic_fixture_prefixes"])
        and Path(path).suffix.lower() == ".txt"
    ]
    large_files = [
        path for path in related_files if (root / path).is_file() and (root / path).stat().st_size > int(policy["large_file_threshold_bytes"])
    ]
    private_paths = private_absolute_path_rows(root)
    rows = []
    rows.extend(absence_row("forbidden_output_directory_absent", path) for path in forbidden_dirs)
    rows.extend(absence_row("no_step74_vtr", path) for path in vtr_files)
    rows.extend(absence_row("no_step74_particle_npy", path) for path in particle_npy_files)
    rows.extend(absence_row("no_protected_real_geometry_candidate_file", path) for path in protected_real_geometry)
    rows.extend(absence_row("no_external_taichi_lbm3d_file", path) for path in protected_external)
    rows.extend(absence_row("no_unapproved_raw_geometry_file", path) for path in raw_geometry_files)
    rows.extend(absence_row("no_large_step74_file", path) for path in large_files)
    rows.extend(absence_row("no_private_absolute_path", path) for path in private_paths)
    rows.append(bool_row("synthetic_fixture_count_within_limit", len(synthetic_fixtures), 1, "outputs/step74_synthetic_geometry_fixture"))
    summary = {
        "external_taichi_lbm3d_edit_count": len(protected_external),
        "forbidden_output_directory_count": len(forbidden_dirs),
        "large_file_count": len(large_files),
        "particle_npy_count": len(particle_npy_files),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "private_absolute_path_count": len(private_paths),
        "protected_real_geometry_candidate_edit_count": len(protected_real_geometry),
        "raw_geometry_file_count": len(raw_geometry_files),
        "real_geometry_output_policy_audit_pass": False,
        "row_count": len(rows),
        "step74_vtr_count": len(vtr_files),
        "synthetic_fixture_count": len(synthetic_fixtures),
    }
    summary["real_geometry_output_policy_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["forbidden_output_directory_count"] == 0
        and summary["step74_vtr_count"] == 0
        and summary["particle_npy_count"] == 0
        and summary["protected_real_geometry_candidate_edit_count"] == 0
        and summary["external_taichi_lbm3d_edit_count"] == 0
        and summary["raw_geometry_file_count"] == 0
        and summary["synthetic_fixture_count"] <= 1
        and summary["private_absolute_path_count"] == 0
        and summary["large_file_count"] == 0
    )
    return rows, summary


def bool_row(check: str, actual, expected_max, path: str) -> dict:
    return {
        "actual": actual,
        "check": check,
        "expected_max": expected_max,
        "pass": int(actual) <= int(expected_max),
        "path": path,
    }


def absence_row(check: str, path: str) -> dict:
    return {"actual": True, "check": check, "expected": False, "pass": False, "path": path}


def is_allowed_synthetic_fixture(path: str, policy: dict) -> bool:
    return any(path.startswith(prefix) for prefix in policy["allowed_synthetic_fixture_prefixes"]) and path.endswith(".txt")


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for relative in step74_related_files(root):
        if not relative.startswith(("outputs/step74_", "logs/step74_")):
            continue
        path = root / relative
        if path.is_file() and PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(relative)
    return paths


def step74_related_files(root: Path) -> list[str]:
    explicit_paths = {
        "README.md",
        "docs/00_project_status.md",
        "docs/ACTIVATION_PRECONDITIONS.md",
        "docs/REAL_GEOMETRY_DATA_BOUNDARY.md",
        "docs/REAL_GEOMETRY_CANDIDATE_POLICY.md",
        "docs/74_real_geometry_data_boundary_audit.md",
        "STEP74_REAL_GEOMETRY_DATA_BOUNDARY_AUDIT_GOAL.md",
        "STEP74_REAL_GEOMETRY_DATA_BOUNDARY_AUDIT_REPORT.md",
    }
    rows = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        lower = rel.lower()
        if "step74" in lower or "real_geometry_data_boundary" in lower or rel in explicit_paths:
            rows.append(rel)
    return sorted(rows)
