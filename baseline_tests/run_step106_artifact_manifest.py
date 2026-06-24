import os
import re
from pathlib import Path

from step106_common import ROOT, read_json, write_log
from src.mpm_lbm.evidence.step106_common import summary_rows, write_csv_rows, write_json


FIELDS = ["path", "size_bytes", "extension", "step106_related"]
PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def main():
    os.chdir(ROOT)
    policy = read_json("configs/step106_artifact_manifest_policy.json")
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step106_rows = [row for row in rows if row["step106_related"]]
    summary = {
        "artifact_budget_pass": False,
        "file_count": len(rows),
        "large_file_count": sum(
            1 for row in step106_rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"])
        ),
        "private_absolute_path_count": len(private_absolute_path_rows(ROOT)),
        "step106_ansys_proprietary_file_count": sum(1 for row in step106_rows if is_official_file(row, policy)),
        "step106_driver_run_dir_count": int(
            (ROOT / "outputs/step106_driver_runs/fluent_duct_flap_proxy_48_20step_outlet_repair_regression_smoke").is_dir()
        ),
        "step106_file_count": len(step106_rows),
        "step106_total_size_bytes": sum(int(row["size_bytes"]) for row in step106_rows),
        "step106_total_size_mb": sum(int(row["size_bytes"]) for row in step106_rows) / (1024.0 * 1024.0),
    }
    summary["artifact_budget_pass"] = bool(
        summary["step106_file_count"] <= int(policy["max_step106_file_count"])
        and summary["step106_total_size_mb"] < float(policy["max_step106_total_size_mb"])
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["step106_ansys_proprietary_file_count"] == 0
        and summary["step106_driver_run_dir_count"] == 1
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step106 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step106_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "artifact_manifest.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step106 artifact manifest finished"
    write_log("logs/step106_artifact_manifest.log", [marker, f"step106_file_count={summary['step106_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step106_artifact_manifest/"):
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
        "step106_related": is_step106_related(rel),
    }


def is_step106_related(path: str) -> bool:
    lower = path.lower()
    return "step106" in lower or lower in {
        "docs/106_fluent_duct_flap_proxy_outlet_boundary_flow_propagation_repair.md",
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
        if not rel.startswith(("outputs/step106_", "logs/step106_")):
            continue
        if path.suffix.lower() not in {".json", ".csv", ".log"}:
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(rel)
    return paths


if __name__ == "__main__":
    main()
