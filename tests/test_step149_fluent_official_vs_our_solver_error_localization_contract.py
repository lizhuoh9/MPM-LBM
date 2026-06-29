import csv
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


BUG_CATEGORIES = {
    "geometry_mapping_error",
    "unit_mapping_error",
    "fluid_boundary_error",
    "structural_model_error",
    "coupling_force_transfer_error",
    "solid_to_fluid_motion_error",
    "time_integration_or_subcycling_error",
    "monitor_extraction_error",
    "numerical_stability_error",
}


def test_step149_missing_official_monitor_is_reported_without_fabricated_metrics(tmp_path):
    import experiments.steps.step149_fluent_official_vs_our_solver_error_localization as step149

    solver_monitor = tmp_path / "solver_monitor.csv"
    write_csv(
        solver_monitor,
        [
            {
                "time_s": 0.0,
                "step": 0,
                "flap_tip_total_displacement_m": 0.0,
                "flap_tip_x_displacement_m": 0.0,
                "flap_tip_y_displacement_m": 0.0,
                "flap_tip_velocity_m_per_s": 0.0,
                "fluid_force_x_n": 0.0,
                "fluid_force_y_n": 0.0,
                "fluid_force_magnitude_n": 0.0,
            }
        ],
    )

    out_dir = tmp_path / "step149_missing"
    summary = step149.run_step149_error_localization(
        official_monitor=tmp_path / "missing_official_monitor.csv",
        solver_monitor=solver_monitor,
        solver_force_monitor=solver_monitor,
        solver_summary=None,
        output_dir=out_dir,
        force=True,
    )

    assert summary["step"] == 149
    assert summary["status"] == "missing_official_monitor"
    assert summary["missing_reason"] == "official_reference_missing"
    assert summary["official_reference_loaded"] is False
    assert summary["solver_monitor_loaded"] is True
    assert summary["error_metrics_present"] is False
    assert summary["solver_bug_hypotheses_present"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["fabricated_metrics_used"] is False
    assert (out_dir / "error_localization_summary.json").is_file()
    assert (out_dir / "report.md").is_file()


def test_step149_synthetic_comparison_computes_metrics_and_hypotheses(tmp_path):
    import experiments.steps.step149_fluent_official_vs_our_solver_error_localization as step149

    official = tmp_path / "official_monitor.csv"
    solver = tmp_path / "solver_monitor.csv"
    write_csv(
        official,
        [
            {
                "time_s": 0.0,
                "flap_tip_total_displacement_m": 0.0,
                "fluid_force_magnitude_n": 0.0,
            },
            {
                "time_s": 0.5,
                "flap_tip_total_displacement_m": 2.0,
                "fluid_force_magnitude_n": 10.0,
            },
            {
                "time_s": 1.0,
                "flap_tip_total_displacement_m": 0.0,
                "fluid_force_magnitude_n": 0.0,
            },
        ],
    )
    write_csv(
        solver,
        [
            {
                "time_s": 0.0,
                "step": 0,
                "flap_tip_total_displacement_m": 0.0,
                "flap_tip_x_displacement_m": 0.0,
                "flap_tip_y_displacement_m": 0.0,
                "flap_tip_velocity_m_per_s": 0.0,
                "fluid_force_x_n": 0.0,
                "fluid_force_y_n": 0.0,
                "fluid_force_magnitude_n": 0.0,
            },
            {
                "time_s": 0.5,
                "step": 1,
                "flap_tip_total_displacement_m": 1.0,
                "flap_tip_x_displacement_m": 0.1,
                "flap_tip_y_displacement_m": 0.9,
                "flap_tip_velocity_m_per_s": 2.0,
                "fluid_force_x_n": 0.0,
                "fluid_force_y_n": 2.0,
                "fluid_force_magnitude_n": 2.0,
            },
            {
                "time_s": 1.0,
                "step": 2,
                "flap_tip_total_displacement_m": 0.2,
                "flap_tip_x_displacement_m": 0.0,
                "flap_tip_y_displacement_m": 0.2,
                "flap_tip_velocity_m_per_s": 1.6,
                "fluid_force_x_n": 0.0,
                "fluid_force_y_n": 0.0,
                "fluid_force_magnitude_n": 0.0,
            },
        ],
    )

    out_dir = tmp_path / "step149_compare"
    summary = step149.run_step149_error_localization(
        official_monitor=official,
        solver_monitor=solver,
        solver_force_monitor=solver,
        solver_summary=None,
        output_dir=out_dir,
        force=True,
    )

    assert summary["step"] == 149
    assert summary["status"] == "comparison_complete"
    assert summary["official_reference_loaded"] is True
    assert summary["solver_monitor_loaded"] is True
    assert summary["error_metrics_present"] is True
    assert summary["solver_bug_hypotheses_present"] is True
    assert summary["interpolation_method"] == "linear_time_overlap"
    assert summary["validation_claim_allowed"] is False

    displacement = read_json(out_dir / "displacement_error_metrics.json")
    assert displacement["sample_count"] == 3
    assert displacement["rms_abs_error_m"] > 0.0
    assert displacement["normalized_rms_error"] > 0.0
    assert -1.0 <= displacement["shape_correlation"] <= 1.0
    assert isinstance(displacement["sign_agreement_fraction"], float)
    assert math.isfinite(displacement["peak_time_error_s"])

    force = read_json(out_dir / "force_error_metrics.json")
    assert force["force_reference_loaded"] is True
    assert force["rms_abs_error_n"] > 0.0
    assert force["impulse_abs_error_n_s"] >= 0.0

    phase = read_json(out_dir / "phase_lag_metrics.json")
    assert phase["status"] == "computed"
    assert math.isfinite(phase["force_displacement_peak_lag_s"])

    hypotheses = read_json(out_dir / "solver_bug_hypotheses.json")
    categories = {item["category"] for item in hypotheses["hypotheses"]}
    assert categories
    assert categories <= BUG_CATEGORIES
    assert hypotheses["next_fix_step_recommended"] == 150

    aligned_rows = read_csv(out_dir / "aligned_monitor_comparison.csv")
    assert aligned_rows
    assert "official_flap_tip_total_displacement_m" in aligned_rows[0]
    assert "solver_flap_tip_total_displacement_m" in aligned_rows[0]


def test_step149_source_defines_full_bug_taxonomy():
    source = (ROOT / "experiments/steps/step149_fluent_official_vs_our_solver_error_localization.py").read_text(
        encoding="utf-8"
    )
    for category in BUG_CATEGORIES:
        assert category in source
    assert "missing_official_monitor" in source
    assert "missing_solver_monitor" in source


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_csv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
