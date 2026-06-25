# Step114 Fluent Solver Physics Repair Goal

## User Request

Use the attached review as the implementation contract. The review concludes
that Step113 exposed real solver-level problems rather than a report-only
mistake. The next work must modify code and tests, not tune images with
damping/caps. The full review identifies seven interacting gaps:

1. Subcycled FSI exchanges only the final LBM substep wall force with MPM.
2. LBM viscosity/Reynolds mapping still follows legacy `niu=0.1` semantics.
3. The current explicit finite-deformation MPM model is not Fluent's
   small-strain linear elasticity model.
4. Duct velocity inlet and pressure outlet reset all D3Q19 populations to
   equilibrium, erasing non-equilibrium stress.
5. Moving-boundary reaction transfer is volume-sampled and capped, not a
   conservative wall-traction-to-structure map.
6. The current 3D voxel proxy is not Fluent's 2D planar/symmetry model.
7. The current flap monitor is a free-tip particle average, not the official
   Fluent structural point surface style monitor.

## Step114 Objective

Implement the first bounded solver-physics repair layer that is small enough to
verify in this repository while directly addressing the review's highest-risk
items. Step114 must make real code changes, add tests that would have failed
before the changes, and document the remaining Fluent-parity gaps honestly.

Step114 must not claim Fluent validation, exact Figure 29.3/29.5 parity, exact
official mesh/case reproduction, or production readiness. The correct outcome
is a safer and more explicit solver path with artifact-backed diagnostics.

## Required P0 Code Changes

### P0.1 Subcycled Moving-Boundary Force Accumulation

Problem: `FSIDriver3D._step_moving_boundary_subcycled()` currently performs one
projection, then runs `lbm.step_moving_bounceback()` for
`lbm_substeps_per_fsi_step`, then advances MPM once. Because
`LBMFluid3D.step_moving_bounceback()` clears moving-boundary diagnostics at the
start of each substep, the MPM side sees only the last substep's `hydro_force`.

Required implementation:

- Add explicit moving-boundary force accumulation support in
  `src/mpm_lbm/sim/lbm/fluid.py`.
- Accumulate each substep's `hydro_force` into a dedicated field such as
  `hydro_force_accum` or `hydro_impulse_accum`.
- Add a clear/start method for one official FSI exchange window.
- Add a finalize/apply method that exposes either:
  - mean substep force, `hydro_force_accum / substep_count`, or
  - integrated impulse converted to effective official-step force.
- Update `src/mpm_lbm/sim/drivers/fsi_driver.py` so the subcycled path clears
  the accumulator before the substep loop, accumulates after each LBM substep,
  and advances MPM using the accumulated/mean force rather than only the final
  substep field.
- Preserve non-subcycled behavior by default.
- Add diagnostics for the accumulation window:
  `mb_subcycle_force_accumulation_mode`, `mb_subcycle_force_sample_count`,
  `mb_subcycle_force_accum_norm_max`, and
  `mb_subcycle_force_mean_norm_max`.

Required tests:

- A contract test must prove that subcycled moving-boundary reaction transfer
  uses accumulated/mean force from all substeps, not only the final substep.
- The test should be lightweight and deterministic. It may use small arrays or
  source-level inspection if Taichi kernel execution would be too slow.
- Existing Step104, Step112, and Step113 tests must still pass.

### P0.2 Physical Viscosity/Re Mapping Surface

Problem: Step113 still uses the legacy external LBM parameter path. The review
calculates that default `niu=0.1` at 96^3 with the official time mapping implies
an effective physical viscosity around `5.8e-3 m^2/s`, giving Re around 69 for
the 0.04 m duct height, not the public 10 m/s turbulent air case.

Required implementation:

- Add explicit fields to `src/mpm_lbm/sim/drivers/fsi_config.py`:
  - `fluid_density_kg_m3`
  - `fluid_kinematic_viscosity_m2_s`
  - `target_reynolds_number`
  - `lbm_viscosity_semantics`
- Valid semantics must include at least:
  - `legacy_external`
  - `physical_nu_mapping`
- When `lbm_viscosity_semantics == "physical_nu_mapping"`, compute:
  - `dx_phys = physical_duct_length_m / n_grid`
  - `dt_phys = lbm_dt_phys_override_s` if present, otherwise `sim.lbm_dt_phys`
  - `nu_lbm = nu_phys * dt_phys / dx_phys**2`
  - `tau = 3 * nu_lbm + 0.5`
  - legacy external `niu = 3 * (tau - 0.5)` if the current backend still stores
    the value as `niu`
- Reject unstable viscosity mappings that produce `tau <= 0.5` or
  non-finite values.
- Include the physical mapping in the duct boundary/driver config report so a
  Step114/Step115 run cannot silently fall back to legacy `niu=0.1`.

Required tests:

- A test must assert the 96^3 official mapping computes a lattice viscosity
  matching the formula above.
- A test must assert `legacy_external` preserves the existing default behavior.
- A test must reject invalid physical viscosity values.

### P0.3 Fluent-Like Monitor Surface

Problem: the current `collect_flap_tip_monitor()` reports the mean displacement
of `free_tip_proxy_mask` particles. Fluent's report definition uses a
structural point surface/vertex-average-like displacement near
`x=0.0505, y=0.0095`.

Required implementation:

- Add config fields to enable an official-point-like monitor without replacing
  the existing free-tip monitor:
  - monitor mode/name
  - physical point coordinates
  - nearest particle count or averaging radius
- Output separate fields for:
  - mean free-tip displacement
  - max free-tip displacement
  - official-point-like displacement
- Preserve the old CSV schema where existing tests depend on it, or write an
  additional monitor CSV if the schema must expand.
- Mark the monitor as proxy/vertex-average-like, not exact Fluent equivalence.

Required tests:

- A deterministic numpy-level test must verify nearest-particle monitor
  selection and displacement averaging.
- A driver/config test must prove the monitor config is serialized and the old
  free-tip monitor is not silently redefined.

## Required P1 Contract/Guard Changes

These items may be implemented as code surfaces, guards, or explicit
non-activation reports in Step114 if a full solver replacement is too large for
one commit. They must not be ignored.

### P1.1 Boundary-Condition Guard

- Add a field that records boundary-condition implementation semantics.
- Existing all-population equilibrium overwrite behavior must be named
  explicitly, e.g. `equilibrium_all_population_reset`.
- A future standard BC path should be represented as a separate opt-in enum
  value such as `zou_he_reconstruct_unknowns` or `regularized_velocity_pressure`.
- Step114 does not need to complete a full D3Q19 Zou-He implementation if doing
  so would be unvalidated, but it must prevent reports from implying the
  current boundary is Fluent-like.

### P1.2 Structure-Model Guard

- Add explicit config/report fields distinguishing:
  - current finite-deformation explicit MPM
  - future `small_strain_linear_elastic`
  - future `plane_strain_2d` or `plane_stress_2d`
- Step114 must not claim that the existing MPM is Fluent linear elasticity.
- If a not-yet-implemented mode is selected, it must fail fast with a clear
  error instead of silently using the existing model.

### P1.3 Reaction-Transfer Guard

- Add explicit diagnostics/reporting that the current `engineering` moving
  boundary reaction path is volume-sampled and may apply to all active
  particles.
- Add a config enum placeholder for a future interface-only conservative
  traction mapping, but fail fast if selected before implementation.
- Keep `force_cap_norm` marked as an emergency limiter/non-physical limiter in
  Step114 reports when it is nonzero.

### P1.4 Quasi-2D/Symmetry Guard

- Add an explicit flow-dimensionality/report field for duct-flap runs:
  current `thin_3d_no_slip_z_walls` or equivalent.
- Add future/placeholder enum values for `d2q9_planar` or
  `d3q19_quasi_2d_periodic_z`.
- Step114 does not need to implement D2Q9, but it must stop labeling the
  current z-wall proxy as a true Fluent planar/symmetry case.

## Required Artifacts

Create or update:

- `STEP114_FLUENT_SOLVER_PHYSICS_REPAIR_GOAL.md`
- `STEP114_FLUENT_SOLVER_PHYSICS_REPAIR_REPORT.md`
- `docs/114_fluent_solver_physics_repair.md`
- tests covering the P0 code paths and P1 guards
- any small config/report fixture needed for Step114 validation
- README Step114 implementation and boundary entry

Do not commit private Ansys case/data/mesh files. Do not touch
`external/taichi_LBM3D`.

## Verification Plan

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\mpm_lbm\sim\drivers\fsi_config.py src\mpm_lbm\sim\drivers\fsi_driver.py src\mpm_lbm\sim\lbm\fluid.py src\mpm_lbm\sim\coupling\moving_boundary.py
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step114_fluent_solver_physics_repair_contract.py tests\test_step104_fluent_duct_flap_setup_repair_contract.py tests\test_step112_planar_constraint_contract.py tests\test_step113_mirrored_duct_flap_geometry_contract.py
& 'D:\working\taichi\env\python.exe' -m pytest -q
git diff --check
```

Expected result:

- New Step114 tests fail before implementation and pass after implementation.
- Full existing suite passes.
- README/docs/report describe the new solver surfaces accurately.
- The final pushed commit includes code, tests, goal, report, docs, and any
  small Step114 artifacts needed to explain what changed.

## Push Requirement

After implementation and verification, commit and push to the configured GitHub
remote `origin/main`. Report the commit hash, branch, tests run, and any known
remaining gaps.
