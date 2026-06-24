# Step94 Taichi GGUI Visualization Smoke Report

Step94 accepted.

Step94 runs exactly one required GGUI visualization smoke row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke
```

The row uses:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 1
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
ggui_visualization_enabled = true
write_vtk = false
write_particles = false
```

Step94 calls the canonical `src.mpm_lbm.sim.drivers.fsi_driver.FSIDriver3D`
and then renders one Taichi GGUI frame through the independent Step94 evidence
renderer. The driver completed one LBM step with two diagnostics rows in
66.49477119999938 seconds. The GGUI renderer created a Taichi window, scene,
and camera, rendered 1024 deterministic procedural squid-proxy visualization
points, drew the domain box and wall-velocity proxy segments, and wrote exactly
one PNG screenshot:

```text
outputs/step94_ggui_visualization/step94_ggui_visual_smoke.png
```

The screenshot size is 132386 bytes. The render report passes, video is
disabled, and no video file was written.

The GGUI renderer visualizes procedural `squid_proxy` visualization proxy
points, not exported physical particle trajectories.

## Acceptance Evidence

```text
step94_taichi_ggui_visualization_smoke_matrix_pass = true
step94_taichi_ggui_visualization_quality_pass = true
step94_activation_guard_pass = true
output_guard_pass = true
step94_step93_regression_guard_pass = true
step94_step92_regression_guard_pass = true
step94_step90_regression_guard_pass = true
artifact_budget_pass = true
```

Numerical smoke bounds:

```text
rho_min_min = 0.9996863007545471
rho_max_max = 1.0000003576278687
lbm_max_v_max = 0.0003139966866001487
mpm_min_J_min = 0.9999617338180542
mpm_max_speed_max = 0.0017955973744392395
completed_lbm_steps = 1
diagnostics_row_count = 2
activation_feature_count = 4
```

Output guard:

```text
step94_required_driver_run_dir_count = 1
step94_optional_driver_run_dir_count = 0
step94_ggui_screenshot_count = 1
step94_ggui_video_count = 0
step94_vtr_count = 0
step94_particle_npy_count = 0
step94_raw_geometry_output_count = 0
step94_real_geometry_candidate_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
```

Artifact budget:

```text
step94_file_count = 81
step94_total_size_mb = 0.4794197082519531
large_file_count = 0
```

## Boundaries

Step94 does not write VTR.
Step94 does not write particle NPY.
Step94 does not write video.
Step94 does not enable real geometry candidate data.
Step94 does not enable link-area transfer.
Step94 does not enable 48^3 or 64^3.
Step94 does not mutate geometry.
Step94 does not change solver formulas.
Step94 does not claim physical validation, squid swimming, real squid
validation, or production readiness.

Correct claim:

```text
Taichi GGUI visualization path can render the first-user envelope in a minimal 32^3 / 1-step smoke.
```
