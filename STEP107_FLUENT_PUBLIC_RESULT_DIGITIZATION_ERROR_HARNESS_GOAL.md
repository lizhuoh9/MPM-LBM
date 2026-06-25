# Step107 Fluent Public Result Digitization Error Harness Goal

## Source Commit And Scope

This goal starts from `origin/main` commit `c1d3d6dbd7adeebabde2b75c001f5de354e8bf7d`, where Step106 repaired the x-right pressure outlet flow propagation path and pushed gap-only evidence. Step107 must not change solver behavior. It builds the first public-reference comparison harness around the Ansys Fluent public tutorial webpage result plot.

Step107 answers this specific question:

> Can this repository load an approximate digitized public Fluent Figure 29.4 displacement curve, load one of our committed solver displacement time series, and emit finite error metrics with explicit uncertainty and strict no-validation/no-official-payload guards?

It does not answer whether the solver is physically correct, equivalent to Fluent, or validated against official Fluent case data.

## One-Sentence Goal

Convert the public Ansys Fluent Figure 29.4 displacement plot into a checked-in approximate reference time series with uncertainty metadata, then build a reusable error-comparison harness that compares our committed solver displacement curve against that public-plot reference while forbidding validation/equivalence claims and official Fluent payload commits.

## Public Source Boundary

Step107 may use only information publicly visible on the Ansys Fluent tutorial page:

- URL: `https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_tg/flu_tg_fsi_2way.html`
- tutorial: Modeling Two-Way Fluid-Structure Interaction Within Fluent
- public result plot: Figure 29.4, the vertex average displacement of the flap point surface
- report/monitor name: `structural-point-flap`
- report quantity: total displacement
- operation: vertex average
- structural point coordinates: `x = 0.0505 m`, `y = 0.0095 m`
- transient settings: `50` steps, `0.0005 s` time step, final time `0.025 s`
- geometry/material public fields listed in the Step107 metadata config

Do not download, commit, or require:

- `fsi_2way.zip`
- `flap.msh`
- Fluent journal files
- Fluent `.cas`, `.cas.h5`, `.dat`, or `.dat.h5` files
- official PNG/JPG/SVG images copied from the Ansys page
- private Fluent CSV exports

Step107 may commit only derived, approximate public-plot digitized numeric data plus source metadata and uncertainty fields.

## Allowed Claims

The final Step107 report may claim:

- A public Fluent tutorial plot was represented by an approximate digitized reference curve.
- The digitized curve records source metadata, digitization method, interpolation status, and uncertainty.
- The repository can compute finite displacement error metrics between our solver output and the public-plot reference.
- The comparison is a public-plot approximate comparison only.

## Forbidden Claims

The final Step107 report, docs, logs, tests, and artifact text must not claim:

- Fluent validation passed
- Fluent equivalence achieved
- official mesh/case reproduced
- official case/data/journal/mesh used
- official Fluent result file used
- exact monitor equivalence
- physical validation complete
- production readiness

## Solver Boundary

Step107 must not modify solver behavior.

Do not modify:

- `src/mpm_lbm/sim/lbm/fluid.py`
- LBM collision, streaming, tau, or boundary kernels
- MPM stress/update/integration
- moving bounce-back
- moving-boundary coupling
- reaction transfer
- driver stepping logic
- force scaling
- Step106 outlet repair behavior

The only allowed source additions are validation/reference loaders, error metric helpers, evidence builders, guards, runners, tests, docs, configs, and committed artifacts.

## Required TDD Sequence

Step107 must be implemented red-to-green:

1. Add Step107 contract tests before adding the production implementation.
2. Run the focused Step107 tests and confirm they fail because Step107 metadata/reference/error/guard artifacts are missing.
3. Implement the public-reference loader, digitized reference artifact generation, solver curve loader, error metrics, output guard, artifact manifest, docs, and reports.
4. Run the Step107 evidence generators.
5. Re-run the Step107 focused tests until they pass.
6. Run full repository verification before commit and push.

The tests must be hook-friendly. They should primarily validate committed configs, CSV/JSON/MD artifacts, and pure Python helpers. They must not require Taichi runtime execution, network access, or official image files.

## Required New Files

Goal, report, and docs:

- `STEP107_FLUENT_PUBLIC_RESULT_DIGITIZATION_ERROR_HARNESS_GOAL.md`
- `STEP107_FLUENT_PUBLIC_RESULT_DIGITIZATION_ERROR_HARNESS_REPORT.md`
- `docs/107_fluent_public_result_digitization_error_harness.md`

Configs:

- `configs/step107_public_fluent_reference_metadata.json`
- `configs/step107_digitization_policy.json`
- `configs/step107_error_metric_policy.json`
- `configs/step107_output_guard_policy.json`
- `configs/step107_artifact_manifest_policy.json`

Public derived reference data:

- `benchmarks/public/fluent_fsi_2way_digitized/figure_29_4_structural_point_flap_digitized.csv`
- `benchmarks/public/fluent_fsi_2way_digitized/figure_29_4_digitization_notes.md`

Source modules:

- `src/mpm_lbm/validation/fluent_public_reference.py`
- `src/mpm_lbm/validation/error_metrics.py`
- `src/mpm_lbm/evidence/step107_common.py`
- `src/mpm_lbm/evidence/step107_public_reference_digitization.py`
- `src/mpm_lbm/evidence/step107_error_comparison_harness.py`
- `src/mpm_lbm/evidence/step107_output_guard.py`

Optional local-image helper script:

- `tools/reference_digitization/digitize_fluent_figure_29_4.py`

Baseline runners:

- `baseline_tests/step107_common.py`
- `baseline_tests/run_step107_public_reference_digitization.py`
- `baseline_tests/run_step107_error_comparison_harness.py`
- `baseline_tests/run_step107_output_guard.py`
- `baseline_tests/run_step107_artifact_manifest.py`

Tests:

- `tests/test_step107_public_reference_digitization_contract.py`
- `tests/test_step107_error_comparison_harness_contract.py`
- `tests/test_step107_output_guard_contract.py`

Outputs:

- `outputs/step107_public_reference_digitization/public_reference_metadata.json`
- `outputs/step107_public_reference_digitization/figure_29_4_digitized_reference.csv`
- `outputs/step107_public_reference_digitization/digitization_quality_report.json`
- `outputs/step107_error_comparison/error_report.json`
- `outputs/step107_error_comparison/error_report.csv`
- `outputs/step107_error_comparison/error_report.md`
- `outputs/step107_output_guard/output_guard_report.json`
- `outputs/step107_artifact_manifest/artifact_manifest.json`

README should receive one concise Step107 bullet in the implemented-step list.

## Required Metadata Config

`configs/step107_public_fluent_reference_metadata.json` must include:

- `source_name = "Ansys Fluent Tutorial Chapter 29, Modeling Two-Way Fluid-Structure Interaction Within Fluent"`
- `source_url`
- `public_result_figure = "Figure 29.4"`
- `figure_title = "The Vertex Average Displacement of the Flap's Point Surface"`
- `monitor_name = "structural-point-flap"`
- `monitor_quantity = "total_displacement"`
- `monitor_operation = "vertex_average"`
- `monitor_x_m = 0.0505`
- `monitor_y_m = 0.0095`
- `official_steps = 50`
- `official_dt_s = 0.0005`
- `official_final_time_s = 0.025`
- `duct_length_m = 0.10`
- `duct_height_m = 0.04`
- `flap_height_m = 0.01`
- `flap_thickness_m = 0.003`
- `inlet_velocity_mps = 10.0`
- `material_density = 1600.0`
- `material_youngs_modulus = 1000000.0`
- `material_poisson_ratio = 0.47`
- `official_case_files_used = false`
- `official_png_committed = false`
- `digitized_from_public_plot = true`
- `digitization_uncertainty_m > 0`
- `validation_claim_allowed = false`
- `direct_quantitative_equivalence_allowed = false`

## Digitized Reference Requirements

The committed digitized CSV must:

- represent Figure 29.4 as an approximate public-plot reference, not an official Fluent data export
- include `51` rows aligned to `time_s = 0.0000, 0.0005, ..., 0.0250`
- include columns:
  - `time_s`
  - `fluent_public_digitized_total_displacement_m`
  - `digitization_uncertainty_m`
  - `source_figure`
  - `digitization_method`
- have non-negative finite displacement values
- cover at least `0.0` through `0.025 s`
- have positive uncertainty on every row
- record whether the 51 rows were interpolated from visual anchor points

The first Step107 reference may be a manual visual digitization from the public plot with conservative uncertainty. The report must explicitly say this is approximate and not official Fluent raw output.

## Required Public Reference APIs

`src/mpm_lbm/validation/fluent_public_reference.py` must provide pure Python helpers:

- `load_public_fluent_reference_curve(path)`
- `load_solver_displacement_curve(path, monitor_name)`
- `resample_to_common_time_grid(reference_rows, solver_rows)`
- `write_reference_csv(path, rows)`

`load_solver_displacement_curve` must support the current committed Step106 proxy file:

- `outputs/step106_fsi_outlet_repair_regression/flap_tip_displacement_timeseries.csv`
- time column: `time_s`
- displacement column: `flap_tip_total_displacement_m`
- monitor name: `free_tip_proxy_mean`
- monitor equivalence: `false`

## Required Error Metric APIs

`src/mpm_lbm/validation/error_metrics.py` must provide:

- `compute_displacement_error_metrics(reference_rows, solver_rows, policy)`
- `shape_correlation(reference_values, solver_values)`
- `finite_metric_row(metrics)`

Required metrics:

- `reference_loaded`
- `solver_curve_loaded`
- `monitor_equivalence`
- `monitor_used`
- `sample_count`
- `peak_reference_m`
- `peak_solver_m`
- `peak_abs_error_m`
- `peak_relative_error`
- `rms_abs_error_m`
- `normalized_rms_error`
- `final_reference_m`
- `final_solver_m`
- `final_abs_error_m`
- `final_relative_error`
- `time_of_peak_reference_s`
- `time_of_peak_solver_s`
- `peak_time_error_s`
- `shape_correlation`
- `sign_consistency`
- `all_metrics_finite`
- `validation_claim_allowed = false`
- `direct_quantitative_equivalence_allowed = false`

Step107 does not require the errors to be small. It requires the comparison to be computed and honestly labeled.

## Required Error Comparison Harness

`src/mpm_lbm/evidence/step107_error_comparison_harness.py` must:

1. Load the Step107 public reference CSV.
2. Load the selected solver displacement CSV.
3. Resample/interpolate the solver curve to the reference time grid.
4. Compute the error metrics.
5. Write JSON, CSV, and Markdown reports under `outputs/step107_error_comparison/`.
6. Record `monitor_equivalence = false` when using the current free-tip proxy mean curve.
7. Keep `validation_claim_allowed = false`.
8. Keep `direct_quantitative_equivalence_allowed = false`.

## Required Output Guard

Step107 output guard must check:

- `official_case_file_count = 0`
- `official_mesh_file_count = 0`
- `official_journal_file_count = 0`
- `official_case_data_h5_count = 0`
- `official_png_committed_count = 0`
- `private_fluent_csv_committed_count = 0`
- `validation_claim_count = 0`
- `direct_equivalence_claim_count = 0`
- `protected_external_edit_count = 0`
- `protected_real_geometry_candidate_edit_count = 0`
- artifact budget pass

Allowed:

- digitized CSV derived from public Figure 29.4
- reference metadata JSON
- digitization notes
- error metric outputs

## Acceptance Criteria

Step107 is complete only when:

- public reference metadata exists and passes schema checks
- digitized Figure 29.4 reference CSV exists
- digitized reference has required columns
- digitized reference has at least 51 samples aligned to `0.0` through `0.025 s`
- all digitized values and uncertainties are finite
- uncertainty is positive
- the solver displacement CSV can be loaded
- error metrics JSON/CSV/MD are emitted
- all error metrics are finite
- `sample_count >= 10`, and expected Step107 output should use `51`
- `monitor_equivalence = false` when using Step106 free-tip proxy mean
- `validation_claim_allowed = false`
- `direct_quantitative_equivalence_allowed = false`
- no official case/journal/mesh/data files are committed
- no official image file is committed
- no private Fluent CSV is committed
- focused Step107 tests pass
- full repository pytest passes
- `git diff --check` passes
- final commit is pushed to `origin/main`

## Required Verification Commands

Use the trusted Taichi environment first:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\mpm_lbm\validation\fluent_public_reference.py src\mpm_lbm\validation\error_metrics.py src\mpm_lbm\evidence\step107_common.py src\mpm_lbm\evidence\step107_public_reference_digitization.py src\mpm_lbm\evidence\step107_error_comparison_harness.py src\mpm_lbm\evidence\step107_output_guard.py baseline_tests\step107_common.py baseline_tests\run_step107_public_reference_digitization.py baseline_tests\run_step107_error_comparison_harness.py baseline_tests\run_step107_output_guard.py baseline_tests\run_step107_artifact_manifest.py tests\test_step107_public_reference_digitization_contract.py tests\test_step107_error_comparison_harness_contract.py tests\test_step107_output_guard_contract.py
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step107_public_reference_digitization_contract.py tests\test_step107_error_comparison_harness_contract.py tests\test_step107_output_guard_contract.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step107_public_reference_digitization.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step107_error_comparison_harness.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step107_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step107_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step107_public_reference_digitization_contract.py tests\test_step107_error_comparison_harness_contract.py tests\test_step107_output_guard_contract.py
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Then verify hook-equivalent and Git checks:

```powershell
& 'D:\TOOL\Anaconda\python.exe' -m pytest -q
pytest -q
git diff --check
git status --short --branch
```

If sandbox blocks the Anaconda or `pytest.exe` entrypoint, rerun with approval and report the sandbox symptom separately from test status.

## Final Report Requirements

The final Step107 report must state:

- This step uses the public Fluent tutorial result plot, not official case files.
- No official Fluent mesh/journal/case/data/image file is committed.
- The digitized curve is an approximate public-plot reference with recorded uncertainty.
- The comparison is against the public plot, not against proprietary Fluent result files.
- Validation/equivalence claims remain forbidden.
- The current comparison uses the Step106 free-tip proxy mean, not the exact Fluent structural-point monitor, so `monitor_equivalence = false`.

## Next Step Boundary

Step107 only solves comparison infrastructure. It does not tune the solver. After Step107:

- Step108 should address low-Mach dimensional velocity/time-scale mapping for the public 10 m/s problem without destabilizing LBM.
- Step109 should address steady preflow restart.
- Step110 should address structural-point proxy monitor and structural-model gap.
- Step111 should run a 50-step official-scaled candidate and emit the error report from this harness.
