# Moving-Boundary Calibration

Step 15 adds moving-boundary reaction calibration diagnostics and recommended stable-window configs for the existing `moving_boundary` path.

Step 15 does not change the moving bounce-back formula. Step 15 does not add new FSI physics. The Step 8 link-wise moving-boundary path, the Step 9 `MovingBoundaryFSICoupler3D` transfer formula, the Step 10 driver mode matrix, and the Step 14 scale baselines remain intact.

## Scope

Step 15 records diagnostic quantities that already exist in the solver state:

- LBM link-wise impulse from `bb_net_fluid_impulse`
- LBM diagnostic wall force from `hydro_force`
- the existing sampled MPM applied grid force from `MovingBoundaryFSICoupler3D`
- the equal-and-opposite reaction convention used for accounting tables
- MPM solid particle momentum from `sum(mass[p] * v[p])`

`MomentumAccounting3D` is diagnostic-only. It copies Taichi fields to NumPy and reduces them in Python. It does not initialize Taichi, step LBM, step MPM, or write solver fields.

The transfer remains an engineering coupling scale.
Strict link-area momentum-conserving coupling is future work.
squid_proxy is procedural and not real squid validation.

## Accounting Convention

The existing Step 9 engineering transfer applies a sampled value to `solid.grid_f_ext`. Step 15 preserves that applied value in the accounting rows as:

```text
applied_particle_reaction_force_x
applied_grid_reaction_force_x
```

The contract-facing `net_particle_reaction_force_x` and `net_grid_reaction_force_x` use the equal-and-opposite reaction convention for sign consistency checks. This is a diagnostic convention only; it does not change `MovingBoundaryFSICoupler3D`.

## Reaction Scale Calibration

The 32^3 box sweep uses:

```text
reaction_scale = [0.25, 0.5, 1.0, 2.0]
force_cap_norm = 0.0001
target_u_lbm_x = 0.01
```

All four rows stayed within the Step 15 hard stability thresholds. The lowest rho span and score selected `reaction_scale = 0.25` for the 32^3 sweep note, but the 48^3 box recommendation is selected from the 48^3 force-cap evidence.

## Force Cap Calibration

The 48^3 box sweep uses:

```text
force_cap_norm = [0.00001, 0.000025, 0.00005, 0.0001]
reaction_scale = 1.0
target_u_lbm_x = 0.005
```

The conservative `force_cap_norm = 0.00001` row was well behaved. The Step 14 known-good `force_cap_norm = 0.000025` row stayed stable, while higher caps exceeded the rho upper bound and remain recorded as failed evidence.

Recommended box 48^3 config:

```text
configs/step15_mb_recommended_box_48.json
reaction_scale = 1.0
force_cap_norm = 0.00001
```

## Squid Proxy Calibration

The 48^3 `squid_proxy` sweep uses:

```text
reaction_scale = [0.5, 1.0]
force_cap_norm = [0.000025, 0.00005]
target_u_lbm_x = 0.005
```

All four procedural proxy rows were stable. The recommended row is the more conservative well-behaved setting:

```text
configs/step15_mb_recommended_squid_proxy_48.json
reaction_scale = 0.5
force_cap_norm = 0.000025
```

## Limitations

Step 15 is calibration and accounting infrastructure. It is not final sharp-interface FSI, not real squid validation, not squid swimming validation, not two-phase flow, not contact angle physics, and not sparse-storage work.

## Step 16 Use Of Calibrated Settings

Step 16 does not add new FSI physics. It uses the Step 15 recommended moving_boundary settings directly:

| case | reaction_scale | force_cap_norm | target_u_lbm_x |
| ---- | -------------: | -------------: | ---------------: |
| 48^3 box long-run | 1.0 | 0.00001 | 0.005 |
| 48^3 procedural squid_proxy long-run | 0.5 | 0.000025 | 0.005 |
| 64^3 moving_boundary feasibility | 1.0 | 0.000005 | 0.0025 |

The 64^3 moving_boundary row is a feasibility baseline. squid_proxy is procedural and not real squid validation. Strict link-area momentum-conserving coupling remains future work.

## Step 17 Direction-Wise Accounting

Step 17 adds diagnostic-only direction-wise and link-area proxy accounting. It records per-D3Q19 direction link counts, fluid impulse, solid reaction, and correction statistics on top of the Step 15 calibration path.

The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. These are diagnostic proxy policies, not final surface-area reconstruction. Strict link-area momentum-conserving coupling remains future work. squid_proxy is procedural and not real squid validation.
