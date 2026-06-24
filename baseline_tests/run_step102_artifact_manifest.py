import os
import re
from pathlib import Path

from step102_common import ROOT, read_json, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["path", "size_bytes", "extension", "step102_related"]
PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def main():
    os.chdir(ROOT)
    policy = read_json("configs/step102_artifact_manifest_policy.json")
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step102_rows = [row for row in rows if row["step102_related"]]
    screenshot_extensions = set(policy["screenshot_extensions"])
    video_extensions = set(policy["video_extensions"])
    raw_geometry_extensions = set(policy["raw_geometry_extensions"])
    summary = {
        "artifact_budget_pass": False,
        "file_count": len(rows),
        "large_file_count": sum(
            1 for row in step102_rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"])
        ),
        "private_absolute_path_count": len(private_absolute_path_rows(ROOT)),
        "protected_external_taichi_lbm3d_step102_file_count": sum(
            1 for row in step102_rows if row["path"].startswith("external/taichi_LBM3D/")
        ),
        "protected_real_geometry_candidates_step102_file_count": sum(
            1 for row in step102_rows if row["path"].startswith("data/real_geometry_candidates/")
        ),
        "protected_sim_or_diagnostics_step102_file_count": sum(
            1
            for row in step102_rows
            if row["path"].startswith("src/mpm_lbm/sim/") or row["path"].startswith("src/mpm_lbm/diagnostics/")
        ),
        "raw_geometry_file_count": sum(1 for row in step102_rows if row["extension"] in raw_geometry_extensions),
        "step102_ansys_proprietary_file_count": sum(
            1 for row in step102_rows if is_official_or_private_file(row, policy)
        ),
        "step102_driver_run_dir_count": step102_driver_run_dir_count(ROOT),
        "step102_file_count": len(step102_rows),
        "step102_fluent_run_output_count": sum(1 for row in step102_rows if is_fluent_run_output(row, policy)),
        "step102_ggui_screenshot_count": sum(1 for row in step102_rows if row["extension"] in screenshot_extensions),
        "step102_ggui_video_count": sum(1 for row in step102_rows if row["extension"] in video_extensions),
        "step102_particle_npy_count": sum(
            1 for row in step102_rows if row["extension"] == ".npy" and "particle" in row["path"].lower()
        ),
        "step102_total_size_bytes": sum(int(row["size_bytes"]) for row in step102_rows),
        "step102_total_size_mb": sum(int(row["size_bytes"]) for row in step102_rows) / (1024.0 * 1024.0),
        "step102_vtr_count": sum(1 for row in step102_rows if row["extension"] == ".vtr"),
    }
    summary["artifact_budget_pass"] = bool(
        summary["step102_file_count"] <= int(policy["max_step102_file_count"])
        and summary["step102_total_size_mb"] < float(policy["max_step102_total_size_mb"])
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["protected_external_taichi_lbm3d_step102_file_count"] == 0
        and summary["protected_real_geometry_candidates_step102_file_count"] == 0
        and summary["protected_sim_or_diagnostics_step102_file_count"] == 0
        and summary["raw_geometry_file_count"] == 0
        and summary["step102_ansys_proprietary_file_count"] == 0
        and summary["step102_driver_run_dir_count"] == 0
        and summary["step102_fluent_run_output_count"] == 0
        and summary["step102_ggui_screenshot_count"] == 0
        and summary["step102_ggui_video_count"] == 0
        and summary["step102_particle_npy_count"] == 0
        and summary["step102_vtr_count"] == 0
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step102 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step102_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step102 artifact manifest finished"
    write_log("logs/step102_artifact_manifest.log", [marker, f"step102_file_count={summary['step102_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step102_artifact_manifest/"):
            continue
        parts = set(path.parts)
        if ".git" in parts or "__pycache__" in parts or ".pytest_cache" in parts:
            continue
        yield path


def manifest_row(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    return {
        "extension": path.suffix.lower(),
        "path": rel,
        "size_bytes": int(path.stat().st_size),
        "step102_related": is_step102_related(rel),
    }


def is_step102_related(path: str) -> bool:
    lower = path.lower()
    return "step102" in lower or lower in {
        "docs/102_fluent_official_2way_fsi_benchmark_intake_and_guard.md",
    }


def is_fluent_run_output(row: dict, policy: dict) -> bool:
    lower = row["path"].lower()
    return lower.endswith(tuple(suffix.lower() for suffix in policy["case_data_suffixes"])) or Path(lower).name in set(
        name.lower() for name in policy["official_file_names"]
    )


def is_official_or_private_file(row: dict, policy: dict) -> bool:
    lower = row["path"].lower()
    names = set(name.lower() for name in policy["official_file_names"])
    return Path(lower).name in names or lower.endswith(tuple(suffix.lower() for suffix in policy["case_data_suffixes"]))


def step102_driver_run_dir_count(root: Path) -> int:
    run_root = root / "outputs" / "step102_driver_runs"
    if not run_root.exists():
        return 0
    return sum(1 for path in run_root.iterdir() if path.is_dir())


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not rel.startswith(("outputs/step102_", "logs/step102_")):
            continue
        if path.suffix.lower() not in {".json", ".csv", ".log"}:
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(rel)
    return paths


if __name__ == "__main__":
    main()
