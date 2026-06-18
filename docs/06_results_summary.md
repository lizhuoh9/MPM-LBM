# Results Summary

This page summarizes committed Step 10 results. These are small-scale engineering baselines, not final accuracy validation.

## Step 10 Mode Matrix

| mode | projection_zone_ux_final | solid_vx_final | rho_min | rho_max | cell_force_max_norm | hydro_force_max_norm |
| ---- | -----------------------: | -------------: | ------: | ------: | ------------------: | -------------------: |
| none | 0.000000000e+00 | 1.562558860e-01 | 1.000000358e+00 | 1.000000358e+00 | 0.000000000e+00 | 0.000000000e+00 |
| penalty | 3.118396126e-05 | 1.536530405e-01 | 9.999890327e-01 | 1.000013232e+00 | 1.964970033e-05 | 1.964970033e-05 |
| moving_boundary | 1.293938956e-03 | 1.509043574e-01 | 9.851434231e-01 | 1.014919758e+00 | 0.000000000e+00 | 4.021631479e-01 |

Trend:

```text
projection_zone_ux_final(moving_boundary) > projection_zone_ux_final(penalty) > projection_zone_ux_final(none)
```

## Step 10 Performance Profile

| mode | total_time | projection_time | coupling_time | lbm_time | mpm_time |
| ---- | ---------: | --------------: | ------------: | -------: | -------: |
| none | 4.373437290e+01 | 8.247374999e-01 | 0.000000000e+00 | 3.809378300e+00 | 2.849920500e+00 |
| penalty | 1.652768771e+02 | 7.281521100e+00 | 5.183930000e-01 | 4.336646700e+01 | 5.827792260e+01 |
| moving_boundary | 7.204992740e+01 | 8.267775000e-01 | 6.620363001e-01 | 4.862220000e+00 | 4.369796800e+00 |

The performance numbers include Python/Taichi execution costs and diagnostic/export overhead in the committed baseline environment. They should be used for regression comparison, not hardware-independent benchmarking.

## Interpretation

- `none` verifies shared driver coexistence without coupling forces.
- `penalty` produces a weak projection-zone velocity response through diffuse forcing.
- `moving_boundary` produces a stronger projection-zone response through opt-in moving bounce-back and reaction transfer.

The current evidence supports mode comparison and stability-window tracking. It does not establish final physical accuracy.
