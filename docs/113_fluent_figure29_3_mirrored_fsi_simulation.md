# Step113 Fluent Figure 29.3 Mirrored FSI Simulation

Step113 consolidates the post-Step112 velocity-cloud rendering and mirrored
duct-flap FSI attempts. The target visual context is the public Ansys Fluent
two-way-FSI duct/flap tutorial, but these runs use this repository's procedural
proxy geometry and Taichi MPM-LBM solver.

This is a diagnostic report, not a Fluent validation claim. It does not import
the official mesh, does not run Fluent, and does not assert exact structural,
dynamic-mesh, monitor, or contour equivalence.

## Completed Evidence

- Step112 velocity-cloud rerender:
  `outputs/step112_velocity_cloud_render/`
- Thin extruded static two-flap flow visualization:
  `outputs/step113_fluent_like_thin_extruded_3d_velocity_render/`
- Unstabilized full-FSI failure data:
  `outputs/step113_full_fsi_mirrored_duct_flap_96/`
- Stabilized completed full-FSI run:
  `outputs/step113_full_fsi_mirrored_duct_flap_96_stabilized/`
- Machine-readable inventory:
  `outputs/step113_simulation_data_inventory.json`

## Stabilized Full-FSI Run

The completed run is
`stabilized_full_two_way_fsi_mirrored_duct_flap_proxy`.

Configuration summary:

- 96^3 fluid grid, 884736 cells.
- 8192 MPM particles.
- Two mirrored procedural flaps.
- Moving-boundary coupling with reaction transfer.
- 50 official FSI samples through `0.025 s`.
- 240 LBM substeps per official FSI step, 12000 LBM substeps total.
- 250 MPM substeps total.
- Stabilizers: lock-z planar constraint, velocity damping, smaller MPM
  substeps, and capped moving-boundary reaction.

Final summary artifact:
`outputs/step113_full_fsi_mirrored_duct_flap_96_stabilized/full_fsi_run_summary.json`.

Final render artifacts:

- `outputs/step113_full_fsi_mirrored_duct_flap_96_stabilized/figure29_3_style_full_fsi_step050_scale0_28p1.png`
- `outputs/step113_full_fsi_mirrored_duct_flap_96_stabilized/figure29_3_style_full_fsi_step050_field_only.png`

## Findings

- The earlier Step112 render was a 48^3 single-flap visualization rerun, not
  the full mirrored duct/flap model.
- The 480 x 240 x 12 thin extruded run is a static LBM visualization. It can
  produce an official-style velocity cloud, but it is not two-way FSI.
- The 96^3 dimensional mapping requires `lbm_substeps_per_fsi_step = 240` for
  the 10 m/s public inlet reference with `target_u_lbm = 0.02`.
- The unstabilized full-FSI attempt failed: negative `J` appeared at official
  step 5 and NaN/Inf diagnostics aborted the run after step 6.
- The stabilized full-FSI run completed, but the final flap-tip displacement
  was only `1.2151136616012082e-05 m`; this under-deformation explains why the
  final velocity image still does not match the Fluent jet/nozzle shape.

## Verification

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\mpm_lbm\sim\geometry\duct_flap_proxy.py tests\test_step113_mirrored_duct_flap_geometry_contract.py
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step113_mirrored_duct_flap_geometry_contract.py tests\test_step104_fluent_duct_flap_setup_repair_contract.py tests\test_step112_planar_constraint_contract.py
```
