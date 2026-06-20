# Step 31 Controlled Squid Proxy Region Projection And Static Driver Smoke Goal

## 1. Name

Step 31 Controlled Squid Proxy Region Projection And Static Driver Smoke

Short scope statement:

Step 31 carries the Step 30 static squid proxy region semantics into region-aware projection diagnostics and short static `FSIDriver3D` smoke. Step 31 does not implement mantle contraction, funnel actuation, squid swimming, new FSI physics, or production validation.

## 2. Starting Point

Step 30 is accepted on GitHub. It provides a static squid-like proxy region contract with seven required regions:

- `mantle_outer`
- `mantle_cavity_proxy`
- `funnel_outlet_proxy`
- `head_proxy`
- `arms_proxy`
- `left_fin_proxy`
- `right_fin_proxy`

Step 30 also provides deterministic region masks, region quality checks, documented overlap diagnostics, and 32^3 / 48^3 projection-only smoke. Step 30 deliberately does not run `FSIDriver3D`.

Step 31 must bridge that gap conservatively: reuse the Step 30 region schema and geometry, add 64^3 region-aware projection diagnostics, then run a short static 48^3 driver smoke matrix with existing modes only. The driver remains static: no kinematics, no mantle/funnel motion, no swimming, and no new solver physics.

## 3. Non-Negotiable Boundaries

Step 31 must not implement or claim any of the following:

- mantle contraction;
- funnel actuation;
- squid actuation;
- squid swimming;
- free-body motion;
- jet model;
- internal fluid cavity model;
- real squid simulation validation;
- anatomical squid validation;
- production sharp-interface FSI readiness;
- final solver readiness;
- new FSI physics;
- new coupling formula;
- changes to moving bounce-back formula;
- changes to `PenaltyFSICoupler3D`;
- changes to `MovingBoundaryFSICoupler3D`;
- changes to `LinkAreaMovingBoundaryCoupler3D`;
- changes to LBM step formulas;
- changes to MPM constitutive formulas;
- changes to projection formulas;
- two-phase flow;
- contact-angle physics;
- sparse storage;
- production mesh repair;
- automatic remeshing;
- raw real geometry ingestion;
- scan-data commits;
- edits to `external/taichi_LBM3D`.

Step 31 is allowed to implement:

- region-aware projection scale summaries;
- short static `squid_proxy` driver configs;
- short static `FSIDriver3D` smoke runs;
- region/driver diagnostic alignment postprocessing;
- engineering vs link-area static comparison for moving-boundary rows;
- strict quality report aggregation;
- Step 30 regression guard;
- artifact manifest and small committed outputs;
- docs, report, logs, and contract tests.

## 4. Required Source File

Create:

- `src/squid_region_driver_diagnostics.py`

This file must be a postprocessing/helper module. It may load Step 30 `GeometryConfig` and `SquidProxyRegionConfig`, read Step 31 projection and driver rows, and summarize region-driver context. It must not modify `FSIDriver3D`, LBM, MPM, projection, moving-boundary, penalty, or link-area formulas.

Recommended functions:

- `load_region_driver_context(geometry_config_path, region_config_path) -> tuple`
- `summarize_region_projection_alignment(region_projection_rows, driver_rows) -> list[dict]`
- `summarize_static_driver_region_context(driver_row, projection_rows) -> dict`
- `write_region_driver_summary(rows, csv_path, json_path, summary=None) -> None`

Required alignment output fields:

- `case`
- `mode`
- `reaction_transfer_mode`
- `driver_projected_mass`
- `region_context_projected_mass_total`
- `mass_delta`
- `driver_active_cell_count`
- `region_context_active_cell_count_total`
- `active_cell_delta`
- `mantle_outer_projected_mass`
- `mantle_cavity_proxy_projected_mass`
- `funnel_outlet_proxy_projected_mass`
- `alignment_pass`
- `semantic_overlap_note`
- `scope_note`

Important semantic rule:

Region projection is semantic context, not a mass partition, unless explicitly non-overlapping. Step 30 documents intentional overlaps, so Step 31 must not require `mass_delta` to be near zero. Alignment acceptance means finite, positive, deterministic region context is available beside driver diagnostics.

## 5. Required Config Files

Reuse:

- `configs/step30_squid_proxy_geometry.json`
- `configs/step30_squid_proxy_region_config.json`

Create four static 48^3 driver configs:

- `configs/step31_squid_proxy_region_48_none.json`
- `configs/step31_squid_proxy_region_48_penalty.json`
- `configs/step31_squid_proxy_region_48_moving_boundary.json`
- `configs/step31_squid_proxy_region_48_link_area.json`

Every Step 31 driver config must explicitly include:

```json
{
  "geometry_type": "squid_proxy",
  "geometry_config_path": "configs/step30_squid_proxy_geometry.json",
  "n_grid": 48,
  "n_particles": 4096,
  "n_lbm_steps": 5,
  "mpm_substeps_per_lbm_step": 5,
  "output_interval": 1,
  "quality_check_enabled": true,
  "quality_check_strict": true,
  "write_vtk": false,
  "write_particles": false
}
```

The four effective rows must be:

- `coupling_mode = "none"`, `reaction_transfer_mode = "engineering"`
- `coupling_mode = "penalty"`, `reaction_transfer_mode = "engineering"`
- `coupling_mode = "moving_boundary"`, `reaction_transfer_mode = "engineering"`
- `coupling_mode = "moving_boundary"`, `reaction_transfer_mode = "link_area_experimental"`

The link-area row must explicitly include:

```json
{
  "link_area_policy": "inverse_length",
  "link_area_scale_min": 0.25,
  "link_area_scale_max": 2.0
}
```

## 6. Region-Aware Projection Scale Contract

Grid sizes:

- 32^3
- 48^3
- 64^3

Required regions:

- `mantle_outer`
- `mantle_cavity_proxy`
- `funnel_outlet_proxy`
- `head_proxy`
- `arms_proxy`
- `left_fin_proxy`
- `right_fin_proxy`

Expected rows:

- `3 grids * 7 regions = 21 rows`

Acceptance:

- `row_count == 21`
- `grid_size_count == 3`
- `required_region_count == 7`
- `pass_count == 21`
- every required region appears for 32^3, 48^3, and 64^3;
- `projected_mass > 0` for every row;
- `active_cell_count > 0` for every row;
- `solid_phi_min >= 0`;
- `solid_phi_max <= 1`;
- `has_nan == false`;
- `has_inf == false`;
- `projected_mass_total > 0`;
- `active_cell_count_total > 0`.

## 7. Static Driver Smoke Contract

Run only these four rows:

- `squid_proxy_region_48_none`
- `squid_proxy_region_48_penalty`
- `squid_proxy_region_48_moving_boundary`
- `squid_proxy_region_48_link_area`

Driver acceptance:

- `row_count == 4`
- `stable_count == 4`
- `quality_report_count == 4`
- `quality_pass_count == 4`
- `strict_count == 4`
- every row completes at least 5 LBM steps;
- every row completes at least 25 MPM substeps;
- `rho_min > 0.95`
- `rho_max < 1.05`
- `lbm_max_v < 0.1`
- `mpm_min_J > 0`
- `mpm_max_speed < 10`
- `projected_mass > 0`
- `active_cell_count > 0`
- no NaN;
- no Inf;
- `quality_pass == true`
- `quality_severity == "ok"`
- `quality_gate_strict == true`

Mode-specific acceptance:

- none row:
  - `cell_force_max_norm == 0`
  - `bb_link_count_max == 0`
- penalty row:
  - `cell_force_max_norm > 0`
  - `bb_link_count_max == 0`
- moving-boundary engineering row:
  - `cell_force_max_norm == 0`
  - `bb_link_count_max > 0`
  - `active_reaction_particle_count_max > 0`
- moving-boundary link-area row:
  - `cell_force_max_norm == 0`
  - `bb_link_count_max > 0`
  - `active_reaction_particle_count_max > 0`
  - `0.25 <= area_scale_final <= 2.0`

## 8. Region Driver Alignment Contract

Inputs:

- `outputs/step31_region_projection_scale/region_projection_scale.json`
- `outputs/step31_static_driver_smoke/static_driver_results.csv`

Outputs:

- `outputs/step31_region_driver_alignment/region_driver_alignment.csv`
- `outputs/step31_region_driver_alignment/region_driver_alignment.json`
- `logs/step31_region_driver_alignment.log`

Acceptance:

- `row_count == 4`
- `pass_count == 4`
- `alignment_pass == true` for every row;
- `driver_projected_mass > 0`;
- `driver_active_cell_count > 0`;
- `region_context_projected_mass_total > 0`;
- `region_context_active_cell_count_total > 0`;
- `mass_delta` finite;
- `active_cell_delta` finite;
- `semantic_overlap_note` present and says region projection is semantic context, not mass partition.

Do not require `mass_delta` to be close to zero because Step 30 region masks intentionally overlap.

## 9. Engineering Vs Link-Area Static Comparison Contract

Compare only the two moving-boundary static rows:

- engineering
- `link_area_experimental`

Outputs:

- `outputs/step31_engineering_vs_link_area_static_comparison/engineering_vs_link_area_static.csv`
- `outputs/step31_engineering_vs_link_area_static_comparison/engineering_vs_link_area_static.json`
- `logs/step31_engineering_vs_link_area_static_comparison.log`

Acceptance:

- `row_count == 1`
- `pass_count == 1`
- `comparison_pass == true`
- `abs(rho_min_delta) <= 1.0e-3`
- `abs(rho_max_delta) <= 1.0e-3`
- `abs(lbm_max_v_delta) <= 1.0e-3`
- `abs(mpm_min_J_delta) <= 1.0e-3`
- `abs(projected_mass_delta) <= 1.0e-4`
- `active_cell_count_delta` finite
- `0.25 <= link_area_area_scale_final <= 2.0`

## 10. Quality Report Aggregation Contract

Outputs:

- `outputs/step31_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step31_quality_report_aggregation/quality_report_summary.json`
- `logs/step31_quality_report_aggregation.log`

Acceptance:

- `quality_report_count == 4`
- `strict_count == 4`
- `pass_count == 4`
- `error_count == 0`
- `warning_count == 0`
- `quality_report_max_size_bytes < 100000`

## 11. Step 30 Regression Guard Contract

Inputs:

- `STEP30_CONTROLLED_SQUID_PROXY_REGION_GEOMETRY_REPORT.md`
- `outputs/step30_region_schema_validation/region_schema_validation.json`
- `outputs/step30_region_mask_sampling/region_mask_summary.json`
- `outputs/step30_region_projection_smoke/region_projection_results.json`
- `outputs/step30_artifact_manifest/artifact_summary.json`

Acceptance:

- Step 30 report exists;
- Step 30 required region count is 7;
- Step 30 region mask deterministic hashes exist and repeat;
- Step 30 region projection pass is true;
- Step 30 large-file count is 0;
- Step 30 vtr count is 0;
- Step 30 particle npy count is 0.

## 12. Required Baseline Runners

Create:

- `baseline_tests/step31_common.py`
- `baseline_tests/run_step31_region_projection_scale.py`
- `baseline_tests/run_step31_static_driver_smoke.py`
- `baseline_tests/run_step31_region_driver_alignment.py`
- `baseline_tests/run_step31_engineering_vs_link_area_static_comparison.py`
- `baseline_tests/run_step31_quality_report_aggregation.py`
- `baseline_tests/run_step31_step30_regression_guard.py`
- `baseline_tests/run_step31_artifact_manifest.py`

All runners must write small, committed artifacts under `outputs/step31_*` and logs under `logs/step31_*.log`.

## 13. Artifact Manifest Contract

Outputs:

- `outputs/step31_artifact_manifest/artifact_manifest.csv`
- `outputs/step31_artifact_manifest/artifact_summary.csv`
- `outputs/step31_artifact_manifest/artifact_summary.json`
- `logs/step31_artifact_manifest.log`

Acceptance:

- `large_file_count == 0`
- `step31_total_size_mb < 10`
- repository `total_size_mb < 185`
- `step31_vtr_count == 0`
- `step31_particle_npy_count == 0`
- `raw_candidate_large_file_count == 0`
- `scan_data_file_count == 0`
- `private_absolute_path_count == 0`

The manifest runner must exclude local `__pycache__` and `.pyc` files from committed artifact evidence.

## 14. Contract Test

Create:

- `tests/test_step31_squid_proxy_region_static_driver_contract.py`

Required tests:

- `test_step31_required_artifacts_exist`
- `test_step31_driver_configs_are_valid`
- `test_step31_region_projection_scale_is_valid`
- `test_step31_static_driver_smoke_is_valid`
- `test_step31_region_driver_alignment_is_valid`
- `test_step31_engineering_vs_link_area_static_comparison_is_valid`
- `test_step31_quality_report_aggregation_is_valid`
- `test_step31_step30_regression_guard_is_valid`
- `test_step31_default_modes_remain_unchanged`
- `test_step31_docs_scope_and_forbidden_claims_are_valid`
- `test_step31_artifact_budget_is_valid`
- `test_step31_report_acceptance_complete`
- `test_step31_no_solver_formula_changes_claimed`

Forbidden claims in docs/report/config notes:

- `real squid simulation is validated`
- `validated squid swimming`
- `squid actuation is implemented`
- `mantle contraction is implemented`
- `funnel actuation is implemented`
- `production-ready sharp-interface FSI`
- `final solver readiness`
- `production mesh repair is complete`
- `automatic remeshing is implemented`
- `strict momentum-conserving FSI is complete`
- `implements two_phase`
- `implements contact_angle`

Required scope phrases:

- `Step 31 is controlled squid proxy region projection and static driver smoke.`
- `Step 31 uses static squid proxy region semantics only.`
- `Step 31 is not real squid validation.`
- `Step 31 does not implement squid actuation.`
- `Step 31 does not implement squid swimming.`
- `Step 31 does not implement mantle contraction.`
- `Step 31 does not implement funnel actuation.`
- `Step 31 does not implement new FSI physics.`
- `The default quality_check_enabled remains false.`
- `The default quality_check_strict remains false.`
- `The default reaction_transfer_mode remains engineering.`
- `The moving bounce-back formula is unchanged.`
- `PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.`

## 15. Required Docs And Report

Create:

- `docs/31_controlled_squid_proxy_region_static_driver.md`
- `STEP31_CONTROLLED_SQUID_PROXY_REGION_STATIC_DRIVER_REPORT.md`

Update:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/11_artifact_policy.md`
- `docs/12_geometry_ingestion.md`
- `docs/29_controlled_real_geometry_64_stability_envelope.md`
- `docs/30_controlled_squid_proxy_region_geometry.md`

Report sections:

- Goal
- Files Created And Updated
- Explicit Non-Goals
- Region Projection Scale
- Static Driver Smoke
- Region Driver Alignment
- Engineering Vs Link-Area Static Comparison
- Quality Report Aggregation
- Step 30 Regression Guard
- Artifact Manifest Summary
- Verification Commands
- GitHub Sync Information
- Acceptance Checklist
- Decision For Step 32

Decision for Step 32:

Step 32 should be `Controlled Squid Proxy Prescribed Kinematics Schedule Contract`. It should define mantle radius schedule, mantle cavity volume proxy schedule, funnel aperture proxy schedule, cycle period, phase/ramp, and kinematic repeatability only. It should not integrate kinematics into the driver yet. Driver integration should wait for Step 33.

## 16. Verification Commands

Run these commands before completion:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\squid_region_driver_diagnostics.py baseline_tests\step31_common.py baseline_tests\run_step31_region_projection_scale.py baseline_tests\run_step31_static_driver_smoke.py baseline_tests\run_step31_region_driver_alignment.py baseline_tests\run_step31_engineering_vs_link_area_static_comparison.py baseline_tests\run_step31_quality_report_aggregation.py baseline_tests\run_step31_step30_regression_guard.py baseline_tests\run_step31_artifact_manifest.py tests\test_step31_squid_proxy_region_static_driver_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_region_projection_scale.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_static_driver_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_region_driver_alignment.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_engineering_vs_link_area_static_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_step30_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step31_squid_proxy_region_static_driver_contract.py -q
pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

If plain `pytest -q` fails because of the local shell/shim environment, rerun the same command with the trusted environment and document both the exact failure and the trusted pass. Do not ignore a real test failure.

## 17. Acceptance Checklist

- [ ] region projection scale passes at 32^3
- [ ] region projection scale passes at 48^3
- [ ] region projection scale passes at 64^3
- [ ] all required Step 30 regions are present
- [ ] region projected mass is finite
- [ ] region active cell count is finite
- [ ] static driver none row passes
- [ ] static driver penalty row passes
- [ ] static driver moving_boundary engineering row passes
- [ ] static driver moving_boundary link_area row passes
- [ ] every Step 31 driver row writes geometry_quality_report.json
- [ ] every Step 31 quality gate is strict
- [ ] every Step 31 quality report passes
- [ ] quality warning count == 0
- [ ] quality error count == 0
- [ ] all driver rows have completed_lbm_steps >= 5
- [ ] all driver rows have total_mpm_substeps >= 25
- [ ] rho_min > 0.95
- [ ] rho_max < 1.05
- [ ] lbm_max_v < 0.1
- [ ] mpm_min_J > 0
- [ ] mpm_max_speed < 10
- [ ] projected_mass > 0
- [ ] active_cell_count > 0
- [ ] no NaN
- [ ] no Inf
- [ ] none row has zero cell force
- [ ] penalty row has positive cell force
- [ ] moving_boundary rows have positive bb_link_count
- [ ] moving_boundary rows have active reaction particles
- [ ] link_area row has finite bounded area_scale
- [ ] region-driver alignment passes
- [ ] semantic overlap note is present
- [ ] engineering vs link_area static comparison passes
- [ ] Step 30 regression guard passes
- [ ] default quality_check_enabled remains false
- [ ] default quality_check_strict remains false
- [ ] default reaction_transfer_mode remains engineering
- [ ] no FSI formula changes
- [ ] no moving bounce-back formula changes
- [ ] no LBM formula changes
- [ ] no MPM constitutive formula changes
- [ ] no projection formula changes
- [ ] no production mesh repair claims
- [ ] no automatic remeshing claims
- [ ] no real squid validation claims
- [ ] no squid swimming claims
- [ ] no squid actuation claims
- [ ] no mantle contraction claims
- [ ] no funnel actuation claims
- [ ] no production sharp-interface FSI claims
- [ ] no final readiness claims
- [ ] no `external/taichi_LBM3D` edits
- [ ] no committed large raw real geometry
- [ ] no committed scan data
- [ ] no private absolute paths in committed outputs
- [ ] no Step 31 `.vtr` outputs
- [ ] no Step 31 particle `.npy` outputs
- [ ] artifact `large_file_count == 0`
- [ ] Step 31 output total-size budget passes
- [ ] repo artifact summary `total_size_mb < 185`
- [ ] `logs/step31_pytest.log` exists
- [ ] full pytest passes
- [ ] Step 31 contract test passes
- [ ] `git diff --check` passes
- [ ] staged whitespace check passes
- [ ] pre-push hook passes
- [ ] Step 31 artifacts are pushed to `origin/main`

## 18. Commit And Push

Use commit message:

```text
test: add step31 squid proxy region static driver smoke
```

After local verification, commit all relevant source, configs, tests, docs, reports, logs, and small outputs. Push to `origin/main` because the user explicitly approved push after modifications. Report the final commit hash, remote branch, and verification results.
