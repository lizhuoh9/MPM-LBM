# Step97 48^3 Taichi GGUI First User Visualization Expansion Plan And Guard Goal

## Source Baseline

The user verified GitHub before this work:

```text
origin/main = 9ec9877b1f997777a9b43792c52b0f2b84d3814e
test: add step96 taichi ggui 10step first user visualization run
```

Step96 is accepted. Step97 has not started.

Step96 proved only this bounded claim:

```text
Taichi GGUI visualization can render the accepted 32^3 / 10-step first-user dry-run envelope.
```

Step97 must build the next bounded planning layer. It must not run the next
simulation or visualization.

## Step Name And Commit

Step name:

```text
Step97 48^3 Taichi GGUI First User Visualization Expansion Plan And Guard
```

Required commit message after implementation and verification:

```text
test: add step97 48cube taichi ggui visualization expansion plan and guard
```

## Objective

Implement Step97 as a plan-and-guard-only step for one future Step98 row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke
```

Step97 must establish the config, guards, regression evidence, output guard,
artifact manifest, docs, tests, report, and logs needed to prove the Step98
expansion is planned and bounded.

Step97 must not execute Step98.

## Allowed Claim

Step97 may claim exactly:

```text
48^3 Taichi GGUI visualization smoke is planned and guarded for Step98.
```

Step97 must not claim:

```text
48^3 run passed
48^3 ready
64^3 ready
production ready
physical validation complete
real squid validated
squid swimming works
```

## Strict Runtime Boundary

Step97 must not run or create:

```text
FSIDriver3D
driver.run()
simulation
GGUI window
screenshot
video
VTR
particle NPY
raw geometry output
real geometry candidate output
dense wall velocity output
sparse wall velocity output
dense displacement output
displaced-particle output
```

Step97 must not modify:

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

Step97 must not open or plan beyond its envelope:

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
```

## Planned Step98 Row

Step97 may plan exactly one future Step98 required row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke
```

Planned Step98 row values:

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

The intended changes from Step96 to the future Step98 row are exactly:

```text
n_grid = 32 -> 48
n_lbm_steps = 10 -> 1
```

The duration reduction is intentional grid-expansion smoke isolation, not a
claim that 10-step 48^3 is ready.

What must remain unchanged from the accepted Step96 envelope:

```text
n_particles = 1024
mpm_substeps_per_lbm_step = 1
geometry_type = squid_proxy
target_u_lbm = [0.0, 0.0, 0.0]
runtime geometry = diagnostic_only
wall velocity = solid_vel_experimental
write_vtk = false
write_particles = false
video = false
real geometry = false
link_area = false
```

## Required New Files

Root:

```text
STEP97_48CUBE_TAICHI_GGUI_VISUALIZATION_EXPANSION_PLAN_AND_GUARD_GOAL.md
STEP97_48CUBE_TAICHI_GGUI_VISUALIZATION_EXPANSION_PLAN_AND_GUARD_REPORT.md
```

Configs:

```text
configs/step97_48cube_taichi_ggui_visualization_expansion_plan.json
configs/step97_48cube_taichi_ggui_visualization_expansion_guard_policy.json
configs/step97_step96_regression_policy.json
configs/step97_step94_regression_policy.json
configs/step97_step92_regression_policy.json
configs/step97_output_guard_policy.json
configs/step97_artifact_manifest_policy.json
```

Evidence modules:

```text
src/mpm_lbm/evidence/step97_48cube_taichi_ggui_visualization_expansion_plan.py
src/mpm_lbm/evidence/step97_48cube_taichi_ggui_visualization_expansion_guard.py
src/mpm_lbm/evidence/step97_step96_regression_guard.py
src/mpm_lbm/evidence/step97_step94_regression_guard.py
src/mpm_lbm/evidence/step97_step92_regression_guard.py
src/mpm_lbm/evidence/step97_output_guard.py
```

Baseline runners:

```text
baseline_tests/step97_common.py
baseline_tests/run_step97_48cube_taichi_ggui_visualization_expansion_plan.py
baseline_tests/run_step97_48cube_taichi_ggui_visualization_expansion_guard.py
baseline_tests/run_step97_step96_regression_guard.py
baseline_tests/run_step97_step94_regression_guard.py
baseline_tests/run_step97_step92_regression_guard.py
baseline_tests/run_step97_output_guard.py
baseline_tests/run_step97_artifact_manifest.py
```

Tests:

```text
tests/test_step97_48cube_taichi_ggui_visualization_expansion_plan_contract.py
tests/test_step97_48cube_taichi_ggui_visualization_expansion_guard_contract.py
tests/test_step97_step96_regression_contract.py
tests/test_step97_step94_regression_contract.py
tests/test_step97_step92_regression_contract.py
tests/test_step97_output_guard_contract.py
```

Docs:

```text
docs/97_48cube_taichi_ggui_visualization_expansion_plan_and_guard.md
```

Outputs:

```text
outputs/step97_48cube_taichi_ggui_visualization_expansion_plan/
outputs/step97_48cube_taichi_ggui_visualization_expansion_guard/
outputs/step97_step96_regression_guard/
outputs/step97_step94_regression_guard/
outputs/step97_step92_regression_guard/
outputs/step97_output_guard/
outputs/step97_artifact_manifest/
```

Logs:

```text
logs/step97_*.log
```

Allowed docs updates:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

## Step97 Plan Config Contract

Create `configs/step97_48cube_taichi_ggui_visualization_expansion_plan.json`.
It must include, at minimum:

```text
step = Step97
campaign_id = step97_48cube_taichi_ggui_visualization_expansion_plan_and_guard
previous_step = Step96
previous_required_commit = 9ec9877b1f997777a9b43792c52b0f2b84d3814e

activation_kind = 48cube_taichi_ggui_visualization_expansion_plan_only
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
ggui_run_allowed = false
screenshot_output_allowed_in_step97 = false

step98_allowed = true
step98_allowed_row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke
step98_allowed_n_grid = 48
step98_allowed_n_particles = 1024
step98_allowed_n_lbm_steps = 1
step98_allowed_mpm_substeps_per_lbm_step = 1
step98_allowed_coupling_mode = moving_boundary
step98_allowed_reaction_transfer_mode = engineering
step98_allowed_output_interval = 1

from_step96_grid_expansion = true
previous_step96_n_grid = 32
planned_step98_n_grid = 48
duration_reduction_for_grid_expansion_isolation = true
previous_step96_n_lbm_steps = 10
planned_step98_n_lbm_steps = 1
only_new_dimension_from_step96 = n_grid_48

ggui_visualization_planned_for_step98 = true
ggui_interactive_window_allowed_for_step98 = true
ggui_screenshot_allowed_for_step98 = true
ggui_video_allowed_for_step98 = false
ggui_required_backend_policy = local_desktop_taichi_environment
ggui_screenshot_count_allowed_for_step98 = 1

squid_proxy_planned_for_step98 = true
geometry_type_allowed_for_step98 = squid_proxy
geometry_config_path_allowed_for_step98 = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled_allowed_for_step98 = true
quality_check_strict_allowed_for_step98 = false
geometry_quality_report_required_for_step98 = true

runtime_geometry_planned_for_step98 = true
geometry_motion_mode_allowed_for_step98 = prescribed_kinematic
geometry_motion_application_mode_allowed_for_step98 = diagnostic_only
geometry_motion_config_path_allowed_for_step98 = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_application_config_path_allowed_for_step98 = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_interface_report_required_for_step98 = true
geometry_motion_application_report_required_for_step98 = true
geometry_mutation_allowed = false

wall_velocity_planned_for_step98 = true
boundary_motion_mode_allowed_for_step98 = prescribed_kinematic
boundary_motion_config_path_allowed_for_step98 = configs/step34_boundary_motion_interface_prescribed_kinematic.json
boundary_motion_report_required_for_step98 = true
wall_velocity_application_mode_allowed_for_step98 = solid_vel_experimental
wall_velocity_application_config_path_allowed_for_step98 = configs/step36_wall_velocity_application_solid_vel_experimental.json
wall_velocity_application_report_required_for_step98 = true
target_lbm_field_planned_for_step98 = solid_vel

target_u_lbm_allowed_for_step98 = [0.0, 0.0, 0.0]
target_u_lbm_policy = same_zero_background_flow_as_step90_step92_step94_step96

combined_runtime_geometry_wall_velocity_planned_for_step98 = true
planned_step98_activation_feature_count = 5
step97_activation_feature_count = 0

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
```

## Step97 Guard Policy Contract

Create `configs/step97_48cube_taichi_ggui_visualization_expansion_guard_policy.json`.
It must check the Step97 plan artifact and prove:

```text
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
ggui_run_allowed = false
screenshot_output_allowed_in_step97 = false

step97_activation_feature_count = 0
planned_step98_activation_feature_count = 5

step98_allowed_row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke
step98_allowed_n_grid = 48
step98_allowed_n_particles = 1024
step98_allowed_n_lbm_steps = 1
step98_allowed_mpm_substeps_per_lbm_step = 1

from_step96_grid_expansion = true
previous_step96_n_grid = 32
planned_step98_n_grid = 48
duration_reduction_for_grid_expansion_isolation = true
previous_step96_n_lbm_steps = 10
planned_step98_n_lbm_steps = 1
only_new_dimension_from_step96 = n_grid_48

ggui_visualization_planned_for_step98 = true
ggui_screenshot_allowed_for_step98 = true
ggui_video_allowed_for_step98 = false

squid_proxy_planned_for_step98 = true
runtime_geometry_planned_for_step98 = true
wall_velocity_planned_for_step98 = true
combined_runtime_geometry_wall_velocity_planned_for_step98 = true

geometry_motion_application_mode_allowed_for_step98 = diagnostic_only
wall_velocity_application_mode_allowed_for_step98 = solid_vel_experimental
target_lbm_field_planned_for_step98 = solid_vel
target_u_lbm_allowed_for_step98 = [0.0, 0.0, 0.0]

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
```

## Required Evidence Outputs

Step97 plan output:

```text
outputs/step97_48cube_taichi_ggui_visualization_expansion_plan/48cube_taichi_ggui_visualization_expansion_plan.json
outputs/step97_48cube_taichi_ggui_visualization_expansion_plan/48cube_taichi_ggui_visualization_expansion_plan.csv
outputs/step97_48cube_taichi_ggui_visualization_expansion_plan/48cube_taichi_ggui_visualization_expansion_plan_summary.csv
```

The plan summary must include:

```text
step97_48cube_taichi_ggui_visualization_expansion_plan_pass = true
previous_step = Step96
previous_commit = 9ec9877b1f997777a9b43792c52b0f2b84d3814e
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
ggui_run_allowed = false
screenshot_output_allowed_in_step97 = false
step98_allowed = true
step98_allowed_row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke
step98_allowed_n_grid = 48
step98_allowed_n_particles = 1024
step98_allowed_n_lbm_steps = 1
from_step96_grid_expansion = true
previous_step96_n_grid = 32
planned_step98_n_grid = 48
duration_reduction_for_grid_expansion_isolation = true
previous_step96_n_lbm_steps = 10
planned_step98_n_lbm_steps = 1
ggui_visualization_planned_for_step98 = true
ggui_screenshot_allowed_for_step98 = true
ggui_video_allowed_for_step98 = false
write_vtk_allowed = false
write_particles_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
video_output_allowed = false
step97_activation_feature_count = 0
planned_step98_activation_feature_count = 5
real_geometry_allowed = false
link_area_allowed = false
grid_64_allowed = false
```

Step97 guard output:

```text
outputs/step97_48cube_taichi_ggui_visualization_expansion_guard/48cube_taichi_ggui_visualization_expansion_guard.json
outputs/step97_48cube_taichi_ggui_visualization_expansion_guard/48cube_taichi_ggui_visualization_expansion_guard.csv
outputs/step97_48cube_taichi_ggui_visualization_expansion_guard/48cube_taichi_ggui_visualization_expansion_guard_summary.csv
```

The guard summary must include:

```text
step97_48cube_taichi_ggui_visualization_expansion_guard_pass = true
guard_row_count > 0
guard_pass_count = guard_row_count
step97_activation_feature_count = 0
planned_step98_activation_feature_count = 5
planned_step98_n_grid = 48
planned_step98_n_lbm_steps = 1
duration_reduction_for_grid_expansion_isolation = true
ggui_visualization_planned_for_step98 = true
ggui_screenshot_allowed_for_step98 = true
ggui_video_allowed_for_step98 = false
squid_proxy_planned_for_step98 = true
runtime_geometry_planned_for_step98 = true
wall_velocity_planned_for_step98 = true
combined_runtime_geometry_wall_velocity_planned_for_step98 = true
vtr_output_planned_for_step98 = false
particle_npy_output_planned_for_step98 = false
video_output_planned_for_step98 = false
real_geometry_planned_for_step98 = false
real_geometry_candidate_data_planned_for_step98 = false
link_area_planned_for_step98 = false
grid_64_planned_for_step98 = false
```

## Regression Guards

Step96 regression output:

```text
outputs/step97_step96_regression_guard/step96_regression_guard.json
outputs/step97_step96_regression_guard/step96_regression_guard.csv
outputs/step97_step96_regression_guard/step96_regression_guard_summary.csv
```

It must verify:

```text
step96_taichi_ggui_10step_visualization_run_matrix_pass = true
step96_taichi_ggui_10step_visualization_quality_pass = true
step96_activation_guard_pass = true
step96_output_guard_pass = true
step96_step95_regression_guard_pass = true
step96_step94_regression_guard_pass = true
step96_step92_regression_guard_pass = true
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

Step94 regression output:

```text
outputs/step97_step94_regression_guard/step94_regression_guard.json
outputs/step97_step94_regression_guard/step94_regression_guard.csv
outputs/step97_step94_regression_guard/step94_regression_guard_summary.csv
```

It must verify:

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

Step92 regression output:

```text
outputs/step97_step92_regression_guard/step92_regression_guard.json
outputs/step97_step92_regression_guard/step92_regression_guard.csv
outputs/step97_step92_regression_guard/step92_regression_guard_summary.csv
```

It must verify:

```text
step92_first_user_simulation_10step_dry_run_matrix_pass = true
step92_first_user_simulation_10step_dry_run_quality_pass = true
step92_activation_guard_pass = true
step92_output_guard_pass = true
step92_artifact_budget_pass = true
step92_activation_feature_count = 3
step92_completed_lbm_steps = 10
step92_squid_proxy_enabled_count = 1
step92_runtime_geometry_enabled_count = 1
step92_wall_velocity_enabled_count = 1
step92_vtr_count = 0
step92_particle_npy_count = 0
```

## Output Guard And Artifact Manifest

Step97 output guard:

```text
outputs/step97_output_guard/output_guard.json
outputs/step97_output_guard/output_guard.csv
outputs/step97_output_guard/output_guard_summary.csv
```

It must prove:

```text
output_guard_pass = true
step97_driver_run_dir_count = 0
step97_ggui_screenshot_count = 0
step97_ggui_video_count = 0
step97_vtr_count = 0
step97_particle_npy_count = 0
step97_raw_geometry_output_count = 0
step97_real_geometry_candidate_output_count = 0
step97_dense_wall_velocity_output_count = 0
step97_sparse_wall_velocity_output_count = 0
step97_dense_displacement_output_count = 0
step97_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step97_large_file_count = 0
```

Step97 artifact manifest:

```text
outputs/step97_artifact_manifest/artifact_manifest.csv
outputs/step97_artifact_manifest/artifact_summary.csv
outputs/step97_artifact_manifest/artifact_summary.json
```

It must prove:

```text
artifact_budget_pass = true
step97_file_count <= 70
step97_total_size_mb < 5
step97_driver_run_dir_count = 0
step97_ggui_screenshot_count = 0
step97_ggui_video_count = 0
step97_vtr_count = 0
step97_particle_npy_count = 0
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step97_file_count = 0
protected_real_geometry_candidates_step97_file_count = 0
raw_geometry_file_count = 0
```

Do not hard-code the exact artifact byte total in the prose report because the
report itself is part of the manifest.

## Required Tests

Add focused contract tests:

```text
tests/test_step97_48cube_taichi_ggui_visualization_expansion_plan_contract.py
tests/test_step97_48cube_taichi_ggui_visualization_expansion_guard_contract.py
tests/test_step97_step96_regression_contract.py
tests/test_step97_step94_regression_contract.py
tests/test_step97_step92_regression_contract.py
tests/test_step97_output_guard_contract.py
```

Use TDD:

1. Add tests first.
2. Run the focused Step97 tests and confirm they fail only because the Step97
   artifacts do not exist yet.
3. Implement configs, evidence modules, baseline runners, docs, and report.
4. Generate Step97 artifacts with the baseline runners.
5. Rerun focused tests and full tests.

## Verification Commands

Baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step97_48cube_taichi_ggui_visualization_expansion_plan.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step97_48cube_taichi_ggui_visualization_expansion_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step97_step96_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step97_step94_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step97_step92_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step97_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step97_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step97_48cube_taichi_ggui_visualization_expansion_plan_contract.py tests\test_step97_48cube_taichi_ggui_visualization_expansion_guard_contract.py tests\test_step97_step96_regression_contract.py tests\test_step97_step94_regression_contract.py tests\test_step97_step92_regression_contract.py tests\test_step97_output_guard_contract.py -q
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
git status --short src/mpm_lbm/sim src/mpm_lbm/diagnostics
```

Also run the legacy Step93 file-visualization route-token grep specified in
the source attachment. It must return no output. Do not write those route-token
literals into new Step97 files.

## Required Report Contents

`STEP97_48CUBE_TAICHI_GGUI_VISUALIZATION_EXPANSION_PLAN_AND_GUARD_REPORT.md`
must clearly state:

```text
Step97 accepted.

Step97 is a plan-and-guard step only.
Step97 does not run FSIDriver3D.
Step97 does not call driver.run().
Step97 does not execute simulation.
Step97 does not open a GGUI window.
Step97 does not write screenshots.
Step97 does not write video.
Step97 does not write VTR.
Step97 does not write particle NPY.

Step97 only plans and guards Step98:
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke

Step98 may run exactly one 48^3 / 1024-particle / 1-step /
moving_boundary / engineering row with:
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

The only grid expansion from Step96 is:
n_grid = 32 -> 48

The duration reduction from 10 steps to 1 step is intentional grid-expansion smoke isolation.

Step98 must not enable 64^3.
Step98 must not enable VTR.
Step98 must not enable particle NPY.
Step98 must not enable real geometry candidate data.
Step98 must not enable link-area transfer.
Step98 must not change solver formulas.
Step98 must not claim 48^3 production readiness, physical validation, squid swimming, or real squid validation.
```

The report must include the real verification results and artifact-manifest
summary after all final logs have been generated.

## Future Step98 Direction

If Step97 passes, Step98 may be:

```text
Step98 48^3 Taichi GGUI Visualization Smoke
```

Step98 required row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke
```

After Step98 passes, the maximum allowed claim should still be:

```text
48^3 / 1-step Taichi GGUI visualization smoke passed for the first-user envelope.
```

It must still not claim:

```text
48^3 10-step ready
64^3 ready
production visualization ready
physical validation complete
real squid validated
squid swimming validated
```

## Done Criteria

Step97 is done only when:

1. Detailed goal file exists and active goal references it.
2. Focused Step97 tests were first RED due to missing Step97 artifacts.
3. Step97 configs, evidence modules, baseline runners, docs, tests, report,
   logs, outputs, output guard, and artifact manifest are implemented.
4. No Step97 driver run, GGUI run, screenshot, video, VTR, particle NPY, real
   geometry output, or protected runtime/vendor edit exists.
5. Step97 baseline runners pass.
6. Focused Step97 pytest passes.
7. Full pytest passes with `D:\working\taichi\env\python.exe`.
8. Full pytest passes with `D:\TOOL\Anaconda\python.exe`.
9. Final output guard and artifact manifest are refreshed after final logs.
10. `git diff --check`, `git diff --cached --check`, protected-path statuses,
    and the legacy route-token grep all pass.
11. Work is committed with the required commit message.
12. Commit is pushed to `origin/main`.
13. Final response reports the remote branch, final commit hash, key pass
    counts, and artifact-manifest summary.
