# Step153 Goal: Official Tutorial Setup Parity Correction

## Source Contract

Step153 follows the user-provided review of `origin/main =
123c50258f689ef5f34525a65045df878f621190` and the public Ansys Chapter 29
two-way FSI tutorial setup. Step152's blocked behavior was correct for targeted
solver patches because no real official monitor was available, but the next
useful action is not another blocked gate. Step153 must correct our local
solver reproduction setup so it matches the official tutorial setup window and
metadata before any official-vs-solver error localization is attempted.

The current repository already has a historical Step148 solver reproduction
that runs a Fluent-like duct/flap proxy. Its default run window is broader than
the tutorial:

```text
Step148 default n_steps = 250
Step148 dt_s = 0.0005
Step148 total time = 0.125 s
```

The official tutorial setup window is:

```text
Number of Time Steps = 50
Time Step Size = 0.0005 s
Total tutorial time = 0.025 s
Max Iterations / Time Step = 40
```

Step153 must therefore produce a new solver-run artifact family instead of
overwriting Step148.

## Objective

Implement:

```text
Step153 Official Tutorial Setup Parity Correction
```

This step must convert our own `FSIDriver3D` reproduction from a generic proxy
FSI run into a proxy reproduction explicitly aligned to the public Ansys
Chapter 29 tutorial setup. It uses public setup truth only. It must not require
or fabricate `official_monitor.csv`, and it must not claim Fluent validation
or error localization.

## Required Runner

Add a new executable module:

```text
experiments/steps/step153_official_tutorial_setup_parity.py
```

The default command is:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step153_official_tutorial_setup_parity `
  --official-private-root benchmarks\private\fluent_fsi_2way `
  --output-dir outputs\step153_official_tutorial_setup_parity `
  --grid 48 `
  --n-steps 50 `
  --dt-s 0.0005 `
  --force
```

The runner must call the real `FSIDriver3D` path through the Step148 runner
helper surface. It must not call Step121, Fluent, a pure design-only report,
or a synthetic monitor generator.

## Official Tutorial Constants

Encode these public setup constants in Step153 artifacts:

```json
{
  "duct_length_m": 0.10,
  "duct_height_m": 0.04,
  "flap_height_m": 0.01,
  "flap_thickness_m": 0.003,
  "half_domain_mode": true,
  "inlet_air_velocity_mps": 10.0,
  "outlet_type": "pressure_outlet",
  "monitor_point_m": [0.0505, 0.0095],
  "monitor_quantity": "Structure / Total Displacement",
  "official_tutorial_time_steps": 50,
  "official_tutorial_dt_s": 0.0005,
  "official_tutorial_total_time_s": 0.025,
  "max_iterations_per_time_step": 40
}
```

Encode these official material constants:

```json
{
  "material_name": "silicone-rubber",
  "solid_density_kg_m3": 1600.0,
  "youngs_modulus_pa": 1000000.0,
  "poisson_ratio": 0.47
}
```

The monitor point is already used by Step148 as a Fluent-like proxy monitor.
Step153 must promote it from a proxy assumption to an artifact-backed official
tutorial setup constant.

## Material Mapping Requirement

If `FSIDriverConfig` can carry the official structural material fields, Step153
should populate them and report:

```json
{
  "official_structural_material_applied": true,
  "material_mapping_gap_blocks_physics_parity": false
}
```

If the solver cannot yet consume those fields, Step153 must not pretend
otherwise. It must report:

```json
{
  "official_structural_material_applied": false,
  "missing_solver_config_fields": ["..."],
  "material_mapping_gap_blocks_physics_parity": true
}
```

The preferred implementation is to add explicit material fields to
`FSIDriverConfig` and wire them into the Step153 configuration/reporting
surface. This is a setup-parity contract, not a claim that the solver now
matches Fluent's FEM structural formulation.

## Boundary And FSI Semantic Report

Step153 must write:

```text
outputs/step153_official_tutorial_setup_parity/boundary_semantics_gap_report.json
```

It must include at least:

```json
{
  "official_velocity_inlet_present": true,
  "official_pressure_outlet_present": true,
  "official_fixed_flap_attach_present": true,
  "official_intrinsic_fsi_wall_present": true,
  "official_dynamic_mesh_fsi_wall_shadow_present": true,
  "official_stationary_dynamic_mesh_zones": [
    "pressure_outlet",
    "symmetry",
    "velocity_inlet",
    "wall"
  ],
  "our_solver_equivalent_moving_boundary_mode": "moving_boundary",
  "semantic_gaps": [
    "Fluent intrinsic FSI solid zone is FEM-like linear elasticity; our solid is MPM",
    "Fluent dynamic mesh smoothing is linearly elastic solid; our LBM grid uses moving-boundary/proxy coupling"
  ]
}
```

## Required Output Artifacts

Generate:

```text
outputs/step153_official_tutorial_setup_parity/
  official_tutorial_setup_report.json
  official_tutorial_setup_report.md
  solver_run_manifest.json
  solver_monitor.csv
  solver_force_monitor.csv
  solver_reproduction_summary.json
  geometry_mapping_report.json
  material_mapping_report.json
  boundary_semantics_gap_report.json
  official_reference_gap_report.json
```

Update:

```text
docs/campaigns/fluent_duct_flap/steps/153/report.md
docs/current/STATUS.md
docs/current/ACTIVE_CAMPAIGN.json
docs/current/READING_ORDER.md
docs/current/VALIDATION_GATES.md
README.md
```

Do not overwrite Step148 artifacts. Step148 remains historical evidence of the
broader 250-step reproduction.

## Acceptance Summary

The Step153 summary must include:

```json
{
  "step": 153,
  "status": "official_tutorial_setup_parity_run_complete",
  "our_solver_run_executed": true,
  "solver_monitor_found": true,
  "solver_monitor_rows": "> 0",
  "official_tutorial_time_steps": 50,
  "official_tutorial_dt_s": 0.0005,
  "official_tutorial_total_time_s": 0.025,
  "solver_time_end_s": 0.025,
  "monitor_point_m": [0.0505, 0.0095],
  "material_density_kg_m3": 1600.0,
  "youngs_modulus_pa": 1000000.0,
  "poisson_ratio": 0.47,
  "official_monitor_required_for_error_metrics": true,
  "official_monitor_loaded": false,
  "validation_claim_allowed": false,
  "selected96_execution_allowed": false,
  "selected96_ready": false
}
```

`solver_time_end_s` may be computed from the emitted monitor. It must be
within a tight tolerance of `0.025` for the official 50-step setup.

## Contract Tests

Add:

```text
tests/test_step153_official_tutorial_setup_parity_contract.py
```

The tests must cover:

1. Official constants are encoded: duct `0.10 m`, height `0.04 m`, flap
   `0.01 m`, thickness `0.003 m`, inlet `10 m/s`, density `1600`, `E=1e6`,
   `nu=0.47`, monitor point `(0.0505, 0.0095)`, `n_steps=50`, and `dt=0.0005`.
2. The runner uses `FSIDriver3D` through Step148's real solver path and does
   not call Step121.
3. The runner can produce `solver_monitor.csv` with time ending at `0.025 s`
   when driven by a monkeypatched real-run helper.
4. Official monitor data is not required for the setup-parity run.
5. Official payload and official monitor bodies are not committed.
6. `material_mapping_report.json` states whether official structural material
   was applied.
7. `boundary_semantics_gap_report.json` lists the Fluent intrinsic-FSI versus
   our moving-boundary/MPM semantic gaps.
8. `selected96_ready`, `selected96_execution_allowed`, and
   `validation_claim_allowed` remain false.

Tests must be lightweight and must not require Fluent, private official data,
selected96, or a long solver job.

## Follow-Up Boundaries

After Step153:

If a real `official_monitor.csv` exists, Step155 can run true official-vs-
Step153-solver error localization using:

```text
outputs/step153_official_tutorial_setup_parity/solver_monitor.csv
outputs/step153_official_tutorial_setup_parity/solver_force_monitor.csv
outputs/step153_official_tutorial_setup_parity/solver_reproduction_summary.json
```

If no real official monitor exists, the next useful step is Step154 official
Figure 29.4 / report-file reference extraction as diagnostic-only evidence.
Digitized figure references must remain low confidence and cannot enable
validation claims.

## Prohibited Actions

Do not:

```text
write another blocked gate as the main feature
overwrite Step148 outputs
modify solver formulas to chase a comparison curve
run Fluent
run selected96
claim official validation, Figure 29.3 parity, or production readiness
commit benchmarks/private payloads
commit official_monitor.csv or raw Fluent exports
fabricate official monitor samples from solver outputs
fake Step150 error localization
fake Step151 targeted fix plan
fake solver patch readiness
```

## Done Criteria

Step153 is complete when:

- The detailed goal file exists and the active goal references it.
- The Step153 parity runner and contract tests exist.
- Step153 produces the official tutorial setup reports and solver monitors
  under `outputs/step153_official_tutorial_setup_parity/`.
- The solver run uses the official tutorial time window: 50 steps, `dt=0.0005`,
  total `0.025 s`.
- Official geometry, material, monitor point, and boundary semantics are
  recorded in committed artifacts.
- No private official monitor body is staged or committed.
- No Fluent validation or selected96 readiness is claimed.
- Focused Step153 tests pass with `D:\working\taichi\env\python.exe`.
- The Step153 runner command completes in the current checkout.
- Relevant docs are updated.
- The finished code, tests, docs, and generated public artifacts are committed
  and pushed to `origin/main`.
