import json
import os
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.artifact_utils import scan_artifacts, summarize_artifacts, write_artifact_manifest, write_artifact_summary  # noqa: E402


STEP19_SCALE_CONFIGS = [
    "configs/step19_long_box_48_link_area.json",
    "configs/step19_long_squid_proxy_48_link_area.json",
    "configs/step19_feasibility_64_link_area_box.json",
    "configs/step19_compare_64_engineering_vs_link_area.json",
]


def _check_config_exports_disabled():
    for relative_path in STEP19_SCALE_CONFIGS:
        with open(os.path.join(ROOT, relative_path), "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("write_vtk") is not False or data.get("write_particles") is not False:
            raise RuntimeError(f"{relative_path} must disable heavy outputs")

    with open(
        os.path.join(ROOT, "configs", "step19_compare_48_long_engineering_vs_link_area.json"),
        "r",
        encoding="utf-8",
    ) as f:
        nested = json.load(f)
    for name, data in nested.items():
        if data.get("write_vtk") is not False or data.get("write_particles") is not False:
            raise RuntimeError(f"step19_compare_48 {name} must disable heavy outputs")


def main():
    os.chdir(ROOT)
    _check_config_exports_disabled()
    out_dir = os.path.join(ROOT, "outputs", "step19_artifact_manifest")
    os.makedirs(out_dir, exist_ok=True)

    rows = scan_artifacts(
        root_paths=[
            "logs",
            "outputs",
            "STEP*_REPORT.md",
            "docs",
            "paper",
            "configs",
        ]
    )
    summary = summarize_artifacts(rows)
    if summary["file_count"] <= 0:
        raise RuntimeError("artifact manifest found no files")
    if summary["total_size_bytes"] <= 0:
        raise RuntimeError("artifact manifest total size is zero")
    if summary["large_file_count"] != 0:
        raise RuntimeError("Step 19 artifact manifest found large files")

    manifest_path = os.path.join(out_dir, "artifact_manifest.csv")
    summary_path = os.path.join(out_dir, "artifact_summary.json")
    write_artifact_manifest(rows, manifest_path)
    write_artifact_summary(summary, summary_path)

    print("Step 19 artifact manifest")
    print(f"file_count={summary['file_count']}")
    print(f"total_size_bytes={summary['total_size_bytes']}")
    print(f"total_size_mb={summary['total_size_mb']:.6f}")
    print(f"large_file_count={summary['large_file_count']}")
    print(f"manifest={manifest_path}")
    print(f"summary={summary_path}")
    print("[OK] Step 19 artifact manifest finished")


if __name__ == "__main__":
    main()
