import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_CSV = "benchmarks/public/fluent_fsi_2way_digitized/figure_29_4_structural_point_flap_digitized.csv"
OUTPUT_REFERENCE_CSV = "outputs/step107_public_reference_digitization/figure_29_4_digitized_reference.csv"


def test_step107_public_reference_metadata_matches_fluent_page_boundary():
    metadata = read_json("configs/step107_public_fluent_reference_metadata.json")
    output_metadata = read_json("outputs/step107_public_reference_digitization/public_reference_metadata.json")

    assert metadata == output_metadata
    assert metadata["source_name"] == "Ansys Fluent Tutorial Chapter 29, Modeling Two-Way Fluid-Structure Interaction Within Fluent"
    assert metadata["source_url"] == "https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_tg/flu_tg_fsi_2way.html"
    assert metadata["public_result_figure"] == "Figure 29.4"
    assert metadata["monitor_name"] == "structural-point-flap"
    assert metadata["monitor_quantity"] == "total_displacement"
    assert metadata["monitor_operation"] == "vertex_average"
    assert metadata["monitor_x_m"] == 0.0505
    assert metadata["monitor_y_m"] == 0.0095
    assert metadata["official_steps"] == 50
    assert metadata["official_dt_s"] == 0.0005
    assert metadata["official_final_time_s"] == 0.025
    assert metadata["inlet_velocity_mps"] == 10.0
    assert metadata["material_density"] == 1600.0
    assert metadata["material_youngs_modulus"] == 1000000.0
    assert metadata["material_poisson_ratio"] == 0.47
    assert metadata["official_case_files_used"] is False
    assert metadata["official_png_committed"] is False
    assert metadata["digitized_from_public_plot"] is True
    assert metadata["digitization_uncertainty_m"] > 0.0
    assert metadata["validation_claim_allowed"] is False
    assert metadata["direct_quantitative_equivalence_allowed"] is False


def test_step107_digitized_reference_curve_exists_and_has_required_schema():
    committed_rows = read_csv(REFERENCE_CSV)
    output_rows = read_csv(OUTPUT_REFERENCE_CSV)
    quality = read_json("outputs/step107_public_reference_digitization/digitization_quality_report.json")

    assert committed_rows == output_rows
    assert len(committed_rows) == 51
    assert quality["digitization_quality_pass"] is True
    assert quality["sample_count"] == 51
    assert quality["digitized_from_public_plot"] is True
    assert quality["interpolated_to_official_time_grid"] is True
    assert quality["official_png_committed"] is False
    assert quality["validation_claim_allowed"] is False
    assert quality["direct_quantitative_equivalence_allowed"] is False

    required = {
        "time_s",
        "fluent_public_digitized_total_displacement_m",
        "digitization_uncertainty_m",
        "source_figure",
        "digitization_method",
    }
    assert required.issubset(committed_rows[0].keys())
    times = [float(row["time_s"]) for row in committed_rows]
    values = [float(row["fluent_public_digitized_total_displacement_m"]) for row in committed_rows]
    uncertainty = [float(row["digitization_uncertainty_m"]) for row in committed_rows]

    assert math.isclose(times[0], 0.0, abs_tol=1.0e-12)
    assert math.isclose(times[-1], 0.025, abs_tol=1.0e-12)
    assert all(math.isclose(time, index * 0.0005, abs_tol=1.0e-12) for index, time in enumerate(times))
    assert all(math.isfinite(value) and value >= 0.0 for value in values)
    assert all(math.isfinite(value) and value > 0.0 for value in uncertainty)
    assert max(values) > 3.0e-4
    assert min(values) == 0.0
    assert {row["source_figure"] for row in committed_rows} == {"Figure 29.4"}


def test_step107_reference_loader_reads_committed_curve():
    from src.mpm_lbm.validation.fluent_public_reference import load_public_fluent_reference_curve

    rows = load_public_fluent_reference_curve(ROOT / REFERENCE_CSV)

    assert len(rows) == 51
    assert rows[0]["time_s"] == 0.0
    assert rows[-1]["time_s"] == 0.025
    assert rows[0]["fluent_public_digitized_total_displacement_m"] == 0.0
    assert max(row["fluent_public_digitized_total_displacement_m"] for row in rows) > 3.0e-4


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_csv(path):
    with (ROOT / path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
