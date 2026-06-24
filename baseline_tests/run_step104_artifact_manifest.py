import os
import re
from pathlib import Path

from step104_common import ROOT, read_json, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["path", "size_bytes", "extension", "step104_related"]
PRIVATE_ABSOLUTE_RE = re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+|D:[\\/]+working[\\/]+)")


def main():
    os.chdir(ROOT)
    policy = read_json("configs/step104_artifact_manifest_policy.json")
    rows = [manifest_row(path) for path in repo_files(ROOT)]
    step104_rows = [row for row in rows if row["step104_related"]]
    summary = {
        "artifact_budget_pass": False,
        "file_count": len(rows),
        "large_file_count": sum(
            1 for row in step104_rows if int(row["size_bytes"]) > int(policy["large_file_threshold_bytes"])
        ),
        "private_absolute_path_count": len(private_absolute_path_rows(ROOT)),
        "step104_ansys_proprietary_file_count": sum(
            1 for row in step104_rows if is_official_file(row, policy)
        ),
        "step104_driver_run_dir_count": int(
            (ROOT / "outputs/step104_driver_runs/fluent_duct_flap_setup_repair_48_5step_smoke").is_dir()
        ),
        "step104_file_count": len(step104_rows),
        "step104_total_size_bytes": sum(int(row["size_bytes"]) for row in step104_rows),
        "step104_total_size_mb": sum(int(row["size_bytes"]) for row in step104_rows) / (1024.0 * 1024.0),
    }
    summary["artifact_budget_pass"] = bool(
        summary["step104_file_count"] <= int(policy["max_step104_file_count"])
        and summary["step104_total_size_mb"] < float(policy["max_step104_total_size_mb"])
        and summary["large_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
        and summary["step104_ansys_proprietary_file_count"] == 0
        and summary["step104_driver_run_dir_count"] == 1
    )
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step104 artifact manifest failed: {summary}")
    out_dir = ROOT / "outputs" / "step104_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "artifact_manifest.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step104 artifact manifest finished"
    write_log("logs/step104_artifact_manifest.log", [marker, f"step104_file_count={summary['step104_file_count']}"])
    print(marker)


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("outputs/step104_artifact_manifest/"):
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
        "step104_related": is_step104_related(rel),
    }


def is_step104_related(path: str) -> bool:
    lower = path.lower()
    return "step104" in lower or lower in {
        "docs/104_fluent_duct_flap_official_problem_setup_repair.md",
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
        if not rel.startswith(("outputs/step104_", "logs/step104_")):
            continue
        if path.suffix.lower() not in {".json", ".csv", ".log"}:
            continue
        if PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(rel)
    return paths


if __name__ == "__main__":
    main()
