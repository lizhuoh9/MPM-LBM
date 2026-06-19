# Step 25 Goal: Controlled Real Geometry Intake Contract

This file is the authoritative execution contract for Step 25 in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Step 25 starts only when a `/goal` message explicitly references this file.

## 1. Status Before Step 25

Step 24 is accepted on GitHub at commit:

```text
ccf0c63381ee4c1dc6ee3b7c046bf9d9ed0dc5d1
```

Step 24 established:

- strict quality-gated synthetic imported geometry long-run validation;
- `quality_check_enabled = true` and `quality_check_strict = true` for selected synthetic imported geometry rows;
- 9 strict driver rows, all stable;
- quality report aggregation with 9 pass, 0 warnings, 0 errors;
- Step 23 prefix comparison with 7 comparable rows, 2 Step 24-only rows explicitly marked as missing Step 23 overlap, and deltas near `1e-6`;
- strict vs non-strict report comparison with 9/9 reports matched;
- artifact manifest with `large_file_count == 0`;
- Step 24 output size under budget;
- `pytest -q`: 184 passed;
- pre-push hook `pytest -q`: 184 passed;
- `external/taichi_LBM3D` unchanged.

Step 24 explicitly did not validate real squid geometry and did not change:

- `PenaltyFSICoupler3D`;
- `MovingBoundaryFSICoupler3D`;
- `LinkAreaMovingBoundaryCoupler3D`;
- moving bounce-back formulas;
- LBM step formulas;
- MPM constitutive formulas;
- projection formulas;
- default `reaction_transfer_mode = "engineering"`;
- default `quality_check_enabled = false`;
- default `quality_check_strict = false`.

Step 25 must preserve all of the above.

## 2. Step 25 Objective

Build a controlled intake contract for real geometry candidate files.

The correct description is:

```text
Step 25 controlled real geometry intake contract:
geometry QA, normalization, fingerprinting, and sampling reproducibility only.
```

Step 25 moves the project from:

```text
small synthetic imported geometry fixtures only
```

to:

```text
controlled candidate geometry intake with manifest, fingerprint, QA, normalization report, deterministic sampling reproducibility, and projection-only smoke diagnostics
```

Step 25 must prove that:

1. Candidate geometry descriptors can be validated deterministically.
2. Candidate source files can be fingerprinted without leaking absolute local paths into committed artifacts.
3. Mesh and voxel candidates can be loaded through an explicit intake policy.
4. Mesh and voxel candidates can be QA'd through existing geometry diagnostics and strict quality gates.
5. Candidate geometry can be normalized to the simulation domain with a recorded report.
6. Normalization is reporting or copy-generation only; it is not mesh repair, automatic remeshing, or source mutation.
7. Candidate particle sampling is deterministic and reproducible.
8. Projection-only diagnostics can run without entering FSI driver validation.
9. Raw large real geometry files and scan data are not committed.
10. Artifact budgets remain controlled.
11. Defaults remain unchanged: `quality_check_enabled = false`, `quality_check_strict = false`, and `reaction_transfer_mode = "engineering"`.
12. Solver, coupler, LBM, MPM, moving-boundary, and projection formulas remain unchanged.

Step 25 is not real squid validation. It is an intake, QA, normalization, reproducibility, and projection-only smoke step.

## 3. Hard Boundaries

Do not implement:

- real squid simulation validation;
- squid swimming;
- squid actuation;
- production sharp-interface FSI;
- production solver readiness claims;
- new FSI physics;
- new coupling formulas;
- changes to `PenaltyFSICoupler3D`;
- changes to `MovingBoundaryFSICoupler3D`;
- changes to `LinkAreaMovingBoundaryCoupler3D`;
- changes to the moving bounce-back formula;
- changes to LBM step formulas;
- changes to MPM constitutive formulas;
- changes to projection formulas;
- production mesh repair;
- automatic remeshing;
- mesh cleanup or mesh fixing;
- scan-data processing pipeline;
- two-phase flow;
- contact angle physics;
- sparse storage;
- `ReducedSquidFSI`;
- edits to `external/taichi_LBM3D`;
- committing large raw real mesh or voxel artifacts;
- committing scan data;
- committing private absolute local geometry paths.

Allowed work:

- candidate descriptor schema and validation;
- geometry file fingerprinting;
- candidate manifest generation;
- real-candidate intake policy documentation;
- small controlled smoke candidates;
- `.gitignore` policy for local candidate geometry;
- mesh and voxel QA orchestration;
- normalization reports;
- optional small normalized copy outputs only when under budget and explicitly marked as non-repair;
- deterministic sampling reproducibility checks;
- projection-only smoke diagnostics;
- Step 24 regression guard over existing artifacts;
- docs, reports, tests, logs, and small reproducibility outputs;
- minimal helper code in new intake modules and baseline scripts.

Any change that touches core solver formulas is out of scope and must be rejected.

## 4. Required Source And Artifact Files

Create:

```text
STEP25_CONTROLLED_REAL_GEOMETRY_INTAKE_GOAL.md
STEP25_CONTROLLED_REAL_GEOMETRY_INTAKE_REPORT.md

src/geometry_fingerprint.py
src/geometry_candidate_manifest.py
src/geometry_normalization.py
src/geometry_intake.py

configs/step25_candidate_smoke_mesh_descriptor.json
configs/step25_candidate_smoke_voxel_descriptor.json
configs/step25_intake_policy.json

data/real_geometry_candidates/README.md
data/real_geometry_candidates/.gitkeep

baseline_tests/step25_common.py
baseline_tests/run_step25_candidate_manifest.py
baseline_tests/run_step25_real_geometry_intake_smoke.py
baseline_tests/run_step25_mesh_candidate_quality.py
baseline_tests/run_step25_voxel_candidate_quality.py
baseline_tests/run_step25_normalization_reports.py
baseline_tests/run_step25_sampling_reproducibility.py
baseline_tests/run_step25_projection_smoke.py
baseline_tests/run_step25_step24_regression_guard.py
baseline_tests/run_step25_artifact_manifest.py

docs/24_controlled_real_geometry_intake.md
docs/25_real_geometry_candidate_policy.md

tests/test_step25_controlled_real_geometry_intake_contract.py
```

Update:

```text
.gitignore
README.md
docs/08_roadmap.md
docs/09_api_reference.md
docs/11_artifact_policy.md
docs/12_geometry_ingestion.md
docs/19_geometry_import_pipeline.md
docs/21_geometry_quality_checks.md
docs/22_quality_gated_imported_geometry_validation.md
docs/23_strict_quality_gated_imported_geometry_long_run.md
```

Do not edit:

```text
external/taichi_LBM3D
```

## 5. Candidate Data Policy

Step 25 must define a controlled local candidate directory:

```text
data/real_geometry_candidates/
```

The directory is for local candidate geometry intake only.

Required policy:

- do not commit large raw real geometry files;
- do not commit scan data;
- do not commit private anatomy, proprietary CAD, or private absolute paths;
- descriptors may be committed when they use repo-relative smoke fixtures or redacted local paths;
- small smoke fixtures may be committed only when they are clearly synthetic or controlled intake fixtures;
- a passing intake report is not real squid validation;
- a passing intake report is not swimming validation;
- a passing intake report is not production mesh repair;
- a passing intake report is not production sharp-interface FSI.

Update `.gitignore` to exclude raw local candidates by default:

```text
data/real_geometry_candidates/*
!data/real_geometry_candidates/README.md
!data/real_geometry_candidates/.gitkeep
!data/real_geometry_candidates/*_descriptor.json
```

If the implementation needs committed smoke source files, place them under an already committed small-fixture directory such as:

```text
data/geometry_fixtures/
```

and name them as controlled intake smoke fixtures, not anatomical squid assets.

## 6. Candidate Descriptor Contract

Create JSON descriptors:

```text
configs/step25_candidate_smoke_mesh_descriptor.json
configs/step25_candidate_smoke_voxel_descriptor.json
```

Required descriptor fields:

```json
{
  "candidate_id": "real_candidate_smoke_mesh",
  "geometry_type": "mesh",
  "source_file": "data/geometry_fixtures/step25_real_candidate_smoke_mesh.obj",
  "source_policy": "controlled_intake_smoke_not_anatomical_validation",
  "license_status": "small_committed_smoke_fixture",
  "commit_policy": "small_controlled_fixture_allowed",
  "normalize_to_domain": true,
  "preserve_aspect_ratio": true,
  "padding": 0.08,
  "n_particles": 4096,
  "quality_check_enabled": true,
  "quality_check_strict": true,
  "artifact_policy": "no_vtk_no_particles_no_large_raw_geometry",
  "validation_scope": "intake_qa_normalization_sampling_projection_only"
}
```

`candidate_id` rules:

- non-empty string;
- lowercase snake case;
- unique across Step 25 descriptors;
- must not imply validated anatomy or swimming;
- must not contain private source names unless user explicitly authorizes them.

`geometry_type` rules:

- must be `mesh` or `voxel`;
- no new geometry type is required for Step 25.

`source_file` rules:

- repo-relative for committed smoke fixtures;
- redacted or descriptor-local for local-only real candidates;
- no absolute Windows user path in committed output artifacts;
- must not point under `external/taichi_LBM3D`.

`commit_policy` allowed values:

```text
small_controlled_fixture_allowed
do_not_commit_large_raw_geometry
local_candidate_only
```

`validation_scope` must be:

```text
intake_qa_normalization_sampling_projection_only
```

## 7. `src/geometry_fingerprint.py` Contract

Implement:

```python
def sha256_file(path) -> str:
    ...

def file_size_bytes(path) -> int:
    ...

def fingerprint_geometry_file(path, *, root=None, redact_absolute=True, large_threshold_bytes=1_000_000) -> dict:
    ...
```

Required output fields:

```text
path
filename
extension
size_bytes
sha256
is_large
path_policy
mtime_policy_note
```

Requirements:

- SHA-256 must be deterministic and computed from file bytes.
- `size_bytes` must be exact.
- `is_large` must be true when `size_bytes >= large_threshold_bytes`.
- Do not include private absolute local paths in committed summaries when `redact_absolute=True`.
- Use repo-relative paths for files under the repo root.
- Raise a clear error for missing files or directories.

## 8. `src/geometry_candidate_manifest.py` Contract

Implement:

```python
def load_candidate_descriptor(path) -> dict:
    ...

def validate_candidate_descriptor(payload, *, descriptor_path=None) -> dict:
    ...

def candidate_manifest_row(descriptor_path, *, root=None) -> dict:
    ...

def write_candidate_manifest(rows, csv_path, json_path):
    ...
```

Required manifest row fields:

```text
candidate_id
geometry_type
descriptor_path
source_file
source_file_redacted
source_policy
license_status
commit_policy
validation_scope
n_particles
normalize_to_domain
preserve_aspect_ratio
padding
quality_check_enabled
quality_check_strict
size_bytes
sha256
is_large
manifest_pass
notes
```

Manifest validation must reject:

- duplicate `candidate_id`;
- unknown geometry type;
- missing source file unless descriptor is explicitly local-only and marked unavailable;
- `quality_check_enabled != true`;
- `quality_check_strict != true`;
- `n_particles <= 0`;
- `padding < 0`;
- `padding >= 0.5`;
- committed large raw geometry;
- source paths under `external/taichi_LBM3D`;
- validation scope other than intake-only.

## 9. `src/geometry_normalization.py` Contract

Implement:

```python
def normalize_mesh_candidate(descriptor) -> dict:
    ...

def normalize_voxel_candidate(descriptor) -> dict:
    ...

def write_normalization_report(report, path):
    ...
```

Required report fields:

```text
candidate_id
geometry_type
source_file_fingerprint
source_bounds_min
source_bounds_max
normalized_bounds_min
normalized_bounds_max
domain_min
domain_max
padding
preserve_aspect_ratio
scale_factor
translation
normalized_inside_domain
normalization_changed_coordinates
source_file_modified
repair_performed
remeshing_performed
notes
```

Requirements:

- `normalized_inside_domain == true`;
- `source_file_modified == false`;
- `repair_performed == false`;
- `remeshing_performed == false`;
- scale and translation values must be finite;
- mesh normalization must reuse existing normalization behavior where possible;
- voxel normalization may report bounds and occupancy-domain mapping without rewriting the source;
- normalization report must not claim mesh repair.

## 10. `src/geometry_intake.py` Contract

Implement:

```python
def run_candidate_intake(descriptor_path, out_dir) -> dict:
    ...

def run_candidate_quality_check(descriptor_path, out_dir) -> dict:
    ...

def run_candidate_sampling_reproducibility(descriptor_path, out_dir) -> dict:
    ...

def run_candidate_projection_smoke(descriptor_path, out_dir) -> dict:
    ...
```

The orchestrator must stay intake-focused:

- descriptor validation;
- fingerprint generation;
- quality report generation;
- normalization report generation;
- deterministic sampling reproducibility;
- projection-only smoke diagnostics.

It must not run the FSI driver as validation.

If an implementation reuses `FSIDriverConfig` or `GeometryConfig`, it must only do so for geometry loading, sampling, and projection-only checks. Do not write a Step 25 long-run FSI matrix.

## 11. Baseline Runner Contracts

### 11.1 `run_step25_candidate_manifest.py`

Generate:

```text
outputs/step25_candidate_manifest/candidate_manifest.csv
outputs/step25_candidate_manifest/candidate_manifest.json
logs/step25_candidate_manifest.log
```

Checks:

- descriptors exist;
- candidate IDs are unique;
- geometry types are valid;
- source file policy is valid;
- SHA-256 is recorded;
- raw geometry commit policy is obeyed;
- large raw candidate files are not committed.

Log success marker:

```text
[OK] Step 25 candidate manifest finished
```

### 11.2 `run_step25_real_geometry_intake_smoke.py`

Run complete smoke intake:

```text
descriptor -> fingerprint -> load -> QA -> normalization report -> manifest row
```

Generate:

```text
outputs/step25_real_geometry_intake_smoke/intake_smoke_summary.csv
outputs/step25_real_geometry_intake_smoke/intake_smoke_summary.json
logs/step25_real_geometry_intake_smoke.log
```

Checks:

- at least one mesh smoke candidate passes;
- at least one voxel smoke candidate passes;
- no raw large candidate is committed;
- no solver validation is claimed.

Log success marker:

```text
[OK] Step 25 real geometry intake smoke finished
```

### 11.3 `run_step25_mesh_candidate_quality.py`

Generate:

```text
outputs/step25_mesh_candidate_quality/mesh_candidate_quality.csv
outputs/step25_mesh_candidate_quality/mesh_candidate_quality.json
outputs/step25_mesh_candidate_quality/<candidate_id>/geometry_quality_report.json
logs/step25_mesh_candidate_quality.log
```

Checks:

- `vertices_count > 0`;
- `faces_count > 0`;
- `has_valid_face_indices == true`;
- finite vertices;
- clean smoke candidate has `degenerate_face_count == 0`;
- clean smoke candidate has `boundary_edge_count == 0`;
- clean smoke candidate has `nonmanifold_edge_count == 0`;
- `quality_pass == true`;
- `quality_severity == "ok"`.

Log success marker:

```text
[OK] Step 25 mesh candidate quality finished
```

### 11.4 `run_step25_voxel_candidate_quality.py`

Generate:

```text
outputs/step25_voxel_candidate_quality/voxel_candidate_quality.csv
outputs/step25_voxel_candidate_quality/voxel_candidate_quality.json
outputs/step25_voxel_candidate_quality/<candidate_id>/geometry_quality_report.json
logs/step25_voxel_candidate_quality.log
```

Checks:

- `occupied_count > 0`;
- `connected_component_count >= 1`;
- `largest_component_fraction` finite;
- `quality_pass == true` for clean smoke candidate;
- `quality_severity == "ok"` for clean smoke candidate;
- domain-boundary contact is recorded if present.

Log success marker:

```text
[OK] Step 25 voxel candidate quality finished
```

### 11.5 `run_step25_normalization_reports.py`

Generate:

```text
outputs/step25_normalization_reports/normalization_summary.csv
outputs/step25_normalization_reports/normalization_summary.json
outputs/step25_normalization_reports/<candidate_id>/normalization_report.json
logs/step25_normalization_reports.log
```

Checks:

- normalized bounds are inside `[0, 1]^3`;
- padding is respected;
- preserve-aspect-ratio behavior is recorded;
- scale factor is finite;
- translation is finite;
- `repair_performed == false`;
- `remeshing_performed == false`;
- `source_file_modified == false`.

Log success marker:

```text
[OK] Step 25 normalization reports finished
```

### 11.6 `run_step25_sampling_reproducibility.py`

Run deterministic sampling twice for each committed smoke candidate.

Generate:

```text
outputs/step25_sampling_reproducibility/sampling_reproducibility.csv
outputs/step25_sampling_reproducibility/sampling_reproducibility.json
logs/step25_sampling_reproducibility.log
```

Checks:

- same particle count;
- same geometry volume;
- same particle mass sum;
- same sampled position hash;
- same `vol0` hash;
- same mass hash;
- finite relative mass error;
- reproducibility pass for every candidate.

Log success marker:

```text
[OK] Step 25 sampling reproducibility finished
```

### 11.7 `run_step25_projection_smoke.py`

Run projection-only diagnostics.

Generate:

```text
outputs/step25_projection_smoke/projection_smoke_results.csv
outputs/step25_projection_smoke/projection_smoke_results.json
logs/step25_projection_smoke.log
```

Checks:

- `projected_mass > 0`;
- `active_cell_count > 0`;
- `solid_phi_min >= 0`;
- `solid_phi_max <= 1`;
- no NaN;
- no Inf;
- no FSI driver long-run claim;
- no real squid validation claim.

Log success marker:

```text
[OK] Step 25 projection smoke finished
```

### 11.8 `run_step25_step24_regression_guard.py`

Do not rerun Step 24 heavy long-run.

Generate:

```text
outputs/step25_step24_regression_guard/step24_regression_guard.csv
outputs/step25_step24_regression_guard/step24_regression_guard.json
logs/step25_step24_regression_guard.log
```

Checks:

- Step 24 report exists;
- Step 24 quality report aggregation exists;
- Step 24 `quality_report_count == 9`;
- Step 24 `large_file_count == 0`;
- Step 24 pytest log exists;
- Step 24 docs still avoid real validation claims.

Log success marker:

```text
[OK] Step 25 Step 24 regression guard finished
```

### 11.9 `run_step25_artifact_manifest.py`

Generate:

```text
outputs/step25_artifact_manifest/artifact_manifest.csv
outputs/step25_artifact_manifest/artifact_summary.json
logs/step25_artifact_manifest.log
```

Checks:

- `large_file_count == 0`;
- Step 25 output total size under 10 MB;
- repo artifact summary `total_size_mb < 160`;
- no committed raw candidate file over 1 MB;
- no committed scan data;
- no Step 25 `.vtr` files;
- no Step 25 particle `.npy` outputs;
- candidate descriptors and policy docs are included.

Log success marker:

```text
[OK] Step 25 artifact manifest finished
```

## 12. Contract Test Requirements

Create:

```text
tests/test_step25_controlled_real_geometry_intake_contract.py
```

Required tests:

```text
test_step25_required_artifacts_exist
test_step25_candidate_descriptors_are_valid
test_step25_real_geometry_candidate_policy_is_documented
test_step25_candidate_manifest_is_valid
test_step25_mesh_quality_report_is_valid
test_step25_voxel_quality_report_is_valid
test_step25_normalization_report_is_valid
test_step25_sampling_reproducibility_is_valid
test_step25_projection_smoke_is_valid
test_step25_step24_regression_guard_is_valid
test_step25_no_solver_or_coupler_formula_changes_claimed
test_step25_artifact_budget_is_valid
test_step25_report_acceptance_complete
```

The contract test must verify:

- every required Step 25 source file exists;
- every required Step 25 baseline script exists;
- every required Step 25 descriptor exists;
- every required Step 25 output exists after baselines run;
- descriptors use intake-only validation scope;
- descriptors enable strict quality checks;
- candidate IDs are unique;
- source files are allowed by policy;
- manifest includes SHA-256 and size;
- manifest does not leak absolute local paths;
- mesh quality report passes for the clean smoke candidate;
- voxel quality report passes for the clean smoke candidate;
- normalization reports are finite and domain-bounded;
- normalization does not perform repair;
- sampling reproducibility hashes match;
- projection smoke has positive mass and active cells;
- Step 24 regression guard passes;
- defaults remain disabled in `src/geometry_config.py` and `src/fsi_config.py`;
- docs and report include required scope language;
- docs and report do not include forbidden claims;
- artifact manifest passes budget;
- `logs/step25_pytest.log` exists;
- all expected Step 25 logs contain success markers;
- `external/taichi_LBM3D` is unchanged.

## 13. Required Scope Language

The exact phrases below must appear across docs and report:

```text
Step 25 is controlled real geometry intake, not real squid validation.
Step 25 performs geometry QA, normalization, fingerprinting, sampling reproducibility, and projection-only smoke diagnostics.
Step 25 does not implement squid swimming.
Step 25 does not implement squid actuation.
Step 25 does not implement new FSI physics.
Step 25 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Candidate intake does not perform production mesh repair or automatic remeshing.
Raw large real geometry files and scan data are not committed.
```

Forbidden claims:

```text
real squid simulation is validated
validated squid swimming
production mesh repair is complete
automatic remeshing is implemented
production-ready mesh import
production-ready sharp-interface FSI
strict momentum-conserving FSI is complete
implements two_phase
implements contact_angle
validated squid actuation
final solver readiness
```

## 14. Required Report

Create:

```text
STEP25_CONTROLLED_REAL_GEOMETRY_INTAKE_REPORT.md
```

Required sections:

```text
## 1. Goal
## 2. Files Created And Updated
## 3. Explicit Non-Goals
## 4. Candidate Manifest
## 5. Intake Smoke
## 6. Mesh Candidate Quality
## 7. Voxel Candidate Quality
## 8. Normalization Reports
## 9. Sampling Reproducibility
## 10. Projection Smoke
## 11. Step 24 Regression Guard
## 12. Artifact Manifest Summary
## 13. Verification Commands
## 14. GitHub Sync Information
## 15. Acceptance Checklist
## 16. Decision For Step 26
```

The report must include:

- exact commands;
- exact artifact paths;
- exact row counts;
- exact summary values;
- artifact budget numbers;
- final commit hash after push;
- target remote branch.

## 15. Verification Command Order

Run in this order:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\geometry_intake.py src\geometry_fingerprint.py src\geometry_normalization.py src\geometry_candidate_manifest.py baseline_tests\step25_common.py baseline_tests\run_step25_candidate_manifest.py baseline_tests\run_step25_real_geometry_intake_smoke.py baseline_tests\run_step25_mesh_candidate_quality.py baseline_tests\run_step25_voxel_candidate_quality.py baseline_tests\run_step25_normalization_reports.py baseline_tests\run_step25_sampling_reproducibility.py baseline_tests\run_step25_projection_smoke.py baseline_tests\run_step25_step24_regression_guard.py baseline_tests\run_step25_artifact_manifest.py tests\test_step25_controlled_real_geometry_intake_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_candidate_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_real_geometry_intake_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_mesh_candidate_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_voxel_candidate_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_normalization_reports.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_sampling_reproducibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_projection_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_step24_regression_guard.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step25_controlled_real_geometry_intake_contract.py -q

git diff --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Also write full pytest output to:

```text
logs/step25_pytest.log
```

If any baseline fails, stop and diagnose the failed artifact. Do not weaken thresholds, remove no-claim checks, or add solver shortcuts to force a pass.

## 16. Commit And Push Requirements

After Step 25 implementation is accepted locally:

1. Review `git diff`.
2. Confirm `external/taichi_LBM3D` is unchanged.
3. Confirm raw large candidate geometry and scan data are not staged.
4. Commit all relevant Step 25 code, configs, docs, logs, outputs, tests, goal, and report.
5. Use a conventional commit message, recommended:

```text
test: add step25 controlled real geometry intake contract
```

6. Push to the configured GitHub remote, normally `origin main`, unless the user explicitly says not to push.
7. Record the final commit hash and remote branch in the Step 25 report and completion message.

Do not run:

```powershell
git add data/real_geometry_candidates/*
```

unless the files are the README, `.gitkeep`, or intentionally committed descriptor files allowed by policy.

## 17. Acceptance Checklist

The final Step 25 report must include this checklist with every accepted item checked:

```text
- [ ] candidate manifest generation passes
- [ ] candidate descriptors are valid
- [ ] candidate IDs are unique
- [ ] raw candidate geometry commit policy is enforced
- [ ] mesh candidate strict quality report passes
- [ ] voxel candidate strict quality report passes
- [ ] normalization reports are finite and domain-bounded
- [ ] normalization does not perform repair
- [ ] normalization does not perform remeshing
- [ ] original candidate files are not modified
- [ ] deterministic sampling reproducibility passes
- [ ] sampled_position_hash is repeatable
- [ ] particle mass hash is repeatable
- [ ] particle volume hash is repeatable
- [ ] projection smoke passes
- [ ] projected_mass > 0
- [ ] active_cell_count > 0
- [ ] projection smoke has no NaN
- [ ] projection smoke has no Inf
- [ ] projection smoke is not reported as FSI validation
- [ ] Step 24 regression guard passes
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
- [ ] no production sharp-interface FSI claims
- [ ] no final solver readiness claims
- [ ] no external/taichi_LBM3D edits
- [ ] no committed large raw real geometry
- [ ] no committed scan data
- [ ] no private absolute geometry paths in committed manifest outputs
- [ ] no Step 25 .vtr outputs
- [ ] no Step 25 particle .npy outputs
- [ ] artifact large_file_count == 0
- [ ] Step 25 output total size budget passes
- [ ] repo artifact_summary total_size_mb < 160
- [ ] logs/step25_pytest.log exists
- [ ] pytest -q passes
- [ ] Step 25 contract test passes
- [ ] git diff --check passes
- [ ] pre-push hook passes if push is performed
- [ ] Step 25 artifacts are pushed to GitHub origin/main unless user explicitly says not to push
```

## 18. Decision For Step 26

If Step 25 passes, the next step should be:

```text
Step 26 Controlled Real Geometry Projection-Only And Short Driver Feasibility
```

Step 26 should start from the Step 25 intake artifacts and should remain conservative:

- controlled real geometry projection-only diagnostics;
- optional very short driver feasibility;
- no squid actuation;
- no swimming;
- no production sharp-interface FSI claim;
- no final solver readiness claim.

Step 26 should not immediately claim validated squid swimming or production FSI.
