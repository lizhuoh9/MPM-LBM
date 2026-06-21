from __future__ import annotations

import json
import subprocess
from pathlib import Path


LARGE_FILE_THRESHOLD_BYTES = 100 * 1024 * 1024


def build_canonical_driver_32_duration_output_guard(
    root: Path,
    output_policy_path: str = "configs/step62_output_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / output_policy_path)
    run_root = root / "outputs" / "step62_driver_runs"
    rows = [output_row(root, path, run_root, policy) for path in step62_output_files(root)]
    run_dirs = [path for path in run_root.iterdir() if path.is_dir()] if run_root.exists() else []
    forbidden_rows = [row for row in rows if row["forbidden"]]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "step62_driver_run_dir_count": len(run_dirs),
        "step62_required_driver_run_dir_count": sum(1 for path in run_dirs if not path.name.endswith("_optional")),
        "step62_optional_driver_run_dir_count": sum(1 for path in run_dirs if path.name.endswith("_optional")),
        "step62_vtr_count": sum(1 for row in rows if row["extension"] == ".vtr"),
        "step62_particle_npy_count": sum(
            1 for row in rows if row["extension"] == ".npy" and "particle" in row["path"].lower()
        ),
        "step62_large_file_count": sum(1 for row in rows if int(row["size_bytes"]) > LARGE_FILE_THRESHOLD_BYTES),
        "step62_forbidden_file_count": len(forbidden_rows),
        "step62_total_size_bytes": sum(int(row["size_bytes"]) for row in rows),
        "step62_total_size_mb": sum(int(row["size_bytes"]) for row in rows) / (1024.0 * 1024.0),
        "external_edit_count": len(git_changed_paths(root, "external/taichi_LBM3D")),
        "real_geometry_candidates_edit_count": len(git_changed_paths(root, "data/real_geometry_candidates")),
        "private_absolute_path_count": private_absolute_path_count(root, rows),
        "output_guard_pass": False,
    }
    summary["output_guard_pass"] = bool(
        summary["step62_required_driver_run_dir_count"] == int(policy["expected_required_driver_run_dir_count"])
        and summary["step62_optional_driver_run_dir_count"] == 0
        and summary["step62_vtr_count"] == 0
        and summary["step62_particle_npy_count"] == 0
        and summary["step62_large_file_count"] == 0
        and summary["step62_forbidden_file_count"] == 0
        and float(summary["step62_total_size_mb"]) < float(policy["max_step62_total_size_mb"])
        and summary["external_edit_count"] == 0
        and summary["real_geometry_candidates_edit_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["row_count"] == summary["pass_count"]
    )
    return rows, summary


def output_row(root: Path, path: Path, run_root: Path, policy: dict) -> dict:
    rel = path.relative_to(root).as_posix()
    extension = path.suffix.lower()
    forbidden = is_forbidden(path, run_root, policy)
    return {
        "path": rel,
        "size_bytes": int(path.stat().st_size),
        "extension": extension,
        "forbidden": forbidden,
        "pass": not forbidden and int(path.stat().st_size) <= LARGE_FILE_THRESHOLD_BYTES,
    }


def step62_output_files(root: Path):
    files = []
    for base in (root / "outputs", root / "logs"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if rel.startswith("outputs/step62_") or rel.startswith("logs/step62_"):
                files.append(path)
    return sorted(files)


def is_forbidden(path: Path, run_root: Path, policy: dict) -> bool:
    name = path.name
    lower = path.as_posix().lower()
    if any(token.lower() in lower for token in policy["forbidden_filename_tokens"]):
        return True
    try:
        path.relative_to(run_root)
    except ValueError:
        return False
    return name not in set(policy["allowed_driver_run_files"])


def git_changed_paths(root: Path, pathspec: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", pathspec],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"git_diff_error:{result.stderr.strip()}"]
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def private_absolute_path_count(root: Path, rows: list[dict]) -> int:
    count = 0
    for row in rows:
        path = root / row["path"]
        if path.suffix.lower() not in {".json", ".csv", ".log"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore") if path.is_file() else ""
        if "C:\\Users\\lizhu" in text or "D:\\working" in text:
            count += 1
    return count


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
