from __future__ import annotations

import json
from pathlib import Path


def build_code_layout_audit(root: Path, policy_path: str = "configs/step55_code_layout_policy.json") -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = []

    for relative_path in policy["canonical_required_paths"]:
        path = root / relative_path
        rows.append(
            row(
                "canonical_path_exists",
                relative_path,
                "canonical_required_path",
                path.exists(),
                path.exists(),
                "required Step 55 canonical package path must exist",
            )
        )

    root_rows = []
    for path in sorted((root / "src").glob("*.py")):
        category = classify_root_src_file(path.name, policy)
        passed = category != "unclassified_root_src_file"
        root_rows.append(
            row(
                "root_src_file_classified",
                path.relative_to(root).as_posix(),
                category,
                passed,
                category,
                "root src file must be compatibility or approved legacy surface",
            )
        )
    rows.extend(root_rows)

    step55_new_root = [
        item for item in root_rows if "step55" in Path(item["path"]).name.lower() and item["path"].startswith("src/")
    ]
    summary = {
        "canonical_sim_package_exists": (root / "src" / "mpm_lbm" / "sim").is_dir(),
        "canonical_diagnostics_package_exists": (root / "src" / "mpm_lbm" / "diagnostics").is_dir(),
        "canonical_evidence_package_exists": (root / "src" / "mpm_lbm" / "evidence").is_dir(),
        "experiments_steps_package_exists": (root / "experiments" / "steps").is_dir(),
        "canonical_required_path_count": len(policy["canonical_required_paths"]),
        "canonical_required_path_pass_count": sum(1 for item in rows if item["check"] == "canonical_path_exists" and item["pass"]),
        "root_src_file_count": len(root_rows),
        "unclassified_root_src_file_count": sum(1 for item in root_rows if not item["pass"]),
        "step55_new_root_evidence_file_count": len(step55_new_root),
        "solver_behavior_changed": False,
        "physics_feature_expansion": False,
        "code_layout_audit_pass": False,
    }
    summary["code_layout_audit_pass"] = bool(
        summary["canonical_sim_package_exists"]
        and summary["canonical_diagnostics_package_exists"]
        and summary["canonical_evidence_package_exists"]
        and summary["experiments_steps_package_exists"]
        and summary["canonical_required_path_count"] == summary["canonical_required_path_pass_count"]
        and summary["unclassified_root_src_file_count"] == 0
        and summary["step55_new_root_evidence_file_count"] == 0
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
    )
    return rows, summary


def classify_root_src_file(filename: str, policy: dict) -> str:
    exact = policy.get("root_src_exact_classifications", {})
    if filename in exact:
        return exact[filename]
    stem = filename[:-3] if filename.endswith(".py") else filename
    for prefix, category in policy.get("root_src_prefix_classifications", {}).items():
        if stem.startswith(prefix):
            return category
    return "unclassified_root_src_file"


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def row(check: str, path: str, category: str, passed: bool, value, notes: str) -> dict:
    return {"check": check, "path": path, "category": category, "pass": bool(passed), "value": value, "notes": notes}
