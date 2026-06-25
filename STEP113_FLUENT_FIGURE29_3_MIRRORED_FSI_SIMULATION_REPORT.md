# Step113 Fluent Figure 29.3 Mirrored FSI Simulation Report

Step113 consolidates the velocity-cloud renders and full-FSI attempts made
after Step112. The target visual reference is the public Ansys Fluent
two-way-FSI duct/flap tutorial Figure 29.3/29.5 context, but every run here
uses this repository's procedural proxy geometry and Taichi MPM-LBM solver.

This is not a Fluent validation result. It does not import `flap.msh`, does not
run Fluent, does not reproduce the official dynamic mesh, and does not assert
point-by-point equivalence to the public tutorial images.

## Runs

| Run | Scope | Data | Result |
| --- | --- | --- | --- |
| Step112 velocity-cloud rerender | Reran Step112 best candidate `cap_1e-2_E_2e4` only to capture dense velocity fields for plotting. Grid is 48^3 and the model is the older single-flap proxy. | `outputs/step112_velocity_cloud_render/` | Render data exists, but it exposed that the prior visualization was too coarse and used only one flap. |
| Thin extruded static two-flap flow | Procedural full-domain two-flap duct, 480 x 240 x 12 cells, periodic thin z layer, static flaps, no MPM deformation. | `outputs/step113_fluent_like_thin_extruded_3d_velocity_render/` | Useful for a Figure 29.3-style static velocity cloud, but it is not FSI and cannot answer flap-deformation questions. |
| Unstabilized full FSI attempt | 96^3 duct-flap proxy, 8192 particles, two mirrored flaps, moving-boundary coupling, official material reference, 240 LBM substeps per official FSI step. | `outputs/step113_full_fsi_mirrored_duct_flap_96/` | Aborted around official step 6 after negative Jacobian growth and NaN/Inf diagnostics. |
| Stabilized full FSI run | Same mirrored 96^3/8192-particle full-FSI setup, with lock-z planar constraint, velocity damping, smaller MPM substeps, and capped reaction. | `outputs/step113_full_fsi_mirrored_duct_flap_96_stabilized/` | Completed the 50-step, 0.025 s official tutorial window and produced Figure 29.3-style velocity plots. |

## Stabilized Full-FSI Summary

Final artifact:
`outputs/step113_full_fsi_mirrored_duct_flap_96_stabilized/full_fsi_run_summary.json`.

Key settings:

- `n_grid = 96`, so the fluid lattice is 884736 cells.
- `n_particles = 8192`.
- `coupling_mode = moving_boundary`.
- `flap.mirrored_pair = true`, giving upper and lower flaps in the procedural full domain.
- `target_inlet_velocity_mps = 10.0`, `target_u_lbm = 0.02`.
- `official_fsi_dt_s = 0.0005`.
- `lbm_substeps_per_fsi_step = 240`, for 12000 LBM substeps over 50 official FSI samples.
- `mpm_substeps_per_lbm_step = 5`, `mpm_dt = 0.0001`.
- Stabilization: `mpm_planar_constraint_mode = lock_z`,
  `mpm_velocity_damping = 50.0`, `mb_force_cap_norm = 0.001`.

Final diagnostics:

- `rho_min = 0.9999998807907104`
- `rho_max = 1.012130856513977`
- `lbm_max_v = 0.049227576702833176`, mapped to `24.613786697387695 m/s`
- `fluid_mean_ux = 0.016015877947211266`
- `mpm_min_J = 0.9995114803314209`
- `mpm_max_speed = 0.009615207090973854`
- `active_reaction_particle_count = 8192`
- `bb_link_count = 47266`
- final flap-tip displacement at 0.025 s:
  `1.2151136616012082e-05 m`

Figure-style render:

- `outputs/step113_full_fsi_mirrored_duct_flap_96_stabilized/figure29_3_style_full_fsi_step050_scale0_28p1.png`
- `outputs/step113_full_fsi_mirrored_duct_flap_96_stabilized/figure29_3_style_full_fsi_step050_field_only.png`

## What The Simulation Did

Step113 added procedural support for a mirrored duct-flap pair. The default
`duct_flap_proxy` still produces one flap for backward compatibility, while
`flap["mirrored_pair"] = true` adds the upper flap and reports
`flap_count = 2` in sampling and static-geometry metadata.

The stabilized full-FSI run used the real solver path:

- LBM flow in the duct with x-min velocity inlet and x-max pressure outlet.
- MPM solid particles for the two flexible flaps.
- Moving-boundary coupling and reaction transfer back to MPM particles.
- Full 50 official FSI samples through `0.025 s`.
- Dense velocity snapshots and Figure 29.3-style post-processing.

## Errors And Mismatches Found

1. The first Step112 velocity-cloud image was not the official-like geometry:
   it was 48^3, single-flap, and only a rerun for visualization capture.
2. The first thin extruded 480 x 240 x 12 visualization was static LBM flow,
   not two-way FSI. It can show a duct jet, but it cannot validate flap
   deformation or reaction transfer.
3. For `n_grid = 96`, the correct dimensional mapping for 10 m/s and
   `target_u_lbm = 0.02` requires `lbm_substeps_per_fsi_step = 240`, not 120.
4. The unstabilized two-flap full-FSI attempt became structurally unstable:
   by step 5 `mpm_min_J` was negative, and by step 6 diagnostics contained
   NaN/Inf. See
   `outputs/step113_full_fsi_mirrored_duct_flap_96/unstabilized_failure_summary.json`.
5. The stabilized full-FSI run completed, but stabilization also suppresses
   flap deformation. The final flap-tip displacement is about 0.012 mm, so the
   final velocity plot does not form the same narrow, strongly deformed nozzle
   seen in the Fluent tutorial image.
6. The current model is still a voxelized procedural proxy, not a conformal
   Fluent mesh. That alone changes the throat shape, wall resolution, and
   jet-shear layer.

## Data Inventory

Machine-readable inventory:
`outputs/step113_simulation_data_inventory.json`.

Important directories:

- `outputs/step112_velocity_cloud_render/`: Step112 rerun velocity field and PNGs.
- `outputs/step113_fluent_like_thin_extruded_3d_velocity_render/`: static
  thin-layer two-flap LBM field data, geometry, metadata, and official-style PNGs.
- `outputs/step113_full_fsi_mirrored_duct_flap_96/`: failed unstabilized full-FSI
  setup, geometry, and failure summary.
- `outputs/step113_full_fsi_mirrored_duct_flap_96_stabilized/`: completed full-FSI
  run, diagnostics CSV/NPZ, displacement CSV, velocity snapshots, and PNGs.

Total newly organized output payload covered by this report: 52 files,
17283908 bytes.

## Verification

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\mpm_lbm\sim\geometry\duct_flap_proxy.py tests\test_step113_mirrored_duct_flap_geometry_contract.py
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step113_mirrored_duct_flap_geometry_contract.py tests\test_step104_fluent_duct_flap_setup_repair_contract.py tests\test_step112_planar_constraint_contract.py
```

The Step113 contract test ensures the default single-flap behavior remains
unchanged and the opt-in mirrored-pair geometry exposes two flaps to component
masks, sampling metadata, and static voxel geometry when requested.
