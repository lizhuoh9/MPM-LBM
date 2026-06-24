import os
import re
from pathlib import Path

from step93_common import ROOT, read_json, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["path", "size_bytes", "extension", "step93_related"]
PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def main():
    os.chdir(ROOT)
    policy = read_json("configs/step93_artifact_manifest_policy.json")
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step93_rows = [row for row in rows if row["step93_related"]]
    screenshot_extensions = set(policy["screenshot_extensions"])
    summary = {
        "artifact_budget_pass": False,
        "file_count": len(rows),
        "large_file_count": sum(
            1 for row in step93_rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"])
        ),
        "private_absolute_path_count": len(private_absolute_path_rows(ROOT)),
        "protected_external_taichi_lbm3d_step93_file_count": sum(
            1 for row in step93_rows if row["path"].startswith("external/taichi_LBM3D/")
        ),
        "protected_real_geometry_candidates_step93_file_count": sum(
            1 for row in step93_rows if row["path"].startswith("data/real_geometry_candidates/")
        ),
        "raw_geometry_file_count": sum(
            1 for row in step93_rows if row["extension"] in set(policy["raw_geometry_extensions"])
        ),
        "step93_driver_run_dir_count": step93_driver_run_dir_count(ROOT),
        "step93_file_count": len(step93_rows),
        "step93_ggui_screenshot_count": sum(1 for row in step93_rows if row["extension"] in screenshot_extensions),
        "step93_particle_npy_count": sum(
            1 for row in step93_rows if row["extension"] == ".npy" and "particle" in row["path"].lower()
        ),
        "step93_total_size_bytes": sum(int(row["size_bytes"]) for row in step93_rows),
        "step93_total_size_mb": sum(int(row["size_bytes"]) for row in step93_rows) / (1024.0 * 1024.0),
        "vtr_file_count": sum(1 for row in step93_rows if row["extension"] == ".vtr"),
    }
    summary["artifact_budget_pass"] = bool(
        summary["step93_file_count"] <= int(policy["max_step93_file_count"])
        and summary["step93_total_size_mb"] < float(policy["max_step93_total_size_mb"])
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["protected_external_taichi_lbm3d_step93_file_count"] == 0
        and summary["protected_real_geometry_candidates_step93_file_count"] == 0
        and summary["raw_geometry_file_count"] == 0
        and summary["step93_driver_run_dir_count"] == 0
        and summary["step93_particle_npy_count"] == 0
        and summary["step93_ggui_screenshot_count"] == 0
        and summary["vtr_file_count"] == 0
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step93 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step93_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step93 artifact manifest finished"
    write_log("logs/step93_artifact_manifest.log", [marker, f"step93_file_count={summary['step93_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step93_artifact_manifest/"):
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
        "step93_related": is_step93_related(rel),
    }


def is_step93_related(path: str) -> bool:
    lower = path.lower()
    return "step93" in lower or lower in {
        "docs/93_taichi_ggui_visualization_enablement_plan_and_guard.md",
    }


def step93_driver_run_dir_count(root: Path) -> int:
    run_root = root / "outputs" / "step93_driver_runs"
    if not run_root.exists():
        return 0
    return sum(1 for path in run_root.iterdir() if path.is_dir())


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not rel.startswith(("outputs/step93_", "logs/step93_")):
            continue
        if path.suffix.lower() not in {".json", ".csv", ".log"}:
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(rel)
    return paths


if __name__ == "__main__":
    main()
