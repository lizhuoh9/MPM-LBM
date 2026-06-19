import os

from step26_common import ROOT, STEP26_DESCRIPTORS, write_csv_rows, write_json, write_log
from src.geometry_candidate_manifest import candidate_manifest_row


FIELDS = [
    "candidate_id",
    "geometry_type",
    "source_file_redacted",
    "sha256",
    "step25_sha256",
    "size_bytes",
    "step25_size_bytes",
    "validation_scope",
    "quality_check_enabled",
    "quality_check_strict",
    "sha256_matches_step25",
    "size_matches_step25",
    "fingerprint_match",
    "no_private_absolute_path",
    "guard_pass",
]


def main():
    os.chdir(ROOT)
    step25_manifest = {
        row["candidate_id"]: row
        for row in _load_step25_manifest()["rows"]
    }
    rows = []
    for descriptor_path in STEP26_DESCRIPTORS:
        current = candidate_manifest_row(descriptor_path, root=ROOT)
        accepted = step25_manifest[current["candidate_id"]]
        row = {
            "candidate_id": current["candidate_id"],
            "geometry_type": current["geometry_type"],
            "source_file_redacted": current["source_file_redacted"],
            "sha256": current["sha256"],
            "step25_sha256": accepted["sha256"],
            "size_bytes": int(current["size_bytes"]),
            "step25_size_bytes": int(accepted["size_bytes"]),
            "validation_scope": current["validation_scope"],
            "quality_check_enabled": bool(current["quality_check_enabled"]),
            "quality_check_strict": bool(current["quality_check_strict"]),
            "sha256_matches_step25": current["sha256"] == accepted["sha256"],
            "size_matches_step25": int(current["size_bytes"]) == int(accepted["size_bytes"]),
            "no_private_absolute_path": ":" not in current["source_file_redacted"]
            and "\\Users\\" not in current["source_file_redacted"],
        }
        row["fingerprint_match"] = bool(row["sha256_matches_step25"] and row["size_matches_step25"])
        row["guard_pass"] = bool(
            row["fingerprint_match"]
            and row["quality_check_enabled"]
            and row["quality_check_strict"]
            and row["validation_scope"] == "intake_qa_normalization_sampling_projection_only"
            and row["no_private_absolute_path"]
        )
        rows.append(row)

    if len(rows) != 2 or not all(row["guard_pass"] for row in rows):
        raise RuntimeError(f"Step 26 fingerprint guard failed: {rows}")

    out_dir = ROOT / "outputs" / "step26_candidate_fingerprint_guard"
    write_csv_rows(out_dir / "fingerprint_guard.csv", rows, FIELDS)
    write_json(
        out_dir / "fingerprint_guard.json",
        {"row_count": len(rows), "pass_count": sum(1 for row in rows if row["guard_pass"]), "rows": rows},
    )
    marker = "[OK] Step 26 candidate fingerprint guard finished"
    write_log(
        "logs/step26_candidate_fingerprint_guard.log",
        [marker, f"row_count={len(rows)}", f"pass_count={sum(1 for row in rows if row['guard_pass'])}"],
    )
    print(f"row_count={len(rows)}")
    print(marker)


def _load_step25_manifest():
    import json

    with (ROOT / "outputs/step25_candidate_manifest/candidate_manifest.json").open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
