import csv
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _runner_tmp(name: str) -> Path:
    path = ROOT / "outputs/tmp/step116_runner_contract" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_step116_tiny_legacy_and_regularized_runner_emit_diagnostics():
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import Step116RunSpec, run_step116_matrix

    output_dir = _runner_tmp("tiny_legacy_regularized")
    specs = [
        Step116RunSpec(
            name="tiny_legacy",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=5,
            open_boundary_semantics="equilibrium_all_population_reset",
            geometry_mode="duct_only",
        ),
        Step116RunSpec(
            name="tiny_regularized",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=5,
            open_boundary_semantics="regularized_velocity_pressure",
            geometry_mode="duct_only",
        ),
    ]

    summary = run_step116_matrix(output_dir, specs=specs, force=True)

    assert len(summary["runs"]) == 2
    for row in summary["runs"]:
        row_dir = output_dir / row["name"]
        metadata = _read_json(row_dir / "run_metadata.json")
        finite = _read_json(row_dir / "finite_stability_report.json")
        boundary = _read_json(row_dir / "duct_boundary_condition_report.json")

        assert metadata["lbm_open_boundary_semantics"] in (
            "equilibrium_all_population_reset",
            "regularized_velocity_pressure",
        )
        assert metadata["full_fsi_rerun_done"] is False
        assert boundary["validation_claim_allowed"] is False
        assert finite["finite_pass"] is True
        assert finite["flux_balance_reported"] is True

        with (row_dir / "fluid_diagnostics_timeseries.csv").open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            assert {"step", "rho_min", "rho_max", "mass_total", "flux_imbalance_rel"}.issubset(reader.fieldnames)
            rows = list(reader)
            assert rows


def test_step116_runner_skips_strict_tau_margin_before_stepping():
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import Step116RunSpec, run_step116_matrix

    output_dir = _runner_tmp("strict_tau_skip")
    spec = Step116RunSpec(
        name="tiny_strict_tau_skip",
        nx=8,
        ny=6,
        nz=6,
        n_steps=5,
        output_interval=5,
        open_boundary_semantics="regularized_velocity_pressure",
        geometry_mode="duct_only",
        lbm_viscosity_semantics="physical_nu_mapping",
        lbm_tau_stability_policy="strict",
        lbm_min_tau_margin=1.0e-4,
        lbm_dt_phys_override_s=2.0833333333333334e-6,
        physical_duct_length_m=0.1,
        target_inlet_velocity_mps=10.0,
        target_reynolds_number=26666.666666666668,
    )

    summary = run_step116_matrix(output_dir, specs=[spec], force=True)
    row = summary["runs"][0]
    finite = _read_json(output_dir / "tiny_strict_tau_skip" / "finite_stability_report.json")

    assert row["skipped_due_to_tau_margin"] is True
    assert finite["skipped_due_to_tau_margin"] is True
    assert finite["steps_completed"] == 0
