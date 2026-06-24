# Step105 Goal: Fluent Duct-Flap Proxy 50-Step Transient And Dimensional-Gap Audit

## Source Of Truth

This document is the detailed implementation contract for Step105. The active
Codex goal should reference this file instead of inlining the full text,
because the goal text length is limited.

Step104 is accepted and pushed at:

```text
1cac1fc83cca0dc641884f1488cdf95cfbedae6e
```

Step104 correctly repaired the problem setup for the Fluent duct-flap proxy:
`target_u_lbm` is no longer used as solid initial velocity, the duct row has
explicit x-min velocity inlet and x-max pressure outlet setup, the all-fluid
cube geometry was replaced by duct static geometry, the fixed base reaches MPM,
silicone material parameters are mapped into MPM config, Step36 squid wall
velocity is disabled, and a proxy flap-tip displacement time series exists.

Step105 must not jump to solver-formula tuning or Fluent curve fitting. It must
first run a longer proxy transient and make the remaining dimensional and
modeling gaps explicit.

Official public source metadata remains the Ansys Fluent Tutorial Chapter 29
two-way FSI duct/flap tutorial URL recorded in Step102-Step104:

```text
https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_tg/flu_tg_fsi_2way.html
```

Do not commit official Ansys archives, mesh files, journals, case/data files,
screenshots, copied tutorial payloads, or private Fluent CSV data.

Expected final commit message:

```text
test: add step105 duct-flap transient gap audit
```

## One-Sentence Objective

Implement Step105 as a bounded evidence step on top of Step104: run one
50-step Fluent duct-flap proxy transient smoke with the repaired setup, add a
dimensional velocity-mapping report, add flow-development diagnostics and a
complete gap taxonomy, and explicitly preserve the boundary that this is not
Fluent validation or solver-equivalence work.

## Review Conclusion Driving Step105

The remaining blocker is not yet a coupling or bounce-back formula fix. The
post-Step104 review identifies that Step104 solved the setup wiring, but the
current solver still cannot be compared quantitatively to Fluent because:

1. Dimensional velocity mapping is not closed. The public tutorial inlet is
   `10 m/s`, while the current proxy input is `target_u_lbm = [0.02, 0.0, 0.0]`.
   With `n_grid = 48`, normalized `dx = 1/48`, and `dt = 0.0005 s`, this maps
   to roughly `0.0833333333 m/s` over a `0.10 m` duct-length scale, not
   `10 m/s`.
2. The official transient starts from a steady fluid-flow pre-solve, while
   Step104 starts from a quiescent field and runs only five LBM steps.
3. The official structural model is linear elasticity, while the current MPM
   model remains the existing corotated/hyperelastic implementation.
4. The official monitor is a structural point/vertex-average total displacement
   monitor near `x = 0.0505, y = 0.0095`; the current output is a proxy mean
   over the `free_tip_proxy_mask` particle set.
5. Existing tests are setup contracts, not physics validation; they do not
   require flow development, physically comparable displacement magnitude, or
   Fluent curve agreement.

Step105 must make these gaps visible and artifact-backed before any later step
tries to modify reaction transfer, moving-boundary force, structure model, or
other physics.

## Official Problem Facts To Preserve

The public Fluent tutorial facts to preserve in metadata, docs, and reports:

- duct length: `0.10 m`
- duct height: `0.04 m`
- flap height: `0.01 m`
- flap thickness: `0.003 m`
- inlet air velocity: `10 m/s`
- outlet: pressure outlet
- pre-transient initialization: steady fluid-flow solution
- structural model: linear elasticity
- structural material: silicone rubber
- material density: `1600 kg/m^3`
- Young's modulus: `1.0e6 Pa`
- Poisson ratio: `0.47`
- flap attach/base: fixed displacement
- transient shape: `50` time steps at `0.0005 s` each, total `0.025 s`
- official monitor concept: structural-point total displacement near the flap
  tip/upper point

## Allowed Claim

The only accepted Step105 result claim is:

```text
Fluent duct-flap proxy 50-step transient smoke ran with repaired Step104 setup, and dimensional/modeling gaps blocking Fluent-equivalence claims are explicitly audited.
```

## Forbidden Claims

Do not claim any of the following:

- The current solver matches Fluent.
- The current solver is validated against Fluent.
- The current solver reproduces the exact Fluent intrinsic linear-elastic FSI
  formulation.
- The current solver has the same dimensional inlet velocity as the public
  tutorial.
- The current solver has the official steady preflow initial condition.
- The current proxy flap-tip time series is the official Fluent structural
  point monitor.
- The current solver has a validated dynamic mesh equivalent.
- Physical validation is complete.
- Real FSI validation is complete.
- The workflow is production ready.

## Required Step Identity

Required canonical row name:

```text
fluent_duct_flap_proxy_48_50step_transient_gap_smoke
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

Create a new Step105 driver config:

```text
configs/step105_fluent_duct_flap_proxy_48_50step_transient_gap_smoke.json
```

The row must use:

- `n_grid = 48`
- `n_particles = 1024`
- `n_lbm_steps = 50`
- `mpm_dt = 0.0005`
- `mpm_substeps_per_lbm_step = 1`
- `coupling_mode = moving_boundary`
- `reaction_transfer_mode = engineering`
- `geometry_type = duct_flap_proxy`
- `geometry_config_path = configs/step104_fluent_duct_flap_geometry_1024.json`
- `target_u_lbm = [0.02, 0.0, 0.0]`
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

Step105 must not reuse the Step36 squid wall velocity config.

## Required Dimensional Mapping Report

Create a dimensional mapping report under:

```text
outputs/step105_dimensional_mapping/velocity_mapping_report.json
outputs/step105_dimensional_mapping/velocity_mapping_report.csv
outputs/step105_dimensional_mapping/velocity_mapping_report.md
```

The report must include at least these fields:

- `n_grid`
- `dx_norm`
- `mpm_dt`
- `lbm_dt_phys`
- `duct_length_m`
- `target_u_lbm`
- `proxy_inlet_velocity_mps`
- `official_inlet_velocity_mps`
- `velocity_ratio`
- `dimensional_velocity_mapping_gap_present`
- `mapping_formula`
- `direct_quantitative_equivalence_allowed`
- `validation_claim_allowed`

Required semantics:

- `dx_norm = 1 / n_grid`
- `proxy_inlet_velocity_mps = target_u_lbm_x * dx_norm / mpm_dt * duct_length_m`
- `official_inlet_velocity_mps = 10.0`
- `velocity_ratio = proxy_inlet_velocity_mps / official_inlet_velocity_mps`
- `dimensional_velocity_mapping_gap_present = true`
- `direct_quantitative_equivalence_allowed = false`
- `validation_claim_allowed = false`

For the Step105 config this should expose that `0.02` LBM units maps to about
`0.0833333333 m/s`, not the official `10 m/s`.

## Required 50-Step Proxy Transient Smoke

Run exactly one Step105 driver row:

```text
fluent_duct_flap_proxy_48_50step_transient_gap_smoke
```

The row must:

- call canonical `FSIDriver3D.run()`
- complete `50` LBM steps
- write diagnostics for steps `0` through `50`
- write proxy flap-tip displacement time series for steps `0` through `50`
- remain finite: no NaN, no Inf
- keep fixed-base max displacement and velocity at zero tolerance used in
  Step104
- keep `target_u_lbm` applied to inlet, not to solid initial velocity
- keep `all_fluid_geometry_used = false`
- keep Step36 squid wall velocity disabled
- keep `.vtr`, particle `.npy`, video, official Fluent files, and private
  Fluent CSV data absent

The transient may be a smoke run. It must not claim that flow is fully
developed or Fluent-comparable.

## Required Flow-Development Diagnostics

Add flow-development diagnostics from the committed Step105 transient. The
report should live under:

```text
outputs/step105_flow_development/flow_development_report.json
outputs/step105_flow_development/flow_development_report.csv
outputs/step105_flow_development/flow_development_report.md
```

At minimum, summarize the final and/or sampled time-series state for:

- inlet plane mean `ux`
- inlet plane max `ux`
- mid-duct plane mean `ux`
- mid-duct plane max `ux`
- outlet plane mean `ux`
- outlet plane max `ux`
- final fluid mean `ux`
- final far-field fluid mean `ux`
- whether inlet-plane flow is present
- whether mid-duct flow is present
- whether outlet-plane flow is present
- whether flow development is still not Fluent-equivalent

It is acceptable for mid/outlet development to remain weak or incomplete. The
important requirement is that the report shows the plane-specific state rather
than relying only on `lbm_max_v = 0.02`.

## Required Complete Gap Taxonomy

Create a Step105 gap report under:

```text
outputs/step105_gap_taxonomy/gap_taxonomy_report.json
outputs/step105_gap_taxonomy/gap_taxonomy_report.csv
outputs/step105_gap_taxonomy/gap_taxonomy_report.md
```

The report must include at least these named gaps, all still present:

- `dimensionality_2D_vs_3D`
- `conformal_mesh_equivalence`
- `linear_elasticity_equivalence`
- `dynamic_mesh_equivalence`
- `exact_fluent_monitor_equivalence`
- `dimensional_velocity_mapping`
- `turbulence_or_fluid_model_equivalence`
- `steady_preflow_initial_condition`

The report must keep:

- `direct_quantitative_equivalence_allowed = false`
- `validation_claim_allowed = false`
- `gap_count >= 8`

## Required Source Behavior

Step105 may add evidence/reporting helpers and bounded diagnostics, but must
not change solver formulas or broader physics. In particular:

- Do not change LBM collision formulas.
- Do not change tau convention.
- Do not change bounce-back formulas.
- Do not change moving-boundary coupling formulas.
- Do not change reaction transfer formulas.
- Do not change MPM stress/update formulas.
- Do not change vendored `external/taichi_LBM3D`.
- Do not change private benchmark data under `benchmarks/private`.
- Do not change real geometry candidates under `data/real_geometry_candidates`.

If flow-development diagnostics require reading LBM velocity fields, keep the
operation diagnostic-only and do not write back to solver state.

## Required Tests

Add red-to-green tests before implementation. Tests should cover:

1. Step105 config exists and keeps the Step104 repaired setup:
   `n_lbm_steps = 50`, inlet/outlet mode, zero solid initial velocity, Step36
   wall velocity disabled, no VTK, no particle arrays.
2. Dimensional mapping report exists and records the current mapping gap:
   `proxy_inlet_velocity_mps` is approximately `0.0833333333`, official is
   `10.0`, ratio is far below `1.0`, and the mapping gap is present.
3. 50-step transient report passes:
   driver ran, completed `50`, diagnostics rows include steps `0..50`, no
   NaN/Inf, fixed base remains constrained, proxy tip time series exists.
4. Flow-development diagnostics exist and contain inlet/mid/outlet plane
   mean/max `ux` fields, with inlet evidence not confused with full Fluent
   equivalence.
5. Gap taxonomy contains all required eight gaps and keeps validation/equivalence
   claims disabled.
6. Step105 output guard passes and finds no official/proprietary Fluent files,
   no private CSV, no `.vtr`, no particle `.npy`, no video, no Step36 wall
   velocity reference, and no protected external/private data edits.

## Required Artifacts

Create committed artifacts under Step105-specific paths:

```text
outputs/step105_dimensional_mapping/
outputs/step105_driver_runs/fluent_duct_flap_proxy_48_50step_transient_gap_smoke/
outputs/step105_transient_gap_smoke/
outputs/step105_flow_development/
outputs/step105_gap_taxonomy/
outputs/step105_output_guard/
outputs/step105_artifact_manifest/
logs/step105_*.log
docs/105_fluent_duct_flap_proxy_50step_transient_dimensional_gap_audit.md
STEP105_FLUENT_DUCT_FLAP_PROXY_50STEP_TRANSIENT_DIMENSIONAL_GAP_AUDIT_REPORT.md
```

Artifacts must avoid official Ansys payloads, private Fluent CSV data, VTR,
particle NPY, video, large files outside the configured artifact budget, and
absolute private paths in committed JSON/CSV/MD/log content.

## README Requirement

Update `README.md` so the Implemented list and a Step105 boundary section say
that Step105 adds a 50-step duct-flap proxy transient, dimensional mapping
audit, flow-development diagnostics, and expanded gap taxonomy while still
forbidding Fluent validation/equivalence and solver-formula changes.

## Verification Commands

At minimum run:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile <changed python files>
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step105_dimensional_mapping.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step105_fluent_duct_flap_proxy_50step_transient_gap_smoke.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step105_flow_development.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step105_gap_taxonomy.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step105_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step105_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step105_fluent_duct_flap_proxy_transient_gap_contract.py tests\test_step105_output_guard_contract.py
& 'D:\working\taichi\env\python.exe' -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -m pytest -q
pytest -q
```

If a command is blocked by the sandbox or environment, rerun it with the
appropriate approved/escalated path and record the exact outcome in the final
report.

## Completion Criteria

Step105 is complete only when all are true:

- The detailed goal is committed.
- The active Codex goal references this file.
- Step105 config, runners, evidence modules, docs, report, tests, logs, and
  generated artifacts are committed.
- The 50-step transient completed and its artifact says no NaN/Inf.
- Dimensional mapping report explicitly records the velocity gap.
- Flow-development report contains inlet/mid/outlet plane diagnostics.
- Gap taxonomy contains at least the eight required gaps.
- Output guard and artifact manifest pass.
- README matches the actual Step105 behavior.
- Full verification passes.
- The final commit is pushed to `origin/main`.
