# Step 12 Goal: Performance, Memory, and Artifact Hygiene

## Paste-Ready `/goal`

```text
/goal
In D:\working\squid robot\LBM\MPM-LBM, execute Step 12: Performance, memory, and artifact hygiene. The only authoritative execution contract is D:\working\squid robot\LBM\MPM-LBM\STEP12_PERFORMANCE_MEMORY_GOAL.md.

Goal: without changing FSI physics or Step 10 validated behavior, add a repeatable performance/memory/artifact hygiene layer for the current MPM-LBM FSI prototype. Add memory estimate utilities, artifact manifest utilities, lightweight driver profiling, no-physics regression checks, docs, report, logs, outputs, and a pytest contract. Preserve the Step 10 mode matrix and keep all optimization claims conservative.

Hard boundaries: do not implement new FSI physics, do not change solver behavior, do not change lbm.step() default behavior, do not change penalty or moving_boundary formulas, do not replace PenaltyFSICoupler3D or MovingBoundaryFSICoupler3D, do not implement two-phase flow, contact angle physics, squid geometry, sparse storage, ReducedSquidFSI, production-grade optimization, or edits to external/taichi_LBM3D. Required artifacts, execution order, profiling settings, memory formulas, artifact policy, pytest contract, Hard Acceptance Checklist, failure handling, and completion definition are all defined in STEP12_PERFORMANCE_MEMORY_GOAL.md. Finish only after all Step 12 baselines pass, pytest passes, external/taichi_LBM3D remains unchanged, and code/docs/logs/outputs/report are pushed to GitHub.
```

## 1. Current Baseline

Step 11 is accepted and is the starting point.

Current Step 11 final commit:

```text
2817edb4b8523575ca5d560fca475e456ea8e208
```

Step 11 validated:

```text
README.md exists.
docs/ exists and describes status, architecture, numerical methods, modes, running baselines, results, limitations, roadmap, and API reference.
paper/technical_report_draft.md exists.
configs/README.md exists.
tests/test_step11_documentation_contract.py exists.
logs/step11_pytest.log records pytest success.
pytest -q passes with 55 tests.
src/ was not modified by Step 11.
external/taichi_LBM3D was not modified.
```

Step 11 means the repository is now:

```text
readable
reproducible
reviewable
documented
ready for resource-governance work
```

Step 11 still does not mean:

```text
production-grade solver
large-grid performance readiness
strict final momentum-conserving sharp-interface FSI
real squid geometry simulation
two-phase LBM
contact angle physics
sparse storage
```

## 2. Step 12 Objective

Step 12 establishes a performance, memory, and artifact hygiene framework before adding geometry or larger-grid work.

Implement a small engineering layer that provides:

```text
1. repeatable memory estimates for dense LBM, MPM, and coupling state
2. lightweight timing/profile matrix for none, penalty, moving_boundary
3. artifact manifest generation for logs, outputs, reports, docs, paper, and configs
4. scratch-output policy and .gitignore hygiene
5. no-physics regression baseline proving Step 10 mode behavior is preserved
6. docs for performance/memory and artifact policy
7. pytest contract for Step 12 files, logs, outputs, and non-goals
8. STEP12_PERFORMANCE_MEMORY_REPORT.md
```

This step is not about making the solver production-grade. It is about measuring and governing resource growth.

## 3. Workspace And Environment

Work in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Known Python environment:

```powershell
& 'D:\working\taichi\env\python.exe' ...
```

Primary verification command:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Runtime baselines should use the existing project pattern and Taichi GPU backend when required by the existing scripts:

```python
ti.init(arch=ti.gpu, default_fp=ti.f32)
```

If a GPU-specific Taichi initialization fails, record the exact error and do not silently downgrade final acceptance to CPU unless the contract is explicitly revised.

## 4. Strict Non-Goals

Do not implement these in Step 12:

```text
1. No new FSI physics.
2. No new coupling mode.
3. No changes to Step 8 moving bounce-back formula.
4. No changes to penalty-force formula.
5. No changes to moving_boundary reaction formula.
6. No replacement or deletion of PenaltyFSICoupler3D.
7. No replacement or deletion of MovingBoundaryFSICoupler3D.
8. No change to lbm.step() default behavior.
9. No two-phase flow.
10. No contact angle physics.
11. No squid geometry.
12. No sparse storage implementation.
13. No ReducedSquidFSI.
14. No edits to external/taichi_LBM3D.
15. No production-grade optimization claim.
16. No deletion of Step 10 mode matrix artifacts required by existing tests.
```

Allowed in Step 12:

```text
performance and timing helpers
memory estimate helpers
artifact manifest helpers
small JSON profile configs
lightweight Step 12 baseline scripts
docs for performance/memory and artifact policy
.gitignore scratch-output policy
README and roadmap links
pytest contract
Step 12 report
logs and outputs for Step 12
```

Any `src/` edits must be limited to new helper modules or export updates. Do not touch solver physics modules unless an import/export-only change is strictly necessary and documented.

## 5. Required Final Structure

Create:

```text
src/
  performance.py
  artifact_utils.py

docs/
  10_performance_memory.md
  11_artifact_policy.md

configs/
  step12_profile_none.json
  step12_profile_penalty.json
  step12_profile_moving_boundary.json

baseline_tests/
  run_step12_memory_estimate.py
  run_step12_driver_profile_matrix.py
  run_step12_artifact_manifest.py
  run_step12_no_physics_regression.py

outputs/
  step12_memory_estimate/
  step12_profile_matrix/
  step12_artifact_manifest/
  step12_no_physics_regression/

logs/
  step12_memory_estimate.log
  step12_profile_matrix.log
  step12_artifact_manifest.log
  step12_no_physics_regression.log
  step12_pytest.log

tests/
  test_step12_performance_memory_contract.py

STEP12_PERFORMANCE_MEMORY_REPORT.md
```

Update:

```text
.gitignore
README.md
docs/08_roadmap.md
src/__init__.py, only if exporting the new helper functions is useful
```

Do not delete Step 1-11 reports, logs, or outputs.

## 6. `src/performance.py` Contract

Create:

```text
src/performance.py
```

Required public API:

```python
class PerformanceTimer:
    def __init__(self):
        ...

    def start(self, name: str):
        ...

    def stop(self, name: str):
        ...

    def row(self) -> dict:
        ...


def estimate_lbm_memory_bytes(n_grid: int, dtype_bytes: int = 4) -> dict:
    ...


def estimate_mpm_memory_bytes(n_grid: int, n_particles: int, dtype_bytes: int = 4) -> dict:
    ...


def estimate_coupling_memory_bytes(n_grid: int, dtype_bytes: int = 4) -> dict:
    ...


def estimate_total_memory_bytes(n_grid: int, n_particles: int, dtype_bytes: int = 4) -> dict:
    ...
```

Validation behavior:

```text
n_grid must be positive.
n_particles must be positive where used.
dtype_bytes must be positive.
returned byte counts must be non-negative integers.
returned MB fields must be finite floats.
```

### LBM Memory Estimate

Base the dense LBM estimate on current `LBMFluid3D` fields:

```text
f: 19 floats / cell
F: 19 floats / cell
rho: 1 float / cell
v: 3 floats / cell
solid_phi: 1 float / cell
solid_mass: 1 float / cell
solid_vel: 3 floats / cell
cell_force: 3 floats / cell
hydro_force: 3 floats / cell
solid: 1 int8 / cell
static_solid: 1 int8 / cell
old_solid: 1 int8 / cell
reinit_flag: 1 int8 / cell
```

Approximate per-cell estimate:

```text
float fields per cell = 53
float bytes per cell = 53 * dtype_bytes
int8 fields per cell = 4
LBM dense field estimate = n_grid^3 * (53 * dtype_bytes + 4)
```

This estimate excludes Taichi runtime overhead, allocator overhead, scalar fields, and MRT matrices. The function must state these assumptions in returned metadata.

### MPM Memory Estimate

Particle fields:

```text
x: 3 floats / particle
v: 3 floats / particle
C: 9 floats / particle
F: 9 floats / particle
Jp: 1 float / particle
mass: 1 float / particle
vol0: 1 float / particle
```

Approximate:

```text
particle floats = 27
particle bytes = n_particles * 27 * dtype_bytes
```

Grid fields:

```text
grid_v: 3 floats / grid node
grid_m: 1 float / grid node
grid_f_ext: 3 floats / grid node
```

Approximate:

```text
grid floats = 7
grid bytes = n_grid^3 * 7 * dtype_bytes
```

### Coupling Memory Estimate

Projection and coupling mostly reuse LBM fields plus scalar diagnostics. Estimate additional large arrays as zero for the current implementation and include metadata:

```text
projection fields are counted in LBM estimate
coupling scalar diagnostics are negligible compared with dense LBM / MPM grid fields
```

### Total Estimate

`estimate_total_memory_bytes()` must return a dictionary containing at least:

```text
n_grid
n_cells
n_particles
lbm_estimated_bytes
mpm_particle_estimated_bytes
mpm_grid_estimated_bytes
coupling_estimated_bytes
total_estimated_bytes
lbm_estimated_mb
mpm_particle_estimated_mb
mpm_grid_estimated_mb
coupling_estimated_mb
total_estimated_mb
```

## 7. `src/artifact_utils.py` Contract

Create:

```text
src/artifact_utils.py
```

Required public API:

```python
def format_size(num_bytes: int) -> str:
    ...


def scan_artifacts(root_paths=("logs", "outputs")) -> list[dict]:
    ...


def write_artifact_manifest(rows, csv_path):
    ...


def summarize_artifacts(rows) -> dict:
    ...


def write_artifact_summary(summary, json_path):
    ...
```

Manifest row schema:

```text
path
kind
extension
size_bytes
size_mb
is_large
```

Rules:

```text
kind is the top-level category, such as logs, outputs, docs, paper, configs, reports
extension is lowercase
size_bytes is integer
size_mb is size_bytes / 1024 / 1024
is_large is true when size_mb >= 5.0
scan order must be deterministic
```

Summary schema:

```json
{
  "file_count": 0,
  "total_size_bytes": 0,
  "total_size_mb": 0.0,
  "large_file_count": 0,
  "by_extension": {}
}
```

Do not delete files. This module only scans and writes manifests.

## 8. `.gitignore` Contract

Update:

```text
.gitignore
```

Required scratch policy:

```gitignore
# Python
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Taichi / runtime cache
.taichi_cache/
.cache/

# Local scratch outputs
outputs/tmp/
outputs/scratch/
logs/tmp/
logs/scratch/

# Large ad-hoc experiment dumps
outputs/experiments/
logs/experiments/

# Local environments
.venv/
.env/
```

Do not ignore:

```text
outputs/step*
logs/step*
```

The current committed step artifacts are part of reproducibility and existing tests.

## 9. Config Contracts

Create:

```text
configs/step12_profile_none.json
configs/step12_profile_penalty.json
configs/step12_profile_moving_boundary.json
```

All three should use:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
mpm_dt = 4.0e-4
write_vtk = false
write_particles = false
output_interval = 10
```

Mode-specific:

```text
none: coupling_mode = "none"
penalty: coupling_mode = "penalty"
moving_boundary: coupling_mode = "moving_boundary"
```

The configs are for timing/profile baselines, not final physical validation.

## 10. Baseline 1: Memory Estimate

Create:

```text
baseline_tests/run_step12_memory_estimate.py
```

Purpose:

```text
Generate memory estimates for representative dense-grid sizes.
```

Required cases:

```text
n_grid = 32,  n_particles = 4096
n_grid = 64,  n_particles = 32768
n_grid = 96,  n_particles = 110592
n_grid = 128, n_particles = 262144
```

Required outputs:

```text
outputs/step12_memory_estimate/memory_estimate.csv
outputs/step12_memory_estimate/memory_estimate.npz
logs/step12_memory_estimate.log
```

Required CSV fields:

```text
n_grid
n_cells
n_particles
lbm_estimated_mb
mpm_particle_estimated_mb
mpm_grid_estimated_mb
coupling_estimated_mb
total_estimated_mb
```

Required log marker:

```text
[OK] Step 12 memory estimate finished
```

Acceptance:

```text
memory_estimate.csv exists
memory_estimate.npz exists
all values finite
total_estimated_mb increases monotonically with n_grid
32^3 estimate < 1024 MB
128^3 estimate is reported, not necessarily runnable
```

## 11. Baseline 2: Driver Profile Matrix

Create:

```text
baseline_tests/run_step12_driver_profile_matrix.py
```

Purpose:

```text
Run a lightweight profile matrix using FSIDriver3D with reduced I/O.
```

Use modes:

```text
none
penalty
moving_boundary
```

Required settings:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
write_vtk = false
write_particles = false
output_interval = 10
```

Required outputs:

```text
outputs/step12_profile_matrix/profile_matrix.csv
outputs/step12_profile_matrix/profile_matrix.npz
logs/step12_profile_matrix.log
```

Required CSV fields:

```text
mode
total_time
init_time
projection_time
coupling_time
lbm_step_time
mpm_substep_time
diagnostics_time
export_time
steps
substeps
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
```

Required log marker:

```text
[OK] Step 12 driver profile matrix finished
```

Acceptance:

```text
all modes finish
all timing values finite
total_time > 0
projection_time >= 0
coupling_time >= 0
moving_boundary and penalty both stable
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
```

## 12. Baseline 3: Artifact Manifest

Create:

```text
baseline_tests/run_step12_artifact_manifest.py
```

Purpose:

```text
Scan committed and generated artifacts so future steps can see where repository size grows.
```

Scan roots:

```text
logs/
outputs/
STEP*_REPORT.md
docs/
paper/
configs/
```

Required outputs:

```text
outputs/step12_artifact_manifest/artifact_manifest.csv
outputs/step12_artifact_manifest/artifact_summary.json
logs/step12_artifact_manifest.log
```

Required log marker:

```text
[OK] Step 12 artifact manifest finished
```

Acceptance:

```text
manifest exists
summary exists
file_count > 0
total_size_bytes > 0
large_file_count >= 0
no NaN
no Inf
```

## 13. Baseline 4: No-Physics Regression

Create:

```text
baseline_tests/run_step12_no_physics_regression.py
```

Purpose:

```text
Prove Step 12 did not change Step 10 physics behavior.
```

Method:

```text
Use FSIDriver3D to run a lightweight mode matrix.
Do not copy solver physics.
Do not add new FSI physics.
```

Recommended settings:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
write_vtk = false
write_particles = false
output_interval = 10
```

Required outputs:

```text
outputs/step12_no_physics_regression/no_physics_regression.csv
outputs/step12_no_physics_regression/no_physics_regression.npz
logs/step12_no_physics_regression.log
```

Required checks:

```text
none stable
penalty stable
moving_boundary stable
projection_zone_ux_final(moving_boundary) > projection_zone_ux_final(penalty) > projection_zone_ux_final(none)
penalty cell_force_max_norm > 0
moving_boundary cell_force_max_norm == 0
moving_boundary bb_link_count > 0
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
```

Required log marker:

```text
[OK] Step 12 no-physics regression finished
```

## 14. Documentation Updates

Create:

```text
docs/10_performance_memory.md
docs/11_artifact_policy.md
```

Update:

```text
README.md
docs/08_roadmap.md
```

### `docs/10_performance_memory.md`

Must include:

```text
Step 12 scope
dense-grid memory model
LBM estimate fields
MPM particle estimate fields
MPM grid estimate fields
coupling estimate assumptions
current baseline scale n_grid = 32 and n_particles = 4096
scaling warning for 128^3 and larger
profile matrix explanation
```

Must state:

```text
Step 12 estimates dense-grid memory and records timing baselines.
Step 12 does not implement optimization or new solver physics.
```

### `docs/11_artifact_policy.md`

Must include:

```text
committed artifacts policy
scratch artifacts policy
heavy experiments policy
manifest fields
large-file threshold
do not commit ad-hoc large outputs unless they are documented step baselines
```

Required scratch locations:

```text
outputs/tmp/
outputs/scratch/
logs/tmp/
logs/scratch/
outputs/experiments/
logs/experiments/
```

### README Update

Add a concise section:

```markdown
## Performance and Artifact Policy

See:
- docs/10_performance_memory.md
- docs/11_artifact_policy.md
```

Do not change the project positioning from engineering prototype.

### Roadmap Update

Update `docs/08_roadmap.md` so Step 12 is marked as current or completed after Step 12 succeeds, and Step 13 remains:

```text
geometry ingestion / squid proxy geometry
```

## 15. Step 12 Report Contract

Create:

```text
STEP12_PERFORMANCE_MEMORY_REPORT.md
```

Required sections:

```markdown
# Step 12 Performance, Memory, and Artifact Hygiene Report

## 1. Goal
## 2. Files
## 3. Explicit Non-Goals
## 4. Memory Estimate Baseline
## 5. Driver Profile Matrix
## 6. Artifact Manifest
## 7. No-Physics Regression
## 8. Documentation Updates
## 9. Verification
## 10. GitHub Sync
## 11. Acceptance Checklist
## 12. Decision
```

The report must include:

```text
commands run
key memory estimate table
profile timing table
artifact summary
no-physics regression result
pytest command/result
confirmation that no external/taichi_LBM3D edits occurred
confirmation that no solver physics changed
final commit hash
remote branch after push
```

Before final verification, checklist items may be unchecked. They must be checked only after baselines and pytest pass.

## 16. Pytest Contract

Create:

```text
tests/test_step12_performance_memory_contract.py
```

The test must check required paths:

```python
required_paths = [
    "src/performance.py",
    "src/artifact_utils.py",
    "docs/10_performance_memory.md",
    "docs/11_artifact_policy.md",
    "configs/step12_profile_none.json",
    "configs/step12_profile_penalty.json",
    "configs/step12_profile_moving_boundary.json",
    "baseline_tests/run_step12_memory_estimate.py",
    "baseline_tests/run_step12_driver_profile_matrix.py",
    "baseline_tests/run_step12_artifact_manifest.py",
    "baseline_tests/run_step12_no_physics_regression.py",
    "logs/step12_memory_estimate.log",
    "logs/step12_profile_matrix.log",
    "logs/step12_artifact_manifest.log",
    "logs/step12_no_physics_regression.log",
    "outputs/step12_memory_estimate/memory_estimate.csv",
    "outputs/step12_memory_estimate/memory_estimate.npz",
    "outputs/step12_profile_matrix/profile_matrix.csv",
    "outputs/step12_profile_matrix/profile_matrix.npz",
    "outputs/step12_artifact_manifest/artifact_manifest.csv",
    "outputs/step12_artifact_manifest/artifact_summary.json",
    "outputs/step12_no_physics_regression/no_physics_regression.csv",
    "outputs/step12_no_physics_regression/no_physics_regression.npz",
    "STEP12_PERFORMANCE_MEMORY_REPORT.md",
]
```

The test must check source keywords:

```text
estimate_lbm_memory_bytes
estimate_mpm_memory_bytes
estimate_total_memory_bytes
scan_artifacts
write_artifact_manifest
summarize_artifacts
FSIDriver3D
coupling_mode
```

The test must check log success markers:

```text
[OK] Step 12 memory estimate finished
[OK] Step 12 driver profile matrix finished
[OK] Step 12 artifact manifest finished
[OK] Step 12 no-physics regression finished
```

The test must parse Step 12 CSV/JSON outputs and verify:

```text
memory total values are finite
memory total values increase monotonically
profile matrix contains none, penalty, moving_boundary
profile total_time values are finite and positive
artifact summary file_count > 0
artifact summary total_size_bytes > 0
no-physics regression trend is preserved
```

The test must check forbidden implementation tokens in Step 12 source/scripts:

```text
two_phase
contact_angle
ReducedSquidFSI
```

Do not forbid the phrase `sparse storage` in docs because it is a documented non-goal.

The test must check the Step 12 report checklist items are marked `[x]`.

## 17. Required Execution Order

Follow this order:

```text
1. Confirm git status, branch, remote, README, and Step 11 baseline.
2. Read STEP12_PERFORMANCE_MEMORY_GOAL.md.
3. Read README.md, docs/08_roadmap.md, STEP11_WRITING_MODULE_REPORT.md, and Step 10/11 contracts as needed.
4. Add tests/test_step12_performance_memory_contract.py first.
5. Run pytest and confirm RED because Step 12 artifacts are missing.
6. Implement src/performance.py and memory estimate baseline.
7. Run memory estimate baseline and save log.
8. Implement src/artifact_utils.py and artifact manifest baseline.
9. Run artifact manifest baseline and save log.
10. Add Step 12 profile configs.
11. Implement driver profile matrix baseline.
12. Implement no-physics regression baseline.
13. Run both profile/regression baselines and save logs.
14. Add docs/10_performance_memory.md and docs/11_artifact_policy.md.
15. Update README.md, docs/08_roadmap.md, and .gitignore.
16. Add STEP12_PERFORMANCE_MEMORY_REPORT.md with unchecked checklist.
17. Run pytest -q.
18. Fix only Step 12 issues.
19. Save final pytest log as logs/step12_pytest.log.
20. Confirm src solver physics modules are unchanged except new helper exports, if any.
21. Confirm external/taichi_LBM3D is unchanged.
22. Update STEP12_PERFORMANCE_MEMORY_REPORT.md checklist to checked.
23. Run final pytest -q.
24. Run git diff --check and git diff --cached --check.
25. Commit Step 12 artifacts.
26. Push to GitHub.
27. Verify local HEAD equals origin/main.
```

Do not report a short probe as Step 12 acceptance. Step 12 acceptance requires all four Step 12 baselines, pytest, report, and GitHub push.

## 18. Verification Commands

Primary:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Baseline commands:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step12_memory_estimate.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step12_driver_profile_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step12_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step12_no_physics_regression.py
```

Log-saving form:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step12_memory_estimate.py 2>&1 | Tee-Object -FilePath logs\step12_memory_estimate.log
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step12_driver_profile_matrix.py 2>&1 | Tee-Object -FilePath logs\step12_profile_matrix.log
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step12_artifact_manifest.py 2>&1 | Tee-Object -FilePath logs\step12_artifact_manifest.log
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step12_no_physics_regression.py 2>&1 | Tee-Object -FilePath logs\step12_no_physics_regression.log
& 'D:\working\taichi\env\python.exe' -m pytest -q 2>&1 | Tee-Object -FilePath logs\step12_pytest.log
```

For UTF-8 logs on Windows, it is acceptable to capture output and write with `Out-File -Encoding utf8`.

Git hygiene:

```powershell
git status --short --branch
git status --short external
git diff --check
git diff --cached --check
```

## 19. Hard Acceptance Checklist

All must be true before Step 12 is complete:

```text
[ ] main is on the Step 12 final commit
[ ] src/performance.py exists
[ ] src/artifact_utils.py exists
[ ] docs/10_performance_memory.md exists
[ ] docs/11_artifact_policy.md exists
[ ] .gitignore exists and ignores tmp/scratch/experiments
[ ] configs/step12_profile_none.json exists
[ ] configs/step12_profile_penalty.json exists
[ ] configs/step12_profile_moving_boundary.json exists
[ ] baseline_tests/run_step12_memory_estimate.py exists
[ ] baseline_tests/run_step12_driver_profile_matrix.py exists
[ ] baseline_tests/run_step12_artifact_manifest.py exists
[ ] baseline_tests/run_step12_no_physics_regression.py exists
[ ] memory_estimate.csv exists
[ ] memory_estimate.npz exists
[ ] memory estimate values are finite
[ ] memory estimate total increases monotonically with n_grid
[ ] profile_matrix.csv exists
[ ] profile_matrix.npz exists
[ ] none / penalty / moving_boundary profiles complete
[ ] artifact_manifest.csv exists
[ ] artifact_summary.json exists
[ ] no-physics regression passes
[ ] Step 10 mode trend is preserved
[ ] rho_min > 0.95
[ ] rho_max < 1.05
[ ] lbm_max_v < 0.1
[ ] mpm_min_J > 0
[ ] no NaN
[ ] no Inf
[ ] no new FSI physics
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] README links Step 12 docs
[ ] docs/08_roadmap.md updated
[ ] STEP12_PERFORMANCE_MEMORY_REPORT.md complete
[ ] tests/test_step12_performance_memory_contract.py exists
[ ] pytest -q passes
[ ] logs/step12_pytest.log exists
[ ] Step 12 artifacts are committed
[ ] Step 12 artifacts are pushed to GitHub
```

## 20. Failure Handling

If a profile baseline is slow:

```text
Do not shrink it below the contract and still call it accepted.
Reduce optional I/O first.
Keep n_grid = 32, n_particles = 4096, n_lbm_steps = 10 unless the report explicitly marks a smaller run as a probe.
```

If a memory estimate seems too optimistic:

```text
State that it is a dense-field lower-bound estimate and excludes Taichi runtime/allocator overhead.
Do not present it as measured GPU allocation.
```

If no-physics regression fails:

```text
Stop and inspect whether Step 12 changed behavior.
Do not weaken the trend check without documenting the reason.
Do not change solver physics to force the trend.
```

If artifact manifest finds large files:

```text
Record them in the manifest and summary.
Do not delete committed baseline artifacts unless explicitly requested.
```

If pytest fails:

```text
Record the exact failing tests and error text.
Fix only issues caused by Step 12 unless the user explicitly broadens scope.
```

If GitHub push fails:

```text
Keep the local commit.
Record the exact push error.
Do not force-push unless explicitly requested.
```

## 21. Completion Definition

Step 12 is complete only when:

```text
1. all required Step 12 files exist
2. memory estimate baseline passes
3. driver profile matrix baseline passes
4. artifact manifest baseline passes
5. no-physics regression baseline passes
6. docs and README updates are complete
7. Step 12 report has a completed checklist
8. pytest -q passes
9. logs/step12_pytest.log is saved
10. external/taichi_LBM3D remains unchanged
11. no solver physics was changed
12. final Step 12 commit is pushed to GitHub
13. local HEAD matches origin/main
```

Only after those conditions are satisfied may the report mark:

```text
Can proceed to Step 13?

- [x] Yes
- [ ] No
```
