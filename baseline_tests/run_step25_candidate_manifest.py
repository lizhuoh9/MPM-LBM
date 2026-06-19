import os

from step25_common import ROOT, STEP25_DESCRIPTORS, write_log
from src.geometry_candidate_manifest import candidate_manifest_row, write_candidate_manifest


def main():
    os.chdir(ROOT)
    rows = [candidate_manifest_row(path, root=ROOT) for path in STEP25_DESCRIPTORS]
    candidate_ids = [row["candidate_id"] for row in rows]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise RuntimeError(f"duplicate Step 25 candidate IDs: {candidate_ids}")
    if any(row["geometry_type"] not in {"mesh", "voxel"} for row in rows):
        raise RuntimeError(f"unexpected geometry type in manifest: {rows}")
    if any(row["manifest_pass"] is not True for row in rows):
        raise RuntimeError(f"candidate manifest failed: {rows}")
    if any(row["is_large"] and row["commit_policy"] == "small_controlled_fixture_allowed" for row in rows):
        raise RuntimeError(f"large committed smoke candidate found: {rows}")

    out_dir = ROOT / "outputs" / "step25_candidate_manifest"
    write_candidate_manifest(
        rows,
        out_dir / "candidate_manifest.csv",
        out_dir / "candidate_manifest.json",
    )
    marker = "[OK] Step 25 candidate manifest finished"
    write_log(
        "logs/step25_candidate_manifest.log",
        [
            marker,
            f"row_count={len(rows)}",
            f"candidate_ids={','.join(candidate_ids)}",
        ],
    )
    print(f"row_count={len(rows)}")
    print(marker)


if __name__ == "__main__":
    main()
