# Step104 Goal: Fluent Duct-Flap Official Problem Setup Repair

## Source Of Truth

This document is the detailed implementation contract for Step104. The active
Codex goal should reference this file instead of inlining the full text,
because the goal text length is limited.

Step103 is accepted and pushed. Step104 starts from the post-Step103 baseline
where the solver ran a Fluent-inspired proxy smoke, but the committed evidence
shows that the driver/problem setup is not yet the official public Fluent
duct-flap two-way FSI problem.

Official public source metadata remains the Ansys Fluent Tutorial Chapter 29
two-way FSI duct/flap tutorial URL recorded in Step102/Step103:

```text
https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_tg/flu_tg_fsi_2way.html
```

Do not commit official Ansys archives, mesh files, journals, case/data files,
screenshots, copied tutorial payloads, or private Fluent CSV data.

Expected final commit message:

```text
test: add step104 fluent duct-flap setup repair
```

## One-Sentence Objective

Implement Step104 as a bounded problem-setup repair step: correct the
duct-flap driver setup so it begins to solve the same class of public Fluent
duct/flap two-way FSI problem, add tests and artifacts proving the repaired
setup is wired, and explicitly avoid claiming Fluent validation or numerical
equivalence.

## Root-Cause Conclusion From Step103 Review

The current mismatch is not primarily a numerical tolerance issue. The Step103
solver/driver is solving a different problem from the public Fluent duct-flap
tutorial because the core boundary, geometry, structural constraint, material,
and monitor definitions are wrong or incomplete.

Concrete issues to fix or guard in Step104:

1. `target_u_lbm` is currently applied as initial solid velocity in
   `FSIDriver3D.initialize()`. For the duct-flap problem, this value represents
   an inlet flow target, not an initial flap velocity.
2. The LBM side has no explicit velocity inlet / pressure outlet setup for the
   duct-flap row. Existing defaults are effectively inappropriate for the
   official problem shape.
3. The current generated LBM geometry is an all-fluid cube, not a duct with
   top/bottom walls, inlet, outlet, and a flap obstacle/interface.
4. `fixed_base = true` exists only as metadata in the Step103 geometry config.
   No fixed-base mask is passed into MPM, so the flap attach/base is not
   constrained.
5. The material reference is recorded in JSON but not applied to the MPM
   configuration. The Step104 row must at least map density, Young's modulus,
   and Poisson ratio into the structural config, while still disclosing that
   the current MPM stress path is not exact Fluent intrinsic linear elasticity.
6. Step103 incorrectly wires a Step36 squid wall-velocity config into the
   duct-flap row. The official passive flap setup must not use squid wall
   velocity.
7. There is no comparable committed flap-tip displacement monitor. Step104 must
   add a proxy monitor time series with fields that can later be compared to a
   private Fluent CSV when such data is available.

## Official Problem Facts To Preserve

The public Fluent tutorial problem is a two-way FSI duct/flap case with these
setup facts reflected in Step104 metadata and docs:

- duct length: `0.10 m`
- duct height: `0.04 m`
- flap height: `0.01 m`
- flap thickness: `0.003 m`
- inlet air velocity: `10 m/s`
- outlet: pressure outlet
- structural material: silicone rubber
- material density: `1600 kg/m^3`
- Young's modulus: `1.0e6 Pa`
- Poisson ratio: `0.47`
- flap attach/base: fixed displacement
- Fluent transient shape: `50` time steps at `0.0005 s` each, total `0.025 s`
- official monitor concept: structural point/flap total displacement near the
  flap tip/upper point

Step104 may run only a short smoke row. It must not claim it completed the full
50-step public tutorial validation unless a later step explicitly does that.

## Allowed Claim

The only accepted Step104 result claim is:

```text
Fluent duct-flap problem setup repair is wired for a short proxy smoke, and the remaining Fluent-equivalence gaps are explicitly reported.
```

## Forbidden Claims

Do not claim any of the following:

- The current solver matches Fluent.
- The current solver is validated against Fluent.
- The current solver reproduces the exact Fluent intrinsic linear-elastic FSI
  formulation.
- The current solver has completed the full 50-step public tutorial run.
- The current solver has a validated dynamic mesh equivalent.
- Physical validation is complete.
- Real FSI validation is complete.
- The workflow is production ready.

## Required Step Identity

Required canonical row name:

```text
fluent_duct_flap_setup_repair_48_5step_smoke
```

Required driver module:

```text
src.mpm_lbm.sim.drivers.fsi_driver
```

Required geometry type:

```text
duct_flap_proxy
```

## Required Driver Configuration

Create a new Step104 driver config:

```text
configs/step104_fluent_duct_flap_setup_repair_48_5step_smoke.json
```

The row must use:

- `n_grid = 48`
- `n_particles = 1024`
- `n_lbm_steps = 5`
- `mpm_substeps_per_lbm_step = 1`
- `coupling_mode = moving_boundary`
- `reaction_transfer_mode = engineering`
- `geometry_type = duct_flap_proxy`
- `geometry_config_path = configs/step104_fluent_duct_flap_geometry_1024.json`
- `target_u_lbm = [0.02, 0.0, 0.0]` as the LBM inlet target only
- `initial_solid_velocity_norm = [0.0, 0.0, 0.0]`
- `lbm_boundary_condition_mode = duct_velocity_inlet_pressure_outlet`
- `velocity_inlet_axis = x`
- `velocity_inlet_side = min`
- `pressure_outlet_side = max`
- `wall_velocity_application_mode = disabled`
- `wall_velocity_application_config_path = null`
- `write_vtk = false`
- `write_particles = false`
- `output_interval = 1`

Step104 must not reuse the Step36 squid wall velocity config.

## Required Geometry Configuration

Create a new Step104 geometry config:

```text
configs/step104_fluent_duct_flap_geometry_1024.json
```

It must preserve the Step103 normalized duct/flap proxy shape, while adding
explicit setup fields needed by Step104:

- normalized duct:
  - `x = [0.0, 1.0]`
  - `y = [0.3, 0.7]`
  - `z = [0.45, 0.55]`
- normalized flap:
  - `anchor_x = 0.505`
  - `anchor_y = 0.3`
  - `height_over_duct_height = 0.25`
  - `thickness_over_duct_height = 0.075`
  - `normalized_height = 0.10`
  - `normalized_thickness = 0.03`
  - `z = [0.45, 0.55]`
  - `fixed_base = true`
- dimensional metadata:
  - `duct_length_m = 0.10`
  - `duct_height_m = 0.04`
  - `flap_height_m = 0.01`
  - `flap_thickness_m = 0.003`
  - `inlet_velocity_mps = 10.0`
  - `transient_dt_s = 0.0005`
  - `official_transient_steps = 50`
- material reference:
  - `density = 1600.0`
  - `youngs_modulus = 1000000.0`
  - `poisson_ratio = 0.47`
  - `used_for_mpm_config = true`
  - `used_for_exact_structural_model = false`
- fixed base:
  - `fixed_base = true`
  - a deterministic fixed-base particle mask is generated for particles near
    the attached lower flap/base region
- monitor:
  - `flap_tip_monitor_enabled = true`
  - `time_series_fields = step,time_s,flap_tip_total_displacement_m,flap_tip_x_displacement_m,flap_tip_y_displacement_m`

## Required Source Behavior

### Solid Initial Velocity Repair

Add explicit driver config support for:

```text
initial_solid_velocity_norm
```

Default must be `[0.0, 0.0, 0.0]`. `target_u_lbm` must no longer imply solid
initial velocity. Any old tests or configs that intentionally need a moving
solid must opt in through the new field.

### LBM Duct Boundary Metadata And Application

Add Step104-safe support for an explicit duct boundary mode:

```text
duct_velocity_inlet_pressure_outlet
```

At minimum, the Step104 row must write a boundary-condition report proving:

- `target_u_lbm` is assigned to the inlet-flow target.
- left/min-x duct fluid cells are the velocity inlet region.
- right/max-x duct fluid cells are the pressure outlet region.
- top/bottom duct walls are solid/no-slip geometry.
- the row is not periodic/all-fluid.

If runtime LBM boundary application is implemented in this step, it must be
covered by tests and the report. If a part remains report-only, the gap must be
explicitly marked as not yet Fluent-equivalent.

### Duct Static Geometry Repair

Replace the all-fluid cube geometry for the Step104 row with a deterministic
duct/flap static geometry artifact. The artifact must not be named or reported
as all-fluid. The report must include counts for:

- fluid cells inside the duct
- solid duct wall cells
- inlet fluid boundary cells
- pressure outlet fluid boundary cells
- flap proxy/interface cells if represented in the static geometry artifact

### Fixed-Base MPM Constraint

The geometry sampler must expose a fixed-base mask for duct-flap particles
when `fixed_base = true`. MPM/driver logic must consume this mask and keep fixed
particles at their initial positions with zero velocity after substeps.

The committed Step104 smoke report must include:

- `fixed_base_particle_count > 0`
- `fixed_base_max_displacement_norm` close to zero
- `fixed_base_max_velocity_norm` close to zero

### Material Mapping

The Step104 duct-flap row must map the material reference to the MPM
configuration:

- `p_rho = 1600.0`
- `young_modulus = 1000000.0`
- `poisson_ratio = 0.47`

The gap report must still state that this is not exact Fluent intrinsic
linear-elastic structural equivalence.

### Step36 Wall-Velocity Disconnect

The Step104 row must disable Step36 squid wall velocity. Acceptance must fail
if `configs/step36_wall_velocity_application_solid_vel_experimental.json`
appears in the Step104 driver config or Step104 runtime report.

### Flap-Tip Monitor

Write a committed Step104 proxy time series artifact:

```text
outputs/step104_fluent_duct_flap_setup_repair/flap_tip_displacement_timeseries.csv
```

Required columns:

```text
step,time_s,flap_tip_total_displacement_m,flap_tip_x_displacement_m,flap_tip_y_displacement_m
```

The monitor is a proxy monitor unless and until a later step proves it is
directly equivalent to Fluent's official structural-point monitor. The gap
report must expose both:

- `proxy_flap_tip_displacement_available = true`
- `direct_quantitative_equivalence_allowed = false`

## Required Policy And Evidence Files

Create or update Step104-specific files:

- `configs/step104_acceptance_policy.json`
- `configs/step104_output_guard_policy.json`
- `src/mpm_lbm/evidence/step104_fluent_duct_flap_setup_repair_runner.py`
- `src/mpm_lbm/evidence/step104_fluent_duct_flap_setup_gap_report.py`
- `src/mpm_lbm/evidence/step104_output_guard.py`
- `baseline_tests/run_step104_fluent_duct_flap_setup_repair.py`
- `baseline_tests/run_step104_output_guard.py`
- `baseline_tests/run_step104_artifact_manifest.py`
- `tests/test_step104_fluent_duct_flap_setup_repair_contract.py`
- `tests/test_step104_output_guard_contract.py`
- `docs/104_fluent_duct_flap_official_problem_setup_repair.md`
- `STEP104_FLUENT_DUCT_FLAP_OFFICIAL_PROBLEM_SETUP_REPAIR_REPORT.md`

Reuse existing Step103 helpers when that reduces duplication, but keep Step104
artifact names and claims separate.

## Required Outputs And Logs

Produce and commit Step104 artifacts under:

- `outputs/step104_fluent_duct_flap_setup_repair/`
- `outputs/step104_output_guard/`
- `outputs/step104_artifact_manifest/`
- `logs/step104_*.log`

Required artifacts:

- `outputs/step104_fluent_duct_flap_setup_repair/setup_repair_report.json`
- `outputs/step104_fluent_duct_flap_setup_repair/setup_repair_report.csv`
- `outputs/step104_fluent_duct_flap_setup_repair/setup_repair_report.md`
- `outputs/step104_fluent_duct_flap_setup_repair/flap_tip_displacement_timeseries.csv`
- `outputs/step104_fluent_duct_flap_setup_repair/duct_boundary_condition_report.json`
- `outputs/step104_fluent_duct_flap_setup_repair/duct_static_geometry_report.json`
- `outputs/step104_output_guard/output_guard_report.json`
- `outputs/step104_artifact_manifest/artifact_manifest.json`

## Required Acceptance Criteria

### Setup Repair

- `target_u_lbm_applied_to_solid_initial_velocity = false`
- `initial_solid_velocity_norm = [0.0, 0.0, 0.0]`
- `target_u_lbm_applied_to_inlet = true`
- `lbm_boundary_condition_mode = duct_velocity_inlet_pressure_outlet`
- `velocity_inlet_cell_count > 0`
- `pressure_outlet_cell_count > 0`
- `duct_wall_cell_count > 0`
- `all_fluid_geometry_used = false`
- `fixed_base_particle_count > 0`
- `fixed_base_constraint_applied = true`
- `material_reference_used_for_mpm_config = true`
- `step36_squid_wall_velocity_config_used = false`
- `proxy_flap_tip_displacement_available = true`
- `direct_quantitative_equivalence_allowed = false`
- `validation_claim_allowed = false`

### Solver Smoke

- `driver_run_called = true`
- row name equals `fluent_duct_flap_setup_repair_48_5step_smoke`
- `geometry_type = duct_flap_proxy`
- `n_grid = 48`
- `n_particles = 1024`
- `n_lbm_steps = 5`
- completed steps equals `5`
- diagnostics row count is at least `6`
- `has_nan = false`
- `has_inf = false`
- stable is `true`

### Output Guard

- official/proprietary Fluent file count is `0`
- private Fluent CSV committed count is `0`
- `.vtr` count is `0`
- particle `.npy` count is `0`
- video count is `0`
- protected external edits count is `0`
- protected real-geometry edits count is `0`
- Step104 config does not reference the Step36 squid wall-velocity config
- committed reports do not claim Fluent validation or physical validation

## Red-To-Green Test Requirement

Before production code edits, add focused Step104 tests that fail on the
current Step103 behavior for the intended reasons:

- `target_u_lbm` incorrectly initializes solid velocity.
- Step104 setup lacks explicit duct inlet/outlet boundary reporting.
- Step104 setup would use all-fluid geometry instead of duct geometry.
- no fixed-base mask/constraint is applied.
- material reference is not mapped into MPM config.
- Step36 squid wall velocity is still accepted for a duct-flap row.
- no proxy flap-tip displacement time series exists.

Then implement the minimum code and artifacts needed to make those tests pass.

## Required Verification Commands

Run focused Step104 runners:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step104_fluent_duct_flap_setup_repair.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step104_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step104_artifact_manifest.py
```

Run focused Step104 tests:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests/test_step104_fluent_duct_flap_setup_repair_contract.py tests/test_step104_output_guard_contract.py
```

Run full tests with the trusted Taichi interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Run broader local compatibility only if time/environment permits:

```powershell
& 'D:\TOOL\Anaconda\python.exe' -m pytest -q
```

Run Git/pre-push checks:

```powershell
git diff --check
git status --short benchmarks/private
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
git grep -n "fsi_2way.zip\|flap.msh\|steady_fluid_flow.jou\|flap_fsi_2way.cas.h5\|flap_fsi_2way.dat.h5"
```

The final `git grep` may only find policy/docs/tests that forbid or describe
private inputs; it must not indicate that official Fluent file contents are
committed or used as runtime inputs.

## Push Rule

After implementation, artifacts, docs, focused tests, relevant full tests, and
guards pass, commit and push to `origin main`. Report the final commit hash and
pushed branch. Mark the active goal complete only after the push succeeds.
