# Step101 48cube 10-Step Taichi GGUI Visualization Plan And Guard Goal

## Source State

The source attachment says GitHub is aligned at:

```text
origin/main = c0f74ad299451b1f27ce172bf77e7d497e8022a0
```

The accepted predecessor is:

```text
Step100 accepted.
```

Step100's accepted claim is limited to:

```text
48^3 / 5-step Taichi GGUI visualization run passed for the first-user envelope.
```

Step101 has not started. Step101 must be:

```text
Step101 48^3 / 10-Step Taichi GGUI Visualization Plan And Guard
```

Suggested commit message:

```text
test: add step101 48cube 10step taichi ggui visualization plan and guard
```

## Objective

Implement Step101 as a plan-and-guard-only step for a future Step102 48^3 / 10-step Taichi GGUI visualization run.

Step101 must not run simulation. Step101 must not run GGUI. Step101 must not write screenshots or driver-run outputs. Its only purpose is to create the configs, guards, regression evidence, docs, report, tests, output guard, and artifact manifest that define the exact future Step102 envelope.

## Correct Step101 Claim

Step101 may claim only:

```text
48^3 / 10-step Taichi GGUI visualization run is planned and guarded for Step102.
```

Step101 must not claim:

```text
48^3 / 10-step run passed
48^3 production ready
64^3 ready
physical validation complete
real squid validated
squid swimming works
grid convergence complete
```

## Runtime Prohibitions

Step101 must not execute:

```text
FSIDriver3D
driver.run()
simulation
GGUI window
screenshot
video
VTR
particle NPY
```

Step101 must not modify:

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

Step101 must not activate:

```text
64^3
real geometry candidate data
link_area
VTR
particle NPY
video output
dense wall velocity output
dense displacement output
solver formula changes
tau migration
physical validation claim
production readiness claim
real squid validation claim
squid swimming claim
squid actuation claim
grid convergence claim
```

## Future Step102 Envelope

Step101 must plan exactly one future Step102 required row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_10step_ggui_visual_run
```

Step102 may later run only:

```text
n_grid = 48
n_particles = 1024
n_lbm_steps = 10
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
geometry_motion_report_enabled = true
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

The only intended change from Step100 to the planned Step102 row is:

```text
n_lbm_steps = 5 -> 10
```

Everything else must remain unchanged from Step100:

```text
n_grid = 48
n_particles = 1024
mpm_substeps_per_lbm_step = 1
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
runtime geometry = diagnostic_only
wall velocity = solid_vel_experimental
GGUI screenshot = true for Step102 only
GGUI video = false
write_vtk = false
write_particles = false
real geometry = false
link_area = false
grid_64 = false
```

## Required Files

Add these Step101 root artifacts:

```text
STEP101_48CUBE_10STEP_TAICHI_GGUI_VISUALIZATION_PLAN_AND_GUARD_GOAL.md
STEP101_48CUBE_10STEP_TAICHI_GGUI_VISUALIZATION_PLAN_AND_GUARD_REPORT.md
```

Add these configs:

```text
configs/step101_48cube_10step_taichi_ggui_visualization_plan.json
configs/step101_48cube_10step_taichi_ggui_visualization_guard_policy.json
configs/step101_step100_regression_policy.json
configs/step101_step99_regression_policy.json
configs/step101_step98_regression_policy.json
configs/step101_output_guard_policy.json
configs/step101_artifact_manifest_policy.json
```

Add these evidence modules:

```text
src/mpm_lbm/evidence/step101_48cube_10step_taichi_ggui_visualization_plan.py
src/mpm_lbm/evidence/step101_48cube_10step_taichi_ggui_visualization_guard.py
src/mpm_lbm/evidence/step101_step100_regression_guard.py
src/mpm_lbm/evidence/step101_step99_regression_guard.py
src/mpm_lbm/evidence/step101_step98_regression_guard.py
src/mpm_lbm/evidence/step101_output_guard.py
```

Add these baseline runners:

```text
baseline_tests/step101_common.py
baseline_tests/run_step101_48cube_10step_taichi_ggui_visualization_plan.py
baseline_tests/run_step101_48cube_10step_taichi_ggui_visualization_guard.py
baseline_tests/run_step101_step100_regression_guard.py
baseline_tests/run_step101_step99_regression_guard.py
baseline_tests/run_step101_step98_regression_guard.py
baseline_tests/run_step101_output_guard.py
baseline_tests/run_step101_artifact_manifest.py
```

Add these contract tests:

```text
tests/test_step101_48cube_10step_taichi_ggui_visualization_plan_contract.py
tests/test_step101_48cube_10step_taichi_ggui_visualization_guard_contract.py
tests/test_step101_step100_regression_contract.py
tests/test_step101_step99_regression_contract.py
tests/test_step101_step98_regression_contract.py
tests/test_step101_output_guard_contract.py
```

Add this doc:

```text
docs/101_48cube_10step_taichi_ggui_visualization_plan_and_guard.md
```

Generate these outputs:

```text
outputs/step101_48cube_10step_taichi_ggui_visualization_plan/
outputs/step101_48cube_10step_taichi_ggui_visualization_guard/
outputs/step101_step100_regression_guard/
outputs/step101_step99_regression_guard/
outputs/step101_step98_regression_guard/
outputs/step101_output_guard/
outputs/step101_artifact_manifest/
```

Generate:

```text
logs/step101_*.log
```

Allowed doc updates:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

Only update optional docs if they already exist and clearly track the same Step surface. At minimum, README and the Step101 doc/report must be aligned.

## Step101 Plan Config Requirements

`configs/step101_48cube_10step_taichi_ggui_visualization_plan.json` must include:

```text
step = Step101
campaign_id = step101_48cube_10step_taichi_ggui_visualization_plan_and_guard
previous_step = Step100
previous_required_commit = c0f74ad299451b1f27ce172bf77e7d497e8022a0
activation_kind = 48cube_10step_taichi_ggui_visualization_plan_only
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
ggui_run_allowed = false
screenshot_output_allowed_in_step101 = false
step102_allowed = true
step102_allowed_row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_10step_ggui_visual_run
step102_allowed_n_grid = 48
step102_allowed_n_particles = 1024
step102_allowed_n_lbm_steps = 10
step102_allowed_mpm_substeps_per_lbm_step = 1
step102_allowed_coupling_mode = moving_boundary
step102_allowed_reaction_transfer_mode = engineering
step102_allowed_output_interval = 1
from_step100_duration_expansion = true
previous_step100_n_grid = 48
previous_step100_n_lbm_steps = 5
planned_step102_n_grid = 48
planned_step102_n_lbm_steps = 10
only_new_dimension_from_step100 = n_lbm_steps_10
ggui_visualization_planned_for_step102 = true
ggui_interactive_window_allowed_for_step102 = true
ggui_screenshot_allowed_for_step102 = true
ggui_video_allowed_for_step102 = false
ggui_required_backend_policy = local_desktop_taichi_environment
ggui_screenshot_count_allowed_for_step102 = 1
squid_proxy_planned_for_step102 = true
geometry_type_allowed_for_step102 = squid_proxy
geometry_config_path_allowed_for_step102 = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled_allowed_for_step102 = true
quality_check_strict_allowed_for_step102 = false
geometry_quality_report_required_for_step102 = true
runtime_geometry_planned_for_step102 = true
geometry_motion_mode_allowed_for_step102 = prescribed_kinematic
geometry_motion_application_mode_allowed_for_step102 = diagnostic_only
geometry_motion_config_path_allowed_for_step102 = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_application_config_path_allowed_for_step102 = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_interface_report_required_for_step102 = true
geometry_mutation_allowed = false
wall_velocity_planned_for_step102 = true
boundary_motion_mode_allowed_for_step102 = prescribed_kinematic
boundary_motion_config_path_allowed_for_step102 = configs/step34_boundary_motion_interface_prescribed_kinematic.json
boundary_motion_report_required_for_step102 = true
wall_velocity_application_mode_allowed_for_step102 = solid_vel_experimental
wall_velocity_application_config_path_allowed_for_step102 = configs/step36_wall_velocity_application_solid_vel_experimental.json
wall_velocity_application_report_required_for_step102 = true
target_lbm_field_planned_for_step102 = solid_vel
target_u_lbm_allowed_for_step102 = [0.0, 0.0, 0.0]
target_u_lbm_policy = same_zero_background_flow_as_step90_step92_step94_step96_step98_step100
combined_runtime_geometry_wall_velocity_planned_for_step102 = true
planned_step102_activation_feature_count = 5
step101_activation_feature_count = 0
write_vtk_allowed = false
write_particles_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
video_output_allowed = false
real_geometry_allowed = false
real_geometry_candidate_data_allowed = false
link_area_allowed = false
grid_64_allowed = false
dense_wall_velocity_output_allowed = false
dense_displacement_output_allowed = false
runtime_code_changed = false
solver_behavior_changed = false
solver_formula_change_allowed = false
tau_migration_allowed = false
physical_validation_claim_allowed = false
production_readiness_claim_allowed = false
real_squid_validation_claim_allowed = false
squid_swimming_claim_allowed = false
squid_actuation_claim_allowed = false
grid_convergence_claim_allowed = false
```

## Step101 Guard Policy Requirements

`configs/step101_48cube_10step_taichi_ggui_visualization_guard_policy.json` must check the plan artifact and enforce:

```text
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
ggui_run_allowed = false
screenshot_output_allowed_in_step101 = false
step101_activation_feature_count = 0
planned_step102_activation_feature_count = 5
step102_allowed_row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_10step_ggui_visual_run
step102_allowed_n_grid = 48
step102_allowed_n_particles = 1024
step102_allowed_n_lbm_steps = 10
step102_allowed_mpm_substeps_per_lbm_step = 1
from_step100_duration_expansion = true
previous_step100_n_grid = 48
previous_step100_n_lbm_steps = 5
planned_step102_n_grid = 48
planned_step102_n_lbm_steps = 10
only_new_dimension_from_step100 = n_lbm_steps_10
ggui_visualization_planned_for_step102 = true
ggui_screenshot_allowed_for_step102 = true
ggui_video_allowed_for_step102 = false
squid_proxy_planned_for_step102 = true
runtime_geometry_planned_for_step102 = true
wall_velocity_planned_for_step102 = true
combined_runtime_geometry_wall_velocity_planned_for_step102 = true
geometry_motion_application_mode_allowed_for_step102 = diagnostic_only
wall_velocity_application_mode_allowed_for_step102 = solid_vel_experimental
target_lbm_field_planned_for_step102 = solid_vel
target_u_lbm_allowed_for_step102 = [0.0, 0.0, 0.0]
write_vtk_allowed = false
write_particles_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
video_output_allowed = false
real_geometry_allowed = false
real_geometry_candidate_data_allowed = false
link_area_allowed = false
grid_64_allowed = false
physical_validation_claim_allowed = false
production_readiness_claim_allowed = false
real_squid_validation_claim_allowed = false
squid_swimming_claim_allowed = false
grid_convergence_claim_allowed = false
```

## Required Output Summaries

Plan output:

```text
outputs/step101_48cube_10step_taichi_ggui_visualization_plan/48cube_10step_taichi_ggui_visualization_plan.json
outputs/step101_48cube_10step_taichi_ggui_visualization_plan/48cube_10step_taichi_ggui_visualization_plan.csv
outputs/step101_48cube_10step_taichi_ggui_visualization_plan/48cube_10step_taichi_ggui_visualization_plan_summary.csv
```

Plan summary must include:

```text
step101_48cube_10step_taichi_ggui_visualization_plan_pass = true
previous_step = Step100
previous_commit = c0f74ad299451b1f27ce172bf77e7d497e8022a0
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
ggui_run_allowed = false
screenshot_output_allowed_in_step101 = false
step102_allowed = true
step102_allowed_row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_10step_ggui_visual_run
step102_allowed_n_grid = 48
step102_allowed_n_particles = 1024
step102_allowed_n_lbm_steps = 10
from_step100_duration_expansion = true
previous_step100_n_grid = 48
previous_step100_n_lbm_steps = 5
planned_step102_n_grid = 48
planned_step102_n_lbm_steps = 10
ggui_visualization_planned_for_step102 = true
ggui_screenshot_allowed_for_step102 = true
ggui_video_allowed_for_step102 = false
write_vtk_allowed = false
write_particles_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
video_output_allowed = false
step101_activation_feature_count = 0
planned_step102_activation_feature_count = 5
real_geometry_allowed = false
link_area_allowed = false
grid_64_allowed = false
grid_convergence_claim_allowed = false
```

Guard output:

```text
outputs/step101_48cube_10step_taichi_ggui_visualization_guard/48cube_10step_taichi_ggui_visualization_guard.json
outputs/step101_48cube_10step_taichi_ggui_visualization_guard/48cube_10step_taichi_ggui_visualization_guard.csv
outputs/step101_48cube_10step_taichi_ggui_visualization_guard/48cube_10step_taichi_ggui_visualization_guard_summary.csv
```

Guard summary must include:

```text
step101_48cube_10step_taichi_ggui_visualization_guard_pass = true
guard_row_count > 0
guard_pass_count = guard_row_count
step101_activation_feature_count = 0
planned_step102_activation_feature_count = 5
planned_step102_n_grid = 48
planned_step102_n_lbm_steps = 10
from_step100_duration_expansion = true
ggui_visualization_planned_for_step102 = true
ggui_screenshot_allowed_for_step102 = true
ggui_video_allowed_for_step102 = false
squid_proxy_planned_for_step102 = true
runtime_geometry_planned_for_step102 = true
wall_velocity_planned_for_step102 = true
combined_runtime_geometry_wall_velocity_planned_for_step102 = true
vtr_output_planned_for_step102 = false
particle_npy_output_planned_for_step102 = false
video_output_planned_for_step102 = false
real_geometry_planned_for_step102 = false
real_geometry_candidate_data_planned_for_step102 = false
link_area_planned_for_step102 = false
grid_64_planned_for_step102 = false
```

## Regression Guards

Step100 regression output:

```text
outputs/step101_step100_regression_guard/step100_regression_guard.json
outputs/step101_step100_regression_guard/step100_regression_guard.csv
outputs/step101_step100_regression_guard/step100_regression_guard_summary.csv
```

Step100 regression summary must check:

```text
step100_48cube_5step_taichi_ggui_visualization_run_matrix_pass = true
step100_48cube_5step_taichi_ggui_visualization_quality_pass = true
step100_activation_guard_pass = true
step100_output_guard_pass = true
step100_step99_regression_guard_pass = true
step100_step98_regression_guard_pass = true
step100_step96_regression_guard_pass = true
step100_artifact_budget_pass = true
step100_activation_feature_count = 5
step100_completed_lbm_steps = 5
step100_n_grid = 48
step100_grid_48_enabled_count = 1
step100_grid_64_enabled_count = 0
step100_squid_proxy_enabled_count = 1
step100_runtime_geometry_enabled_count = 1
step100_wall_velocity_enabled_count = 1
step100_ggui_screenshot_count = 1
step100_ggui_video_count = 0
step100_vtr_count = 0
step100_particle_npy_count = 0
```

Step99 regression output:

```text
outputs/step101_step99_regression_guard/step99_regression_guard.json
outputs/step101_step99_regression_guard/step99_regression_guard.csv
outputs/step101_step99_regression_guard/step99_regression_guard_summary.csv
```

Step99 regression summary must check:

```text
step99_48cube_5step_taichi_ggui_visualization_plan_pass = true
step99_48cube_5step_taichi_ggui_visualization_guard_pass = true
step99_step98_regression_guard_pass = true
step99_step97_regression_guard_pass = true
step99_step96_regression_guard_pass = true
step99_output_guard_pass = true
step99_artifact_budget_pass = true
step99_activation_feature_count = 0
planned_step100_activation_feature_count = 5
step99_driver_run_dir_count = 0
step99_ggui_screenshot_count = 0
step99_ggui_video_count = 0
step99_vtr_count = 0
step99_particle_npy_count = 0
```

Step98 regression output:

```text
outputs/step101_step98_regression_guard/step98_regression_guard.json
outputs/step101_step98_regression_guard/step98_regression_guard.csv
outputs/step101_step98_regression_guard/step98_regression_guard_summary.csv
```

Step98 regression summary must check:

```text
step98_48cube_taichi_ggui_visualization_smoke_matrix_pass = true
step98_48cube_taichi_ggui_visualization_quality_pass = true
step98_activation_guard_pass = true
step98_output_guard_pass = true
step98_artifact_budget_pass = true
step98_activation_feature_count = 5
step98_completed_lbm_steps = 1
step98_n_grid = 48
step98_grid_48_enabled_count = 1
step98_grid_64_enabled_count = 0
step98_squid_proxy_enabled_count = 1
step98_runtime_geometry_enabled_count = 1
step98_wall_velocity_enabled_count = 1
step98_ggui_screenshot_count = 1
step98_ggui_video_count = 0
step98_vtr_count = 0
step98_particle_npy_count = 0
```

## Output Guard Requirements

Step101 output guard artifacts:

```text
outputs/step101_output_guard/output_guard.json
outputs/step101_output_guard/output_guard.csv
outputs/step101_output_guard/output_guard_summary.csv
```

Summary must prove:

```text
output_guard_pass = true
step101_driver_run_dir_count = 0
step101_ggui_screenshot_count = 0
step101_ggui_video_count = 0
step101_vtr_count = 0
step101_particle_npy_count = 0
step101_raw_geometry_output_count = 0
step101_real_geometry_candidate_output_count = 0
step101_dense_wall_velocity_output_count = 0
step101_sparse_wall_velocity_output_count = 0
step101_dense_displacement_output_count = 0
step101_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step101_large_file_count = 0
```

## Artifact Manifest Requirements

Step101 artifact manifest artifacts:

```text
outputs/step101_artifact_manifest/artifact_manifest.csv
outputs/step101_artifact_manifest/artifact_summary.csv
outputs/step101_artifact_manifest/artifact_summary.json
```

Summary target:

```text
artifact_budget_pass = true
step101_file_count <= 70
step101_total_size_mb < 5
step101_driver_run_dir_count = 0
step101_ggui_screenshot_count = 0
step101_ggui_video_count = 0
step101_vtr_count = 0
step101_particle_npy_count = 0
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step101_file_count = 0
protected_real_geometry_candidates_step101_file_count = 0
raw_geometry_file_count = 0
```

Do not hard-code exact final byte totals in the prose report. The report should point to `outputs/step101_artifact_manifest/artifact_summary.json` for exact file-count and size values.

## Test Contracts

Add tests for:

```text
tests/test_step101_48cube_10step_taichi_ggui_visualization_plan_contract.py
tests/test_step101_48cube_10step_taichi_ggui_visualization_guard_contract.py
tests/test_step101_step100_regression_contract.py
tests/test_step101_step99_regression_contract.py
tests/test_step101_step98_regression_contract.py
tests/test_step101_output_guard_contract.py
```

The plan contract must require:

```text
step101_48cube_10step_taichi_ggui_visualization_plan_pass = true
previous_step = Step100
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
ggui_run_allowed = false
screenshot_output_allowed_in_step101 = false
step102_allowed = true
step102_allowed_row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_10step_ggui_visual_run
step102_allowed_n_grid = 48
step102_allowed_n_particles = 1024
step102_allowed_n_lbm_steps = 10
from_step100_duration_expansion = true
previous_step100_n_grid = 48
previous_step100_n_lbm_steps = 5
planned_step102_n_grid = 48
planned_step102_n_lbm_steps = 10
ggui_visualization_planned_for_step102 = true
ggui_screenshot_allowed_for_step102 = true
ggui_video_allowed_for_step102 = false
write_vtk_allowed = false
write_particles_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
grid_64_allowed = false
grid_convergence_claim_allowed = false
step101_activation_feature_count = 0
planned_step102_activation_feature_count = 5
```

The guard contract must require:

```text
step101_48cube_10step_taichi_ggui_visualization_guard_pass = true
step101_activation_feature_count = 0
planned_step102_activation_feature_count = 5
planned_step102_n_grid = 48
planned_step102_n_lbm_steps = 10
from_step100_duration_expansion = true
ggui_visualization_planned_for_step102 = true
ggui_screenshot_allowed_for_step102 = true
ggui_video_allowed_for_step102 = false
squid_proxy_planned_for_step102 = true
runtime_geometry_planned_for_step102 = true
wall_velocity_planned_for_step102 = true
combined_runtime_geometry_wall_velocity_planned_for_step102 = true
vtr_output_planned_for_step102 = false
particle_npy_output_planned_for_step102 = false
video_output_planned_for_step102 = false
grid_64_planned_for_step102 = false
```

The output guard contract must require:

```text
output_guard_pass = true
step101_driver_run_dir_count = 0
step101_ggui_screenshot_count = 0
step101_ggui_video_count = 0
step101_vtr_count = 0
step101_particle_npy_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
```

## Verification Commands

Use the trusted Taichi interpreter for Step101 runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step101_48cube_10step_taichi_ggui_visualization_plan.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step101_48cube_10step_taichi_ggui_visualization_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step101_step100_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step101_step99_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step101_step98_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step101_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step101_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step101_48cube_10step_taichi_ggui_visualization_plan_contract.py tests\test_step101_48cube_10step_taichi_ggui_visualization_guard_contract.py tests\test_step101_step100_regression_contract.py tests\test_step101_step99_regression_contract.py tests\test_step101_step98_regression_contract.py tests\test_step101_output_guard_contract.py -q
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

Also run the legacy Step93 VTR token grep required by the source plan, but construct the search pattern outside committed files so the check does not self-match this Step101 goal/report/docs. The scan should return no output.

## Report Requirements

`STEP101_48CUBE_10STEP_TAICHI_GGUI_VISUALIZATION_PLAN_AND_GUARD_REPORT.md` must state:

```text
Step101 accepted.
Step101 is a plan-and-guard step only.
Step101 does not run FSIDriver3D.
Step101 does not call driver.run().
Step101 does not execute simulation.
Step101 does not open a GGUI window.
Step101 does not write screenshots.
Step101 does not write video.
Step101 does not write VTR.
Step101 does not write particle NPY.
```

The report must state that Step101 only plans and guards Step102:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_10step_ggui_visual_run
```

The report must state that Step102 may run exactly one 48^3 / 1024-particle / 10-step / moving_boundary / engineering row with:

```text
geometry_type = squid_proxy
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
target_u_lbm = [0.0, 0.0, 0.0]
ggui_visualization_enabled = true
ggui_screenshot_enabled = true
ggui_video_enabled = false
write_vtk = false
write_particles = false
```

The report must explicitly state:

```text
The only intended expansion from Step100 is:
n_lbm_steps = 5 -> 10
```

The report must forbid:

```text
64^3
VTR
particle NPY
video
real geometry candidate data
link-area transfer
solver formula changes
grid convergence claim
48^3 production readiness claim
physical validation claim
squid swimming claim
real squid validation claim
```

## README And Docs

Update README so it includes Step101 in the implemented Step list and a Step101 boundary section near the Step98-Step100 entries.

Add `docs/101_48cube_10step_taichi_ggui_visualization_plan_and_guard.md` with the same boundary:

- Step101 is plan-and-guard only.
- Step101 runs no driver and writes no screenshot.
- Step101 plans exactly one future Step102 48^3 / 10-step GGUI visual run.
- The only planned expansion from Step100 is `n_lbm_steps = 5 -> 10`.
- All broader claims and output modes remain closed.

## Done Criteria

Step101 is done only when:

1. The detailed goal file exists and the active goal references it.
2. Step101 tests first fail before generated outputs exist, then pass after implementation.
3. Plan, guard, Step100 regression, Step99 regression, Step98 regression, output guard, and artifact manifest runners all pass.
4. Focused Step101 contract tests pass.
5. Full pytest passes with `D:\working\taichi\env\python.exe`.
6. Full pytest passes with `D:\TOOL\Anaconda\python.exe`.
7. `git diff --check` and `git diff --cached --check` pass.
8. Protected path status checks for solver, diagnostics, external Taichi LBM, and real geometry candidate data are clean.
9. The legacy Step93 VTR token grep returns no output without committing the tokens into Step101 files.
10. README, docs, goal, report, configs, evidence, baseline runners, tests, logs, and outputs are committed.
11. The commit is pushed to `origin/main`.
12. The final response reports the commit hash, branch, push result, and verification counts.
