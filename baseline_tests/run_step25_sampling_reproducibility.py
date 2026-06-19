import math
import os

from step25_common import ROOT, STEP25_DESCRIPTORS, write_csv_rows, write_json, write_log
from src.geometry_intake import run_candidate_sampling_reproducibility


FIELDS = [
    "candidate_id",
    "geometry_type",
    "particle_count_first",
    "particle_count_second",
    "geometry_volume_first",
    "geometry_volume_second",
    "mass_sum_first",
    "mass_sum_second",
    "sampled_position_hash_first",
    "sampled_position_hash_second",
    "vol0_hash_first",
    "vol0_hash_second",
    "mass_hash_first",
    "mass_hash_second",
    "relative_mass_error",
    "reproducibility_pass",
]


def main():
    os.chdir(ROOT)
    out_dir = ROOT / "outputs" / "step25_sampling_reproducibility"
    rows = [run_candidate_sampling_reproducibility(path, out_dir) for path in STEP25_DESCRIPTORS]
    for row in rows:
        _assert_sampling_row(row)

    write_csv_rows(out_dir / "sampling_reproducibility.csv", rows, FIELDS)
    write_json(out_dir / "sampling_reproducibility.json", {"row_count": len(rows), "rows": rows})
    marker = "[OK] Step 25 sampling reproducibility finished"
    write_log("logs/step25_sampling_reproducibility.log", [marker, f"row_count={len(rows)}"])
    print(f"row_count={len(rows)}")
    print(marker)


def _assert_sampling_row(row):
    if row["particle_count_first"] != row["particle_count_second"]:
        raise RuntimeError(f"particle count changed across deterministic sampling: {row}")
    if row["geometry_volume_first"] != row["geometry_volume_second"]:
        raise RuntimeError(f"geometry volume changed across deterministic sampling: {row}")
    if row["mass_sum_first"] != row["mass_sum_second"]:
        raise RuntimeError(f"mass sum changed across deterministic sampling: {row}")
    if row["sampled_position_hash_first"] != row["sampled_position_hash_second"]:
        raise RuntimeError(f"sampled positions are not reproducible: {row}")
    if row["vol0_hash_first"] != row["vol0_hash_second"]:
        raise RuntimeError(f"vol0 is not reproducible: {row}")
    if row["mass_hash_first"] != row["mass_hash_second"]:
        raise RuntimeError(f"mass array is not reproducible: {row}")
    if not math.isfinite(float(row["relative_mass_error"])):
        raise RuntimeError(f"relative mass error is not finite: {row}")
    if row["reproducibility_pass"] is not True:
        raise RuntimeError(f"sampling reproducibility failed: {row}")


if __name__ == "__main__":
    main()
