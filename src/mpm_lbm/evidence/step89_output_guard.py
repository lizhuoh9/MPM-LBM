from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def build_step89_output_guard(
    root: Path,
    policy_path: str = "configs/step89_output_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    raw_geometry_extensions = set(policy["raw_geometry_extensions"])
    rows = [output_row(root, path, policy) for path in step89_output_files(root)]
    forbidden_rows = [row for row in rows if row["forbidden"]]
    private_paths = private_absolute_path_rows(root)
    protected_external = git_changed_paths(root, "external/taichi_LBM3D")
    protected_real_geometry = git_changed_paths(root, "data/real_geometry_candidates")
    protected_sim = git_changed_paths(root, "src/mpm_lbm/sim")
    protected_diagnostics = git_changed_paths(root, "src/mpm_lbm/diagnostics")
    driver_run_dirs = step89_driver_run_dirs(root, policy)
    total_size_bytes = sum(int(row["size_bytes"]) for row in rows)
    total_size_mb = total_size_bytes / (1024.0 * 1024.0)
    large_file_count = sum(1 for row in rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"]))
    artifact_budget_pass = bool(total_size_mb < float(policy["max_step89_total_size_mb"]) and large_file_count == 0)
    summary = {
        "artifact_budget_pass": artifact_budget_pass,
        "output_guard_pass": False,
        "pass_count": sum(1 for row in rows if row["pass"]),
        "private_absolute_path_count": len(private_paths),
        "protected_diagnostics_edit_count": len(protected_diagnostics),
        "protected_external_edit_count": len(protected_external),
        "protected_real_geometry_candidate_edit_count": len(protected_real_geometry),
        "protected_sim_edit_count": len(protected_sim),
        "row_count": len(rows),
        "step89_dense_displacement_output_count": sum(1 for row in rows if "dense_displacement" in row["path"].lower()),
        "step89_dense_wall_velocity_output_count": sum(1 for row in rows if "dense_wall_velocity" in row["path"].lower()),
        "step89_displaced_particle_output_count": sum(1 for row in rows if "displaced_particle" in row["path"].lower()),
        "step89_driver_run_dir_count": len(driver_run_dirs),
        "step89_forbidden_file_count": len(forbidden_rows),
        "step89_large_file_count": large_file_count,
        "step89_particle_npy_count": sum(
            1 for row in rows if row["extension"] == ".npy" and "particle" in row["path"].lower()
        ),
        "step89_raw_geometry_output_count": sum(1 for row in rows if row["extension"] in raw_geometry_extensions),
        "step89_real_geometry_candidate_output_count": sum(
            1 for row in rows if "real_geometry_candidate" in row["path"].lower()
        ),
        "step89_sparse_wall_velocity_output_count": sum(
            1 for row in rows if "sparse_wall_velocity" in row["path"].lower()
        ),
        "step89_total_size_bytes": total_size_bytes,
        "step89_total_size_mb": total_size_mb,
        "step89_vtr_count": sum(1 for row in rows if row["extension"] == ".vtr"),
    }
    summary["output_guard_pass"] = bool(
        rows
        and summary["row_count"] == summary["pass_count"]
        and summary["step89_driver_run_dir_count"] == 0
        and summary["step89_vtr_count"] == 0
        and summary["step89_particle_npy_count"] == 0
        and summary["step89_dense_wall_velocity_output_count"] == 0
        and summary["step89_sparse_wall_velocity_output_count"] == 0
        and summary["step89_dense_displacement_output_count"] == 0
        and summary["step89_displaced_particle_output_count"] == 0
        and summary["step89_raw_geometry_output_count"] == 0
        and summary["step89_real_geometry_candidate_output_count"] == 0
        and summary["step89_forbidden_file_count"] == 0
        and summary["artifact_budget_pass"]
        and summary["private_absolute_path_count"] == 0
        and summary["protected_external_edit_count"] == 0
        and summary["protected_real_geometry_candidate_edit_count"] == 0
        and summary["protected_sim_edit_count"] == 0
        and summary["protected_diagnostics_edit_count"] == 0
    )
    return rows, summary


def output_row(root: Path, path: Path, policy: dict) -> dict:
    rel = path.relative_to(root).as_posix()
    extension = path.suffix.lower()
    forbidden = is_forbidden(path, policy)
    large = path.stat().st_size > int(policy["large_file_threshold_bytes"])
    return {
        "extension": extension,
        "forbidden": forbidden,
        "pass": not forbidden and not large,
        "path": rel,
        "size_bytes": int(path.stat().st_size),
    }


def step89_output_files(root: Path) -> list[Path]:
    files = []
    for base in (root / "outputs", root / "logs"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if rel.startswith("outputs/step89_") or rel.startswith("logs/step89_"):
                files.append(path)
    return sorted(files)


def is_forbidden(path: Path, policy: dict) -> bool:
    lower = path.as_posix().lower()
    return any(token.lower() in lower for token in policy["forbidden_filename_tokens"])


def step89_driver_run_dirs(root: Path, policy: dict) -> list[Path]:
    run_root = root / policy["driver_run_root"]
    if not run_root.exists():
        return []
    return [path for path in run_root.iterdir() if path.is_dir()]


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in step89_output_files(root):
        if path.suffix.lower() not in {".json", ".csv", ".log"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if PRIVATE_ABSOLUTE_RE.search(text):
            paths.append(path.relative_to(root).as_posix())
    return paths


def git_changed_paths(root: Path, pathspec: str) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--", pathspec],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"git_status_error:{result.stderr.strip()}"]
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
