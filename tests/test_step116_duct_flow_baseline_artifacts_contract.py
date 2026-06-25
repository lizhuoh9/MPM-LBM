import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "outputs/step116_regularized_lbm_duct_flow_baseline"


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_step116_committed_solver_report_and_matrix_are_simulation_backed():
    report = _read_json(OUTPUT_DIR / "solver_report.json")
    matrix = _read_json(OUTPUT_DIR / "run_matrix_summary.json")

    assert report["step"] == 116
    assert report["simulation_backed_artifacts"] is True
    assert report["fluent_validation_claim_allowed"] is False
    assert report["full_fsi_rerun_done"] is False
    assert report["regularized_velocity_pressure_used"] is True
    assert matrix["step"] == 116
    assert len(matrix["runs"]) >= 4
    assert any(row["name"] == "duct_only_48_regularized_boundary_500step" for row in matrix["runs"])


def test_step116_each_committed_run_has_required_artifact_schema():
    matrix = _read_json(OUTPUT_DIR / "run_matrix_summary.json")

    for row in matrix["runs"]:
        row_dir = OUTPUT_DIR / row["name"]
        metadata = _read_json(row_dir / "run_metadata.json")
        finite = _read_json(row_dir / "finite_stability_report.json")
        boundary = _read_json(row_dir / "duct_boundary_condition_report.json")

        assert "lbm_open_boundary_semantics" in metadata
        assert metadata["full_fsi_rerun_done"] is False
        assert boundary["boundary_condition_equivalence_claim_allowed"] is False
        assert boundary["validation_claim_allowed"] is False
        assert "finite_pass" in finite
        assert "density_gate_pass" in finite
        assert "flux_balance_reported" in finite

        if not finite.get("skipped_due_to_tau_margin", False):
            with (row_dir / "fluid_diagnostics_timeseries.csv").open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                assert {
                    "step",
                    "rho_min",
                    "rho_max",
                    "rho_mean",
                    "mass_total",
                    "mass_total_delta_rel",
                    "inlet_flux",
                    "outlet_flux",
                    "flux_imbalance_abs",
                    "flux_imbalance_rel",
                    "max_v",
                    "mach_proxy_observed",
                }.issubset(reader.fieldnames)
                assert list(reader)


def test_step116_static_flap_artifact_answers_scope_questions():
    matrix = _read_json(OUTPUT_DIR / "run_matrix_summary.json")
    static_rows = [row for row in matrix["runs"] if row["geometry_mode"] == "static_two_flap"]
    assert static_rows

    row_dir = OUTPUT_DIR / static_rows[0]["name"]
    flap = _read_json(row_dir / "flap_region_flow_summary.json")
    throat = _read_json(row_dir / "throat_speed_summary.json")
    recirculation = _read_json(row_dir / "recirculation_proxy_summary.json")

    assert flap["static_flap_fluid_only"] is True
    assert flap["full_fsi_rerun_done"] is False
    assert throat["finite_pass"] in (True, False)
    assert recirculation["proxy_name"] == "negative_ux_fraction_near_flaps"
