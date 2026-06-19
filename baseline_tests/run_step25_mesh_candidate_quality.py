import os

from step25_common import ROOT, STEP25_DESCRIPTORS, load_json, write_csv_rows, write_json, write_log
from src.geometry_intake import run_candidate_quality_check


FIELDS = [
    "candidate_id",
    "geometry_type",
    "quality_kind",
    "quality_pass",
    "quality_severity",
    "quality_warnings_count",
    "quality_reasons_count",
    "quality_report_path",
    "vertices_count",
    "faces_count",
    "has_valid_face_indices",
    "degenerate_face_count",
    "boundary_edge_count",
    "nonmanifold_edge_count",
]


def main():
    os.chdir(ROOT)
    out_dir = ROOT / "outputs" / "step25_mesh_candidate_quality"
    rows = []
    for path in STEP25_DESCRIPTORS:
        descriptor = load_json(path)
        if descriptor["geometry_type"] == "mesh":
            row = run_candidate_quality_check(path, out_dir / descriptor["candidate_id"])
            _assert_mesh_row(row)
            rows.append(row)
    if not rows:
        raise RuntimeError("no Step 25 mesh candidate quality rows")

    write_csv_rows(out_dir / "mesh_candidate_quality.csv", rows, FIELDS)
    write_json(out_dir / "mesh_candidate_quality.json", {"row_count": len(rows), "rows": rows})
    marker = "[OK] Step 25 mesh candidate quality finished"
    write_log("logs/step25_mesh_candidate_quality.log", [marker, f"row_count={len(rows)}"])
    print(f"row_count={len(rows)}")
    print(marker)


def _assert_mesh_row(row):
    if row["vertices_count"] <= 0 or row["faces_count"] <= 0:
        raise RuntimeError(f"mesh quality row has no geometry: {row}")
    if row["has_valid_face_indices"] is not True:
        raise RuntimeError(f"mesh face indices are invalid: {row}")
    if row["degenerate_face_count"] != 0:
        raise RuntimeError(f"mesh has degenerate faces: {row}")
    if row["boundary_edge_count"] != 0:
        raise RuntimeError(f"mesh has boundary edges: {row}")
    if row["nonmanifold_edge_count"] != 0:
        raise RuntimeError(f"mesh has nonmanifold edges: {row}")
    if row["quality_pass"] is not True or row["quality_severity"] != "ok":
        raise RuntimeError(f"mesh strict quality gate failed: {row}")


if __name__ == "__main__":
    main()
