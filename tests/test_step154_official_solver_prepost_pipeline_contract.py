import json
import math
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REQUIRED_ARTIFACTS = [
    "compiled_case.json",
    "geometry_masks.npz",
    "boundary_masks.npz",
    "fsi_interface_masks.npz",
    "dimensionless_mapping.json",
    "material_model_mapping.json",
    "preprocess_report.json",
    "postprocess_spec.json",
    "geometry_preview.png",
    "step154_summary.json",
    "report.md",
]


def test_step154_runner_writes_canonical_prepost_artifacts(tmp_path):
    import experiments.steps.step154_official_solver_prepost_pipeline as step154

    output_dir = tmp_path / "step154"
    summary = step154.run_step154_official_solver_prepost_pipeline(
        step153_root=ROOT / "outputs/step153_official_tutorial_setup_parity",
        output_dir=output_dir,
        grid=48,
        force=True,
    )

    assert summary["step"] == 154
    assert summary["status"] == "official_solver_prepost_pipeline_ready"
    assert summary["compiled_case_ready_for_step155"] is True
    assert summary["preprocessor_ready"] is True
    assert summary["postprocessor_ready"] is True
    assert summary["solver_run_executed"] is False
    assert summary["fluent_run_executed"] is False
    assert summary["step150_executed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["figure_29_3_parity_claim_allowed"] is False
    assert summary["selected96_execution_allowed"] is False

    for name in REQUIRED_ARTIFACTS:
        path = output_dir / name
        assert path.is_file(), name
        assert path.stat().st_size > 0, name


def test_step154_compiled_case_constants_and_boundary_semantics(tmp_path):
    import experiments.steps.step154_official_solver_prepost_pipeline as step154

    output_dir = tmp_path / "step154"
    step154.run_step154_official_solver_prepost_pipeline(
        step153_root=ROOT / "outputs/step153_official_tutorial_setup_parity",
        output_dir=output_dir,
        grid=48,
        force=True,
        write_preview=False,
    )

    compiled = _read_json(output_dir / "compiled_case.json")
    setup = compiled["official_tutorial_setup"]
    material = compiled["official_material"]

    assert compiled["step"] == 154
    assert compiled["status"] == "compiled_case_ready_for_step155"
    assert compiled["source_step153_status"] == "official_tutorial_setup_parity_run_complete"
    assert setup["official_tutorial_time_steps"] == 50
    assert setup["official_tutorial_dt_s"] == 0.0005
    assert setup["official_tutorial_total_time_s"] == 0.025
    assert setup["duct_length_m"] == 0.10
    assert setup["duct_height_m"] == 0.04
    assert setup["flap_height_m"] == 0.01
    assert setup["flap_thickness_m"] == 0.003
    assert setup["inlet_air_velocity_mps"] == 10.0
    assert setup["outlet_type"] == "pressure_outlet"
    assert material["solid_density_kg_m3"] == 1600.0
    assert material["youngs_modulus_pa"] == 1.0e6
    assert material["poisson_ratio"] == 0.47
    assert compiled["validation_claim_allowed"] is False
    assert compiled["official_mesh_imported"] is False
    assert compiled["official_fluent_files_used_as_runtime_input"] is False

    boundary = compiled["boundary_condition_spec"]
    assert boundary["inlet"] == "velocity_inlet"
    assert boundary["outlet"] == "pressure_outlet"
    assert boundary["wall"] == "no_slip"
    assert boundary["flap_wall"] == "fsi_moving_wall"

    lbm_required = compiled["lbm_boundary_semantics_required_for_step155"]
    assert lbm_required["legacy_all_population_reset_allowed"] is False
    assert lbm_required["minimum_open_boundary_semantics"] == "regularized_velocity_pressure_limited"


def test_step154_mask_integrity_and_monitor_mapping(tmp_path):
    import experiments.steps.step154_official_solver_prepost_pipeline as step154

    output_dir = tmp_path / "step154"
    step154.run_step154_official_solver_prepost_pipeline(
        step153_root=ROOT / "outputs/step153_official_tutorial_setup_parity",
        output_dir=output_dir,
        grid=48,
        force=True,
        write_preview=False,
    )

    compiled = _read_json(output_dir / "compiled_case.json")
    preprocess = _read_json(output_dir / "preprocess_report.json")
    geometry = np.load(output_dir / "geometry_masks.npz")
    boundary = np.load(output_dir / "boundary_masks.npz")
    fsi = np.load(output_dir / "fsi_interface_masks.npz")

    for name in (
        "fluid_mask",
        "solid_mask",
        "duct_context_mask",
        "duct_wall_mask",
        "flap_solid_mask",
        "flap_fixed_base_mask",
        "flap_free_region_mask",
        "monitor_cell_mask",
    ):
        assert name in geometry.files
        assert geometry[name].shape == (48, 48, 48)
        assert geometry[name].dtype == np.bool_

    for name in (
        "velocity_inlet_mask",
        "pressure_outlet_mask",
        "no_slip_wall_mask",
        "symmetry_or_periodic_z_min_mask",
        "symmetry_or_periodic_z_max_mask",
        "flap_wall_mask",
        "fsi_wall_mask",
    ):
        assert name in boundary.files
        assert boundary[name].shape == (48, 48, 48)
        assert boundary[name].dtype == np.bool_

    for name in (
        "fluid_interface_mask",
        "solid_interface_mask",
        "flap_fixed_interface_mask",
        "flap_free_interface_mask",
    ):
        assert name in fsi.files
        assert fsi[name].shape == (48, 48, 48)
        assert fsi[name].dtype == np.bool_

    assert int(geometry["fluid_mask"].sum()) > 0
    assert int(geometry["solid_mask"].sum()) > 0
    assert int(geometry["flap_solid_mask"].sum()) > 0
    assert int(boundary["velocity_inlet_mask"].sum()) > 0
    assert int(boundary["pressure_outlet_mask"].sum()) > 0
    assert int(boundary["fsi_wall_mask"].sum()) > 0
    assert int(geometry["monitor_cell_mask"].sum()) == 1

    monitor = compiled["monitor_spec"]
    assert monitor["monitor_point_m"] == [0.0505, 0.0095]
    assert len(monitor["monitor_index"]) == 3
    assert all(0 <= int(value) < 48 for value in monitor["monitor_index"])
    for actual, expected in zip(monitor["monitor_point_normalized"], [0.505, 0.395, 0.5]):
        assert math.isclose(actual, expected, rel_tol=1.0e-12, abs_tol=1.0e-12)

    mask_counts = preprocess["mask_counts"]
    assert mask_counts["monitor_cell_count"] == 1
    assert mask_counts["fluid_cell_count"] == int(geometry["fluid_mask"].sum())
    assert mask_counts["fsi_wall_cell_count"] == int(boundary["fsi_wall_mask"].sum())


def test_step154_postprocess_spec_and_reports(tmp_path):
    import experiments.steps.step154_official_solver_prepost_pipeline as step154

    output_dir = tmp_path / "step154"
    step154.run_step154_official_solver_prepost_pipeline(
        step153_root=ROOT / "outputs/step153_official_tutorial_setup_parity",
        output_dir=output_dir,
        grid=48,
        force=True,
    )

    postprocess = _read_json(output_dir / "postprocess_spec.json")
    expected_values = {
        "velocity_magnitude_step050.png",
        "velocity_ux_step050.png",
        "velocity_uy_step050.png",
        "streamline_or_quiver_step050.png",
        "geometry_overlay_step050.png",
        "centerline_velocity_profile.csv",
        "x_plane_flux_profile.csv",
        "monitor_displacement_plot.png",
        "force_monitor_plot.png",
        "postprocess_summary.json",
        "solver_acceptance_report.json",
        "official_comparison_report.json",
    }
    assert expected_values.issubset(set(postprocess["expected_outputs"].values()))
    assert postprocess["validation_claim_allowed"] is False
    assert postprocess["step156_required_before_velocity_plots"] is True

    material = _read_json(output_dir / "material_model_mapping.json")
    assert material["status"] == "material_mapping_compiled"
    assert material["material_constants_available_to_step155"] is True
    assert material["validation_claim_allowed"] is False

    dimensionless = _read_json(output_dir / "dimensionless_mapping.json")
    assert dimensionless["official_time_steps"] == 50
    assert dimensionless["official_dt_s"] == 0.0005
    assert dimensionless["official_total_time_s"] == 0.025
    assert dimensionless["duct_height_cells"] > 0
    assert dimensionless["physical_reynolds_parity_claim_allowed"] is False
    assert dimensionless["tau_margin_validation_required_before_physical_re_claim"] is True


def test_step154_source_excludes_solver_and_fluent_execution_shortcuts():
    source = (ROOT / "experiments/steps/step154_official_solver_prepost_pipeline.py").read_text(
        encoding="utf-8"
    )
    lowered = source.lower()
    assert "fsidriver3d(" not in lowered
    assert "run_our_solver_fsi_case" not in lowered
    assert "step150_official_monitor_intake" not in lowered
    assert "fluent.exe" not in lowered
    assert "subprocess" not in lowered


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
