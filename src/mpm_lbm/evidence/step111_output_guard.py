from __future__ import annotations

import re
import subprocess
from pathlib import Path

from src.mpm_lbm.evidence.step111_common import read_json


PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def build_step111_output_guard(root: Path, policy_path: str = "configs/step111_output_guard_policy.json") -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [output_row(root, path, policy) for path in step111_files(root)]
    validation_claims = pattern_rows(root, policy["validation_claim_patterns"])
    direct_claims = pattern_rows(root, policy["direct_equivalence_claim_patterns"])
    total_size_bytes = sum(int(row["size_bytes"]) for row in rows)
    source_files = [path for path in (root / "src" / "mpm_lbm" / "evidence").glob("step111_*.py") if path.name != "step111_output_guard.py"]
    source_text = "\n".join(path.read_text(encoding="utf-8") for path in source_files)
    summary = {
        "artifact_budget_pass": total_size_bytes / (1024.0 * 1024.0) < float(policy["max_step111_total_size_mb"]),
        "direct_equivalence_claim_count": len(direct_claims),
        "official_case_file_count": sum(1 for row in rows if row["extension"] in {".cas", ".zip"}),
        "official_case_data_h5_count": sum(1 for row in rows if row["path"].lower().endswith((".cas.h5", ".dat.h5"))),
        "official_journal_file_count": sum(1 for row in rows if row["extension"] == ".jou"),
        "official_mesh_file_count": sum(1 for row in rows if row["extension"] in {".msh", ".gz"}),
        "output_guard_pass": False,
        "pass_count": sum(1 for row in rows if row["pass"]),
        "private_absolute_path_count": len(private_absolute_path_rows(root)),
        "protected_external_edit_count": len(git_changed_paths(root, "external/taichi_LBM3D")),
        "protected_real_geometry_candidate_edit_count": len(git_changed_paths(root, "data/real_geometry_candidates")),
        "real_driver_run_called_count": real_driver_run_called_count(root),
        "real_lbm_preflow_run_called_count": real_lbm_preflow_run_called_count(root),
        "row_count": len(rows),
        "synthetic_candidate_curve_count": source_text.count("synthesize_" + "candidate_curve"),
        "proxy_curve_replay_evidence_mode_count": source_text.count("step110_preflow_monitor_" + "proxy_curve_replay"),
        "solver_curve_generated_from_reference_count": source_text.count("solver_curve_generated_" + "from_reference"),
        "step111_forbidden_file_count": sum(1 for row in rows if row["forbidden"]),
        "step111_total_size_bytes": total_size_bytes,
        "step111_total_size_mb": total_size_bytes / (1024.0 * 1024.0),
        "validation_claim_count": len(validation_claims),
    }
    summary["output_guard_pass"] = bool(
        rows
        and summary["row_count"] == summary["pass_count"]
        and summary["synthetic_candidate_curve_count"] == 0
        and summary["proxy_curve_replay_evidence_mode_count"] == 0
        and summary["solver_curve_generated_from_reference_count"] == 0
        and summary["real_driver_run_called_count"] == 1
        and summary["real_lbm_preflow_run_called_count"] == 1
        and summary["official_case_file_count"] == 0
        and summary["official_case_data_h5_count"] == 0
        and summary["official_mesh_file_count"] == 0
        and summary["official_journal_file_count"] == 0
        and summary["validation_claim_count"] == 0
        and summary["direct_equivalence_claim_count"] == 0
        and summary["protected_external_edit_count"] == 0
        and summary["protected_real_geometry_candidate_edit_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["step111_forbidden_file_count"] == 0
        and summary["artifact_budget_pass"]
    )
    return rows, summary


def output_row(root: Path, path: Path, policy: dict) -> dict:
    rel = path.relative_to(root).as_posix()
    extension = path.suffix.lower()
    forbidden = any(token.lower() in rel.lower() for token in policy["forbidden_filename_tokens"])
    large = path.stat().st_size > int(policy["large_file_threshold_bytes"])
    return {"extension": extension, "forbidden": forbidden, "pass": not forbidden and not large, "path": rel, "size_bytes": int(path.stat().st_size)}


def step111_files(root: Path) -> list[Path]:
    files = []
    for base in (root / "configs", root / "outputs", root / "logs"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if rel.startswith(("outputs/step111_output_guard/", "outputs/step111_artifact_manifest/")):
                continue
            if rel.startswith(("configs/step111_", "outputs/step111_", "logs/step111_")):
                files.append(path)
    return sorted(files)


def pattern_rows(root: Path, patterns: list[str]) -> list[str]:
    compiled = [re.compile(re.escape(pattern), re.IGNORECASE) for pattern in patterns]
    paths = []
    for path in step111_files(root):
        if path.suffix.lower() not in {".json", ".csv", ".log", ".md"}:
            continue
        if path.name.endswith("_policy.json"):
            continue
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if any(pattern.search(text) for pattern in compiled):
            paths.append(path.relative_to(root).as_posix())
    return paths


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in step111_files(root):
        if path.suffix.lower() not in {".json", ".csv", ".log", ".md"}:
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(path.relative_to(root).as_posix())
    return paths


def real_driver_run_called_count(root: Path) -> int:
    path = root / "outputs" / "step111_real_solver_candidate" / "real_solver_candidate_report.json"
    if not path.is_file():
        return 0
    payload = read_json(path)
    return sum(1 for row in payload.get("rows", []) if bool(row.get("driver_run_called", False)))


def real_lbm_preflow_run_called_count(root: Path) -> int:
    path = root / "outputs" / "step111_real_lbm_preflow" / "preflow_report.json"
    if not path.is_file():
        return 0
    payload = read_json(path)
    return sum(1 for row in payload.get("rows", []) if bool(row.get("real_lbm_step_called", False)))


def git_changed_paths(root: Path, pathspec: str) -> list[str]:
    result = subprocess.run(["git", "status", "--short", "--", pathspec], cwd=root, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return [f"git_status_error:{result.stderr.strip()}"]
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
