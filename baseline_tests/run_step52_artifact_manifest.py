import os
from pathlib import Path

from step52_common import ROOT, summary_rows, write_csv_rows, write_json, write_log


SUMMARY_FIELDS = ["metric", "value"]
MANIFEST_FIELDS = ["path", "size_bytes", "extension", "step52_related"]
LARGE_FILE_THRESHOLD_BYTES = 100 * 1024 * 1024


def main():
    os.chdir(ROOT)
    rows, summary = build_manifest()
    if not summary["artifact_budget_pass"]:
        raise RuntimeError(f"Step 52 artifact budget failed: {summary}")
    out_dir = ROOT / "outputs" / "step52_artifact_manifest"
    write_csv_rows(out_dir / "artifact_manifest.csv", rows, MANIFEST_FIELDS)
    write_csv_rows(out_dir / "artifact_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "artifact_summary.json", summary)
    marker = "[OK] Step 52 artifact manifest finished"
    write_log("logs/step52_artifact_manifest.log", [marker, f"file_count={summary['file_count']}", f"step52_total_size_mb={summary['step52_total_size_mb']}"])
    print(f"file_count={summary['file_count']}")
    print(marker)


def build_manifest():
    files = list(repo_files(ROOT))
    rows = [manifest_row(path) for path in files]
    step52 = [row for row in rows if row["step52_related"]]
    summary = {
        "file_count": len(rows),
        "step52_file_count": len(step52),
        "total_size_bytes": sum(int(row["size_bytes"]) for row in rows),
        "total_size_mb": sum(int(row["size_bytes"]) for row in rows) / (1024.0 * 1024.0),
        "step52_total_size_bytes": sum(int(row["size_bytes"]) for row in step52),
        "step52_total_size_mb": sum(int(row["size_bytes"]) for row in step52) / (1024.0 * 1024.0),
        "large_file_count": sum(1 for row in step52 if int(row["size_bytes"]) > LARGE_FILE_THRESHOLD_BYTES),
        "step52_vtr_count": sum(1 for row in step52 if row["extension"] == ".vtr"),
        "step52_particle_npy_count": sum(1 for row in step52 if row["extension"] == ".npy" and "particle" in row["path"].lower()),
        "step52_displaced_particle_output_count": sum(1 for row in step52 if "displaced_particle" in row["path"].lower()),
        "step52_dense_displacement_output_count": sum(1 for row in step52 if "dense_displacement" in row["path"].lower()),
        "raw_candidate_large_file_count": sum(1 for row in rows if "real_geometry_candidates" in row["path"].lower() and int(row["size_bytes"]) > LARGE_FILE_THRESHOLD_BYTES),
        "scan_data_file_count": sum(1 for row in rows if "scan" in row["path"].lower() and is_step52_related(row["path"])),
        "private_absolute_path_count": private_absolute_path_count(files),
        "geo_all_fluid_dat_count_added": sum(1 for row in step52 if Path(row["path"]).name.startswith("geo_all_fluid_") and row["extension"] == ".dat"),
    }
    summary["artifact_budget_pass"] = bool(
        int(summary["large_file_count"]) == 0
        and float(summary["step52_total_size_mb"]) < 10.0
        and float(summary["total_size_mb"]) < 400.0
        and int(summary["step52_vtr_count"]) == 0
        and int(summary["step52_particle_npy_count"]) == 0
        and int(summary["step52_displaced_particle_output_count"]) == 0
        and int(summary["step52_dense_displacement_output_count"]) == 0
        and int(summary["raw_candidate_large_file_count"]) == 0
        and int(summary["scan_data_file_count"]) == 0
        and int(summary["private_absolute_path_count"]) == 0
        and int(summary["geo_all_fluid_dat_count_added"]) == 0
    )
    return rows, summary


def repo_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.parts)
        if ".git" in parts or "__pycache__" in parts:
            continue
        yield path


def manifest_row(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    return {
        "path": rel,
        "size_bytes": int(path.stat().st_size),
        "extension": path.suffix.lower(),
        "step52_related": is_step52_related(rel),
    }


def is_step52_related(path: str) -> bool:
    lower = path.lower()
    return "step52" in lower or lower.startswith("docs/52_")


def private_absolute_path_count(files) -> int:
    count = 0
    windows_user_marker = "C:" + "\\Users\\"
    slash_user_marker = "C:" + "/Users/"
    for path in files:
        if path.suffix.lower() not in {".py", ".json", ".csv", ".md", ".log", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if windows_user_marker in text or slash_user_marker in text:
            count += 1
    return count


if __name__ == "__main__":
    main()
