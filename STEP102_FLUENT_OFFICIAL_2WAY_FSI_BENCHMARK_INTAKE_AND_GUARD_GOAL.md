# Step102 Fluent Official Two-Way FSI Benchmark Intake And Guard Goal

## Source State

The source attachment says GitHub is aligned at:

```text
origin/main = 7bb5df574b0b07a427712ed02596b1d4fef200c8
```

The accepted predecessor is:

```text
Step101 accepted.
```

Step101 was plan-and-guard only. It planned a future 48^3 / 10-step GGUI run, but the current direction changes before that run is executed. Step102 must not continue into the Step101-planned 48^3 / 10-step GGUI run. Step102 must instead intake the official Fluent two-way FSI tutorial as an external benchmark source and define the data, mapping, comparison, and guard boundaries.

Step102 must be:

```text
Step102 Fluent Official Two-Way FSI Benchmark Intake And Guard
```

Suggested commit message:

```text
test: add step102 fluent official two-way fsi benchmark intake and guard
```

## Objective

Implement Step102 as benchmark-intake-and-guard only.

The purpose is to record the Ansys Fluent official two-way intrinsic FSI duct/flap tutorial as an external benchmark source, define what can be compared later, define private-data and proprietary-file boundaries, preserve Step101/Step100 regression evidence, and define a future solver-test route that does not commit Ansys assets and does not claim validation prematurely.

Step102 must not change solver runtime behavior. Step102 must not import Fluent mesh files. Step102 must not run Fluent. Step102 must not run this repo's driver. Step102 must not run any benchmark comparison.

## Correct Step102 Claim

Step102 may claim only:

```text
Fluent official two-way FSI benchmark intake is planned and guarded.
```

Step102 must not claim:

```text
Fluent benchmark passed
our solver matches Fluent
physical validation complete
real FSI validation complete
production ready
```

## Runtime Prohibitions

Step102 must not execute:

```text
FSIDriver3D
driver.run()
Fluent
mesh parser
GGUI
benchmark comparison
simulation
```

Step102 must not commit:

```text
fsi_2way.zip
flap.msh
steady_fluid_flow.jou
*.cas.h5
*.dat.h5
Fluent screenshots
Ansys tutorial copied content
large official proprietary excerpts
```

Step102 must not modify:

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

Step102 must not activate:

```text
48^3 / 10-step GGUI run
64^3
real geometry candidate data
Fluent official mesh import
Fluent case/data import
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
real FSI validation claim
exact Fluent match claim
grid convergence claim
```

## Fluent Benchmark Source Metadata

Add:

```text
configs/step102_fluent_official_2way_fsi_benchmark_source_metadata.json
```

It must record:

```json
{
  "step": "Step102",
  "benchmark_id": "fluent_official_2way_intrinsic_fsi_duct_flap",
  "source_name": "Ansys Fluent Tutorial Chapter 29: Modeling Two-Way Fluid-Structure Interaction (FSI) Within Fluent",
  "source_url": "https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_tg/flu_tg_fsi_2way.html",
  "source_release": "2024 R2",
  "source_access_policy": "user_local_access_required",
  "source_content_policy": "do_not_commit_ansys_proprietary_files_or_large_verbatim_excerpts",
  "official_case_archive_name": "fsi_2way.zip",
  "official_files_expected_locally": [
    "flap.msh",
    "steady_fluid_flow.jou"
  ],
  "problem_family": "two_way_intrinsic_fsi",
  "fluent_model_type": "intrinsic_fsi",
  "geometry_description": "2D duct with vertical flaps, symmetry half-domain",
  "duct_length_m": 0.10,
  "duct_height_m": 0.04,
  "flap_height_m": 0.01,
  "flap_thickness_m": 0.003,
  "inlet_velocity_m_per_s": 10.0,
  "outlet_type": "pressure_outlet",
  "solid_material": {
    "name": "silicone-rubber",
    "density": 1600.0,
    "youngs_modulus": 1000000.0,
    "poisson_ratio": 0.47
  },
  "fluent_transient_settings": {
    "number_of_time_steps": 50,
    "time_step_size_s": 0.0005,
    "max_iterations_per_time_step": 40
  },
  "official_monitor": {
    "name": "structural-point-flap",
    "x": 0.0505,
    "y": 0.0095,
    "reported_quantity": "total_displacement_vertex_average"
  },
  "step102_driver_run_required": false,
  "step102_simulation_run_allowed": false,
  "step102_fluent_run_allowed": false,
  "step102_benchmark_comparison_allowed": false,
  "step102_validation_claim_allowed": false
}
```

## Local Data Directory Policy

The recommended private local data directory is:

```text
benchmarks/private/fluent_fsi_2way/
```

It may contain local user-owned or user-downloaded files such as:

```text
fsi_2way.zip
flap.msh
steady_fluid_flow.jou
flap_fluid.cas.h5
flap_fluid.dat.h5
flap_fsi_2way.cas.h5
flap_fsi_2way.dat.h5
fluent_exports/
```

These files must remain local/private and must not be committed.

Update `.gitignore` narrowly to exclude:

```text
benchmarks/private/fluent_fsi_2way/**
data/fluent_official_private/**
external/fluent_official_private/**
```

Avoid broad global ignores for `*.msh` or `*.jou` unless the repository already uses that policy. Step102 should guard against committing Fluent official files without breaking legitimate repo-owned file types.

## Benchmark Mapping Policy

Add:

```text
configs/step102_fluent_official_2way_fsi_mapping_policy.json
```

It must record:

```json
{
  "mapping_status": "intake_only",
  "direct_equivalence_claim_allowed": false,
  "validation_claim_allowed": false,
  "official_case_dimensionality": "2D",
  "current_solver_dimensionality": "3D",
  "official_mesh_type": "2D conformal fluid-solid mesh",
  "current_solver_geometry_type": "procedural_squid_proxy_or_future_procedural_proxy",
  "official_structure_model": "linear_elasticity_intrinsic_fsi",
  "current_structure_proxy": "mpm_particles_or_future_duct_flap_proxy",
  "comparison_level_allowed_initially": "qualitative_and_diagnostic_only",
  "quantitative_match_claim_allowed": false,
  "allowed_initial_observables": [
    "stability",
    "has_nan",
    "has_inf",
    "density_bounds",
    "velocity_bounds",
    "reaction_norm_bounds",
    "structural_proxy_displacement_trend_if_available",
    "ggui_visual_inspection"
  ],
  "forbidden_initial_observables": [
    "grid_convergence",
    "exact_flap_tip_displacement_match",
    "exact_pressure_load_match",
    "exact_turbulent_flow_match",
    "exact_dynamic_mesh_match"
  ],
  "recommended_future_solver_proxy": "procedural_duct_flap_proxy_not_official_mesh_import"
}
```

## Required Files

Add:

```text
STEP102_FLUENT_OFFICIAL_2WAY_FSI_BENCHMARK_INTAKE_AND_GUARD_GOAL.md
STEP102_FLUENT_OFFICIAL_2WAY_FSI_BENCHMARK_INTAKE_AND_GUARD_REPORT.md

configs/step102_fluent_official_2way_fsi_benchmark_source_metadata.json
configs/step102_fluent_official_2way_fsi_mapping_policy.json
configs/step102_fluent_official_2way_fsi_data_guard_policy.json
configs/step102_step101_regression_policy.json
configs/step102_step100_regression_policy.json
configs/step102_output_guard_policy.json
configs/step102_artifact_manifest_policy.json

src/mpm_lbm/evidence/step102_fluent_official_2way_fsi_benchmark_intake.py
src/mpm_lbm/evidence/step102_fluent_official_2way_fsi_mapping_guard.py
src/mpm_lbm/evidence/step102_fluent_official_2way_fsi_data_guard.py
src/mpm_lbm/evidence/step102_step101_regression_guard.py
src/mpm_lbm/evidence/step102_step100_regression_guard.py
src/mpm_lbm/evidence/step102_output_guard.py

baseline_tests/step102_common.py
baseline_tests/run_step102_fluent_official_2way_fsi_benchmark_intake.py
baseline_tests/run_step102_fluent_official_2way_fsi_mapping_guard.py
baseline_tests/run_step102_fluent_official_2way_fsi_data_guard.py
baseline_tests/run_step102_step101_regression_guard.py
baseline_tests/run_step102_step100_regression_guard.py
baseline_tests/run_step102_output_guard.py
baseline_tests/run_step102_artifact_manifest.py

tests/test_step102_fluent_official_2way_fsi_benchmark_intake_contract.py
tests/test_step102_fluent_official_2way_fsi_mapping_guard_contract.py
tests/test_step102_fluent_official_2way_fsi_data_guard_contract.py
tests/test_step102_step101_regression_contract.py
tests/test_step102_step100_regression_contract.py
tests/test_step102_output_guard_contract.py

docs/102_fluent_official_2way_fsi_benchmark_intake_and_guard.md

outputs/step102_fluent_official_2way_fsi_benchmark_intake/
outputs/step102_fluent_official_2way_fsi_mapping_guard/
outputs/step102_fluent_official_2way_fsi_data_guard/
outputs/step102_step101_regression_guard/
outputs/step102_step100_regression_guard/
outputs/step102_output_guard/
outputs/step102_artifact_manifest/

logs/step102_*.log
```

May update:

```text
README.md
.gitignore
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

Only update optional docs if they already contain directly relevant step-status or activation-boundary content and the update is necessary to keep docs aligned.

## Step102 Intake Evidence

The intake runner must write:

```text
outputs/step102_fluent_official_2way_fsi_benchmark_intake/fluent_official_2way_fsi_benchmark_intake.json
outputs/step102_fluent_official_2way_fsi_benchmark_intake/fluent_official_2way_fsi_benchmark_intake.csv
outputs/step102_fluent_official_2way_fsi_benchmark_intake/fluent_official_2way_fsi_benchmark_intake_summary.csv
```

The summary must include:

```text
step102_fluent_official_2way_fsi_benchmark_intake_pass = true
source_url_recorded = true
official_archive_name = fsi_2way.zip
official_files_expected = flap.msh, steady_fluid_flow.jou
official_mesh_name = flap.msh
official_journal_name = steady_fluid_flow.jou
problem_family = two_way_intrinsic_fsi
official_case_dimensionality = 2D
duct_length_m = 0.10
duct_height_m = 0.04
flap_height_m = 0.01
flap_thickness_m = 0.003
inlet_velocity_m_per_s = 10.0
solid_density = 1600.0
solid_youngs_modulus = 1000000.0
solid_poisson_ratio = 0.47
number_of_time_steps = 50
time_step_size_s = 0.0005
max_iterations_per_time_step = 40
step102_driver_run_required = false
step102_simulation_run_allowed = false
step102_fluent_run_allowed = false
step102_benchmark_comparison_allowed = false
step102_validation_claim_allowed = false
```

## Step102 Data Guard

The data guard runner must write:

```text
outputs/step102_fluent_official_2way_fsi_data_guard/fluent_official_2way_fsi_data_guard.json
```

The summary must include:

```text
step102_fluent_official_2way_fsi_data_guard_pass = true
official_archive_committed_count = 0
official_mesh_committed_count = 0
official_journal_committed_count = 0
fluent_case_data_committed_count = 0
private_benchmark_path_committed_count = 0
ansys_proprietary_file_committed_count = 0
ansys_large_verbatim_excerpt_count = 0
private_absolute_path_count = 0
artifact_budget_pass = true
local_data_required = true
local_data_committed = false
```

The guard must scan for committed forms of:

```text
fsi_2way.zip
flap.msh
steady_fluid_flow.jou
*.cas.h5
*.dat.h5
benchmarks/private/fluent_fsi_2way
```

Policy/docs/tests may mention these names as forbidden or expected local inputs. The committed repository must not contain official binary/case/mesh/journal data.

## Step102 Mapping Guard

The mapping guard runner must write:

```text
outputs/step102_fluent_official_2way_fsi_mapping_guard/fluent_official_2way_fsi_mapping_guard.json
```

The summary must include:

```text
step102_fluent_official_2way_fsi_mapping_guard_pass = true
mapping_status = intake_only
direct_equivalence_claim_allowed = false
validation_claim_allowed = false
official_case_dimensionality = 2D
current_solver_dimensionality = 3D
official_structure_model = linear_elasticity_intrinsic_fsi
current_structure_proxy = mpm_particles_or_future_duct_flap_proxy
comparison_level_allowed_initially = qualitative_and_diagnostic_only
quantitative_match_claim_allowed = false
recommended_future_solver_proxy = procedural_duct_flap_proxy_not_official_mesh_import
```

## Regression Guards

### Step101 Regression Guard

Write:

```text
outputs/step102_step101_regression_guard/step101_regression_guard.json
```

It must check:

```text
step101_48cube_10step_taichi_ggui_visualization_plan_pass = true
step101_48cube_10step_taichi_ggui_visualization_guard_pass = true
step101_output_guard_pass = true
step101_artifact_budget_pass = true
step101_driver_run_dir_count = 0
step101_ggui_screenshot_count = 0
step101_vtr_count = 0
step101_particle_npy_count = 0
```

### Step100 Regression Guard

Write:

```text
outputs/step102_step100_regression_guard/step100_regression_guard.json
```

It must check:

```text
step100_48cube_5step_taichi_ggui_visualization_run_matrix_pass = true
step100_48cube_5step_taichi_ggui_visualization_quality_pass = true
step100_activation_guard_pass = true
step100_output_guard_pass = true
step100_artifact_budget_pass = true
step100_completed_lbm_steps = 5
step100_n_grid = 48
step100_ggui_screenshot_count = 1
step100_vtr_count = 0
step100_particle_npy_count = 0
```

## Step102 Output Guard

The output guard summary must include:

```text
output_guard_pass = true
step102_driver_run_dir_count = 0
step102_ggui_screenshot_count = 0
step102_fluent_run_output_count = 0
step102_vtr_count = 0
step102_particle_npy_count = 0
step102_ansys_proprietary_file_count = 0
step102_large_file_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
```

## Step102 Artifact Budget

The artifact manifest summary must include:

```text
artifact_budget_pass = true
step102_file_count <= 75
step102_total_size_mb < 5
large_file_count = 0
private_absolute_path_count = 0
protected_sim_or_diagnostics_step102_file_count = 0
protected_external_taichi_lbm3d_step102_file_count = 0
protected_real_geometry_candidates_step102_file_count = 0
step102_driver_run_dir_count = 0
step102_ggui_screenshot_count = 0
step102_fluent_run_output_count = 0
step102_vtr_count = 0
step102_particle_npy_count = 0
```

## Contract Tests

Add focused tests:

```text
tests/test_step102_fluent_official_2way_fsi_benchmark_intake_contract.py
tests/test_step102_fluent_official_2way_fsi_mapping_guard_contract.py
tests/test_step102_fluent_official_2way_fsi_data_guard_contract.py
tests/test_step102_step101_regression_contract.py
tests/test_step102_step100_regression_contract.py
tests/test_step102_output_guard_contract.py
```

Run these tests before implementation and confirm RED because Step102 artifacts do not exist yet.

## Verification Commands

Baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step102_fluent_official_2way_fsi_benchmark_intake.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step102_fluent_official_2way_fsi_mapping_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step102_fluent_official_2way_fsi_data_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step102_step101_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step102_step100_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step102_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step102_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step102_fluent_official_2way_fsi_benchmark_intake_contract.py tests\test_step102_fluent_official_2way_fsi_mapping_guard_contract.py tests\test_step102_fluent_official_2way_fsi_data_guard_contract.py tests\test_step102_step101_regression_contract.py tests\test_step102_step100_regression_contract.py tests\test_step102_output_guard_contract.py -q
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
git status --short benchmarks/private
git status --short data/fluent_official_private
git grep -n "fsi_2way.zip\|flap.msh\|steady_fluid_flow.jou\|flap_fsi_2way.cas.h5\|flap_fsi_2way.dat.h5"
```

The final `git grep` may show only policy/docs/tests mentioning these names as forbidden or expected local inputs. It must not show committed official binary data or copied case files.

## Report Requirements

`STEP102_FLUENT_OFFICIAL_2WAY_FSI_BENCHMARK_INTAKE_AND_GUARD_REPORT.md` must state:

```text
Step102 accepted.

Step102 is benchmark intake and guard only.
Step102 does not run FSIDriver3D.
Step102 does not call driver.run().
Step102 does not run Fluent.
Step102 does not import Fluent mesh.
Step102 does not run benchmark comparison.
Step102 does not commit Ansys official files.

Step102 records the Fluent official two-way intrinsic FSI duct/flap benchmark source:
- fsi_2way.zip
- flap.msh
- steady_fluid_flow.jou
- 2D duct/flap intrinsic FSI
- inlet velocity 10 m/s
- silicone rubber material properties
- transient settings 50 time steps, dt = 0.0005, max 40 iterations/time step
- flap displacement monitor point

Step102 defines only an intake/mapping path.
Direct quantitative equivalence is not claimed.
Validation is not claimed.
Physical validation is not claimed.
Production readiness is not claimed.

Official Ansys files must remain local/private and must not be committed.
```

## Future Direction

If Step102 is green, the next recommended step is:

```text
Step103 Fluent-Inspired Duct-Flap Proxy Solver Test Plan And Guard
```

Step103 should not import the Fluent official mesh. It should plan a repo-owned, procedural duct-flap proxy that is safe to commit and can later support qualitative/diagnostic comparisons without exact Fluent-match claims.

Potential later route:

```text
Step104 Fluent-Inspired Duct-Flap Proxy 32^3 / 1-step Smoke
Step105 Fluent-Inspired Duct-Flap Proxy 32^3 / 5-step Run
Step106 Compare Fluent official observables vs our proxy diagnostics qualitatively
```

## Done Criteria

Step102 is done only when:

1. The detailed goal file exists and the active goal references it.
2. All required configs, evidence builders, baseline runners, contract tests, docs, report, logs, and output artifacts exist.
3. Focused Step102 tests pass.
4. Full pytest passes with `D:\working\taichi\env\python.exe`.
5. Full pytest passes with `D:\TOOL\Anaconda\python.exe`.
6. Output guard proves no driver run, no GGUI output, no Fluent run output, no VTR, no particle NPY, no official Ansys file, no private absolute path, and no protected-path edits.
7. Artifact manifest proves `step102_file_count <= 75`, `step102_total_size_mb < 5`, and no large/private/protected/official-output artifacts.
8. Git checks pass.
9. The final commit is pushed to `origin/main`.
