import os
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.artifact_utils import scan_artifacts, summarize_artifacts, write_artifact_manifest, write_artifact_summary  # noqa: E402


def main():
    os.chdir(ROOT)
    out_dir = os.path.join(ROOT, "outputs", "step12_artifact_manifest")
    os.makedirs(out_dir, exist_ok=True)

    root_paths = [
        "logs",
        "outputs",
        "STEP*_REPORT.md",
        "docs",
        "paper",
        "configs",
    ]
    rows = scan_artifacts(root_paths=root_paths)
    summary = summarize_artifacts(rows)

    if summary["file_count"] <= 0:
        raise RuntimeError("artifact manifest found no files")
    if summary["total_size_bytes"] <= 0:
        raise RuntimeError("artifact manifest total size is zero")

    manifest_path = os.path.join(out_dir, "artifact_manifest.csv")
    summary_path = os.path.join(out_dir, "artifact_summary.json")
    write_artifact_manifest(rows, manifest_path)
    write_artifact_summary(summary, summary_path)

    print("Step 12 artifact manifest")
    print(f"file_count={summary['file_count']}")
    print(f"total_size_bytes={summary['total_size_bytes']}")
    print(f"total_size_mb={summary['total_size_mb']:.6f}")
    print(f"large_file_count={summary['large_file_count']}")
    print(f"manifest={manifest_path}")
    print(f"summary={summary_path}")
    print("[OK] Step 12 artifact manifest finished")


if __name__ == "__main__":
    main()
