# Step154 Goal: Official Solver Pre/Post Pipeline

## Source Contract

Step154 follows remote `origin/main` after Step153 commit:

```text
aa4a6cfe9480074cb643ca28add5bffb9127a9fa
```

Step153 completed the official tutorial setup-parity run and produced:

```text
outputs/step153_official_tutorial_setup_parity/
```

Step153 key state:

```json
{
  "status": "official_tutorial_setup_parity_run_complete",
  "solver_monitor_rows": 11,
  "solver_time_end_s": 0.025,
  "official_tutorial_time_steps": 50,
  "official_tutorial_dt_s": 0.0005,
  "official_tutorial_total_time_s": 0.025,
  "official_structural_material_applied": true,
  "official_monitor_loaded": false,
  "validation_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

Step153 is useful but incomplete. It proves the repository can run the current
`FSIDriver3D` path over the official tutorial time window, and it records public
official setup constants. However, it still does not provide a canonical solver
case file, canonical masks, or canonical postprocessing contract. Step154 must
add that missing pre/post pipeline layer.

## Objective

Implement:

```text
Step154 Official Solver Pre/Post Pipeline
```

Step154 must create a canonical, machine-readable compiled case for the public
Ansys Chapter 29 duct/flap tutorial setup and must create the preprocessing and
postprocessing surfaces that Step155 and Step156 will consume.

This step must not be another blocked validation gate. It must implement real
preprocessing artifacts and postprocessing specifications.

Step154 does not run the FSI solver. Step154 prepares the canonical case and
verifies that downstream solver and postprocessing stages have unambiguous
inputs.

## Non-Goals

Step154 must not:

```text
- run Fluent
- import private Fluent mesh files
- fabricate official monitor data
- run Step150 error localization
- run Step151 targeted fix
- run Step152 apply gate
- run Step148 solver helper as the primary operation
- run FSIDriver3D
- claim Fluent validation
- claim Figure 29.3 parity
- claim official mesh reproduction
- claim selected96 readiness
```

Step154 is a preprocessor/postprocessor contract step only.

## Required New Files

Create:

```text
docs/campaigns/fluent_duct_flap/steps/154/goal.md
docs/campaigns/fluent_duct_flap/steps/154/report.md
experiments/steps/step154_official_solver_prepost_pipeline.py
src/mpm_lbm/cases/fluent_duct_flap/__init__.py
src/mpm_lbm/cases/fluent_duct_flap/case_schema.py
src/mpm_lbm/cases/fluent_duct_flap/preprocess.py
src/mpm_lbm/cases/fluent_duct_flap/postprocess.py
tests/test_step154_official_solver_prepost_pipeline_contract.py
```

Create committed artifacts under:

```text
outputs/step154_official_solver_prepost_pipeline/
```

## Required Inputs

Step154 must read these Step153 artifacts:

```text
outputs/step153_official_tutorial_setup_parity/official_tutorial_setup_report.json
outputs/step153_official_tutorial_setup_parity/solver_reproduction_summary.json
outputs/step153_official_tutorial_setup_parity/boundary_semantics_gap_report.json
outputs/step153_official_tutorial_setup_parity/material_mapping_report.json
outputs/step153_official_tutorial_setup_parity/geometry_mapping_report.json
outputs/step153_official_tutorial_setup_parity/official_reference_gap_report.json
```

If optional Step153 files are missing, Step154 may still run only if the
required public tutorial constants can be recovered from
`official_tutorial_setup_report.json` and `solver_reproduction_summary.json`.

Step154 must fail fast if the official tutorial constants are absent or
inconsistent.

## Required Runner

Add executable module:

```text
experiments/steps/step154_official_solver_prepost_pipeline.py
```

Default command:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step154_official_solver_prepost_pipeline `
  --step153-root outputs\step153_official_tutorial_setup_parity `
  --output-dir outputs\step154_official_solver_prepost_pipeline `
  --grid 48 `
  --force
```

Required CLI arguments:

```text
--step153-root
--output-dir
--grid
--force
```

Optional CLI arguments:

```text
--z-cells
--write-preview
--no-preview
```

Default behavior:

```text
--grid 48
--z-cells 48
--write-preview true
```

The runner must be deterministic. Re-running with `--force` must fully refresh
the Step154 output directory.

## Official Tutorial Constants

Step154 must encode and propagate the public tutorial constants already
recorded by Step153:

```json
{
  "duct_length_m": 0.10,
  "duct_height_m": 0.04,
  "flap_height_m": 0.01,
  "flap_thickness_m": 0.003,
  "half_domain_mode": true,
  "inlet_air_velocity_mps": 10.0,
  "outlet_type": "pressure_outlet",
  "monitor_point_m": [0.0505, 0.0095],
  "monitor_quantity": "Structure / Total Displacement",
  "official_tutorial_time_steps": 50,
  "official_tutorial_dt_s": 0.0005,
  "official_tutorial_total_time_s": 0.025,
  "max_iterations_per_time_step": 40
}
```

Official structural material:

```json
{
  "material_name": "silicone-rubber",
  "solid_density_kg_m3": 1600.0,
  "youngs_modulus_pa": 1000000.0,
  "poisson_ratio": 0.47
}
```

These constants must appear in:

```text
compiled_case.json
preprocess_report.json
material_model_mapping.json
dimensionless_mapping.json
```

## Current Solver Geometry Mapping

The official tutorial is a 2D half-domain setup. The repository solver remains
a 3D proxy solver. Step154 must make this mapping explicit.

Use the current repository proxy convention:

```json
{
  "solver_domain_normalized": {
    "x": [0.0, 1.0],
    "y": [0.0, 1.0],
    "z": [0.0, 1.0]
  },
  "duct_normalized": {
    "x": [0.0, 1.0],
    "y": [0.3, 0.7],
    "z": [0.45, 0.55]
  },
  "flap_normalized": {
    "anchor_x": 0.505,
    "anchor_y": 0.3,
    "height": 0.10,
    "thickness": 0.03,
    "z": [0.45, 0.55],
    "mirrored_pair": false
  }
}
```

The physical-to-normalized mapping must be:

```text
x_norm = x_m / duct_length_m
y_norm = duct_y_min_norm + (y_m / duct_height_m) * (duct_y_max_norm - duct_y_min_norm)
z_norm = 0.5
```

For the official monitor point:

```text
monitor_point_m = [0.0505, 0.0095]
x_norm = 0.0505 / 0.10 = 0.505
y_norm = 0.3 + (0.0095 / 0.04) * 0.4 = 0.395
```

Step154 must record:

```json
{
  "monitor_point_normalized": [0.505, 0.395, 0.5]
}
```

The nearest grid monitor index must be computed deterministically from cell
centers:

```text
coord_center(i, n) = (i + 0.5) / n
nearest index = round(norm * n - 0.5), clamped to [0, n - 1]
```

Step154 must write both the normalized point and the chosen integer index.

## Required Case Schema

Implement schema helpers in:

```text
src/mpm_lbm/cases/fluent_duct_flap/case_schema.py
```

Use plain dataclasses or typed dictionaries. The schema must be
JSON-serializable without custom runtime dependencies.

Minimum schema objects:

```text
OfficialTutorialSetup
OfficialMaterial
SolverGrid
SolverGeometryMapping
BoundaryConditionSpec
FSIInterfaceSpec
MonitorSpec
DimensionlessMapping
CompiledOfficialDuctFlapCase
PostprocessSpec
```

The compiled case JSON must include at least:

```json
{
  "step": 154,
  "case_name": "official_tutorial_duct_flap_proxy_case",
  "case_version": 1,
  "source_step": 153,
  "source_step153_root": "outputs/step153_official_tutorial_setup_parity",
  "official_tutorial_setup": {},
  "official_material": {},
  "solver_grid": {
    "nx": 48,
    "ny": 48,
    "nz": 48
  },
  "solver_geometry_mapping": {},
  "boundary_condition_spec": {},
  "fsi_interface_spec": {},
  "monitor_spec": {},
  "dimensionless_mapping": {},
  "mask_artifacts": {},
  "postprocess_spec_path": "outputs/step154_official_solver_prepost_pipeline/postprocess_spec.json",
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "official_mesh_imported": false,
  "official_fluent_files_used_as_runtime_input": false
}
```

## Dimensionless Mapping Requirement

Step154 must write:

```text
outputs/step154_official_solver_prepost_pipeline/dimensionless_mapping.json
```

It must include:

```json
{
  "duct_length_m": 0.10,
  "duct_height_m": 0.04,
  "solver_nx": 48,
  "solver_ny": 48,
  "solver_nz": 48,
  "dx_m_if_x_length_controls": 0.10 / 48,
  "dy_m_if_duct_height_controls": 0.04 / duct_height_cells,
  "inlet_velocity_mps": 10.0,
  "official_dt_s": 0.0005,
  "official_total_time_s": 0.025,
  "official_time_steps": 50,
  "mapping_scope": "preprocessor_case_metadata_only",
  "direct_physical_reynolds_validation_allowed": false,
  "physical_reynolds_parity_claim_allowed": false,
  "tau_margin_validation_required_before_physical_re_claim": true
}
```

`duct_height_cells` must be computed from the generated fluid mask. It is the
count of y cells whose centers lie inside the normalized duct interval
`[0.3, 0.7]`.

Step154 must not pretend that LBM physical-Re parity is solved.

## Preprocessing Requirements

Implement in:

```text
src/mpm_lbm/cases/fluent_duct_flap/preprocess.py
```

Required function names:

```python
load_step153_setup(step153_root: Path) -> dict
compile_official_duct_flap_case(step153_root: Path, output_dir: Path, grid: int, z_cells: int | None = None) -> dict
build_geometry_masks(case: dict) -> dict[str, np.ndarray]
build_boundary_masks(case: dict, geometry_masks: dict[str, np.ndarray]) -> dict[str, np.ndarray]
build_fsi_interface_masks(case: dict, geometry_masks: dict[str, np.ndarray]) -> dict[str, np.ndarray]
write_preprocess_artifacts(case: dict, masks: dict, output_dir: Path) -> dict
```

The exact implementation may use dataclasses internally, but it must write JSON
and NPZ outputs that tests can inspect.

### Geometry Masks

Write:

```text
geometry_masks.npz
```

Required arrays:

```text
fluid_mask
solid_mask
duct_context_mask
duct_wall_mask
flap_solid_mask
flap_fixed_base_mask
flap_free_region_mask
monitor_cell_mask
```

Shape:

```text
(nx, ny, nz)
```

Dtypes:

```text
bool
```

Rules:

```text
- duct_context_mask is true for cells inside the normalized duct volume.
- flap_solid_mask is true for cells inside the normalized flap volume.
- fluid_mask is true inside duct_context_mask and false inside flap_solid_mask.
- solid_mask is the inverse of fluid_mask.
- duct_wall_mask is true for solid cells adjacent to duct fluid or outside the duct domain.
- flap_fixed_base_mask is true for the base portion of the flap attached to the wall.
- flap_free_region_mask is true for the rest of the flap.
- monitor_cell_mask contains exactly one true cell.
```

For the current single half-domain proxy flap:

```text
flap anchor side = lower wall
fixed base is the part closest to y = duct_y_min
free region is the rest of the flap
fixed_base_band_norm = max(flap_thickness_norm, 0.2 * flap_height_norm)
```

### Boundary Masks

Write:

```text
boundary_masks.npz
```

Required arrays:

```text
velocity_inlet_mask
pressure_outlet_mask
no_slip_wall_mask
symmetry_or_periodic_z_min_mask
symmetry_or_periodic_z_max_mask
flap_wall_mask
fsi_wall_mask
```

Rules:

```text
- velocity_inlet_mask is the fluid cross-section at x = 0.
- pressure_outlet_mask is the fluid cross-section at x = nx - 1.
- no_slip_wall_mask marks duct wall cells adjacent to fluid.
- flap_wall_mask marks flap solid cells adjacent to fluid.
- fsi_wall_mask marks the fluid-side interface cells adjacent to flap_solid_mask.
- symmetry_or_periodic_z_min_mask and symmetry_or_periodic_z_max_mask must be written even if the current solver treats z as proxy/periodic.
```

`velocity_inlet_mask`, `pressure_outlet_mask`, and `fsi_wall_mask` must be
nonempty.

### FSI Interface Masks

Write:

```text
fsi_interface_masks.npz
```

Required arrays:

```text
fluid_interface_mask
solid_interface_mask
flap_fixed_interface_mask
flap_free_interface_mask
```

Rules:

```text
- solid_interface_mask is flap_solid_mask adjacent to fluid.
- fluid_interface_mask is fluid_mask adjacent to flap_solid_mask.
- flap_fixed_interface_mask is the interface touching fixed-base cells.
- flap_free_interface_mask is the interface touching free-region cells.
```

Adjacency must use 6-neighbor connectivity as the baseline:

```text
±x, ±y, ±z
```

The implementation may also record optional 18/26-neighbor counts, but the
baseline masks must use 6-neighbor adjacency.

## Postprocessing Requirements

Implement in:

```text
src/mpm_lbm/cases/fluent_duct_flap/postprocess.py
```

Required function names:

```python
build_postprocess_spec(compiled_case: dict, output_dir: Path) -> dict
write_geometry_preview(compiled_case: dict, masks: dict, output_path: Path) -> dict
```

Write:

```text
postprocess_spec.json
geometry_preview.png
```

`postprocess_spec.json` must include expected Step156 products:

```json
{
  "velocity_magnitude_plot": "velocity_magnitude_step050.png",
  "velocity_ux_plot": "velocity_ux_step050.png",
  "velocity_uy_plot": "velocity_uy_step050.png",
  "streamline_or_quiver_plot": "streamline_or_quiver_step050.png",
  "geometry_overlay_plot": "geometry_overlay_step050.png",
  "centerline_velocity_profile": "centerline_velocity_profile.csv",
  "x_plane_flux_profile": "x_plane_flux_profile.csv",
  "monitor_displacement_plot": "monitor_displacement_plot.png",
  "force_monitor_plot": "force_monitor_plot.png",
  "postprocess_summary": "postprocess_summary.json",
  "solver_acceptance_report": "solver_acceptance_report.json",
  "official_comparison_report": "official_comparison_report.json"
}
```

`geometry_preview.png` must show at least:

```text
- duct fluid region
- flap solid region
- monitor point
- inlet/outlet markers
```

Use matplotlib only. Do not use seaborn. Do not require a GUI backend.

## Required Output Artifacts

Step154 must write:

```text
outputs/step154_official_solver_prepost_pipeline/
  compiled_case.json
  geometry_masks.npz
  boundary_masks.npz
  fsi_interface_masks.npz
  dimensionless_mapping.json
  material_model_mapping.json
  preprocess_report.json
  postprocess_spec.json
  geometry_preview.png
  step154_summary.json
  report.md
```

## Required `compiled_case.json` Fields

`compiled_case.json` must include:

```json
{
  "step": 154,
  "status": "compiled_case_ready_for_step155",
  "case_name": "official_tutorial_duct_flap_proxy_case",
  "case_version": 1,
  "source_step153_root": "outputs/step153_official_tutorial_setup_parity",
  "source_step153_status": "official_tutorial_setup_parity_run_complete",
  "official_tutorial_setup": {
    "duct_length_m": 0.1,
    "duct_height_m": 0.04,
    "flap_height_m": 0.01,
    "flap_thickness_m": 0.003,
    "half_domain_mode": true,
    "inlet_air_velocity_mps": 10.0,
    "outlet_type": "pressure_outlet",
    "monitor_point_m": [0.0505, 0.0095],
    "monitor_quantity": "Structure / Total Displacement",
    "official_tutorial_time_steps": 50,
    "official_tutorial_dt_s": 0.0005,
    "official_tutorial_total_time_s": 0.025,
    "max_iterations_per_time_step": 40
  },
  "official_material": {
    "material_name": "silicone-rubber",
    "solid_density_kg_m3": 1600.0,
    "youngs_modulus_pa": 1000000.0,
    "poisson_ratio": 0.47
  },
  "solver_grid": {
    "nx": 48,
    "ny": 48,
    "nz": 48
  },
  "boundary_condition_spec": {
    "inlet": "velocity_inlet",
    "inlet_velocity_mps": 10.0,
    "outlet": "pressure_outlet",
    "wall": "no_slip",
    "flap_wall": "fsi_moving_wall",
    "z_boundary_proxy": "periodic_or_symmetry_proxy_reported"
  },
  "lbm_boundary_semantics_required_for_step155": {
    "legacy_all_population_reset_allowed": false,
    "minimum_open_boundary_semantics": "regularized_velocity_pressure_limited"
  },
  "monitor_spec": {
    "monitor_point_m": [0.0505, 0.0095],
    "monitor_point_normalized": [0.505, 0.395, 0.5],
    "monitor_index": [0, 0, 0],
    "monitor_quantity": "Structure / Total Displacement",
    "nearest_cell_policy": "nearest_cell_center"
  },
  "mask_artifacts": {
    "geometry_masks": "outputs/step154_official_solver_prepost_pipeline/geometry_masks.npz",
    "boundary_masks": "outputs/step154_official_solver_prepost_pipeline/boundary_masks.npz",
    "fsi_interface_masks": "outputs/step154_official_solver_prepost_pipeline/fsi_interface_masks.npz"
  },
  "postprocess_spec_path": "outputs/step154_official_solver_prepost_pipeline/postprocess_spec.json",
  "official_mesh_imported": false,
  "official_fluent_files_used_as_runtime_input": false,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

The example `monitor_index` above must be replaced by the actual computed
index.

## Required Reports

`preprocess_report.json` must include:

```json
{
  "step": 154,
  "status": "preprocess_complete",
  "preprocessor_ready": true,
  "official_tutorial_constants_loaded": true,
  "solver_input_case_written": true,
  "geometry_masks_written": true,
  "boundary_masks_written": true,
  "fsi_interface_masks_written": true,
  "monitor_point_mapped": true,
  "grid": {
    "nx": 48,
    "ny": 48,
    "nz": 48
  },
  "mask_counts": {
    "fluid_cell_count": 0,
    "solid_cell_count": 0,
    "flap_solid_cell_count": 0,
    "velocity_inlet_cell_count": 0,
    "pressure_outlet_cell_count": 0,
    "fsi_wall_cell_count": 0,
    "monitor_cell_count": 1
  },
  "geometry_equivalence_claim_allowed": false,
  "validation_claim_allowed": false
}
```

Counts must be real counts from generated masks.

`material_model_mapping.json` must include:

```json
{
  "step": 154,
  "status": "material_mapping_compiled",
  "official_material": {
    "material_name": "silicone-rubber",
    "solid_density_kg_m3": 1600.0,
    "youngs_modulus_pa": 1000000.0,
    "poisson_ratio": 0.47
  },
  "current_solver_structural_model": "finite_deformation_mpm",
  "official_structural_model": "Fluent intrinsic FSI / FEM-like structural model",
  "material_constants_available_to_step155": true,
  "fluent_structural_model_equivalence_claim_allowed": false,
  "validation_claim_allowed": false
}
```

`step154_summary.json` must include:

```json
{
  "step": 154,
  "status": "official_solver_prepost_pipeline_ready",
  "compiled_case_ready_for_step155": true,
  "preprocessor_ready": true,
  "postprocessor_ready": true,
  "official_tutorial_constants_loaded": true,
  "solver_input_case_written": true,
  "geometry_masks_written": true,
  "boundary_masks_written": true,
  "fsi_interface_masks_written": true,
  "monitor_point_mapped": true,
  "geometry_preview_written": true,
  "step155_solver_run_allowed": true,
  "solver_run_executed": false,
  "fluent_run_executed": false,
  "step150_executed": false,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

## Documentation Updates

Update:

```text
docs/current/STATUS.md
docs/current/ACTIVE_CAMPAIGN.json
docs/current/READING_ORDER.md
docs/current/VALIDATION_GATES.md
README.md
docs/campaigns/fluent_duct_flap/steps/154/report.md
```

The documentation must state:

```text
Step154 created the canonical official tutorial solver case and pre/post pipeline artifacts.
Step154 did not run the solver.
Step154 did not run Fluent.
Step154 did not load official monitor data.
Step154 did not run Step150.
Step154 does not make a validation claim.
Step155 is the next implementation step and must consume Step154 compiled_case.json directly.
```

## Test Requirements

Add:

```text
tests/test_step154_official_solver_prepost_pipeline_contract.py
```

Tests must cover at least:

1. Runner artifact contract: run the Step154 runner in a temporary output
   directory using the committed Step153 artifact directory and assert existence
   of `compiled_case.json`, `geometry_masks.npz`, `boundary_masks.npz`,
   `fsi_interface_masks.npz`, `dimensionless_mapping.json`,
   `material_model_mapping.json`, `preprocess_report.json`,
   `postprocess_spec.json`, `geometry_preview.png`, `step154_summary.json`, and
   `report.md`.
2. Compiled case constants: assert official time steps, dt, total time, duct
   and flap dimensions, inlet velocity, outlet type, and
   `validation_claim_allowed = false`.
3. Mask integrity: assert all required arrays exist, have shape `(48, 48, 48)`,
   required masks are nonempty, and `monitor_cell_mask` has exactly one true
   value.
4. Boundary semantics: assert velocity inlet, pressure outlet, no legacy
   all-population reset, and minimum Step155 open-boundary semantics
   `regularized_velocity_pressure_limited`.
5. Monitor mapping: assert monitor physical point, normalized point approximately
   `[0.505, 0.395, 0.5]`, in-bounds monitor index, and exactly one monitor
   cell.
6. Postprocess spec: assert all Step156 expected output names are present.
7. No solver execution: assert `solver_run_executed = false`,
   `fluent_run_executed = false`, and `step150_executed = false`.

## Required Verification Commands

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step154_official_solver_prepost_pipeline `
  --step153-root outputs\step153_official_tutorial_setup_parity `
  --output-dir outputs\step154_official_solver_prepost_pipeline `
  --grid 48 `
  --force
```

Run focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step154_official_solver_prepost_pipeline_contract.py
```

Run compile check:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step154_official_solver_prepost_pipeline.py `
  src\mpm_lbm\cases\fluent_duct_flap\case_schema.py `
  src\mpm_lbm\cases\fluent_duct_flap\preprocess.py `
  src\mpm_lbm\cases\fluent_duct_flap\postprocess.py
```

Run adjacent regression slice using the real filenames in this checkout:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step148_our_solver_fluent_official_case_reproduction_contract.py `
  tests\test_step150_official_monitor_intake_and_error_localization_contract.py `
  tests\test_step151_targeted_solver_fix_from_official_error_contract.py `
  tests\test_step152_apply_targeted_solver_fix_contract.py `
  tests\test_step153_official_tutorial_setup_parity_contract.py `
  tests\test_step154_official_solver_prepost_pipeline_contract.py
```

Run JSON parse check over:

```text
compiled_case.json
dimensionless_mapping.json
material_model_mapping.json
preprocess_report.json
postprocess_spec.json
step154_summary.json
```

Run diff hygiene:

```powershell
git diff --check
```

## Acceptance Criteria

Step154 is accepted only if:

```json
{
  "step": 154,
  "status": "official_solver_prepost_pipeline_ready",
  "compiled_case_ready_for_step155": true,
  "preprocessor_ready": true,
  "postprocessor_ready": true,
  "official_tutorial_constants_loaded": true,
  "solver_input_case_written": true,
  "geometry_masks_written": true,
  "boundary_masks_written": true,
  "fsi_interface_masks_written": true,
  "monitor_point_mapped": true,
  "geometry_preview_written": true,
  "step155_solver_run_allowed": true,
  "solver_run_executed": false,
  "fluent_run_executed": false,
  "step150_executed": false,
  "validation_claim_allowed": false,
  "figure_29_3_parity_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

## Required Report Language

`docs/campaigns/fluent_duct_flap/steps/154/report.md` must say:

```text
Step154 implemented the canonical official tutorial solver pre/post pipeline.

It consumed Step153 setup-parity artifacts and generated a compiled case,
geometry masks, boundary masks, FSI interface masks, material mapping,
dimensionless mapping, postprocess specification, and geometry preview.

Step154 did not run the FSI solver. Step154 did not run Fluent. Step154 did
not use or fabricate official monitor data. Step154 did not run Step150 and
does not make a validation claim.

Step155 must consume:
outputs/step154_official_solver_prepost_pipeline/compiled_case.json

Step155 must not fall back to Step148 helper-driven implicit setup. The Step155
solver runner must directly consume the compiled case and run the 50-step,
0.0005 s official tutorial window.
```

## Next Step After Step154

After Step154 passes, Step155 must implement:

```text
Official Tutorial Solver V1
```

Step155 must consume:

```text
outputs/step154_official_solver_prepost_pipeline/compiled_case.json
```

and must run the solver directly for:

```text
50 steps
dt = 0.0005 s
total time = 0.025 s
```

Step155 must write solver monitors, force monitors, stability monitors, flux
profiles, and velocity snapshots.

Step155 must not rely on Step148 as the primary runner.
