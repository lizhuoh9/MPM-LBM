# Step94 Taichi GGUI Visualization Smoke Goal

## Commit Baseline

The repository baseline for this step is:

```text
origin/main = 40045c06ad79d122eafa10dc7eef5d98e6adb158
test: replace step93 vtr output plan with taichi ggui visualization plan
```

Step93 is accepted as a Taichi GGUI visualization enablement plan and guard.
The old Step93 VTR route is not part of the current tree, and Step94 has not
started at this baseline.

The intended Step94 commit message is:

```text
test: add step94 taichi ggui visualization smoke
```

## Step Name

```text
Step94 Taichi GGUI Visualization Smoke
```

## Purpose

Step94 is the first Taichi GGUI visualization smoke over the first-user
simulation envelope.

Step94 must run one minimal 32^3 / 1-step smoke and render that envelope through
Taichi GGUI. It is intentionally not a VTR output step, not a particle NPY
export step, not a 48^3 or 64^3 step, not a real-geometry step, and not a
production visualization campaign.

The only allowed claim is:

```text
Taichi GGUI visualization path can render the first-user envelope in a minimal 32^3 / 1-step smoke.
```

Step94 must not claim production visualization readiness, full interactive
visualization campaign readiness, physical validation, squid swimming, real
squid validation, or production readiness.

## Required Row

Step94 must run exactly one required row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke
```

No optional row is allowed.

## Driver Envelope

The canonical driver row must use:

```text
n_grid = 32
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
geometry_motion_application_mode = diagnostic_only
geometry_motion_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_application_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json

boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json

wall_velocity_application_mode = solid_vel_experimental
wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json
target_lbm_field = solid_vel

write_vtk = false
write_particles = false
```

The row must use the canonical driver:

```python
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

config = FSIDriverConfig.from_json(
    "configs/step94_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke.json"
)

driver = FSIDriver3D(
    config,
    "outputs/step94_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke",
)

diagnostics = driver.run()
```

## GGUI Configuration Boundary

Do not add unknown `ggui_*` fields to `FSIDriverConfig` if the canonical driver
schema does not accept them. Prefer a separate visualization config read only by
the Step94 evidence renderer:

```text
configs/step94_taichi_ggui_visualization_config.json
```

That independent config must encode:

```text
ggui_visualization_enabled = true
window_title = Step94 GGUI First User Envelope Smoke
window_resolution = [1280, 720]
render_frames = 1
screenshot_enabled = true
screenshot_path = outputs/step94_ggui_visualization/step94_ggui_visual_smoke.png
video_enabled = false
camera_position = [1.6, 1.2, 1.6]
camera_lookat = [0.5, 0.5, 0.5]
camera_up = [0.0, 1.0, 0.0]
visualize_squid_proxy_points = true
visualize_domain_box = true
visualize_boundary_motion_proxy = true
visualize_wall_velocity_proxy = true
max_visual_points = 4096
```

Step94 must call an independent renderer after the driver run:

```python
render_step94_ggui_visual_smoke(
    driver_run_dir="outputs/step94_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke",
    ggui_config_path="configs/step94_taichi_ggui_visualization_config.json",
    output_dir="outputs/step94_ggui_visualization",
)
```

The renderer may read driver outputs, `geometry_quality_report.json`,
`driver_config.json`, the geometry config, diagnostics artifacts, or
deterministic visualization proxy points generated from
`configs/step85_squid_proxy_geometry_1024.json`. It must not modify solver
runtime, driver schemas, coupling code, geometry code, motion code, or wall
velocity code.

If driver outputs cannot reconstruct full physical particle trajectories, the
renderer may visualize deterministic procedural squid-proxy points. In that
case the report must explicitly state:

```text
GGUI visualizes procedural squid_proxy visualization proxy points, not exported physical particle trajectories.
```

## Minimal Visual Content

The screenshot must contain, at minimum:

```text
domain bounding box
squid_proxy sampled/component points
optional active-cell proxy points
optional boundary-motion or wall-velocity proxy arrows/line segments
fixed camera at [1.6, 1.2, 1.6] looking at [0.5, 0.5, 0.5]
one rendered frame
one PNG screenshot
```

## Files To Add

Root:

```text
STEP94_TAICHI_GGUI_VISUALIZATION_SMOKE_GOAL.md
STEP94_TAICHI_GGUI_VISUALIZATION_SMOKE_REPORT.md
```

Configs:

```text
configs/step94_taichi_ggui_visualization_smoke_matrix.json
configs/step94_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke.json
configs/step94_taichi_ggui_visualization_config.json
configs/step94_taichi_ggui_visualization_acceptance_policy.json
configs/step94_activation_guard_policy.json
configs/step94_output_guard_policy.json
configs/step94_step93_regression_policy.json
configs/step94_step92_regression_policy.json
configs/step94_step90_regression_policy.json
configs/step94_artifact_manifest_policy.json
```

Evidence scripts:

```text
src/mpm_lbm/evidence/step94_taichi_ggui_visualization_smoke_runner.py
src/mpm_lbm/evidence/step94_taichi_ggui_visualization_smoke_audit.py
src/mpm_lbm/evidence/step94_taichi_ggui_visualization_quality_audit.py
src/mpm_lbm/evidence/step94_activation_guard.py
src/mpm_lbm/evidence/step94_output_guard.py
src/mpm_lbm/evidence/step94_step93_regression_guard.py
src/mpm_lbm/evidence/step94_step92_regression_guard.py
src/mpm_lbm/evidence/step94_step90_regression_guard.py
```

Baseline runners:

```text
baseline_tests/step94_common.py
baseline_tests/run_step94_taichi_ggui_visualization_smoke_matrix.py
baseline_tests/run_step94_taichi_ggui_visualization_quality.py
baseline_tests/run_step94_activation_guard.py
baseline_tests/run_step94_output_guard.py
baseline_tests/run_step94_step93_regression_guard.py
baseline_tests/run_step94_step92_regression_guard.py
baseline_tests/run_step94_step90_regression_guard.py
baseline_tests/run_step94_artifact_manifest.py
```

Tests:

```text
tests/test_step94_taichi_ggui_visualization_smoke_matrix_contract.py
tests/test_step94_taichi_ggui_visualization_quality_contract.py
tests/test_step94_activation_guard_contract.py
tests/test_step94_output_guard_contract.py
tests/test_step94_step93_regression_contract.py
tests/test_step94_step92_regression_contract.py
tests/test_step94_step90_regression_contract.py
```

Docs:

```text
docs/94_taichi_ggui_visualization_smoke.md
```

Artifact directories:

```text
outputs/step94_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke/
outputs/step94_ggui_visualization/
outputs/step94_taichi_ggui_visualization_smoke_matrix/
outputs/step94_taichi_ggui_visualization_quality/
outputs/step94_activation_guard/
outputs/step94_output_guard/
outputs/step94_step93_regression_guard/
outputs/step94_step92_regression_guard/
outputs/step94_step90_regression_guard/
outputs/step94_artifact_manifest/
```

Logs:

```text
logs/step94_*.log
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

Step94 must not edit:

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

If GGUI smoke fails, inspect the GGUI config, visualization runner, local
desktop/backend availability, screenshot path, field conversion, and output
guard assumptions. Do not change solver runtime to make the visualization pass.

## Expected Outputs

The required driver run directory is:

```text
outputs/step94_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke/
```

Allowed driver files:

```text
boundary_motion_interface_report.json
diagnostics_timeseries.csv
diagnostics_timeseries.npz
driver_config.json
driver_timing.json
geo_all_fluid_32.dat
geometry_motion_interface_report.json
geometry_quality_report.json
wall_velocity_application_report.json
```

The GGUI output directory is:

```text
outputs/step94_ggui_visualization/
```

Allowed GGUI files:

```text
step94_ggui_visual_smoke.png
step94_ggui_visualization_report.json
step94_ggui_visualization_metadata.json
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
```

## Acceptance Criteria

Driver run:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke
n_grid = 32
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

GGUI:

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

Required disabled surfaces:

```text
write_vtk = false
write_particles = false
vtr_output_count = 0
particle_npy_output_count = 0
real_geometry_candidate_enabled = false
link_area_enabled = false
grid_48_enabled = false
grid_64_enabled = false
dense_wall_velocity_output_count = 0
dense_displacement_output_count = 0
```

Numerical smoke bounds:

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

## Output Guard Criteria

```text
output_guard_pass = true
step94_required_driver_run_dir_count = 1
step94_optional_driver_run_dir_count = 0
step94_ggui_screenshot_count = 1
step94_ggui_video_count = 0
step94_vtr_count = 0
step94_particle_npy_count = 0
step94_raw_geometry_output_count = 0
step94_real_geometry_candidate_output_count = 0
step94_dense_wall_velocity_output_count = 0
step94_sparse_wall_velocity_output_count = 0
step94_dense_displacement_output_count = 0
step94_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
artifact_budget_pass = true
step94_file_count <= 100
step94_total_size_mb < 10
large_file_count = 0
```

## Regression Guards

Step93 regression guard must prove:

```text
step93_taichi_ggui_visualization_enablement_plan_pass = true
step93_taichi_ggui_visualization_enablement_guard_pass = true
step93_step92_regression_guard_pass = true
step93_step91_regression_guard_pass = true
step93_step90_regression_guard_pass = true
step93_output_guard_pass = true
step93_artifact_budget_pass = true
step93_activation_feature_count = 0
planned_step94_activation_feature_count = 4
step93_driver_run_dir_count = 0
step93_ggui_screenshot_count = 0
step93_particle_npy_count = 0
vtr_file_count = 0
```

Step92 regression guard must prove:

```text
step92_first_user_simulation_10step_dry_run_matrix_pass = true
step92_first_user_simulation_10step_dry_run_quality_pass = true
step92_activation_guard_pass = true
step92_output_guard_pass = true
step92_artifact_budget_pass = true
step92_activation_feature_count = 3
step92_squid_proxy_enabled_count = 1
step92_runtime_geometry_enabled_count = 1
step92_wall_velocity_enabled_count = 1
step92_completed_lbm_steps = 10
step92_vtr_count = 0
step92_particle_npy_count = 0
```

Step90 regression guard must prove:

```text
step90_first_user_simulation_dry_run_matrix_pass = true
step90_first_user_simulation_dry_run_quality_pass = true
step90_activation_guard_pass = true
step90_output_guard_pass = true
step90_artifact_budget_pass = true
step90_activation_feature_count = 3
step90_completed_lbm_steps = 5
step90_vtr_count = 0
step90_particle_npy_count = 0
```

## Verification Commands

Baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step94_taichi_ggui_visualization_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step94_taichi_ggui_visualization_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step94_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step94_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step94_step93_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step94_step92_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step94_step90_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step94_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step94_taichi_ggui_visualization_smoke_matrix_contract.py tests\test_step94_taichi_ggui_visualization_quality_contract.py tests\test_step94_activation_guard_contract.py tests\test_step94_output_guard_contract.py tests\test_step94_step93_regression_contract.py tests\test_step94_step92_regression_contract.py tests\test_step94_step90_regression_contract.py -q
```

Full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Git checks:

```powershell
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Run the legacy Step93 file-visualization route-token grep from the source
instructions. The final grep should produce no output.

## Report Requirements

`STEP94_TAICHI_GGUI_VISUALIZATION_SMOKE_REPORT.md` must state:

```text
Step94 accepted.

Step94 runs exactly one required GGUI visualization smoke row:
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke

The row uses 32^3, 1024 particles, 1 LBM step, 1 MPM substep per LBM step,
moving_boundary, engineering, target_u_lbm = [0.0, 0.0, 0.0],
geometry_type = squid_proxy, geometry_motion_application_mode =
diagnostic_only, wall_velocity_application_mode = solid_vel_experimental,
target_lbm_field = solid_vel, ggui_visualization_enabled = true,
write_vtk = false, and write_particles = false.

Step94 opens/renders through Taichi GGUI and writes one screenshot artifact.
Step94 does not write VTR.
Step94 does not write particle NPY.
Step94 does not write video.
Step94 does not enable real geometry candidate data.
Step94 does not enable link-area transfer.
Step94 does not enable 48^3 or 64^3.
Step94 does not mutate geometry.
Step94 does not change solver formulas.
Step94 does not claim physical validation, squid swimming, real squid
validation, or production readiness.

Correct claim:
Taichi GGUI visualization path can render the first-user envelope in a minimal 32^3 / 1-step smoke.
```

## Future Steps Reserved

If Step94 is green, the next intended direction is:

```text
Step95 Taichi GGUI 10-Step First User Visualization Plan And Guard
Step96 Taichi GGUI 10-Step First User Visualization Run
```

Step94 must not directly do 10-step GGUI, video, particle NPY, 48^3, 64^3, or
real geometry.
