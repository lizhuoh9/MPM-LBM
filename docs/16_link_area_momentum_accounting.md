# Link-Area Momentum Accounting

Step 17 adds diagnostic-only direction-wise and link-area proxy accounting.

The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. These are diagnostic proxy policies, not final surface-area reconstruction. Strict link-area momentum-conserving coupling remains future work. squid_proxy is procedural and not real squid validation.

## Scope

Step 17 adds moving-boundary diagnostics for:

- per-D3Q19 direction bounce-back link counts
- per-D3Q19 direction fluid impulse
- per-D3Q19 direction solid reaction force
- per-D3Q19 direction correction absolute sum and max
- area proxy budgets for `uniform`, `inverse_length`, and `length`

The diagnostic fields are small 19-entry reductions. They do not change the LBM distribution update, MPM update, projection path, or moving-boundary reaction transfer.

## Direction Classes

The accounting uses the actual `LBMFluid3D.e` direction ordering:

| class | definition |
| ----- | ---------- |
| rest | `||e||_1 = 0` |
| axis | `||e||_1 = 1` |
| face_diagonal | `||e||_1 = 2` |

D3Q19 has no body diagonal directions.

## Area Proxy Policies

| policy | weight |
| ------ | ------ |
| `uniform` | `1` for non-rest directions |
| `inverse_length` | `1 / ||e||` for non-rest directions |
| `length` | `||e||` for non-rest directions |

The default reporting policy is `inverse_length`. The policies are accounting proxies only. They are not a surface mesh reconstruction or final link-area integration.

## Baseline Results

| case | policy | total links | axis links | face diagonal links | area proxy total | rho_min | rho_max | lbm_max_v |
| ---- | ------ | ----------: | ---------: | ------------------: | ---------------: | ------: | ------: | --------: |
| wall Couette | uniform | 10240 | 2048 | 8192 | 10240.000000 | 1.000004411 | 1.000011086 | 0.027463466 |
| wall Couette | inverse_length | 10240 | 2048 | 8192 | 7840.618751 | 1.000004411 | 1.000011086 | 0.027463466 |
| wall Couette | length | 10240 | 2048 | 8192 | 13633.237503 | 1.000004411 | 1.000011086 | 0.027463466 |
| box 48^3 | inverse_length | 5964 | 1232 | 4732 | 4578.029289 | 0.988891542 | 1.017282963 | 0.009996162 |
| squid_proxy 48^3 | inverse_length | 6616 | 1746 | 4870 | 5189.610024 | 0.991027117 | 1.012060523 | 0.007719247 |
| box 64^3 | inverse_length | 11186 | 2424 | 8762 | 8619.669617 | 0.992273271 | 1.002777219 | 0.005351911 |

## Directional Consistency

The directional link sanity baseline produced:

```text
bb_link_count = 10240
sum_link_count_by_dir = 10240
scalar_vs_directional_impulse_error_x = 0.0
```

The scalar moving-boundary diagnostic is finalized from the per-direction reductions, so scalar and direction-wise accounting use a single diagnostic source.

## Limitations

- diagnostic-only accounting
- not a new FSI mode
- not a new reaction transfer formula
- not final surface-area reconstruction
- not real squid validation
- not squid swimming validation
- not strict final momentum conservation
- not two-phase flow
- not contact angle physics
- not sparse storage work
