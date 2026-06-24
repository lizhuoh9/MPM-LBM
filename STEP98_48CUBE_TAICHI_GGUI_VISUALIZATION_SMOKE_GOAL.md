# Step98 48^3 Taichi GGUI Visualization Smoke Goal

## Source Baseline

The user verified GitHub before this work:

```text
origin/main = 20f6d497632b6cb72d9ac962db83284c85d814bd
test: add step97 48cube taichi ggui visualization expansion plan and guard
```

Step97 is accepted. Step98 has not started.

Step97 proved only this bounded claim:

```text
48^3 Taichi GGUI visualization smoke is planned and guarded for Step98.
```

Step98 must activate exactly that planned smoke row. It is not another
plan-only step.

## Step Name And Commit

Step name:

```text
Step98 48^3 Taichi GGUI Visualization Smoke
```

Required commit message after implementation and verification:

```text
test: add step98 48cube taichi ggui visualization smoke
```

## Objective

Implement and verify one real, bounded, 48^3 / 1-step Taichi GGUI visualization
smoke run for the accepted first-user `squid_proxy` envelope.

Correct Step98 claim:

```text
48^3 / 1-step Taichi GGUI visualization smoke passed for the first-user envelope.
```

Step98 must not claim:

```text
48^3 10-step ready
64^3 ready
production visualization ready
production simulation ready
physical validation complete
real squid validated
squid swimming validated
```

## Required Row

Run exactly one required row and no optional rows:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke
```

The row values are:

```text
n_grid = 48
n_particles = 1024
n_lbm_steps = 1
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
geometry_motion_mode = prescribed_kinematic
geometry_motion_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_report_enabled = true
geometry_motion_application_mode = diagnostic_only
geometry_motion_application_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_application_report_enabled = true
boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json
boundary_motion_report_enabled = true
wall_velocity_application_mode = solid_vel_experimental
wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json
wall_velocity_application_report_enabled = true
target_lbm_field = solid_vel
ggui_visualization_enabled = true
ggui_screenshot_enabled = true
ggui_video_enabled = false
write_vtk = false
write_particles = false
output_interval = 1
```

The only Step96-to-Step98 row changes are:

```text
n_grid = 32 -> 48
n_lbm_steps = 10 -> 1
```

The duration reduction is intentional 48^3 grid-expansion smoke isolation.

## Driver Config

Add:

```text
configs/step98_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke.json
```

It must configure the canonical driver row without adding GGUI-specific fields
to `FSIDriverConfig` unless the current schema already supports them:

```json
{
  "boundary_motion_mode": "prescribed_kinematic",
  "boundary_motion_config_path": "configs/step34_boundary_motion_interface_prescribed_kinematic.json",
  "boundary_motion_report_enabled": true,
  "coupling_mode": "moving_boundary",
  "reaction_transfer_mode": "engineering",
  "geometry_type": "squid_proxy",
  "geometry_config_path": "configs/step85_squid_proxy_geometry_1024.json",
  "geometry_motion_mode": "prescribed_kinematic",
  "geometry_motion_config_path": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
  "geometry_motion_report_enabled": true,
  "geometry_motion_application_mode": "diagnostic_only",
  "geometry_motion_application_config_path": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
  "geometry_motion_application_report_enabled": true,
  "wall_velocity_application_mode": "solid_vel_experimental",
  "wall_velocity_application_config_path": "configs/step36_wall_velocity_application_solid_vel_experimental.json",
  "wall_velocity_application_report_enabled": true,
  "target_u_lbm": [0.0, 0.0, 0.0],
  "mpm_substeps_per_lbm_step": 1,
  "n_grid": 48,
  "n_lbm_steps": 1,
  "n_particles": 1024,
  "output_interval": 1,
  "quality_check_enabled": true,
  "quality_check_strict": false,
  "write_particles": false,
  "write_vtk": false
}
```

## GGUI Config

Add a separate visualization config:

```text
configs/step98_taichi_ggui_visualization_config.json
```

Required intent:

```json
{
  "ggui_visualization_enabled": true,
  "window_title": "Step98 48^3 GGUI Visualization Smoke",
  "window_resolution": [1280, 720],
  "render_frames": 1,
  "screenshot_enabled": true,
  "screenshot_path": "outputs/step98_ggui_visualization/step98_48cube_ggui_visual_smoke.png",
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

## Required Files

Add or update these Step98 artifacts:

```text
STEP98_48CUBE_TAICHI_GGUI_VISUALIZATION_SMOKE_GOAL.md
STEP98_48CUBE_TAICHI_GGUI_VISUALIZATION_SMOKE_REPORT.md
configs/step98_48cube_taichi_ggui_visualization_smoke_matrix.json
configs/step98_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke.json
configs/step98_taichi_ggui_visualization_config.json
configs/step98_48cube_taichi_ggui_visualization_acceptance_policy.json
configs/step98_activation_guard_policy.json
configs/step98_output_guard_policy.json
configs/step98_step97_regression_policy.json
configs/step98_step96_regression_policy.json
configs/step98_step94_regression_policy.json
configs/step98_artifact_manifest_policy.json
src/mpm_lbm/evidence/step98_48cube_taichi_ggui_visualization_smoke_runner.py
src/mpm_lbm/evidence/step98_48cube_taichi_ggui_visualization_smoke_audit.py
src/mpm_lbm/evidence/step98_48cube_taichi_ggui_visualization_quality_audit.py
src/mpm_lbm/evidence/step98_activation_guard.py
src/mpm_lbm/evidence/step98_output_guard.py
src/mpm_lbm/evidence/step98_step97_regression_guard.py
src/mpm_lbm/evidence/step98_step96_regression_guard.py
src/mpm_lbm/evidence/step98_step94_regression_guard.py
baseline_tests/step98_common.py
baseline_tests/run_step98_48cube_taichi_ggui_visualization_smoke_matrix.py
baseline_tests/run_step98_48cube_taichi_ggui_visualization_quality.py
baseline_tests/run_step98_activation_guard.py
baseline_tests/run_step98_output_guard.py
baseline_tests/run_step98_step97_regression_guard.py
baseline_tests/run_step98_step96_regression_guard.py
baseline_tests/run_step98_step94_regression_guard.py
baseline_tests/run_step98_artifact_manifest.py
tests/test_step98_48cube_taichi_ggui_visualization_smoke_matrix_contract.py
tests/test_step98_48cube_taichi_ggui_visualization_quality_contract.py
tests/test_step98_activation_guard_contract.py
tests/test_step98_output_guard_contract.py
tests/test_step98_step97_regression_contract.py
tests/test_step98_step96_regression_contract.py
tests/test_step98_step94_regression_contract.py
docs/98_48cube_taichi_ggui_visualization_smoke.md
outputs/step98_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke/
outputs/step98_ggui_visualization/
outputs/step98_48cube_taichi_ggui_visualization_smoke_matrix/
outputs/step98_48cube_taichi_ggui_visualization_quality/
outputs/step98_activation_guard/
outputs/step98_output_guard/
outputs/step98_step97_regression_guard/
outputs/step98_step96_regression_guard/
outputs/step98_step94_regression_guard/
outputs/step98_artifact_manifest/
logs/step98_*.log
```

Allowed documentation updates:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

## Forbidden Edits

Do not edit:

```text
src/mpm_lbm/sim/**
src/mpm_lbm/diagnostics/**
src/mpm_lbm/sim/drivers/**
src/mpm_lbm/sim/coupling/**
src/mpm_lbm/sim/lbm/**
src/mpm_lbm/sim/mpm/**
src/mpm_lbm/sim/geometry/**
src/mpm_lbm/sim/motion/**
src/mpm_lbm/sim/wall_velocity/**
external/taichi_LBM3D/**
data/real_geometry_candidates/**
```

If the driver run or GGUI render fails, diagnose Step98 config, 48^3 geometry
generation assumptions, GGUI config, local desktop/Taichi backend availability,
screenshot output paths, renderer logic, quality report extraction, output
guard assumptions, and artifact manifest assumptions. Do not use the failure as
a reason to modify solver runtime behavior.

## Expected Runtime Outputs

Driver run directory:

```text
outputs/step98_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke/
```

Allowed driver files:

```text
boundary_motion_interface_report.json
diagnostics_timeseries.csv
diagnostics_timeseries.npz
driver_config.json
driver_timing.json
geo_all_fluid_48.dat
geometry_motion_interface_report.json
geometry_quality_report.json
wall_velocity_application_report.json
```

GGUI output directory:

```text
outputs/step98_ggui_visualization/
```

Allowed GGUI files:

```text
step98_48cube_ggui_visual_smoke.png
step98_ggui_visualization_report.json
step98_ggui_visualization_metadata.json
```

Forbidden outputs:

```text
*.vtr
particle*.npy
*.mp4
*.gif
dense_wall_velocity*.npy
sparse_wall_velocity*.npy
dense_displacement*.npy
displaced_particles*.npy
raw geometry output
real geometry candidate output
optional driver run dirs
64^3 outputs
```

## Runner Requirements

The Step98 matrix runner must really call the canonical driver:

```python
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

config = FSIDriverConfig.from_json(
    "configs/step98_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke.json"
)

driver = FSIDriver3D(
    config,
    "outputs/step98_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke",
)

diagnostics = driver.run()
```

Then it must call an independent GGUI renderer:

```python
render_step98_48cube_ggui_visual_smoke(
    driver_run_dir="outputs/step98_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke",
    ggui_config_path="configs/step98_taichi_ggui_visualization_config.json",
    output_dir="outputs/step98_ggui_visualization",
)
```

The renderer may read driver outputs, geometry quality report, geometry config,
diagnostics, and Step94/Step96-compatible procedural visualization proxy data.
It must not change solver runtime code.

## Acceptance Criteria

Driver row:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke
n_grid = 48
n_particles = 1024
n_lbm_steps = 1
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
completed_lbm_steps = 1
total_mpm_substeps >= 1
diagnostics_row_count >= 2
has_nan = false
has_inf = false
stable = true
runtime_hard_fail = false
```

48^3 expansion:

```text
from_step96_grid_expansion = true
previous_step96_n_grid = 32
step98_n_grid = 48
from_step96_duration_reduction = true
previous_step96_n_lbm_steps = 10
step98_n_lbm_steps = 1
grid_expansion_smoke_isolation = true
grid_48_enabled = true
grid_64_enabled = false
```

GGUI visualization:

```text
ggui_visualization_enabled = true
ggui_renderer_called = true
ggui_window_created = true
ggui_scene_created = true
ggui_camera_configured = true
ggui_rendered_frame_count >= 1
ggui_screenshot_enabled = true
ggui_screenshot_exists = true
ggui_screenshot_file_count = 1
ggui_screenshot_size_bytes > 0
ggui_video_enabled = false
ggui_video_file_count = 0
ggui_render_report_exists = true
ggui_render_report_pass = true
```

Squid proxy geometry:

```text
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
squid_proxy_enabled = true
procedural_geometry_enabled = true
real_geometry_candidate_enabled = false
real_geometry_enabled = false
geometry_quality_report_exists = true
geometry_quality_report_pass = true
sampling_particle_count = 1024
mantle_particle_count > 0
head_particle_count > 0
arms_particle_count > 0
```

Runtime geometry diagnostic-only:

```text
runtime_geometry_enabled = true
geometry_motion_application_mode = diagnostic_only
geometry_motion_interface_report_exists = true
geometry_motion_interface_report_pass = true
diagnostic_only = true
no_op_pass = true
mutation_flag_enabled_count = 0
mutate_geometry_state = false
```

Wall velocity solid_vel:

```text
wall_velocity_enabled = true
wall_velocity_application_mode = solid_vel_experimental
wall_velocity_application_report_exists = true
wall_velocity_application_report_pass = true
target_lbm_field = solid_vel
apply_to_lbm_solid_vel = true
apply_to_lbm_populations = false
modify_bounceback_formula = false
finite_pass = true
cap_pass = true
lbm_population_update_count = 0
```

Closed outputs and features:

```text
write_vtk = false
write_particles = false
vtr_output_count = 0
particle_npy_output_count = 0
ggui_video_file_count = 0
real_geometry_candidate_enabled = false
link_area_enabled = false
grid_64_enabled = false
dense_wall_velocity_output_count = 0
dense_displacement_output_count = 0
```

Conservative smoke numeric bounds:

```text
rho_min_min > 0.90
rho_max_max < 1.10
lbm_max_v_max < 0.5
mpm_min_J_min > 0.0
mpm_max_speed_max < 10.0
projected_mass_final > 0.0
active_cell_count_final > 0
bb_link_count_max > 0
max_grid_reaction_norm_max finite
```

## Matrix Summary Requirements

```text
step98_48cube_taichi_ggui_visualization_smoke_matrix_pass = true
required_row_count = 1
optional_row_count = 0
required_stable_count = 1
activation_feature_count = 5
grid_48_enabled_count = 1
grid_64_enabled_count = 0
squid_proxy_enabled_count = 1
runtime_geometry_enabled_count = 1
wall_velocity_enabled_count = 1
combined_runtime_geometry_wall_velocity_enabled_count = 1
ggui_visualization_enabled_count = 1
ggui_screenshot_count = 1
ggui_video_file_count = 0
vtr_output_count = 0
particle_npy_output_count = 0
min_completed_lbm_steps = 1
min_diagnostics_row_count >= 2
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = 48cube_taichi_ggui_visualization_smoke_only
```

## Output Guard Requirements

```text
output_guard_pass = true
step98_required_driver_run_dir_count = 1
step98_optional_driver_run_dir_count = 0
step98_ggui_screenshot_count = 1
step98_ggui_video_count = 0
step98_vtr_count = 0
step98_particle_npy_count = 0
step98_raw_geometry_output_count = 0
step98_real_geometry_candidate_output_count = 0
step98_dense_wall_velocity_output_count = 0
step98_sparse_wall_velocity_output_count = 0
step98_dense_displacement_output_count = 0
step98_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
artifact_budget_pass = true
```

Artifact budget:

```text
step98_file_count <= 110
step98_total_size_mb < 15
large_file_count = 0
```

## Regression Guards

Step97 regression must prove:

```text
step97_48cube_taichi_ggui_visualization_expansion_plan_pass = true
step97_48cube_taichi_ggui_visualization_expansion_guard_pass = true
step97_step96_regression_guard_pass = true
step97_step94_regression_guard_pass = true
step97_step92_regression_guard_pass = true
step97_output_guard_pass = true
step97_artifact_budget_pass = true
step97_activation_feature_count = 0
planned_step98_activation_feature_count = 5
step97_driver_run_dir_count = 0
step97_ggui_screenshot_count = 0
step97_ggui_video_count = 0
step97_vtr_count = 0
step97_particle_npy_count = 0
```

Step96 regression must prove:

```text
step96_taichi_ggui_10step_visualization_run_matrix_pass = true
step96_taichi_ggui_10step_visualization_quality_pass = true
step96_activation_guard_pass = true
step96_output_guard_pass = true
step96_artifact_budget_pass = true
step96_activation_feature_count = 4
step96_completed_lbm_steps = 10
step96_squid_proxy_enabled_count = 1
step96_runtime_geometry_enabled_count = 1
step96_wall_velocity_enabled_count = 1
step96_ggui_screenshot_count = 1
step96_ggui_video_count = 0
step96_vtr_count = 0
step96_particle_npy_count = 0
step96_grid_48_enabled_count = 0
step96_grid_64_enabled_count = 0
```

Step94 regression must prove:

```text
step94_taichi_ggui_visualization_smoke_matrix_pass = true
step94_taichi_ggui_visualization_quality_pass = true
step94_activation_guard_pass = true
step94_output_guard_pass = true
step94_artifact_budget_pass = true
step94_activation_feature_count = 4
step94_completed_lbm_steps = 1
step94_ggui_screenshot_count = 1
step94_ggui_video_count = 0
step94_vtr_count = 0
step94_particle_npy_count = 0
```

## Tests

Add contract tests:

```text
tests/test_step98_48cube_taichi_ggui_visualization_smoke_matrix_contract.py
tests/test_step98_48cube_taichi_ggui_visualization_quality_contract.py
tests/test_step98_activation_guard_contract.py
tests/test_step98_output_guard_contract.py
tests/test_step98_step97_regression_contract.py
tests/test_step98_step96_regression_contract.py
tests/test_step98_step94_regression_contract.py
```

Use TDD:

1. Add Step98 contract tests first.
2. Confirm the focused Step98 test set fails because Step98 artifacts are
   missing.
3. Implement configs, runners, evidence builders, docs, and reports.
4. Generate Step98 driver/GGUI outputs and audit artifacts.
5. Rerun focused Step98 tests and full suites.

## Verification Commands

Baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step98_48cube_taichi_ggui_visualization_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step98_48cube_taichi_ggui_visualization_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step98_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step98_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step98_step97_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step98_step96_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step98_step94_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step98_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step98_48cube_taichi_ggui_visualization_smoke_matrix_contract.py tests\test_step98_48cube_taichi_ggui_visualization_quality_contract.py tests\test_step98_activation_guard_contract.py tests\test_step98_output_guard_contract.py tests\test_step98_step97_regression_contract.py tests\test_step98_step96_regression_contract.py tests\test_step98_step94_regression_contract.py -q
```

Full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Git and guard checks:

```powershell
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
git status --short src/mpm_lbm/sim
git status --short src/mpm_lbm/diagnostics
```

Run the user-specified legacy visualization-output grep from the attachment.
It must return no output. Do not add those legacy tokens to Step98 files.

## Report Requirements

`STEP98_48CUBE_TAICHI_GGUI_VISUALIZATION_SMOKE_REPORT.md` must state:

```text
Step98 accepted.
Step98 runs exactly one required 48^3 GGUI visualization smoke row:
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke
```

It must list the row values, state that the only grid expansion from Step96 is
`n_grid = 32 -> 48`, state that `n_lbm_steps = 10 -> 1` is intentional smoke
isolation, list the single screenshot artifact, and explicitly close VTR,
particle NPY, video, 64^3, real geometry candidate data, link-area transfer,
geometry mutation, solver formula changes, 48^3 production readiness, physical
validation, squid swimming, and real squid validation.

## Completion Criteria

Step98 is done only when all of the following are true:

1. The detailed goal file is committed.
2. The active `/goal` equivalent references this file.
3. Step98 contract tests have a RED-to-GREEN trail.
4. Exactly one Step98 driver row ran through the canonical driver.
5. Exactly one Step98 GGUI screenshot exists and no video exists.
6. Step98 matrix, quality, activation, output, regression, and artifact
   manifest artifacts are generated and committed.
7. No forbidden runtime, diagnostics, vendored, or real-geometry candidate
   paths are edited.
8. Focused Step98 tests pass.
9. Full pytest passes with `D:\working\taichi\env\python.exe`.
10. Full pytest passes with `D:\TOOL\Anaconda\python.exe`.
11. Pre-push hook passes.
12. The final commit is pushed to `origin/main`.
13. The final response reports the commit hash, remote branch, pass counts, and
    Step98 artifact-manifest summary.

## Next-Step Guardrail

If Step98 is green, the suggested next direction is not directly 48^3 / 10-step.
The next bounded route should be a 48^3 / 5-step plan-and-guard step, then a
48^3 / 5-step run. Step98 alone only proves a 48^3 / 1-step smoke.
