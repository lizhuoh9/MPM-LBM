# Step108 Fluent Official-Speed Low-Mach Subcycling

Step108 adds an opt-in official-time low-Mach subcycling path for the Fluent duct-flap proxy.

The public tutorial inlet speed is `10 m/s`. On the current `48^3` proxy grid with `duct_length_m = 0.1`, one official `0.0005 s` FSI step would map to `u_lbm = 2.4`, which is outside the intended low-Mach LBM range. Step108 therefore fixes the lattice inlet at `u_lbm = 0.02` and uses:

```text
dx_phys_m = 0.1 / 48 = 0.0020833333333333333
lbm_dt_phys_s = 0.02 * dx_phys_m / 10 = 4.166666666666667e-6
lbm_substeps_per_fsi_step = 0.0005 / lbm_dt_phys_s = 120
```

The new driver fields are opt-in only:

```text
fsi_exchange_mode = lbm_subcycled_per_fsi_step
physical_duct_length_m = 0.1
target_inlet_velocity_mps = 10.0
official_fsi_dt_s = 0.0005
target_u_lbm_for_dimensional_mapping = 0.02
lbm_substeps_per_fsi_step = 120
lbm_dt_phys_override_s = 4.166666666666667e-6
```

The default driver behavior remains `one_lbm_step_per_fsi_step`.

## Evidence

Step108 produced these artifacts:

- `outputs/step108_dimensional_mapping/low_mach_subcycling_mapping_report.json`
- `outputs/step108_duct_only_low_mach_subcycling/flow_plane_report.json`
- `outputs/step108_low_mach_fsi_candidate/low_mach_fsi_report.json`
- `outputs/step108_error_comparison/error_report.json`
- `outputs/step108_output_guard/output_guard_report.json`
- `outputs/step108_artifact_manifest/artifact_manifest.json`

The duct-only precheck completed `50` official steps and `6000` LBM substeps with final inlet mean `0.020000007`, mid-duct mean `0.01231391`, outlet mean `0.01240715`, and finite density bounds.

The FSI candidate completed `50` official steps and `6000` LBM substeps. Its displacement curve has `51` rows from `0.0 s` to `0.025 s`.

The Step107-style comparison remains a public-plot proxy comparison, not Fluent validation. Step108 improved the current proxy peak from `3.766233760416071e-7 m` to `1.2332112646618043e-6 m`, normalized RMS from `0.6166683693114237` to `0.616126763475836`, and shape correlation from `0.07747139097796335` to `0.07866350821657236`.

## Limits

Step108 does not reproduce the official Fluent mesh, official case, official steady preflow, or exact structural-point monitor. It only repairs the dimensional inlet-speed mapping and records the resulting proxy curve against the Step107 public-reference harness.
