from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.batch_migration_audit import read_json


def build_code_placement_freeze_audit(
    root: Path,
    policy_path: str = "configs/step63_code_placement_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    batch_policy = read_json(root / policy["batch_policy_path"])
    rows = [placement_row(root, migration) for migration in batch_policy["migrations"]]
    rows.extend(global_placement_rows(root))
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "placement_violation_count": sum(1 for row in rows if not row["pass"]),
        "code_placement_freeze_pass": False,
    }
    summary["code_placement_freeze_pass"] = bool(
        summary["row_count"] > 0 and summary["row_count"] == summary["pass_count"]
    )
    return rows, summary


def placement_row(root: Path, migration: dict) -> dict:
    canonical_path = migration["canonical_path"]
    category = migration["category"]
    expected_owner = expected_owner_for_path(canonical_path, category)
    actual_owner = owner_for_path(canonical_path)
    path_exists = (root / canonical_path).is_file()
    passed = bool(path_exists and expected_owner == actual_owner)
    return {
        "path": canonical_path,
        "classification": category,
        "expected_owner": expected_owner,
        "actual_owner": actual_owner,
        "path_exists": path_exists,
        "pass": passed,
    }


def global_placement_rows(root: Path) -> list[dict]:
    forbidden_real_geometry = root / "src" / "mpm_lbm" / "sim" / "geometry" / "real_geometry_feasibility.py"
    evidence_under_sim = list((root / "src" / "mpm_lbm" / "sim").glob("**/*audit.py"))
    return [
        {
            "path": forbidden_real_geometry.relative_to(root).as_posix(),
            "classification": "real_geometry_feasibility",
            "expected_owner": "not_src_mpm_lbm_sim",
            "actual_owner": "src/mpm_lbm/sim" if forbidden_real_geometry.exists() else "not_present",
            "path_exists": forbidden_real_geometry.exists(),
            "pass": not forbidden_real_geometry.exists(),
        },
        {
            "path": "src/mpm_lbm/sim/**/*audit.py",
            "classification": "evidence_audit_code",
            "expected_owner": "src/mpm_lbm/evidence",
            "actual_owner": f"{len(evidence_under_sim)} files under sim",
            "path_exists": bool(evidence_under_sim),
            "pass": not evidence_under_sim,
        },
    ]


def expected_owner_for_path(path: str, category: str) -> str:
    if "/diagnostics/" in path:
        return "src/mpm_lbm/diagnostics"
    if category == "real_geometry_support":
        return "src/mpm_lbm/sim/geometry"
    return "src/mpm_lbm/sim"


def owner_for_path(path: str) -> str:
    if path.startswith("src/mpm_lbm/diagnostics/"):
        return "src/mpm_lbm/diagnostics"
    if path.startswith("src/mpm_lbm/sim/geometry/"):
        return "src/mpm_lbm/sim/geometry"
    if path.startswith("src/mpm_lbm/sim/"):
        return "src/mpm_lbm/sim"
    if path.startswith("src/mpm_lbm/evidence/"):
        return "src/mpm_lbm/evidence"
    return "other"
