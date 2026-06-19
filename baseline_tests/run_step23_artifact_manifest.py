import json
import os
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.artifact_utils import scan_artifacts, summarize_artifacts, write_artifact_manifest, write_artifact_summary  # noqa: E402


STEP23_DRIVER_CONFIGS = [
    "configs/step23_quality_gated_voxel_sphere_48_none.json",
    "configs/step23_quality_gated_voxel_sphere_48_penalty.json",
    "configs/step23_quality_gated_voxel_sphere_48_moving_boundary.json",
    "configs/step23_quality_gated_voxel_sphere_48_link_area.json",
    "configs/step23_quality_gated_mesh_cube_48_none.json",
    "configs/step23_quality_gated_mesh_cube_48_penalty.json",
    "configs/step23_quality_gated_mesh_cube_48_moving_boundary.json",
    "configs/step23_quality_gated_mesh_cube_48_link_area.json",
    "configs/step23_quality_gated_mesh_ellipsoid_48_none.json",
    "configs/step23_quality_gated_mesh_ellipsoid_48_penalty.json",
    "configs/step23_quality_gated_mesh_ellipsoid_48_moving_boundary.json",
    "configs/step23_quality_gated_mesh_ellipsoid_48_link_area.json",
    "configs/step23_quality_gated_voxel_sphere_64_penalty.json",
    "configs/step23_quality_gated_voxel_sphere_64_moving_boundary.json",
    "configs/step23_quality_gated_mesh_cube_64_penalty.json",
]


def _check_driver_configs_disable_heavy_outputs():
    for relative_path in STEP23_DRIVER_CONFIGS:
        with open(os.path.join(ROOT, relative_path), "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("quality_check_enabled") is not True:
            raise RuntimeError(f"{relative_path} must enable quality_check_enabled")
        if data.get("quality_check_strict") is not False:
            raise RuntimeError(f"{relative_path} must keep quality_check_strict=false")
        if data.get("write_vtk") is not False or data.get("write_particles") is not False:
            raise RuntimeError(f"{relative_path} must disable heavy outputs")


def _check_quality_report_sizes():
    roots = [
        "outputs/step23_quality_gated_voxel_sphere_48_modes",
        "outputs/step23_quality_gated_mesh_cube_48_modes",
        "outputs/step23_quality_gated_mesh_ellipsoid_48_modes",
        "outputs/step23_quality_gated_imported_geometry_64_feasibility",
    ]
    report_count = 0
    for root in roots:
        root_path = os.path.join(ROOT, root)
        if not os.path.isdir(root_path):
            raise RuntimeError(f"missing Step 23 output root: {root}")
        for dirpath, _, filenames in os.walk(root_path):
            if "geometry_quality_report.json" not in filenames:
                continue
            path = os.path.join(dirpath, "geometry_quality_report.json")
            report_count += 1
            if os.path.getsize(path) >= 100_000:
                raise RuntimeError(f"quality report is unexpectedly large: {path}")
    if report_count < 15:
        raise RuntimeError(f"expected at least 15 quality reports, got {report_count}")


def _check_fixture_sizes():
    fixture_dir = os.path.join(ROOT, "data", "geometry_fixtures")
    for name in ["voxel_sphere.npy", "cube.obj", "ellipsoid_proxy.obj", "voxel_sphere_metadata.json"]:
        path = os.path.join(fixture_dir, name)
        if not os.path.isfile(path):
            raise RuntimeError(f"missing fixture: {path}")
        if os.path.getsize(path) >= 200_000:
            raise RuntimeError(f"fixture is too large for Step 23: {path}")


def main():
    os.chdir(ROOT)
    _check_driver_configs_disable_heavy_outputs()
    _check_quality_report_sizes()
    _check_fixture_sizes()
    out_dir = os.path.join(ROOT, "outputs", "step23_artifact_manifest")
    os.makedirs(out_dir, exist_ok=True)

    rows = scan_artifacts(
        root_paths=[
            "logs",
            "outputs",
            "STEP*_REPORT.md",
            "STEP*_GOAL.md",
            "docs",
            "paper",
            "configs",
            "data/geometry_fixtures",
        ]
    )
    summary = summarize_artifacts(rows)
    if summary["file_count"] <= 0:
        raise RuntimeError("artifact manifest found no files")
    if summary["total_size_bytes"] <= 0:
        raise RuntimeError("artifact manifest total size is zero")
    if summary["large_file_count"] != 0:
        raise RuntimeError("Step 23 artifact manifest found large files")

    manifest_path = os.path.join(out_dir, "artifact_manifest.csv")
    summary_path = os.path.join(out_dir, "artifact_summary.json")
    write_artifact_manifest(rows, manifest_path)
    write_artifact_summary(summary, summary_path)

    print("Step 23 artifact manifest")
    print(f"file_count={summary['file_count']}")
    print(f"total_size_bytes={summary['total_size_bytes']}")
    print(f"total_size_mb={summary['total_size_mb']:.6f}")
    print(f"large_file_count={summary['large_file_count']}")
    print("[OK] Step 23 artifact manifest finished")


if __name__ == "__main__":
    main()
