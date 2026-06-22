# Step86 Squid Proxy Static Geometry Canonical Driver Smoke

Step86 executes exactly one canonical `FSIDriver3D.run()` row for procedural
static `squid_proxy` geometry:
`canonical_driver_squid_proxy_static_geometry_32_3step_smoke`.

The only positive claim is:

```text
squid_proxy static geometry canonical driver 3-step smoke passed
```

Step86 is not real squid validation, squid swimming, squid actuation, physical
validation, grid convergence, or production readiness.

## Executed Row

```text
campaign_id = step86_squid_proxy_static_geometry_canonical_driver_smoke
row_id = canonical_driver_squid_proxy_static_geometry_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
boundary_motion_mode = static
geometry_motion_mode = static
geometry_motion_application_mode = disabled
wall_velocity_application_mode = disabled
write_vtk = false
write_particles = false
executed_in_step86 = true
```

No optional row is present.

## Smoke Evidence

```text
step86_squid_proxy_static_geometry_smoke_matrix_pass = true
required_row_count = 1
optional_row_count = 0
required_stable_count = 1
driver_run_called_count = 1
completed_lbm_steps = 3
total_mpm_substeps = 3
diagnostics_row_count = 4
rho_min_min = 0.9614667892456055
rho_max_max = 1.0393489599227905
lbm_max_v_max = 0.0288397129625082
mpm_min_J_min = 0.999782145023346
mpm_max_speed_max = 1.567559003829956
projected_mass_final = 0.02264912612736225
active_cell_count_final = 1763
bb_link_count_max = 2574
max_grid_reaction_norm_max = 4.2154038965236396e-05
```

## Quality Evidence

```text
step86_squid_proxy_static_geometry_quality_pass = true
geometry_quality_report_pass_count = 1
quality_check_strict = false
quality_report_occupied_count = 774
quality_report_surface_voxel_count = 358
quality_report_touches_domain_boundary = false
sampling_particle_count = 1024
mantle_particle_count = 867
head_particle_count = 189
arms_particle_count = 52
left_fin_particle_count = 23
right_fin_particle_count = 22
```

## Guarded Closures

```text
activation_feature_count = 1
procedural_geometry_enabled_count = 1
squid_proxy_enabled_count = 1
runtime_geometry_enabled_count = 0
wall_velocity_enabled_count = 0
combined_runtime_geometry_wall_velocity_enabled_count = 0
real_geometry_candidate_enabled_count = 0
real_geometry_enabled_count = 0
link_area_enabled_count = 0
grid_48_enabled_count = 0
grid_64_enabled_count = 0
write_vtk_count = 0
write_particles_count = 0
```

Step86 keeps runtime geometry, wall velocity, combined runtime geometry plus
wall velocity, real geometry candidates, link-area transfer, larger grids, VTR
output, particle NPY output, solver formula changes, tau migration, physical
validation claims, real squid validation claims, squid swimming claims, and
production-readiness claims closed.

## Required Artifacts

Driver run directory:

```text
outputs/step86_driver_runs/canonical_driver_squid_proxy_static_geometry_32_3step_smoke
```

Allowed files in that directory:

```text
diagnostics_timeseries.csv
diagnostics_timeseries.npz
driver_config.json
driver_timing.json
geo_all_fluid_32.dat
geometry_quality_report.json
```

Step86 also records activation, quality, output, Step85 regression, Step84
regression, Step31 reference, and artifact-manifest evidence under
`outputs/step86_*`.
