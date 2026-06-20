# Step 30 Controlled Squid Proxy Region Geometry Goal

## 1. Name

Step 30 Controlled Squid Proxy Region Geometry Contract

Short scope statement:

Step 30 defines squid-like proxy region semantics for the existing procedural `squid_proxy` geometry. It does not add actuation, swimming, new FSI physics, solver formula changes, production mesh repair, or real squid validation claims.

## 2. Starting Point

Step 29 is accepted on GitHub and provides a controlled real geometry 64^3 short-window stability envelope. Step 29 proved that the accepted real-geometry candidate matrix can run stable 20-step moving-boundary windows with strict quality reports, artifact budgets, Step 28 prefix regression, and full pytest coverage.

Step 30 must not jump from that result to real squid actuation. The next safe step is a static semantic region contract for the existing procedural squid-like proxy. The region contract must answer these questions in reproducible artifacts:

- where the mantle outer proxy is;
- where the mantle cavity proxy is;
- where the funnel or siphon outlet proxy is;
- where the head proxy is;
- where the arms proxy is;
- where optional fins are;
- what body axis and body-frame origin mean;
- what reference length means;
- which region IDs are required and stable;
- how region masks, counts, volumes, bboxes, overlaps, and projection-only diagnostics are exported.

## 3. Non-Negotiable Boundaries

Step 30 must not implement or claim any of the following:

- squid actuation;
- mantle contraction;
- funnel aperture motion;
- funnel actuation;
- swimming;
- free-body motion;
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

Step 30 is allowed to implement:

- frozen squid proxy region schema dataclasses;
- JSON-backed region configuration;
- deterministic procedural region masks based on existing squid proxy parameters;
- region summary rows with counts, estimated volumes, bboxes, hashes, and notes;
- region quality checks;
- region overlap diagnostics;
- projection-only region diagnostics at 32^3 and 48^3;
- Step 29 regression guard;
- artifact manifest and small committed outputs;
- docs, report, logs, and contract tests.

## 4. Required Source Files

Create these source modules:

- `src/squid_region_config.py`
- `src/squid_proxy_regions.py`
- `src/squid_region_quality.py`
- `src/squid_region_projection.py`

The modules must be focused, deterministic, and independent from solver formula code. They may use `GeometryConfig` and `GeometrySampler3D` for existing geometry configuration and sampling conventions, but they must not modify LBM, MPM, FSI couplers, moving bounce-back, projection, or vendored external code.

## 5. Region Schema Contract

`src/squid_region_config.py` must define immutable dataclasses similar to:

```python
@dataclass(frozen=True)
class SquidRegion:
    region_id: str
    name: str
    role: str
    material: str
    parent_id: str | None = None
    active_for_actuation: bool = False
    notes: str = ""

@dataclass(frozen=True)
class SquidProxyRegionConfig:
    geometry_type: str = "squid_proxy"
    body_axis: str = "+y"
    reference_length: float = 1.0
    body_frame_origin: tuple[float, float, float] = (0.5, 0.5, 0.5)
    scope_note: str = "procedural squid-like proxy region semantics only; not anatomical validation"
    regions: tuple[SquidRegion, ...] = (...)
    allowed_overlap_pairs: tuple[tuple[str, str], ...] = (...)
```

Required stable region IDs:

- `mantle_outer`
- `mantle_cavity_proxy`
- `funnel_outlet_proxy`
- `head_proxy`
- `arms_proxy`
- `left_fin_proxy`
- `right_fin_proxy`

Allowed roles:

- `solid_region`
- `cavity_proxy`
- `outlet_proxy`
- `appendage_proxy`
- `fin_proxy`

Required semantic rules:

- `geometry_type` must be `squid_proxy`;
- `body_axis` must be one of `+x`, `-x`, `+y`, `-y`, `+z`, `-z`;
- `reference_length` must be positive and finite;
- `body_frame_origin` must be finite length-3 numeric data;
- all required region IDs must exist;
- region IDs must be unique;
- all regions must have non-empty names, roles, materials, and notes;
- all regions must keep `active_for_actuation == False`;
- `scope_note` must explicitly say this is not anatomical validation;
- allowed overlap pairs must explicitly document intentional semantic overlaps.

## 6. Region Geometry And Mask Contract

`src/squid_proxy_regions.py` must provide deterministic mask and summary utilities:

- `default_squid_proxy_region_config() -> SquidProxyRegionConfig`
- `load_squid_proxy_region_config(path) -> SquidProxyRegionConfig`
- `validate_squid_region_config(config) -> dict`
- `sample_squid_proxy_region_points(geometry_config, count, seed) -> np.ndarray`
- `sample_squid_proxy_regions(geometry_config, region_config, points) -> dict[str, np.ndarray]`
- `summarize_region_masks(points, masks, geometry_config, region_config) -> list[dict]`
- `write_region_manifest(rows, csv_path, json_path) -> None`

The masks must be deterministic and based on existing procedural squid proxy geometry parameters:

- `mantle_outer`: existing mantle ellipsoid proxy;
- `mantle_cavity_proxy`: a smaller ellipsoid inside the mantle proxy, semantics only;
- `funnel_outlet_proxy`: a small ellipsoid/capsule-like outlet proxy near the anterior/forward mantle region, semantics only;
- `head_proxy`: existing head ellipsoid proxy;
- `arms_proxy`: coarse arms proxy using the existing arms extent/radius convention;
- `left_fin_proxy`: left fin proxy region;
- `right_fin_proxy`: right fin proxy region.

The implementation must not treat `mantle_cavity_proxy` as a real internal fluid cavity and must not treat `funnel_outlet_proxy` as an actuated jet or moving aperture.

Required deterministic checks:

- sampling the same geometry with the same seed returns the same sampled-position hash;
- assigning region masks twice returns the same region-assignment hash;
- every mask is boolean and finite;
- every required region has a summary row;
- required solid/proxy regions have positive counts under the Step 30 config.

## 7. Region Quality Contract

`src/squid_region_quality.py` must check region-level QA without changing geometry:

- required regions exist;
- region IDs are unique;
- masks are boolean;
- bboxes are finite;
- `mantle_outer`, `head_proxy`, `arms_proxy`, `left_fin_proxy`, and `right_fin_proxy` have positive counts;
- `mantle_cavity_proxy` has positive count;
- `funnel_outlet_proxy` has positive count;
- `mantle_cavity_proxy` is inside or near the mantle proxy condition recorded;
- `funnel_outlet_proxy` is near the mantle boundary/outlet condition recorded;
- overlap matrix is finite;
- unintended overlap count is zero;
- all intentional overlaps are documented by `allowed_overlap_pairs`;
- no forbidden validation/actuation claims appear in scope notes or region notes.

The quality output must be explicit and artifact-backed, not a silent boolean.

## 8. Region Projection-Only Contract

`src/squid_region_projection.py` must provide projection-only diagnostics:

- `run_squid_region_projection_smoke(geometry_config, region_config, grid_sizes, out_dir) -> list[dict]`

Projection-only diagnostics must run at:

- `32^3`
- `48^3`

The projection smoke must not run the FSI driver and must not perform LBM stepping, MPM stepping, moving-boundary coupling, or link-area transfer. It may use a deterministic particle cloud and grid-index accumulation to compute region-specific projected mass and active cell counts.

Required projection row fields:

- `grid_size`
- `region_id`
- `particle_count`
- `estimated_volume`
- `projected_mass`
- `active_cell_count`
- `bbox_min_x`
- `bbox_min_y`
- `bbox_min_z`
- `bbox_max_x`
- `bbox_max_y`
- `bbox_max_z`
- `solid_phi_min`
- `solid_phi_max`
- `has_nan`
- `has_inf`
- `projection_pass`

Acceptance:

- at least `2 * required_region_count` rows;
- total projected mass is positive;
- total active cell count is positive;
- all region projected mass values are finite;
- all region active cell counts are finite;
- `solid_phi_min >= 0`;
- `solid_phi_max <= 1`;
- `has_nan == false`;
- `has_inf == false`;
- `projection_pass == true` for every row.

## 9. Required Config Files

Create:

- `configs/step30_squid_proxy_geometry.json`
- `configs/step30_squid_proxy_region_config.json`

`configs/step30_squid_proxy_geometry.json` must be a procedural squid proxy config with:

- `geometry_type == "squid_proxy"`;
- `n_particles == 4096`;
- deterministic squid-like proxy geometry parameters;
- `quality_check_enabled == true`;
- `quality_check_strict == true`;
- a scope note or metadata stating this is a procedural squid proxy and not real squid validation.

`configs/step30_squid_proxy_region_config.json` must include:

- body axis;
- reference length;
- body-frame origin;
- all required regions;
- allowed overlap pairs;
- scope note saying this is region semantics only and not anatomical validation.

## 10. Required Baseline Runners

Create:

- `baseline_tests/step30_common.py`
- `baseline_tests/run_step30_region_schema_validation.py`
- `baseline_tests/run_step30_region_mask_sampling.py`
- `baseline_tests/run_step30_region_quality.py`
- `baseline_tests/run_step30_region_overlap_diagnostics.py`
- `baseline_tests/run_step30_region_projection_smoke.py`
- `baseline_tests/run_step30_step29_regression_guard.py`
- `baseline_tests/run_step30_artifact_manifest.py`

All runners must write small, committed artifacts under `outputs/step30_*` and logs under `logs/step30_*.log`.

### 10.1 Schema Validation Runner

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_schema_validation.py
```

Outputs:

- `outputs/step30_region_schema_validation/region_schema_validation.csv`
- `outputs/step30_region_schema_validation/region_schema_validation.json`
- `logs/step30_region_schema_validation.log`

Acceptance:

- `required_region_count >= 7`;
- all required region IDs exist;
- region IDs unique;
- body axis valid;
- reference length positive;
- body-frame origin finite;
- scope note contains not anatomical validation;
- `schema_pass == true`.

### 10.2 Region Mask Sampling Runner

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_mask_sampling.py
```

Outputs:

- `outputs/step30_region_mask_sampling/region_mask_summary.csv`
- `outputs/step30_region_mask_sampling/region_mask_summary.json`
- `logs/step30_region_mask_sampling.log`

Acceptance:

- row count is at least 7;
- `mantle_outer_count > 0`;
- `mantle_cavity_proxy_count > 0`;
- `funnel_outlet_proxy_count > 0`;
- `head_proxy_count > 0`;
- `arms_proxy_count > 0`;
- fin counts are finite and positive for this config;
- all masks boolean;
- all counts deterministic across two runs;
- sampled-position hash repeatable;
- region-assignment hash repeatable.

### 10.3 Region Quality Runner

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_quality.py
```

Outputs:

- `outputs/step30_region_quality/region_quality.csv`
- `outputs/step30_region_quality/region_quality.json`
- `logs/step30_region_quality.log`

Acceptance:

- `region_quality_pass == true`;
- no required region missing;
- no region has nonfinite bbox;
- solid region counts are positive;
- cavity proxy count is positive;
- funnel outlet count is positive;
- mantle cavity inside/near mantle condition is recorded;
- funnel outlet near-boundary condition is recorded;
- no forbidden claims.

### 10.4 Region Overlap Diagnostics Runner

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_overlap_diagnostics.py
```

Outputs:

- `outputs/step30_region_overlap_diagnostics/region_overlap_matrix.csv`
- `outputs/step30_region_overlap_diagnostics/region_overlap_summary.json`
- `logs/step30_region_overlap_diagnostics.log`

Acceptance:

- matrix finite;
- diagonal counts match region counts;
- intentional overlaps documented;
- `unintended_overlap_count == 0`;
- overlap diagnostics pass.

### 10.5 Region Projection Smoke Runner

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_projection_smoke.py
```

Outputs:

- `outputs/step30_region_projection_smoke/region_projection_results.csv`
- `outputs/step30_region_projection_smoke/region_projection_results.json`
- `logs/step30_region_projection_smoke.log`

Acceptance:

- rows exist for 32^3 and 48^3;
- rows exist for all required regions;
- projected mass total is positive;
- active-cell total is positive;
- all region projected mass values are finite;
- all region active-cell counts are finite;
- no NaN;
- no Inf;
- projection-only smoke passes.

### 10.6 Step 29 Regression Guard

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_step29_regression_guard.py
```

Outputs:

- `outputs/step30_step29_regression_guard/step29_regression_guard.csv`
- `outputs/step30_step29_regression_guard/step29_regression_guard.json`
- `logs/step30_step29_regression_guard.log`

Acceptance:

- Step 29 report exists;
- Step 29 driver row count is 4;
- Step 29 stable count is 4;
- Step 29 quality report count is 4;
- Step 29 artifact large-file count is 0;
- Step 29 raw candidate large-file count is 0;
- Step 29 scan-data file count is 0;
- Step 29 regression guard passes.

### 10.7 Artifact Manifest

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_artifact_manifest.py
```

Outputs:

- `outputs/step30_artifact_manifest/artifact_manifest.csv`
- `outputs/step30_artifact_manifest/artifact_summary.csv`
- `outputs/step30_artifact_manifest/artifact_summary.json`
- `logs/step30_artifact_manifest.log`

Acceptance:

- `large_file_count == 0`;
- `step30_total_size_mb < 5`;
- repository `total_size_mb < 180`;
- `step30_vtr_count == 0`;
- `step30_particle_npy_count == 0`;
- `raw_candidate_large_file_count == 0`;
- `scan_data_file_count == 0`;
- `private_absolute_path_count == 0`.

## 11. Contract Test

Create:

- `tests/test_step30_squid_proxy_region_geometry_contract.py`

Required tests:

- `test_step30_required_artifacts_exist`
- `test_step30_region_config_schema_is_valid`
- `test_step30_region_mask_sampling_is_deterministic`
- `test_step30_region_quality_is_valid`
- `test_step30_region_overlap_diagnostics_are_valid`
- `test_step30_region_projection_smoke_is_valid`
- `test_step30_step29_regression_guard_is_valid`
- `test_step30_default_modes_remain_unchanged`
- `test_step30_docs_scope_and_forbidden_claims_are_valid`
- `test_step30_artifact_budget_is_valid`
- `test_step30_report_acceptance_complete`
- `test_step30_no_solver_formula_changes_claimed`

The test may include additional focused assertions if needed.

Forbidden claims in docs/report/config notes:

- `real squid simulation is validated`
- `validated squid swimming`
- `squid actuation is implemented`
- `production-ready sharp-interface FSI`
- `final solver readiness`
- `production mesh repair is complete`
- `automatic remeshing is implemented`
- `strict momentum-conserving FSI is complete`
- `mantle contraction is implemented`
- `funnel actuation is implemented`
- `implements two_phase`
- `implements contact_angle`

Required scope phrases in the report and docs:

- `Step 30 is controlled squid proxy region geometry.`
- `Step 30 defines squid-like region semantics only.`
- `Step 30 is not real squid validation.`
- `Step 30 does not implement squid actuation.`
- `Step 30 does not implement squid swimming.`
- `Step 30 does not implement mantle contraction.`
- `Step 30 does not implement funnel actuation.`
- `Step 30 does not implement new FSI physics.`
- `The default quality_check_enabled remains false.`
- `The default quality_check_strict remains false.`
- `The default reaction_transfer_mode remains engineering.`
- `The moving bounce-back formula is unchanged.`
- `PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.`

## 12. Required Docs And Report

Create:

- `docs/30_controlled_squid_proxy_region_geometry.md`
- `STEP30_CONTROLLED_SQUID_PROXY_REGION_GEOMETRY_REPORT.md`

Update existing docs where appropriate:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/11_artifact_policy.md`
- `docs/12_geometry_ingestion.md`
- any directly relevant prior Step docs that maintain a step chain.

Report sections:

- Goal
- Files Created And Updated
- Explicit Non-Goals
- Region Schema Validation
- Region Mask Sampling
- Region Quality
- Region Overlap Diagnostics
- Region Projection Smoke
- Step 29 Regression Guard
- Artifact Manifest Summary
- Verification Commands
- GitHub Sync Information
- Acceptance Checklist
- Decision For Step 31

Decision for Step 31:

Step 31 should be `Controlled Squid Proxy Region Projection And Static Driver Smoke`. It may add a 48^3 static moving-boundary driver smoke with region-aware diagnostics, but it still must not add actuation. Mantle/funnel prescribed kinematics should be left for a later step.

## 13. Verification Commands

Run these commands before completion:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\squid_region_config.py src\squid_proxy_regions.py src\squid_region_quality.py src\squid_region_projection.py baseline_tests\step30_common.py baseline_tests\run_step30_region_schema_validation.py baseline_tests\run_step30_region_mask_sampling.py baseline_tests\run_step30_region_quality.py baseline_tests\run_step30_region_overlap_diagnostics.py baseline_tests\run_step30_region_projection_smoke.py baseline_tests\run_step30_step29_regression_guard.py baseline_tests\run_step30_artifact_manifest.py tests\test_step30_squid_proxy_region_geometry_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_schema_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_mask_sampling.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_overlap_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_projection_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_step29_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step30_squid_proxy_region_geometry_contract.py -q
pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

If plain `pytest -q` fails because of the local shell/shim environment, rerun the same logical check with the trusted Taichi interpreter and document the exact failure plus the trusted-interpreter pass. Do not ignore a real test failure.

## 14. Acceptance Checklist

- [ ] region schema validation passes
- [ ] required squid proxy regions exist
- [ ] region IDs are unique
- [ ] body axis is defined
- [ ] reference length is positive
- [ ] body-frame origin is finite
- [ ] mantle_outer region exists
- [ ] mantle_cavity_proxy region exists
- [ ] funnel_outlet_proxy region exists
- [ ] head_proxy region exists
- [ ] arms_proxy region exists
- [ ] fin proxy regions exist or are explicitly disabled
- [ ] region mask sampling is deterministic
- [ ] region-assignment hash is repeatable
- [ ] sampled-position hash is repeatable
- [ ] every required region has finite diagnostics
- [ ] solid regions have positive count
- [ ] cavity proxy has positive count
- [ ] funnel outlet proxy has positive count
- [ ] region overlap diagnostics pass
- [ ] intentional overlaps are documented
- [ ] projection-only smoke passes at 32^3
- [ ] projection-only smoke passes at 48^3
- [ ] region projected mass is finite
- [ ] region active cell count is finite
- [ ] no NaN
- [ ] no Inf
- [ ] Step 29 regression guard passes
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
- [ ] no Step 30 `.vtr` outputs
- [ ] no Step 30 particle `.npy` outputs
- [ ] artifact `large_file_count == 0`
- [ ] Step 30 output total-size budget passes
- [ ] repo artifact summary `total_size_mb < 180`
- [ ] `logs/step30_pytest.log` exists
- [ ] full pytest passes
- [ ] Step 30 contract test passes
- [ ] `git diff --check` passes
- [ ] staged whitespace check passes
- [ ] pre-push hook passes
- [ ] Step 30 artifacts are pushed to `origin/main`

## 15. Commit And Push

Use commit message:

```text
test: add step30 controlled squid proxy region geometry
```

After local verification, commit all relevant source, configs, tests, docs, reports, logs, and small outputs. Push to `origin/main` because the user explicitly approved push after modifications. Report the final commit hash, remote branch, and verification results.
