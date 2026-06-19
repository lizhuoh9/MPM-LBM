# Long-Run Validation

Step 16 does not add new FSI physics. It uses the Step 15 calibrated moving_boundary settings to run longer 48^3 stability baselines and a conservative 64^3 moving_boundary feasibility baseline.

The 64^3 moving_boundary row is a feasibility baseline. squid_proxy is procedural and not real squid validation. Strict link-area momentum-conserving coupling remains future work.

## Scope

Step 16 validates the existing `FSIDriver3D` paths:

- 48^3 box moving_boundary long-run
- 48^3 procedural squid_proxy moving_boundary long-run
- 64^3 moving_boundary feasibility
- 64^3 none/penalty/moving_boundary mode comparison

The coupling formulas, moving bounce-back formula, reaction transfer formula, penalty coupling path, projection path, and MPM update path are unchanged.

## Required Configs

All required Step 16 configs keep:

```text
write_vtk = false
write_particles = false
```

The long 48^3 box config uses `mb_reaction_scale = 1.0` and `mb_force_cap_norm = 0.00001`. The long 48^3 procedural squid_proxy config uses `mb_reaction_scale = 0.5` and `mb_force_cap_norm = 0.000025`. The 64^3 moving_boundary feasibility config uses `mb_reaction_scale = 1.0`, `mb_force_cap_norm = 0.000005`, and `target_u_lbm_x = 0.0025`.

## Results

| case | mode | n_grid | particles | LBM steps | MPM substeps | rho_min | rho_max | lbm_max_v | mpm_min_J |
| ---- | ---- | -----: | --------: | --------: | -----------: | ------: | ------: | --------: | --------: |
| long box | moving_boundary | 48 | 13824 | 50 | 500 | 0.988891482 | 1.017282963 | 0.012052457 | 0.992399573 |
| long squid_proxy | moving_boundary | 48 | 4096 | 30 | 300 | 0.991026938 | 1.012060523 | 0.007719210 | 0.993878663 |
| feasibility box | moving_boundary | 64 | 32768 | 5 | 25 | 0.992273271 | 1.002777219 | 0.005351932 | 0.995547831 |
| mode compare | none | 64 | 32768 | 5 | 25 | 1.000000000 | 1.000000358 | 0.000000000 | 0.999999702 |
| mode compare | penalty | 64 | 32768 | 5 | 25 | 0.999999285 | 1.000001550 | 0.000002630 | 0.999998987 |
| mode compare | moving_boundary | 64 | 32768 | 5 | 25 | 0.992273331 | 1.002777338 | 0.005351928 | 0.995547831 |

## Mode Matrix Checks

The 64^3 mode comparison preserved the expected mode separation:

- `none`: `cell_force_max_norm = 0` and `bb_link_count_min = 0`
- `penalty`: `cell_force_max_norm > 0` and `bb_link_count_min = 0`
- `moving_boundary`: `cell_force_max_norm = 0` and `bb_link_count_min > 0`

## Outputs

Step 16 writes:

```text
outputs/step16_long_box_48_moving_boundary/
outputs/step16_long_squid_proxy_48_moving_boundary/
outputs/step16_feasibility_64_moving_boundary/
outputs/step16_64_mode_comparison/
outputs/step16_long_run_summary/
outputs/step16_artifact_manifest/
```

The main aggregate files are:

```text
outputs/step16_long_run_summary/step16_summary.csv
outputs/step16_long_run_summary/step16_summary.json
```

## Limitations

- not real squid validation
- not squid swimming validation
- not a final sharp-interface FSI validation
- not strict final momentum conservation
- not two-phase flow
- not contact angle physics
- not sparse storage work

## Step 17 Link-Area Accounting

Step 17 adds diagnostic-only direction-wise and link-area proxy accounting. It reuses the Step 16 calibrated settings to analyze moving-boundary link budgets without changing the Step 16 solver behavior.

The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. These are diagnostic proxy policies, not final surface-area reconstruction. Strict link-area momentum-conserving coupling remains future work. squid_proxy is procedural and not real squid validation.
