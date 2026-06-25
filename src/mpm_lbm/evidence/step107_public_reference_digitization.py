from __future__ import annotations

import shutil
from pathlib import Path

from src.mpm_lbm.evidence.step107_common import (
    ALLOWED_CLAIM,
    read_csv_rows,
    read_json,
    reset_output_dir,
    summary_rows,
    write_csv_rows,
    write_json,
)


def build_step107_public_reference_digitization(
    root: Path,
    policy_path: str = "configs/step107_digitization_policy.json",
) -> tuple[dict, dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    metadata = read_json(root / policy["metadata_path"])
    reference_rows = read_csv_rows(root / policy["digitized_reference_csv"])
    quality = digitization_quality_report(metadata, reference_rows, policy)
    if not quality["digitization_quality_pass"]:
        raise RuntimeError(f"Step107 public reference digitization failed: {quality}")
    out_dir = root / policy["output_dir"]
    reset_output_dir(out_dir, root / "outputs")
    write_json(out_dir / "public_reference_metadata.json", metadata)
    shutil.copy2(root / policy["digitized_reference_csv"], out_dir / "figure_29_4_digitized_reference.csv")
    write_json(out_dir / "digitization_quality_report.json", quality)
    write_csv_rows(out_dir / "digitization_quality_summary.csv", summary_rows(quality), ["metric", "value"])
    return metadata, quality


def digitization_quality_report(metadata: dict, rows: list[dict], policy: dict) -> dict:
    required_columns = set(policy["required_columns"])
    columns_present = set(rows[0].keys()) if rows else set()
    times = [float(row["time_s"]) for row in rows] if rows else []
    values = [float(row["fluent_public_digitized_total_displacement_m"]) for row in rows] if rows else []
    uncertainty = [float(row["digitization_uncertainty_m"]) for row in rows] if rows else []
    expected_count = int(policy["expected_sample_count"])
    expected_final = float(policy["official_final_time_s"])
    expected_dt = float(policy["official_dt_s"])
    quality = {
        "allowed_claim": ALLOWED_CLAIM,
        "columns_present": sorted(columns_present),
        "digitization_method": policy["digitization_method"],
        "digitization_quality_pass": False,
        "digitized_from_public_plot": bool(metadata["digitized_from_public_plot"]),
        "direct_quantitative_equivalence_allowed": False,
        "interpolated_to_official_time_grid": bool(policy["interpolated_to_official_time_grid"]),
        "max_displacement_m": max(values) if values else 0.0,
        "min_displacement_m": min(values) if values else 0.0,
        "official_png_committed": bool(metadata["official_png_committed"]),
        "sample_count": len(rows),
        "time_end_s": times[-1] if times else None,
        "time_start_s": times[0] if times else None,
        "uncertainty_max_m": max(uncertainty) if uncertainty else 0.0,
        "uncertainty_min_m": min(uncertainty) if uncertainty else 0.0,
        "validation_claim_allowed": False,
    }
    time_grid_ok = bool(
        len(times) == expected_count
        and all(abs(time - index * expected_dt) <= 1.0e-12 for index, time in enumerate(times))
        and abs(times[-1] - expected_final) <= 1.0e-12
    )
    quality["digitization_quality_pass"] = bool(
        rows
        and required_columns.issubset(columns_present)
        and len(rows) == expected_count
        and time_grid_ok
        and values
        and min(values) >= 0.0
        and max(values) > 3.0e-4
        and uncertainty
        and min(uncertainty) > 0.0
        and quality["digitized_from_public_plot"]
        and quality["interpolated_to_official_time_grid"]
        and not quality["official_png_committed"]
        and not quality["direct_quantitative_equivalence_allowed"]
        and not quality["validation_claim_allowed"]
    )
    return quality
