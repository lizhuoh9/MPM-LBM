# Step96 Taichi GGUI 10-Step First User Visualization Run Goal

## Source Baseline

- Current accepted upstream baseline: `origin/main = 62d1e51bbcbbb9a1b64bd8c3e1831770846b0709`.
- Previous completed step: Step95, committed as `test: add step95 taichi ggui 10step visualization plan and guard`.
- Step95 accepted claim: `Taichi GGUI 10-step first-user visualization run is planned and guarded for Step96.`
- Step96 must be the next step. The repository must not already contain Step96 files or artifacts before this implementation.

## Goal

Implement Step96 as the real Taichi GGUI 10-step first-user visualization run.

Step96 must run exactly one required canonical driver row, then render exactly
one Taichi GGUI screenshot through an independent evidence renderer. It must
produce artifact-backed matrix, quality, activation, output, regression,
manifest, docs, report, and test evidence.

The correct final Step96 claim is exactly:

`Taichi GGUI visualization can render the accepted 32^3 / 10-step first-user dry-run envelope.`

Step96 must combine two previously accepted capabilities:

- Step92: 32^3 / 1024-particle / 10-step first-user dry run.
- Step94: 32^3 / 1024-particle / 1-step Taichi GGUI screenshot smoke.

Step96 is not plan-only. It must execute the required row through the canonical
`src.mpm_lbm.sim.drivers.fsi_driver.FSIDriver3D` implementation.

## Required Row

Step96 must run only this row:

`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run`

No optional rows are allowed.

Required row fields:

```json
{
  "n_grid": 32,
  "n_particles": 1024,
  "n_lbm_steps": 10,
  "mpm_substeps_per_lbm_step": 1,
  "coupling_mode": "moving_boundary",
  "reaction_transfer_mode": "engineering",
  "target_u_lbm": [0.0, 0.0, 0.0],
  "geometry_type": "squid_proxy",
  "geometry_config_path": "configs/step85_squid_proxy_geometry_1024.json",
  "quality_check_enabled": true,
  "quality_check_strict": false,
  "geometry_motion_mode": "prescribed_kinematic",
  "geometry_motion_application_mode": "diagnostic_only",
  "geometry_motion_config_path": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
  "geometry_motion_application_config_path": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
  "geometry_motion_report_enabled": true,
  "geometry_motion_application_report_enabled": true,
  "boundary_motion_mode": "prescribed_kinematic",
  "boundary_motion_config_path": "configs/step34_boundary_motion_interface_prescribed_kinematic.json",
  "boundary_motion_report_enabled": true,
  "wall_velocity_application_mode": "solid_vel_experimental",
  "wall_velocity_application_config_path": "configs/step36_wall_velocity_application_solid_vel_experimental.json",
  "wall_velocity_application_report_enabled": true,
  "target_lbm_field": "solid_vel",
  "write_vtk": false,
  "write_particles": false,
  "output_interval": 1
}
```

GGUI fields must stay outside `FSIDriverConfig` unless the current driver schema
already supports them. Prefer a separate Step96 GGUI config.

## Required Config Files

- `configs/step96_taichi_ggui_10step_visualization_run_matrix.json`
- `configs/step96_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run.json`
- `configs/step96_taichi_ggui_visualization_config.json`
- `configs/step96_taichi_ggui_10step_visualization_acceptance_policy.json`
- `configs/step96_activation_guard_policy.json`
- `configs/step96_output_guard_policy.json`
- `configs/step96_step95_regression_policy.json`
- `configs/step96_step94_regression_policy.json`
- `configs/step96_step92_regression_policy.json`
- `configs/step96_artifact_manifest_policy.json`

Suggested `configs/step96_taichi_ggui_visualization_config.json`:

```json
{
  "ggui_visualization_enabled": true,
  "window_title": "Step96 GGUI 10-Step First User Visualization",
  "window_resolution": [1280, 720],
  "render_frames": 1,
  "screenshot_enabled": true,
  "screenshot_path": "outputs/step96_ggui_visualization/step96_ggui_10step_visualization.png",
  "video_enabled": false,
  "camera_position": [1.6, 1.2, 1.6],
  "camera_lookat": [0.5, 0.5, 0.5],
  "camera_up": [0.0, 1.0, 0.0],
  "visualize_squid_proxy_points": true,
  "visualize_domain_box": true,
  "visualize_boundary_motion_proxy": true,
  "visualize_wall_velocity_proxy": true,
  "max_visual_points": 4096,
  "visualization_source": "procedural_squid_proxy_proxy_points"
}
```

## Required Code And Test Files

Evidence scripts:

- `src/mpm_lbm/evidence/step96_taichi_ggui_10step_visualization_run_runner.py`
- `src/mpm_lbm/evidence/step96_taichi_ggui_10step_visualization_run_audit.py`
- `src/mpm_lbm/evidence/step96_taichi_ggui_10step_visualization_quality_audit.py`
- `src/mpm_lbm/evidence/step96_activation_guard.py`
- `src/mpm_lbm/evidence/step96_output_guard.py`
- `src/mpm_lbm/evidence/step96_step95_regression_guard.py`
- `src/mpm_lbm/evidence/step96_step94_regression_guard.py`
- `src/mpm_lbm/evidence/step96_step92_regression_guard.py`

Baseline runners:

- `baseline_tests/step96_common.py`
- `baseline_tests/run_step96_taichi_ggui_10step_visualization_run_matrix.py`
- `baseline_tests/run_step96_taichi_ggui_10step_visualization_quality.py`
- `baseline_tests/run_step96_activation_guard.py`
- `baseline_tests/run_step96_output_guard.py`
- `baseline_tests/run_step96_step95_regression_guard.py`
- `baseline_tests/run_step96_step94_regression_guard.py`
- `baseline_tests/run_step96_step92_regression_guard.py`
- `baseline_tests/run_step96_artifact_manifest.py`

Contract tests:

- `tests/test_step96_taichi_ggui_10step_visualization_run_matrix_contract.py`
- `tests/test_step96_taichi_ggui_10step_visualization_quality_contract.py`
- `tests/test_step96_activation_guard_contract.py`
- `tests/test_step96_output_guard_contract.py`
- `tests/test_step96_step95_regression_contract.py`
- `tests/test_step96_step94_regression_contract.py`
- `tests/test_step96_step92_regression_contract.py`

Docs and reports:

- `STEP96_TAICHI_GGUI_10STEP_FIRST_USER_VISUALIZATION_RUN_GOAL.md`
- `STEP96_TAICHI_GGUI_10STEP_FIRST_USER_VISUALIZATION_RUN_REPORT.md`
- `docs/96_taichi_ggui_10step_first_user_visualization_run.md`

Allowed status docs:

- `README.md`
- `docs/00_project_status.md`
- `docs/ACTIVATION_PRECONDITIONS.md`
- `docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md`
- `docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md`

## Required Output Artifacts

Driver run directory:

`outputs/step96_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run/`

Allowed driver files:

- `boundary_motion_interface_report.json`
- `diagnostics_timeseries.csv`
- `diagnostics_timeseries.npz`
- `driver_config.json`
- `driver_timing.json`
- `geo_all_fluid_32.dat`
- `geometry_motion_interface_report.json`
- `geometry_quality_report.json`
- `wall_velocity_application_report.json`

GGUI output directory:

`outputs/step96_ggui_visualization/`

Allowed GGUI files:

- `step96_ggui_10step_visualization.png`
- `step96_ggui_visualization_report.json`
- `step96_ggui_visualization_metadata.json`

Evidence output directories:

- `outputs/step96_taichi_ggui_10step_visualization_run_matrix/`
- `outputs/step96_taichi_ggui_10step_visualization_quality/`
- `outputs/step96_activation_guard/`
- `outputs/step96_output_guard/`
- `outputs/step96_step95_regression_guard/`
- `outputs/step96_step94_regression_guard/`
- `outputs/step96_step92_regression_guard/`
- `outputs/step96_artifact_manifest/`

Logs:

- `logs/step96_*.log`

## Runner Requirements

The Step96 matrix runner must call the canonical driver:

```python
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

config = FSIDriverConfig.from_json(
    "configs/step96_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run.json"
)

driver = FSIDriver3D(
    config,
    "outputs/step96_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run",
)

diagnostics = driver.run()
```

Then it must call an independent Step96 GGUI renderer:

```python
render_step96_ggui_10step_visualization(
    driver_run_dir="outputs/step96_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run",
    ggui_config_path="configs/step96_taichi_ggui_visualization_config.json",
    output_dir="outputs/step96_ggui_visualization",
)
```

The renderer may read driver outputs, the geometry quality report, the geometry
config, diagnostics, and Step94 renderer-compatible procedural visualization
proxy logic. The renderer must not modify solver runtime code.

## Acceptance Criteria

Driver run:

- `driver_run_called = true`
- `canonical_driver_module = "src.mpm_lbm.sim.drivers.fsi_driver"`
- `legacy_driver_module_used_as_implementation = false`
- `row_name = "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run"`
- `n_grid = 32`
- `n_particles = 1024`
- `n_lbm_steps = 10`
- `mpm_substeps_per_lbm_step = 1`
- `coupling_mode = "moving_boundary"`
- `reaction_transfer_mode = "engineering"`
- `target_u_lbm = [0.0, 0.0, 0.0]`
- `completed_lbm_steps = 10`
- `total_mpm_substeps >= 10`
- `diagnostics_row_count >= 11`
- `has_nan = false`
- `has_inf = false`
- `stable = true`
- `runtime_hard_fail = false`

GGUI visualization:

- `ggui_visualization_enabled = true`
- `ggui_renderer_called = true`
- `ggui_window_created = true`
- `ggui_scene_created = true`
- `ggui_camera_configured = true`
- `ggui_rendered_frame_count >= 1`
- `ggui_screenshot_enabled = true`
- `ggui_screenshot_exists = true`
- `ggui_screenshot_file_count = 1`
- `ggui_screenshot_size_bytes > 0`
- `ggui_video_enabled = false`
- `ggui_video_file_count = 0`
- `ggui_render_report_exists = true`
- `ggui_render_report_pass = true`

Duration/GGUI relationship:

- `from_step94_duration_expansion = true`
- `previous_step94_n_lbm_steps = 1`
- `step96_n_lbm_steps = 10`
- `from_step92_adds_ggui_visualization = true`
- `previous_step92_n_lbm_steps = 10`

Squid proxy geometry:

- `geometry_type = "squid_proxy"`
- `geometry_config_path = "configs/step85_squid_proxy_geometry_1024.json"`
- `squid_proxy_enabled = true`
- `procedural_geometry_enabled = true`
- `real_geometry_candidate_enabled = false`
- `real_geometry_enabled = false`
- `geometry_quality_report_exists = true`
- `geometry_quality_report_pass = true`
- `sampling_particle_count = 1024`
- `mantle_particle_count > 0`
- `head_particle_count > 0`
- `arms_particle_count > 0`

Runtime geometry diagnostic-only:

- `runtime_geometry_enabled = true`
- `geometry_motion_application_mode = "diagnostic_only"`
- `geometry_motion_interface_report_exists = true`
- `geometry_motion_interface_report_pass = true`
- `diagnostic_only = true`
- `no_op_pass = true`
- `mutation_flag_enabled_count = 0`
- `mutate_geometry_state = false`

Wall velocity:

- `wall_velocity_enabled = true`
- `wall_velocity_application_mode = "solid_vel_experimental"`
- `wall_velocity_application_report_exists = true`
- `wall_velocity_application_report_pass = true`
- `target_lbm_field = "solid_vel"`
- `apply_to_lbm_solid_vel = true`
- `apply_to_lbm_populations = false`
- `modify_bounceback_formula = false`
- `finite_pass = true`
- `cap_pass = true`
- `lbm_population_update_count = 0`

Forbidden outputs and activations:

- `write_vtk = false`
- `write_particles = false`
- `vtr_output_count = 0`
- `particle_npy_output_count = 0`
- `ggui_video_file_count = 0`
- `real_geometry_candidate_enabled = false`
- `link_area_enabled = false`
- `grid_48_enabled = false`
- `grid_64_enabled = false`
- `dense_wall_velocity_output_count = 0`
- `dense_displacement_output_count = 0`

Numerical bounds:

- `rho_min_min > 0.90`
- `rho_max_max < 1.10`
- `lbm_max_v_max < 0.5`
- `mpm_min_J_min > 0.0`
- `mpm_max_speed_max < 10.0`
- `projected_mass_final > 0.0`
- `active_cell_count_final > 0`
- `bb_link_count_max > 0`
- `max_grid_reaction_norm_max` finite

## Output Guard Contract

The output guard must prove:

- `output_guard_pass = true`
- `step96_required_driver_run_dir_count = 1`
- `step96_optional_driver_run_dir_count = 0`
- `step96_ggui_screenshot_count = 1`
- `step96_ggui_video_count = 0`
- `step96_vtr_count = 0`
- `step96_particle_npy_count = 0`
- `step96_raw_geometry_output_count = 0`
- `step96_real_geometry_candidate_output_count = 0`
- `step96_dense_wall_velocity_output_count = 0`
- `step96_sparse_wall_velocity_output_count = 0`
- `step96_dense_displacement_output_count = 0`
- `step96_displaced_particle_output_count = 0`
- `private_absolute_path_count = 0`
- `protected_sim_edit_count = 0`
- `protected_diagnostics_edit_count = 0`
- `protected_external_edit_count = 0`
- `protected_real_geometry_candidate_edit_count = 0`
- `artifact_budget_pass = true`

Artifact budget:

- `step96_file_count <= 110`
- `step96_total_size_mb < 10`
- `large_file_count = 0`

## Regression Guards

Step95 regression guard:

- `step95_taichi_ggui_10step_visualization_plan_pass = true`
- `step95_taichi_ggui_10step_visualization_guard_pass = true`
- `step95_step94_regression_guard_pass = true`
- `step95_step93_regression_guard_pass = true`
- `step95_step92_regression_guard_pass = true`
- `step95_output_guard_pass = true`
- `step95_artifact_budget_pass = true`
- `step95_activation_feature_count = 0`
- `planned_step96_activation_feature_count = 4`
- `step95_driver_run_dir_count = 0`
- `step95_ggui_screenshot_count = 0`
- `step95_ggui_video_count = 0`
- `step95_vtr_count = 0`
- `step95_particle_npy_count = 0`

Step94 regression guard:

- `step94_taichi_ggui_visualization_smoke_matrix_pass = true`
- `step94_taichi_ggui_visualization_quality_pass = true`
- `step94_activation_guard_pass = true`
- `step94_output_guard_pass = true`
- `step94_artifact_budget_pass = true`
- `step94_activation_feature_count = 4`
- `step94_ggui_visualization_enabled_count = 1`
- `step94_ggui_screenshot_count = 1`
- `step94_ggui_video_count = 0`
- `step94_vtr_count = 0`
- `step94_particle_npy_count = 0`
- `step94_completed_lbm_steps = 1`

Step92 regression guard:

- `step92_first_user_simulation_10step_dry_run_matrix_pass = true`
- `step92_first_user_simulation_10step_dry_run_quality_pass = true`
- `step92_activation_guard_pass = true`
- `step92_output_guard_pass = true`
- `step92_artifact_budget_pass = true`
- `step92_activation_feature_count = 3`
- `step92_completed_lbm_steps = 10`
- `step92_squid_proxy_enabled_count = 1`
- `step92_runtime_geometry_enabled_count = 1`
- `step92_wall_velocity_enabled_count = 1`
- `step92_vtr_count = 0`
- `step92_particle_npy_count = 0`

## Protected Paths

Do not edit:

- `src/mpm_lbm/sim/**`
- `src/mpm_lbm/diagnostics/**`
- `src/mpm_lbm/sim/drivers/**`
- `src/mpm_lbm/sim/coupling/**`
- `src/mpm_lbm/sim/lbm/**`
- `src/mpm_lbm/sim/mpm/**`
- `src/mpm_lbm/sim/geometry/**`
- `src/mpm_lbm/sim/motion/**`
- `src/mpm_lbm/sim/wall_velocity/**`
- `external/taichi_LBM3D/**`
- `data/real_geometry_candidates/**`

If the Step96 run or GGUI render fails, first inspect:

- Step96 driver config.
- Step96 GGUI config.
- Local desktop / Taichi backend availability.
- Screenshot output path.
- GGUI renderer.
- Report extraction.
- Artifact/output guard assumptions.

Do not use a Step96 failure as a reason to change solver runtime code.

## Verification Commands

Baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step96_taichi_ggui_10step_visualization_run_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step96_taichi_ggui_10step_visualization_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step96_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step96_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step96_step95_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step96_step94_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step96_step92_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step96_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step96_taichi_ggui_10step_visualization_run_matrix_contract.py tests\test_step96_taichi_ggui_10step_visualization_quality_contract.py tests\test_step96_activation_guard_contract.py tests\test_step96_output_guard_contract.py tests\test_step96_step95_regression_contract.py tests\test_step96_step94_regression_contract.py tests\test_step96_step92_regression_contract.py -q
```

Full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Git and boundary checks:

```powershell
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Run the legacy Step93 file-visualization route-token grep from the source
instructions. The final grep should return no output.

## Report Requirements

`STEP96_TAICHI_GGUI_10STEP_FIRST_USER_VISUALIZATION_RUN_REPORT.md` must state:

- Step96 accepted.
- Step96 runs exactly one required GGUI 10-step first-user visualization row.
- The row is `first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run`.
- The row uses 32^3, 1024 particles, 10 LBM steps, one MPM substep per LBM step, moving_boundary, engineering, and `target_u_lbm = [0.0, 0.0, 0.0]`.
- The row uses `geometry_type = squid_proxy`.
- The row uses `geometry_motion_application_mode = diagnostic_only`.
- The row uses `wall_velocity_application_mode = solid_vel_experimental`.
- The row uses `target_lbm_field = solid_vel`.
- GGUI visualization is enabled.
- GGUI screenshot is enabled.
- GGUI video is disabled.
- VTR and particle output are disabled.
- Step96 combines the Step92 10-step first-user dry run and the Step94 Taichi GGUI screenshot visualization path.
- Step96 writes exactly one screenshot artifact.
- Step96 does not write VTR.
- Step96 does not write particle NPY.
- Step96 does not write video.
- Step96 does not enable real geometry candidate data.
- Step96 does not enable link-area transfer.
- Step96 does not enable 48^3 or 64^3.
- Step96 does not mutate geometry.
- Step96 does not change solver formulas.
- Step96 does not claim physical validation, squid swimming, real squid validation, or production readiness.

Correct claim:

`Taichi GGUI visualization can render the accepted 32^3 / 10-step first-user dry-run envelope.`

## Forbidden Claims

Do not claim:

- Production visualization readiness.
- Full interactive visualization campaign readiness.
- Physical validation complete.
- Real squid validation complete.
- Squid swimming validation.
- Real geometry readiness.
- 48^3 or 64^3 readiness.

## Commit And Push

After all verification passes:

```powershell
git add .
git diff --cached --check
git commit -m "test: add step96 taichi ggui 10step first user visualization run"
git push origin main
```

After pushing, verify the remote main commit and report:

- Final local commit hash.
- Remote branch pushed: `origin/main`.
- Verification commands and results.
- Any skipped or failed checks, if applicable.
