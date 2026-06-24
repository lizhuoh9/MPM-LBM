# Step100 48cube 5-Step Taichi GGUI Visualization Run Goal

## Objective

Implement and verify:

`Step100 48^3 / 5-Step Taichi GGUI Visualization Run`

Step100 is a real run, not a plan/guard-only step. It must extend the accepted Step98 first-user 48^3 / 1-step GGUI smoke to a 48^3 / 5-step Taichi GGUI visualization run.

The only allowed expansion from Step98 is:

`n_lbm_steps = 1 -> 5`

Everything else must stay inside the Step98/Step99 first-user envelope.

## Baseline

- `origin/main` must start from `32491a3a1f5dd4970b81d98157037a1109e8f0d0`.
- Step98 accepted.
- Step99 accepted.
- Step100 not started.

Step99 planned and guarded the single Step100 row:

`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run`

## Accepted Claim

If green, Step100 may claim only:

`48^3 / 5-step Taichi GGUI visualization run passed for the first-user envelope.`

Step100 must not claim:

- 48^3 10-step readiness.
- 64^3 readiness.
- Production readiness.
- Physical validation complete.
- Real squid validation.
- Squid swimming validation.
- Squid actuation validation.

## Required Row

Run exactly one required row:

`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run`

No optional rows are allowed.

Required driver configuration:

- `n_grid = 48`.
- `n_particles = 1024`.
- `n_lbm_steps = 5`.
- `mpm_substeps_per_lbm_step = 1`.
- `coupling_mode = moving_boundary`.
- `reaction_transfer_mode = engineering`.
- `target_u_lbm = [0.0, 0.0, 0.0]`.
- `geometry_type = squid_proxy`.
- `geometry_config_path = configs/step85_squid_proxy_geometry_1024.json`.
- `quality_check_enabled = true`.
- `quality_check_strict = false`.
- `geometry_motion_mode = prescribed_kinematic`.
- `geometry_motion_application_mode = diagnostic_only`.
- `geometry_motion_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json`.
- `geometry_motion_application_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json`.
- `geometry_motion_report_enabled = true`.
- `geometry_motion_application_report_enabled = true`.
- `boundary_motion_mode = prescribed_kinematic`.
- `boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json`.
- `boundary_motion_report_enabled = true`.
- `wall_velocity_application_mode = solid_vel_experimental`.
- `wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json`.
- `wall_velocity_application_report_enabled = true`.
- `target_lbm_field = solid_vel`.
- `write_vtk = false`.
- `write_particles = false`.
- `output_interval = 1`.

Use a separate GGUI config. Do not add GGUI-only fields to `FSIDriverConfig`.

Required GGUI config:

- `configs/step100_taichi_ggui_visualization_config.json`.
- `ggui_visualization_enabled = true`.
- `window_title = Step100 48^3 5-Step GGUI Visualization Run`.
- `window_resolution = [1280, 720]`.
- `render_frames = 1`.
- `screenshot_enabled = true`.
- `screenshot_path = outputs/step100_ggui_visualization/step100_48cube_5step_ggui_visualization.png`.
- `video_enabled = false`.
- `camera_position = [1.6, 1.2, 1.6]`.
- `camera_lookat = [0.5, 0.5, 0.5]`.
- `camera_up = [0.0, 1.0, 0.0]`.
- `visualize_squid_proxy_points = true`.
- `visualize_domain_box = true`.
- `visualize_boundary_motion_proxy = true`.
- `visualize_wall_velocity_proxy = true`.
- `max_visual_points = 4096`.
- `visualization_source = procedural_squid_proxy_proxy_points`.

## Forbidden Edit Scope

Do not modify:

- `src/mpm_lbm/sim/**`.
- `src/mpm_lbm/diagnostics/**`.
- `src/mpm_lbm/sim/drivers/**`.
- `src/mpm_lbm/sim/coupling/**`.
- `src/mpm_lbm/sim/lbm/**`.
- `src/mpm_lbm/sim/mpm/**`.
- `src/mpm_lbm/sim/geometry/**`.
- `src/mpm_lbm/sim/motion/**`.
- `src/mpm_lbm/sim/wall_velocity/**`.
- `external/taichi_LBM3D/**`.
- `data/real_geometry_candidates/**`.

If the Step100 run or GGUI render fails, diagnose Step100 config, duration assumptions, GGUI config, local desktop backend availability, screenshot path, renderer, quality extraction, output guard assumptions, and artifact manifest assumptions. Do not use failure as permission to change solver runtime.

## Required Files

Add:

- `STEP100_48CUBE_5STEP_TAICHI_GGUI_VISUALIZATION_RUN_GOAL.md`.
- `STEP100_48CUBE_5STEP_TAICHI_GGUI_VISUALIZATION_RUN_REPORT.md`.
- `configs/step100_48cube_5step_taichi_ggui_visualization_run_matrix.json`.
- `configs/step100_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run.json`.
- `configs/step100_taichi_ggui_visualization_config.json`.
- `configs/step100_48cube_5step_taichi_ggui_visualization_acceptance_policy.json`.
- `configs/step100_activation_guard_policy.json`.
- `configs/step100_output_guard_policy.json`.
- `configs/step100_step99_regression_policy.json`.
- `configs/step100_step98_regression_policy.json`.
- `configs/step100_step96_regression_policy.json`.
- `configs/step100_artifact_manifest_policy.json`.
- `src/mpm_lbm/evidence/step100_48cube_5step_taichi_ggui_visualization_run_runner.py`.
- `src/mpm_lbm/evidence/step100_48cube_5step_taichi_ggui_visualization_run_audit.py`.
- `src/mpm_lbm/evidence/step100_48cube_5step_taichi_ggui_visualization_quality_audit.py`.
- `src/mpm_lbm/evidence/step100_activation_guard.py`.
- `src/mpm_lbm/evidence/step100_output_guard.py`.
- `src/mpm_lbm/evidence/step100_step99_regression_guard.py`.
- `src/mpm_lbm/evidence/step100_step98_regression_guard.py`.
- `src/mpm_lbm/evidence/step100_step96_regression_guard.py`.
- `baseline_tests/step100_common.py`.
- `baseline_tests/run_step100_48cube_5step_taichi_ggui_visualization_run_matrix.py`.
- `baseline_tests/run_step100_48cube_5step_taichi_ggui_visualization_quality.py`.
- `baseline_tests/run_step100_activation_guard.py`.
- `baseline_tests/run_step100_output_guard.py`.
- `baseline_tests/run_step100_step99_regression_guard.py`.
- `baseline_tests/run_step100_step98_regression_guard.py`.
- `baseline_tests/run_step100_step96_regression_guard.py`.
- `baseline_tests/run_step100_artifact_manifest.py`.
- `tests/test_step100_48cube_5step_taichi_ggui_visualization_run_matrix_contract.py`.
- `tests/test_step100_48cube_5step_taichi_ggui_visualization_quality_contract.py`.
- `tests/test_step100_activation_guard_contract.py`.
- `tests/test_step100_output_guard_contract.py`.
- `tests/test_step100_step99_regression_contract.py`.
- `tests/test_step100_step98_regression_contract.py`.
- `tests/test_step100_step96_regression_contract.py`.
- `docs/100_48cube_5step_taichi_ggui_visualization_run.md`.
- `outputs/step100_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run/**`.
- `outputs/step100_ggui_visualization/**`.
- `outputs/step100_48cube_5step_taichi_ggui_visualization_run_matrix/**`.
- `outputs/step100_48cube_5step_taichi_ggui_visualization_quality/**`.
- `outputs/step100_activation_guard/**`.
- `outputs/step100_output_guard/**`.
- `outputs/step100_step99_regression_guard/**`.
- `outputs/step100_step98_regression_guard/**`.
- `outputs/step100_step96_regression_guard/**`.
- `outputs/step100_artifact_manifest/**`.
- `logs/step100_*.log`.

Optional docs may be updated only if the existing repo pattern clearly requires it:

- `README.md`.
- `docs/00_project_status.md`.
- `docs/ACTIVATION_PRECONDITIONS.md`.
- `docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md`.
- `docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md`.

## Expected Driver Outputs

Driver run directory:

`outputs/step100_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run/`

Allowed driver files:

- `boundary_motion_interface_report.json`.
- `diagnostics_timeseries.csv`.
- `diagnostics_timeseries.npz`.
- `driver_config.json`.
- `driver_timing.json`.
- `geo_all_fluid_48.dat`.
- `geometry_motion_interface_report.json`.
- `geometry_quality_report.json`.
- `wall_velocity_application_report.json`.

GGUI output directory:

`outputs/step100_ggui_visualization/`

Allowed GGUI files:

- `step100_48cube_5step_ggui_visualization.png`.
- `step100_ggui_visualization_report.json`.
- `step100_ggui_visualization_metadata.json`.

Forbidden outputs:

- VTR files.
- Particle NPY files.
- MP4/GIF video.
- Dense wall velocity NPY.
- Sparse wall velocity NPY.
- Dense displacement NPY.
- Displaced particle NPY.
- Raw geometry output.
- Real geometry candidate output.
- Optional Step100 driver run dirs.
- 64-grid outputs.

## Runner Requirements

The Step100 matrix runner must genuinely call the canonical driver:

```python
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

config = FSIDriverConfig.from_json(
    "configs/step100_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run.json"
)
driver = FSIDriver3D(
    config,
    "outputs/step100_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run",
)
diagnostics = driver.run()
```

After the driver run, call the Step100 GGUI renderer:

```python
render_step100_48cube_5step_ggui_visualization(
    driver_run_dir="outputs/step100_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run",
    ggui_config_path="configs/step100_taichi_ggui_visualization_config.json",
    output_dir="outputs/step100_ggui_visualization",
)
```

The renderer may read only driver outputs, geometry quality report, geometry config, diagnostics, and Step98-compatible procedural visualization proxy data. It must not change solver runtime behavior.

## Acceptance Criteria

### Driver

- `driver_run_called = true`.
- `canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver`.
- `legacy_driver_module_used_as_implementation = false`.
- Required row name matches exactly.
- `n_grid = 48`.
- `n_particles = 1024`.
- `n_lbm_steps = 5`.
- `mpm_substeps_per_lbm_step = 1`.
- `coupling_mode = moving_boundary`.
- `reaction_transfer_mode = engineering`.
- `target_u_lbm = [0.0, 0.0, 0.0]`.
- `completed_lbm_steps = 5`.
- `total_mpm_substeps >= 5`.
- `diagnostics_row_count >= 6`.
- `has_nan = false`.
- `has_inf = false`.
- `stable = true`.
- `runtime_hard_fail = false`.

### Duration Expansion

- `from_step98_duration_expansion = true`.
- `previous_step98_n_grid = 48`.
- `previous_step98_n_lbm_steps = 1`.
- `step100_n_grid = 48`.
- `step100_n_lbm_steps = 5`.
- `only_new_dimension_from_step98 = n_lbm_steps_5`.
- `grid_48_enabled = true`.
- `grid_64_enabled = false`.

### GGUI

- `ggui_visualization_enabled = true`.
- `ggui_renderer_called = true`.
- `ggui_window_created = true`.
- `ggui_scene_created = true`.
- `ggui_camera_configured = true`.
- `ggui_rendered_frame_count >= 1`.
- `ggui_screenshot_enabled = true`.
- `ggui_screenshot_exists = true`.
- `ggui_screenshot_file_count = 1`.
- `ggui_screenshot_size_bytes > 0`.
- `ggui_video_enabled = false`.
- `ggui_video_file_count = 0`.
- `ggui_render_report_exists = true`.
- `ggui_render_report_pass = true`.

### Squid Proxy Geometry

- `geometry_type = squid_proxy`.
- `geometry_config_path = configs/step85_squid_proxy_geometry_1024.json`.
- `squid_proxy_enabled = true`.
- `procedural_geometry_enabled = true`.
- `real_geometry_candidate_enabled = false`.
- `real_geometry_enabled = false`.
- `geometry_quality_report_exists = true`.
- `geometry_quality_report_pass = true`.
- `sampling_particle_count = 1024`.
- `mantle_particle_count > 0`.
- `head_particle_count > 0`.
- `arms_particle_count > 0`.

### Runtime Geometry Diagnostic-Only

- `runtime_geometry_enabled = true`.
- `geometry_motion_application_mode = diagnostic_only`.
- `geometry_motion_interface_report_exists = true`.
- `geometry_motion_interface_report_pass = true`.
- `diagnostic_only = true`.
- `no_op_pass = true`.
- `mutation_flag_enabled_count = 0`.
- `mutate_geometry_state = false`.

### Wall Velocity Solid Velocity Path

- `wall_velocity_enabled = true`.
- `wall_velocity_application_mode = solid_vel_experimental`.
- `wall_velocity_application_report_exists = true`.
- `wall_velocity_application_report_pass = true`.
- `target_lbm_field = solid_vel`.
- `apply_to_lbm_solid_vel_wall_velocity = true`.
- `apply_to_lbm_populations = false`.
- `modify_bounceback_formula = false`.
- `finite_pass = true`.
- `cap_pass = true`.
- `lbm_population_update_count = 0`.

### Disabled Outputs and Features

- `write_vtk = false`.
- `write_particles = false`.
- `vtr_output_count = 0`.
- `particle_npy_output_count = 0`.
- `ggui_video_file_count = 0`.
- `real_geometry_candidate_enabled = false`.
- `link_area_enabled = false`.
- `grid_64_enabled = false`.
- `dense_wall_velocity_output_count = 0`.
- `dense_displacement_output_count = 0`.

### Numeric Smoke Bounds

- `rho_min_min > 0.90`.
- `rho_max_max < 1.10`.
- `lbm_max_v_max < 0.5`.
- `mpm_min_J_min > 0.0`.
- `mpm_max_speed_max < 10.0`.
- `projected_mass_final > 0.0`.
- `active_cell_count_final > 0`.
- `bb_link_count_max > 0`.
- `max_grid_reaction_norm_max` finite.

## Matrix Summary Contract

The matrix summary must include:

- `step100_48cube_5step_taichi_ggui_visualization_run_matrix_pass = true`.
- `required_row_count = 1`.
- `optional_row_count = 0`.
- `required_stable_count = 1`.
- `activation_feature_count = 5`.
- `grid_48_enabled_count = 1`.
- `grid_64_enabled_count = 0`.
- `squid_proxy_enabled_count = 1`.
- `runtime_geometry_enabled_count = 1`.
- `wall_velocity_enabled_count = 1`.
- `combined_runtime_geometry_wall_velocity_enabled_count = 1`.
- `ggui_visualization_enabled_count = 1`.
- `ggui_screenshot_count = 1`.
- `ggui_video_file_count = 0`.
- `vtr_output_count = 0`.
- `particle_npy_output_count = 0`.
- `min_completed_lbm_steps = 5`.
- `min_diagnostics_row_count >= 6`.
- `runtime_code_changed = false`.
- `solver_behavior_changed = false`.
- `physics_feature_expansion = 48cube_5step_taichi_ggui_visualization_run_only`.

## Output Guard Contract

The output guard must include:

- `output_guard_pass = true`.
- `step100_required_driver_run_dir_count = 1`.
- `step100_optional_driver_run_dir_count = 0`.
- `step100_ggui_screenshot_count = 1`.
- `step100_ggui_video_count = 0`.
- `step100_vtr_count = 0`.
- `step100_particle_npy_count = 0`.
- `step100_raw_geometry_output_count = 0`.
- `step100_real_geometry_candidate_output_count = 0`.
- `step100_dense_wall_velocity_output_count = 0`.
- `step100_sparse_wall_velocity_output_count = 0`.
- `step100_dense_displacement_output_count = 0`.
- `step100_displaced_particle_output_count = 0`.
- `private_absolute_path_count = 0`.
- `protected_sim_edit_count = 0`.
- `protected_diagnostics_edit_count = 0`.
- `protected_external_edit_count = 0`.
- `protected_real_geometry_candidate_edit_count = 0`.
- `artifact_budget_pass = true`.

Artifact budget:

- `step100_file_count <= 110`.
- `step100_total_size_mb < 15`.
- `large_file_count = 0`.

## Regression Guards

### Step99

The Step99 regression guard must prove:

- Step99 plan pass.
- Step99 guard pass.
- Step99 Step98 regression pass.
- Step99 Step97 regression pass.
- Step99 Step96 regression pass.
- Step99 output guard pass.
- Step99 artifact budget pass.
- `step99_activation_feature_count = 0`.
- `planned_step100_activation_feature_count = 5`.
- `step99_driver_run_dir_count = 0`.
- `step99_ggui_screenshot_count = 0`.
- `step99_ggui_video_count = 0`.
- `step99_vtr_count = 0`.
- `step99_particle_npy_count = 0`.

### Step98

The Step98 regression guard must prove:

- Step98 matrix pass.
- Step98 quality pass.
- Step98 activation guard pass.
- Step98 output guard pass.
- Step98 artifact budget pass.
- `step98_activation_feature_count = 5`.
- `step98_completed_lbm_steps = 1`.
- `step98_n_grid = 48`.
- `step98_grid_48_enabled_count = 1`.
- `step98_grid_64_enabled_count = 0`.
- `step98_squid_proxy_enabled_count = 1`.
- `step98_runtime_geometry_enabled_count = 1`.
- `step98_wall_velocity_enabled_count = 1`.
- `step98_ggui_screenshot_count = 1`.
- `step98_ggui_video_count = 0`.
- `step98_vtr_count = 0`.
- `step98_particle_npy_count = 0`.

### Step96

The Step96 regression guard must prove:

- Step96 matrix pass.
- Step96 quality pass.
- Step96 activation guard pass.
- Step96 output guard pass.
- Step96 artifact budget pass.
- `step96_activation_feature_count = 4`.
- `step96_completed_lbm_steps = 10`.
- `step96_n_grid = 32`.
- `step96_squid_proxy_enabled_count = 1`.
- `step96_runtime_geometry_enabled_count = 1`.
- `step96_wall_velocity_enabled_count = 1`.
- `step96_ggui_screenshot_count = 1`.
- `step96_ggui_video_count = 0`.
- `step96_vtr_count = 0`.
- `step96_particle_npy_count = 0`.

## Tests

Add:

- `tests/test_step100_48cube_5step_taichi_ggui_visualization_run_matrix_contract.py`.
- `tests/test_step100_48cube_5step_taichi_ggui_visualization_quality_contract.py`.
- `tests/test_step100_activation_guard_contract.py`.
- `tests/test_step100_output_guard_contract.py`.
- `tests/test_step100_step99_regression_contract.py`.
- `tests/test_step100_step98_regression_contract.py`.
- `tests/test_step100_step96_regression_contract.py`.

Tests must read committed artifacts and assert the contract. They must not trigger a driver run themselves.

## Report Requirements

`STEP100_48CUBE_5STEP_TAICHI_GGUI_VISUALIZATION_RUN_REPORT.md` must state:

- Step100 accepted.
- Step100 ran exactly one required 48^3 / 5-step GGUI visualization row.
- It used 1024 particles, one MPM substep per LBM step, moving boundary, engineering transfer, zero background flow, squid proxy, diagnostic-only runtime geometry, solid velocity wall velocity, GGUI screenshot enabled, GGUI video disabled, VTK disabled, particles disabled.
- The only intended expansion from Step98 was `n_lbm_steps = 1 -> 5`.
- It wrote exactly one GGUI screenshot artifact.
- It did not write VTR, VTK file output, particle NPY, video, 64-grid output, real geometry candidate data, link-area output, or solver formula changes.
- It does not claim production readiness, physical validation, squid swimming, or real squid validation.
- Correct claim: `48^3 / 5-step Taichi GGUI visualization run passed for the first-user envelope.`

Do not hardcode exact artifact byte totals in the prose report; keep exact totals in manifest JSON.

## Verification Commands

Baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step100_48cube_5step_taichi_ggui_visualization_run_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step100_48cube_5step_taichi_ggui_visualization_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step100_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step100_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step100_step99_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step100_step98_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step100_step96_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step100_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step100_48cube_5step_taichi_ggui_visualization_run_matrix_contract.py tests\test_step100_48cube_5step_taichi_ggui_visualization_quality_contract.py tests\test_step100_activation_guard_contract.py tests\test_step100_output_guard_contract.py tests\test_step100_step99_regression_contract.py tests\test_step100_step98_regression_contract.py tests\test_step100_step96_regression_contract.py -q
```

Full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Git checks:

- `git diff --check`.
- `git diff --cached --check`.
- `git status --short external/taichi_LBM3D`.
- `git status --short data/real_geometry_candidates`.
- Run the existing legacy-output grep from the task handoff; it must return no output. Do not write its literal tokens into repo files.

## Done Criteria

Step100 is done only when:

- Detailed Step100 goal file exists and active goal references it.
- Step100 driver config, GGUI config, matrix config, acceptance policy, guards, docs, report, tests, baseline runners, logs, and outputs are added.
- The real Step100 driver run completes exactly one required row.
- Step100 GGUI writes exactly one screenshot.
- No forbidden outputs appear.
- No forbidden paths are modified.
- Focused Step100 tests pass.
- Full pytest passes with the trusted Taichi interpreter.
- Full pytest passes with Anaconda Python.
- Git diff checks pass.
- Commit message is `test: add step100 48cube 5step taichi ggui visualization run`.
- The validated commit is pushed to `origin/main`.
