from __future__ import annotations

import re
import subprocess
from pathlib import Path

from src.mpm_lbm.evidence.step106_common import read_json


PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")
FORBIDDEN_VALIDATION_RE = re.compile(
    r"(matches fluent|validated against fluent|fluent validation passed|physical validation complete|production ready)",
    re.IGNORECASE,
)


def build_step106_output_guard(
    root: Path,
    policy_path: str = "configs/step106_output_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    video_extensions = set(policy["video_extensions"])
    rows = [output_row(root, path, policy) for path in step106_output_files(root)]
    forbidden_rows = [row for row in rows if row["forbidden"]]
    private_paths = private_absolute_path_rows(root)
    protected_external = git_changed_paths(root, "external/taichi_LBM3D")
    protected_real_geometry = git_changed_paths(root, "data/real_geometry_candidates")
    validation_claims = forbidden_validation_claim_rows(root)
    step36_references = step36_wall_velocity_reference_rows(root)
    total_size_mb = sum(int(row["size_bytes"]) for row in rows) / (1024.0 * 1024.0)
    large_file_count = sum(1 for row in rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"]))
    summary = {
        "artifact_budget_pass": bool(total_size_mb < float(policy["max_step106_total_size_mb"]) and large_file_count == 0),
        "forbidden_validation_claim_count": len(validation_claims),
        "output_guard_pass": False,
        "pass_count": sum(1 for row in rows if row["pass"]),
        "private_absolute_path_count": len(private_paths),
        "protected_external_edit_count": len(protected_external),
        "protected_real_geometry_candidate_edit_count": len(protected_real_geometry),
        "row_count": len(rows),
        "step106_ansys_proprietary_file_count": sum(1 for row in rows if is_ansys_proprietary_output(row, policy)),
        "step106_fluent_run_output_count": sum(1 for row in rows if is_fluent_run_output(row, policy)),
        "step106_forbidden_file_count": len(forbidden_rows),
        "step106_large_file_count": large_file_count,
        "step106_particle_npy_count": sum(
            1 for row in rows if row["extension"] == ".npy" and "particle" in row["path"].lower()
        ),
        "step106_private_fluent_csv_count": sum(1 for row in rows if row["path"].startswith("benchmarks/private/")),
        "step106_step36_wall_velocity_reference_count": len(step36_references),
        "step106_total_size_bytes": sum(int(row["size_bytes"]) for row in rows),
        "step106_total_size_mb": total_size_mb,
        "step106_video_count": sum(1 for row in rows if row["extension"] in video_extensions),
        "step106_vtr_count": sum(1 for row in rows if row["extension"] == ".vtr"),
    }
    summary["output_guard_pass"] = bool(
        rows
        and summary["row_count"] == summary["pass_count"]
        and summary["step106_ansys_proprietary_file_count"] == 0
        and summary["step106_fluent_run_output_count"] == 0
        and summary["step106_forbidden_file_count"] == 0
        and summary["step106_particle_npy_count"] == 0
        and summary["step106_private_fluent_csv_count"] == 0
        and summary["step106_step36_wall_velocity_reference_count"] == 0
        and summary["step106_video_count"] == 0
        and summary["step106_vtr_count"] == 0
        and summary["artifact_budget_pass"]
        and summary["private_absolute_path_count"] == 0
        and summary["protected_external_edit_count"] == 0
        and summary["protected_real_geometry_candidate_edit_count"] == 0
        and summary["forbidden_validation_claim_count"] == 0
    )
    return rows, summary


def output_row(root: Path, path: Path, policy: dict) -> dict:
    rel = path.relative_to(root).as_posix()
    extension = path.suffix.lower()
    forbidden = is_forbidden(root, path, policy)
    large = path.stat().st_size > int(policy["large_file_threshold_bytes"])
    return {
        "extension": extension,
        "forbidden": forbidden,
        "pass": not forbidden and not large,
        "path": rel,
        "size_bytes": int(path.stat().st_size),
    }


def step106_output_files(root: Path) -> list[Path]:
    files = []
    for base in (root / "configs", root / "outputs", root / "logs"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if rel.startswith(("outputs/step106_output_guard/", "outputs/step106_artifact_manifest/")):
                continue
            if rel.startswith(("configs/step106_", "outputs/step106_", "logs/step106_")):
                files.append(path)
    return sorted(files)


def is_forbidden(root: Path, path: Path, policy: dict) -> bool:
    rel = path.relative_to(root).as_posix()
    lower = rel.lower()
    if any(token.lower() in lower for token in policy["forbidden_filename_tokens"]):
        return True
    for protected in policy["protected_prefixes"]:
        if rel.startswith(protected):
            return True
    return False


def is_fluent_run_output(row: dict, policy: dict) -> bool:
    lower = row["path"].lower()
    return lower.endswith(tuple(suffix.lower() for suffix in policy["case_data_suffixes"])) or Path(lower).name in set(
        name.lower() for name in policy["official_file_names"]
    )


def is_ansys_proprietary_output(row: dict, policy: dict) -> bool:
    lower = row["path"].lower()
    names = set(name.lower() for name in policy["official_file_names"])
    return Path(lower).name in names or any(name in lower for name in names)


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in step106_output_files(root):
        if path.suffix.lower() not in {".json", ".csv", ".log", ".md"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if PRIVATE_ABSOLUTE_RE.search(text):
            paths.append(path.relative_to(root).as_posix())
    return paths


def forbidden_validation_claim_rows(root: Path) -> list[str]:
    paths = []
    for path in step106_output_files(root):
        if path.suffix.lower() not in {".json", ".csv", ".log", ".md"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if FORBIDDEN_VALIDATION_RE.search(text):
            paths.append(path.relative_to(root).as_posix())
    return paths


def step36_wall_velocity_reference_rows(root: Path) -> list[str]:
    paths = []
    for path in step106_output_files(root):
        if path.suffix.lower() not in {".json", ".csv", ".log"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if "step36_wall_velocity_application_solid_vel_experimental" in text:
            paths.append(path.relative_to(root).as_posix())
    return paths


def git_changed_paths(root: Path, pathspec: str) -> list[str]:
    result = subprocess.run(["git", "status", "--short", "--", pathspec], cwd=root, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return [f"git_status_error:{result.stderr.strip()}"]
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
