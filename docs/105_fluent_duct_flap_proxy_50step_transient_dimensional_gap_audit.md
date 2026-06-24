# Step105 Fluent Duct-Flap Proxy 50-Step Transient Dimensional-Gap Audit

Step105 runs one longer duct-flap proxy transient on top of the Step104
problem-setup repair. It is an evidence and audit step, not a Fluent validation
step.

Allowed result claim:

```text
Fluent duct-flap proxy 50-step transient smoke ran with repaired Step104 setup, and dimensional/modeling gaps blocking Fluent-equivalence claims are explicitly audited.
```

## Runtime Envelope

- row: `fluent_duct_flap_proxy_48_50step_transient_gap_smoke`
- driver: `src.mpm_lbm.sim.drivers.fsi_driver`
- grid: `48^3`
- particles: `1024`
- LBM steps: `50`
- MPM substeps per LBM step: `1`
- `mpm_dt = 0.0005`
- geometry type: `duct_flap_proxy`
- geometry config: `configs/step104_fluent_duct_flap_geometry_1024.json`
- inlet/outlet mode: `duct_velocity_inlet_pressure_outlet`
- velocity inlet: x-min, `target_u_lbm = [0.02, 0.0, 0.0]`
- pressure outlet: x-max
- solid initial velocity: `[0.0, 0.0, 0.0]`
- Step36 squid wall velocity: disabled
- VTK, particle arrays, and video output: disabled

## Dimensional Mapping Result

Artifact:

- `outputs/step105_dimensional_mapping/velocity_mapping_report.json`

The current proxy mapping is:

- `dx_norm = 0.020833333333333332`
- `lbm_dt_phys = 0.0005`
- `duct_length_m = 0.1`
- `target_u_lbm_x = 0.02`
- `proxy_inlet_velocity_mps = 0.08333333333333333`
- `official_inlet_velocity_mps = 10.0`
- `velocity_ratio = 0.008333333333333333`
- `dimensional_velocity_mapping_gap_present = true`

This confirms the current proxy inlet is not dimensionally equal to the public
Fluent tutorial inlet.

## Transient And Flow Development Result

Artifacts:

- `outputs/step105_transient_gap_smoke/transient_gap_smoke_report.json`
- `outputs/step105_transient_gap_smoke/flap_tip_displacement_timeseries.csv`
- `outputs/step105_flow_development/flow_development_report.json`

The 50-step row completed with no NaN or Inf. Diagnostics and proxy flap-tip
rows cover steps `0` through `50`. The fixed-base particles remain constrained.

Final flow-development snapshot:

- inlet plane mean `ux`: `0.02000000700354576`
- inlet plane max `ux`: `0.020000005140900612`
- mid-duct plane mean `ux`: `0.010271445848047733`
- mid-duct plane max `ux`: `0.01636887900531292`
- outlet plane mean `ux`: `0.0`
- outlet plane max `ux`: `0.0`
- final fluid mean `ux`: `0.005699269473552704`
- final far-field fluid mean `ux`: `0.005688079632818699`

This shows the inlet boundary is active and the duct interior is developing,
but it is still not a Fluent-equivalent transient.

## Gap Taxonomy

Artifact:

- `outputs/step105_gap_taxonomy/gap_taxonomy_report.json`

Step105 keeps these gaps present:

- `dimensionality_2D_vs_3D`
- `conformal_mesh_equivalence`
- `linear_elasticity_equivalence`
- `dynamic_mesh_equivalence`
- `exact_fluent_monitor_equivalence`
- `dimensional_velocity_mapping`
- `turbulence_or_fluid_model_equivalence`
- `steady_preflow_initial_condition`

The report keeps `direct_quantitative_equivalence_allowed = false` and
`validation_claim_allowed = false`.

## Boundary

Step105 does not import a Fluent mesh, does not commit official Ansys files,
does not require private Fluent CSV data, and does not change solver formulas.
It does not claim Fluent validation, solver equivalence, exact structural
model reproduction, official monitor equivalence, official steady preflow, or
production readiness.
