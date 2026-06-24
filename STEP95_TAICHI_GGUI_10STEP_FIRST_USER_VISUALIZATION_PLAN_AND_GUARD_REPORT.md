# Step95 Taichi GGUI 10-Step First User Visualization Plan And Guard Report

Step95 accepted.

Step95 is plan-and-guard only. It does not run `FSIDriver3D`, does not call
`driver.run()`, does not execute simulation, does not open a GGUI window, does
not write screenshots, does not write video, does not write VTR, and does not
write particle NPY.

Step95 plans exactly one future Step96 row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run
```

The planned Step96 row is:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
ggui_visualization_enabled = true
ggui_screenshot_enabled = true
ggui_video_enabled = false
write_vtk = false
write_particles = false
output_interval = 1
```

Step96 combines the Step92 10-step first-user dry-run envelope with the Step94
Taichi GGUI screenshot path. From Step94, the only planned expansion is duration
from one LBM step to ten LBM steps. From Step92, the only planned new dimension
is Taichi GGUI visualization.

## Acceptance Evidence

```text
step95_taichi_ggui_10step_visualization_plan_pass = true
step95_taichi_ggui_10step_visualization_guard_pass = true
step95_step94_regression_guard_pass = true
step95_step93_regression_guard_pass = true
step95_step92_regression_guard_pass = true
output_guard_pass = true
artifact_budget_pass = true
```

Step95 activation count:

```text
step95_activation_feature_count = 0
planned_step96_activation_feature_count = 4
```

Output guard:

```text
step95_driver_run_dir_count = 0
step95_ggui_screenshot_count = 0
step95_ggui_video_count = 0
step95_vtr_count = 0
step95_particle_npy_count = 0
step95_raw_geometry_output_count = 0
step95_real_geometry_candidate_output_count = 0
step95_dense_wall_velocity_output_count = 0
step95_sparse_wall_velocity_output_count = 0
step95_dense_displacement_output_count = 0
step95_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
```

Artifact budget:

```text
step95_file_count <= 70
step95_total_size_mb < 5
large_file_count = 0
```

## Boundaries

Step95 does not enable VTR.
Step95 does not enable particle NPY.
Step95 does not enable video.
Step95 does not enable real geometry candidates.
Step95 does not enable link-area transfer.
Step95 does not enable 48^3 or 64^3.
Step95 does not change solver formulas.
Step95 does not migrate tau semantics.
Step95 does not claim physical validation, real squid validation, squid
swimming, squid actuation, production visualization readiness, or production
simulation readiness.

The correct Step95 claim is:

```text
Taichi GGUI 10-step first-user visualization run is planned and guarded for Step96.
```
