# Link-Area Long-Run Validation

Step 19 validates the opt-in link_area_experimental transfer over longer windows and 64^3 feasibility.

The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. LinkAreaMovingBoundaryCoupler3D formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. The link-area transfer remains experimental and uses a bounded global area_scale. This is not final strict momentum-conserving sharp-interface FSI. squid_proxy is procedural and not real squid validation.

## Scope

Step 19 is a validation and reproducibility step. It adds longer 48^3 windows, conservative 64^3 feasibility, engineering-vs-link-area comparisons, area_scale drift diagnostics, summary artifacts, logs, and a contract test.

It does not add new FSI physics, a new transfer formula, mesh import, real squid validation, squid actuation, two-phase flow, contact angle physics, sparse storage, or ReducedSquidFSI.

## Baselines

| case | transfer | completed LBM steps | MPM substeps | rho_min | rho_max | lbm_max_v | mpm_min_J | area_scale_min | area_scale_final | stable |
| ---- | -------- | ------------------: | -----------: | ------: | ------: | --------: | --------: | -------------: | ---------------: | ------ |
| box_48_link_area_long | link_area_experimental | 50 | 500 | 0.988891423 | 1.017294407 | 0.011978018 | 0.992365003 | 0.417903900 | 0.853882253 | true |
| squid_proxy_48_link_area_long | link_area_experimental | 30 | 300 | 0.991046309 | 1.012029171 | 0.007718042 | 0.993962169 | 0.784083664 | 0.808569014 | true |
| box_64_link_area_feasibility | link_area_experimental | 5 | 25 | 0.992273211 | 1.002777219 | 0.005351947 | 0.995547712 | 0.777285635 | 0.777285635 | true |

## Comparisons

The engineering rows keep `area_scale = 1.0`. The link_area_experimental rows keep finite bounded area_scale in `[0.25, 2.0]`. No comparison requires link_area_experimental to outperform engineering.

| comparison | rows | status |
| ---------- | ---: | ------ |
| 64^3 engineering vs link_area_experimental | 2 | stable |
| 48^3 box and procedural squid_proxy engineering vs link_area_experimental | 4 | stable |
| Step 18 regression | 3 | stable |

## Artifacts

Primary artifacts:

- `outputs/step19_long_box_48_link_area/`
- `outputs/step19_long_squid_proxy_48_link_area/`
- `outputs/step19_feasibility_64_link_area/`
- `outputs/step19_compare_64_engineering_vs_link_area/`
- `outputs/step19_compare_48_long_engineering_vs_link_area/`
- `outputs/step19_regression_step18/`
- `outputs/step19_long_run_summary/`
- `outputs/step19_artifact_manifest/`

Each link-area run writes `diagnostics_timeseries.csv`, `diagnostics_timeseries.npz`, `link_area_timeseries.csv`, `link_area_timeseries.npz`, and a summary row.

## Decision

Step 19 supports proceeding to Step 20: mesh/voxel geometry import pipeline. The next bottleneck is geometry ingestion, not claiming final strict momentum-conserving sharp-interface FSI.
