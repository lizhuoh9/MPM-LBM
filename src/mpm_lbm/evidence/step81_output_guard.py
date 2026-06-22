from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def build_step81_output_guard(
    root: Path,
    policy_path: str = "configs/step81_output_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [output_row(root, path, policy) for path in step81_output_files(root)]
    forbidden_rows = [row for row in rows if row["forbidden"]]
    private_paths = private_absolute_path_rows(root)
    protected_external = git_changed_paths(root, "external/taichi_LBM3D")
    protected_real_geometry = git_changed_paths(root, "data/real_geometry_candidates")
    driver_run_dirs = step81_driver_run_dirs(root, policy)
    summary = {
        "output_guard_pass": False,
        "pass_count": sum(1 for row in rows if row["pass"]),
        "private_absolute_path_count": len(private_paths),
        "protected_external_edit_count": len(protected_external),
        "protected_real_geometry_candidate_edit_count": len(protected_real_geometry),
        "row_count": len(rows),
        "step81_dense_wall_velocity_output_count": sum(
            1 for row in rows if "dense_wall_velocity" in row["path"].lower()
        ),
        "step81_driver_run_dir_count": len(driver_run_dirs),
        "step81_forbidden_file_count": len(forbidden_rows),
        "step81_large_file_count": sum(
            1 for row in rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"])
        ),
        "step81_particle_npy_count": sum(
            1 for row in rows if row["extension"] == ".npy" and "particle" in row["path"].lower()
        ),
        "step81_sparse_wall_velocity_output_count": sum(
            1 for row in rows if "sparse_wall_velocity" in row["path"].lower()
        ),
        "step81_total_size_bytes": sum(int(row["size_bytes"]) for row in rows),
        "step81_total_size_mb": sum(int(row["size_bytes"]) for row in rows) / (1024.0 * 1024.0),
        "step81_vtr_count": sum(1 for row in rows if row["extension"] == ".vtr"),
    }
    summary["output_guard_pass"] = bool(
        rows
        and summary["row_count"] == summary["pass_count"]
        and summary["step81_driver_run_dir_count"] == 0
        and summary["step81_vtr_count"] == 0
        and summary["step81_particle_npy_count"] == 0
        and summary["step81_dense_wall_velocity_output_count"] == 0
        and summary["step81_sparse_wall_velocity_output_count"] == 0
        and summary["step81_large_file_count"] == 0
        and summary["step81_forbidden_file_count"] == 0
        and summary["step81_total_size_mb"] < float(policy["max_step81_total_size_mb"])
        and summary["private_absolute_path_count"] == 0
        and summary["protected_external_edit_count"] == 0
        and summary["protected_real_geometry_candidate_edit_count"] == 0
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


def step81_output_files(root: Path):
    files = []
    for base in (root / "outputs", root / "logs"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if rel.startswith("outputs/step81_") or rel.startswith("logs/step81_"):
                files.append(path)
    return sorted(files)


def is_forbidden(root: Path, path: Path, policy: dict) -> bool:
    rel = path.relative_to(root).as_posix()
    lower = rel.lower()
    if any(token.lower() in lower for token in policy["forbidden_filename_tokens"]):
        return True
    return any(rel.startswith(prefix) for prefix in policy["protected_prefixes"])


def step81_driver_run_dirs(root: Path, policy: dict) -> list[Path]:
    run_root = root / policy["driver_run_root"]
    if not run_root.exists():
        return []
    return [path for path in run_root.iterdir() if path.is_dir()]


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in step81_output_files(root):
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
