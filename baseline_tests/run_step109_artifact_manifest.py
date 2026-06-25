import os
import re
from pathlib import Path

from step109_common import ROOT, read_json, write_log
from src.mpm_lbm.evidence.step109_common import summary_rows, write_csv_rows, write_json


FIELDS = ["path", "size_bytes", "extension", "step109_related"]
PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def main():
    os.chdir(ROOT)
    policy = read_json("configs/step109_artifact_manifest_policy.json")
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step109_rows = [row for row in rows if row["step109_related"]]
    summary = {
        "artifact_budget_pass": False,
        "artifact_manifest_pass": False,
        "file_count": len(rows),
        "large_file_count": sum(
            1 for row in step109_rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"])
        ),
        "private_absolute_path_count": len(private_absolute_path_rows(ROOT)),
        "step109_ansys_proprietary_file_count": sum(1 for row in step109_rows if is_official_file(row, policy)),
        "step109_driver_run_dir_count": count_step109_driver_run_dirs(ROOT),
        "step109_file_count": len(step109_rows),
        "step109_official_image_count": sum(1 for row in step109_rows if row["extension"] in {".png", ".jpg", ".jpeg", ".svg"}),
        "step109_total_size_bytes": sum(int(row["size_bytes"]) for row in step109_rows),
        "step109_total_size_mb": sum(int(row["size_bytes"]) for row in step109_rows) / (1024.0 * 1024.0),
    }
    summary["artifact_budget_pass"] = bool(
        summary["step109_file_count"] <= int(policy["max_step109_file_count"])
        and summary["step109_total_size_mb"] < float(policy["max_step109_total_size_mb"])
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["step109_ansys_proprietary_file_count"] == 0
        and summary["step109_official_image_count"] == 0
        and summary["step109_driver_run_dir_count"] >= 5
    )
    summary["artifact_manifest_pass"] = bool(summary["artifact_budget_pass"])
    if not summary["artifact_manifest_pass"]:
        raise RuntimeError(f"Step109 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step109_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "artifact_manifest.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step109 artifact manifest finished"
    write_log("logs/step109_artifact_manifest.log", [marker, f"step109_file_count={summary['step109_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step109_artifact_manifest/"):
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
        "step109_related": is_step109_related(rel),
    }


def is_step109_related(path: str) -> bool:
    lower = path.lower()
    return "step109" in lower or lower in {
        "docs/109_fluent_duct_flap_fsi_response_amplitude_sensitivity_matrix.md",
    }


def is_official_file(row: dict, policy: dict) -> bool:
    lower = row["path"].lower()
    names = set(name.lower() for name in policy["official_file_names"])
    return Path(lower).name in names


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not rel.startswith(("outputs/step109_", "logs/step109_")):
            continue
        if path.suffix.lower() not in {".json", ".csv", ".log"}:
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(rel)
    return paths


def count_step109_driver_run_dirs(root: Path) -> int:
    run_root = root / "outputs" / "step109_driver_runs"
    if not run_root.is_dir():
        return 0
    return sum(1 for path in run_root.iterdir() if path.is_dir() and (path / "flap_tip_displacement_timeseries.csv").is_file())


if __name__ == "__main__":
    main()
