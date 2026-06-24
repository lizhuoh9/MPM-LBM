# Step103 Fluent-Inspired Duct-Flap Proxy Solver Comparison Smoke

Step103 adds a real solver smoke run for a procedural duct-flap proxy inspired by the public Ansys Fluent 2-way FSI tutorial metadata captured in Step102.

Allowed result claim:

```text
Fluent-inspired duct-flap proxy comparison smoke ran and produced a solver gap report.
```

This is not a Fluent validation step. It does not claim solver equivalence, physical validation, real FSI validation, or production readiness.

## Runtime Envelope

Canonical row:

```text
fluent_inspired_duct_flap_proxy_48_5step_ggui_comparison_smoke
```

Driver and runtime settings:

- canonical driver: `src.mpm_lbm.sim.drivers.fsi_driver`
- `n_grid = 48`
- `n_particles = 1024`
- `n_lbm_steps = 5`
- `mpm_substeps_per_lbm_step = 1`
- `coupling_mode = moving_boundary`
- `reaction_transfer_mode = engineering`
- `geometry_type = duct_flap_proxy`
- `target_u_lbm = [0.02, 0.0, 0.0]`
- `geometry_motion_application_mode = diagnostic_only`
- `wall_velocity_application_mode = solid_vel_experimental`
- `target_lbm_field = solid_vel`
- GGUI screenshot enabled
- video, VTK, and particle-array export disabled

## Geometry Boundary

`duct_flap_proxy` is procedural. It does not import a Fluent mesh and does not use official Fluent files as runtime inputs.

The duct is recorded as normalized context:

- `x = [0.0, 1.0]`
- `y = [0.3, 0.7]`
- `z = [0.45, 0.55]`

The solid proxy sampled by MPM is the flap:

- `anchor_x = 0.505`
- `anchor_y = 0.3`
- `normalized_height = 0.10`
- `normalized_thickness = 0.03`
- `z = [0.45, 0.55]`
- `height_over_duct_height = 0.25`
- `thickness_over_duct_height = 0.075`

The material reference records the public tutorial values only as reference metadata:

- density `1600`
- Young's modulus `1e6`
- Poisson ratio `0.47`
- `used_for_exact_structural_model = false`

## Comparison Boundary

The optional local Fluent monitor CSV is:

```text
benchmarks/private/fluent_fsi_2way/reference/fluent_structural_point_flap_displacement.csv
```

It is private and optional. If missing, Step103 still emits a committed gap report with `fluent_reference_available = false`.

The report must preserve these limitations:

- official case dimensionality is 2D; current solver dimensionality is 3D
- official case uses a conformal fluid-solid mesh; current geometry is procedural proxy sampling
- official structural model is intrinsic FSI with linear elasticity; current solver does not reproduce that model
- official case has dynamic mesh deformation; current runtime geometry mutation is diagnostic-only/no-op
- official monitor quantity is displacement; current solver does not expose a physically equivalent flap-tip displacement
- official inlet velocity is dimensional 10 m/s; current LBM velocity is nondimensional/mapped

## Artifacts

Primary artifacts:

- `outputs/step103_smoke_matrix/fluent_inspired_duct_flap_proxy_smoke_matrix.json`
- `outputs/step103_fluent_comparison/fluent_solver_gap_report.json`
- `outputs/step103_fluent_comparison/fluent_solver_gap_report.csv`
- `outputs/step103_fluent_comparison/fluent_solver_gap_report.md`
- `outputs/step103_driver_runs/fluent_inspired_duct_flap_proxy_48_5step_ggui_comparison_smoke/`
- `outputs/step103_ggui_visualization/step103_duct_flap_proxy_ggui_visualization.png`

Guard artifacts:

- `outputs/step103_activation_guard/activation_guard.json`
- `outputs/step103_output_guard/output_guard.json`
- `outputs/step103_step102_regression_guard/step102_regression_guard.json`
- `outputs/step103_step100_regression_guard/step100_regression_guard.json`
- `outputs/step103_artifact_manifest/artifact_summary.json`

## Verification

The Step103 baseline runners generate and check the artifacts:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_fluent_inspired_duct_flap_proxy_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_fluent_solver_gap_comparison.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_activation_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_step102_regression_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_step100_regression_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_artifact_manifest.py
```

Full verification also runs focused Step103 pytest, full pytest under the Taichi environment, full pytest under the Anaconda environment, and Git safety checks before push.
