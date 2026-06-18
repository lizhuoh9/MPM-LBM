# Larger Grid Validation

Step 14 extends the current engineering validation from 32^3 cases to 48^3 scale baselines and 64^3 feasibility checks. Step 14 does not add new FSI physics.

These runs are an engineering scale baseline, not production benchmark data, and not real squid validation.

## Scope

Step 14 validates the existing `FSIDriver3D` mode matrix at larger grid sizes:

- 48^3 box validation for `none`, `penalty`, and `moving_boundary`
- 48^3 procedural `squid_proxy` validation for `none`, `penalty`, and `moving_boundary`
- 64^3 short feasibility for `none` and `penalty`

The coupling formulas, LBM step paths, MPM update path, projection path, and moving-boundary reaction transfer are unchanged.

## Tested Scales

| case | geometry | modes | n_grid | n_particles | steps | substeps per LBM step |
| ---- | -------- | ----- | -----: | ----------: | ----: | --------------------: |
| 48^3 box | box | none, penalty, moving_boundary | 48 | 13824 | 10 | 10 |
| 48^3 squid proxy | squid_proxy | none, penalty, moving_boundary | 48 | 4096 | 10 | 10 |
| 64^3 feasibility | box | none, penalty | 64 | 32768 | 5 | 5 |

The 48^3 box moving_boundary config uses `target_u_lbm = [0.005, 0.0, 0.0]` and `mb_force_cap_norm = 0.000025`. An initial `target_u_lbm = [0.01, 0.0, 0.0]` trial produced `rho_max = 1.066477895`, outside the Step 14 acceptance range, so only the Step 14 moving_boundary config was made more conservative.

## Results

### 48^3 Box

| mode | stable | rho_min | rho_max | lbm_max_v | mpm_min_J | time s |
| ---- | ------ | ------: | ------: | --------: | --------: | -----: |
| none | True | 1.000000358 | 1.000000358 | 0.000000000 | 0.999999642 | 44.333 |
| penalty | True | 0.999991417 | 1.000009537 | 0.000015987 | 0.999995530 | 45.785 |
| moving_boundary | True | 0.982743502 | 1.039551854 | 0.021100756 | 0.992788911 | 70.848 |

### 48^3 Squid Proxy

The `squid_proxy` is the Step 13 procedural proxy geometry. It is not anatomical squid geometry and not real squid validation.

| mode | stable | rho_min | rho_max | lbm_max_v | mpm_min_J | time s |
| ---- | ------ | ------: | ------: | --------: | --------: | -----: |
| none | True | 1.000000358 | 1.000000358 | 0.000000000 | 0.999999523 | 69.284 |
| penalty | True | 0.999996662 | 1.000004530 | 0.000007749 | 0.999995649 | 91.868 |
| moving_boundary | True | 0.990947962 | 1.012312770 | 0.007713154 | 0.993707359 | 95.615 |

### 64^3 Feasibility

The 64^3 cases are short feasibility checks, not full 64^3 validation.

| mode | stable | rho_min | rho_max | lbm_max_v | mpm_min_J | time s |
| ---- | ------ | ------: | ------: | --------: | --------: | -----: |
| none | True | 1.000000358 | 1.000000358 | 0.000000000 | 0.999999702 | 155.620 |
| penalty | True | 0.999998331 | 1.000002623 | 0.000005288 | 0.999998629 | 178.103 |

## Scaling Summary

Step 14 writes:

```text
outputs/step14_scaling_summary/scaling_summary.csv
outputs/step14_scaling_summary/scaling_summary.json
```

The summary combines Step 12 lower-bound memory estimates with Step 14 runtime rows. The lower-bound estimates remain planning values and exclude Taichi runtime allocation, driver overhead, temporary buffers, Python/NumPy copies, and optional visualization export.

## Artifact Policy

Required Step 14 configs keep:

```text
write_vtk = false
write_particles = false
```

The committed Step 14 artifacts are CSV, NPZ, JSON, and logs. Step 14 artifact manifest reports:

```text
file_count = 438
total_size_mb = 82.145559
large_file_count = 0
```

## Limitations

- not production benchmark data
- not production readiness evidence
- not 96^3 or 128^3 validation
- not real squid validation
- not squid swimming validation
- no new FSI physics
- no two-phase flow
- no contact angle physics
- no sparse storage implementation
