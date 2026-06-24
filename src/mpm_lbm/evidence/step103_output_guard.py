from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def build_step103_output_guard(
    root: Path,
    policy_path: str = "configs/step103_output_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    screenshot_extensions = set(policy["screenshot_extensions"])
    video_extensions = set(policy["video_extensions"])
    rows = [output_row(root, path, policy) for path in step103_output_files(root)]
    forbidden_rows = [row for row in rows if row["forbidden"]]
    required_dirs = [root / path for path in policy["required_driver_run_dirs"] if (root / path).is_dir()]
    optional_dirs = step103_optional_driver_run_dirs(root, policy)
    private_paths = private_absolute_path_rows(root)
    protected_external = git_changed_paths(root, "external/taichi_LBM3D")
    protected_real_geometry = git_changed_paths(root, "data/real_geometry_candidates")
    total_size_mb = sum(int(row["size_bytes"]) for row in rows) / (1024.0 * 1024.0)
    large_file_count = sum(1 for row in rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"]))
    summary = {
        "artifact_budget_pass": bool(total_size_mb < float(policy["max_step103_total_size_mb"]) and large_file_count == 0),
        "output_guard_pass": False,
        "pass_count": sum(1 for row in rows if row["pass"]),
        "private_absolute_path_count": len(private_paths),
        "protected_external_edit_count": len(protected_external),
        "protected_real_geometry_candidate_edit_count": len(protected_real_geometry),
        "row_count": len(rows),
        "step103_ansys_proprietary_file_count": sum(1 for row in rows if is_ansys_proprietary_output(row, policy)),
        "step103_fluent_run_output_count": sum(1 for row in rows if is_fluent_run_output(row, policy)),
        "step103_forbidden_file_count": len(forbidden_rows),
        "step103_ggui_screenshot_count": sum(1 for row in rows if row["extension"] in screenshot_extensions),
        "step103_ggui_video_count": sum(1 for row in rows if row["extension"] in video_extensions),
        "step103_large_file_count": large_file_count,
        "step103_optional_driver_run_dir_count": len(optional_dirs),
        "step103_particle_npy_count": sum(
            1 for row in rows if row["extension"] == ".npy" and "particle" in row["path"].lower()
        ),
        "step103_required_driver_run_dir_count": len(required_dirs),
        "step103_total_size_bytes": sum(int(row["size_bytes"]) for row in rows),
        "step103_total_size_mb": total_size_mb,
        "step103_vtr_count": sum(1 for row in rows if row["extension"] == ".vtr"),
    }
    summary["output_guard_pass"] = bool(
        rows
        and summary["row_count"] == summary["pass_count"]
        and summary["step103_required_driver_run_dir_count"] == len(policy["required_driver_run_dirs"])
        and summary["step103_optional_driver_run_dir_count"] == 0
        and summary["step103_ggui_screenshot_count"] == 1
        and summary["step103_ggui_video_count"] == 0
        and summary["step103_vtr_count"] == 0
        and summary["step103_particle_npy_count"] == 0
        and summary["step103_ansys_proprietary_file_count"] == 0
        and summary["step103_fluent_run_output_count"] == 0
        and summary["step103_forbidden_file_count"] == 0
        and summary["artifact_budget_pass"]
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
    return {"extension": extension, "forbidden": forbidden, "pass": not forbidden and not large, "path": rel, "size_bytes": int(path.stat().st_size)}


def step103_output_files(root: Path):
    files = []
    for base in (root / "outputs", root / "logs"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if rel.startswith("outputs/step103_") or rel.startswith("logs/step103_"):
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
    driver_root = root / policy["driver_run_root"]
    try:
        path.relative_to(driver_root)
    except ValueError:
        pass
    else:
        return path.name not in set(policy["allowed_driver_run_files"])
    ggui_root = root / policy["ggui_output_dir"]
    try:
        path.relative_to(ggui_root)
    except ValueError:
        return False
    return path.name not in set(policy["allowed_ggui_files"])


def is_fluent_run_output(row: dict, policy: dict) -> bool:
    lower = row["path"].lower()
    return lower.endswith(tuple(suffix.lower() for suffix in policy["case_data_suffixes"])) or lower.endswith(
        (".msh", ".jou", ".zip")
    )


def is_ansys_proprietary_output(row: dict, policy: dict) -> bool:
    lower = row["path"].lower()
    names = ("fsi_2way.zip", "flap.msh", "steady_fluid_flow.jou", "flap_fsi_2way.cas.h5", "flap_fsi_2way.dat.h5")
    return any(name in lower for name in names) or lower.endswith(tuple(suffix.lower() for suffix in policy["case_data_suffixes"]))


def step103_optional_driver_run_dirs(root: Path, policy: dict) -> list[Path]:
    run_root = root / policy["driver_run_root"]
    if not run_root.exists():
        return []
    required = {Path(path).name for path in policy["required_driver_run_dirs"]}
    return [path for path in run_root.iterdir() if path.is_dir() and path.name not in required]


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in step103_output_files(root):
        if path.suffix.lower() not in {".json", ".csv", ".log"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if PRIVATE_ABSOLUTE_RE.search(text):
            paths.append(path.relative_to(root).as_posix())
    return paths


def git_changed_paths(root: Path, pathspec: str) -> list[str]:
    result = subprocess.run(["git", "status", "--short", "--", pathspec], cwd=root, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return [f"git_status_error:{result.stderr.strip()}"]
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
