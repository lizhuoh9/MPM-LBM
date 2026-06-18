# Step 11 Goal: Writing Module, Documentation, and Reproducibility Package

## Paste-Ready `/goal`

```text
/goal
In D:\working\squid robot\LBM\MPM-LBM, execute Step 11: Writing module, project documentation, method write-up, and reproducibility package. The only authoritative execution contract is D:\working\squid robot\LBM\MPM-LBM\STEP11_WRITING_MODULE_GOAL.md.

Goal: convert the validated Step 1-10 MPM-LBM FSI engineering prototype into a readable, reproducible, reviewable documentation and technical-report package. Add README.md, docs/, paper/technical_report_draft.md, configs/README.md, a documentation contract test, and STEP11_WRITING_MODULE_REPORT.md. This is a writing/documentation step, not new solver or FSI physics work.

Hard boundaries: do not implement new FSI physics, do not change solver behavior, do not change the Step 8 moving bounce-back formula, do not replace or delete PenaltyFSICoupler3D or MovingBoundaryFSICoupler3D, do not change FSIDriver3D default behavior, do not implement two-phase flow, contact angle physics, squid geometry, sparse storage, ReducedSquidFSI, strict final momentum-conserving sharp-interface FSI, or edits to external/taichi_LBM3D. Do not overclaim the current project as production-grade, fully validated sharp-interface FSI, real squid simulation, or strict momentum-conserving FSI. Required artifacts, execution order, documentation content contracts, pytest contract, Hard Acceptance Checklist, failure handling, and completion definition are all defined in STEP11_WRITING_MODULE_GOAL.md. Finish only after the documentation contract passes, pytest passes, external/taichi_LBM3D remains unchanged, and code/docs/logs/report are pushed to GitHub.
```

## 1. Current Baseline

Step 10 is accepted and is the starting point.

Current Step 10 final commit:

```text
4f5492de5822c4a04fc041243d11cdb62db659fa
```

Step 10 validated:

```text
FSIDriverConfig supports coupling_mode = none, penalty, moving_boundary.
FSIDriver3D wraps the existing penalty-force path and moving-boundary path.
PenaltyFSICoupler3D remains available and is not replaced.
MovingBoundaryFSICoupler3D remains available and is not replaced.
lbm.step() remains the default penalty-compatible LBM step.
lbm.step_moving_bounceback() remains opt-in for moving-boundary mode.
Common diagnostics timeseries are exported as CSV and NPZ.
Step 10 driver penalty, moving_boundary, mode_matrix, and performance_profile baselines pass.
pytest -q passes with 47 tests.
external/taichi_LBM3D is unchanged.
```

The root repository currently has no `README.md`. Step 11 must create it.

Step 10 means the project currently has:

```text
1. standalone LBM baseline
2. standalone MPM baseline
3. unified units, grid, and timestep scaffold
4. MPM-to-LBM projection
5. penalty-force two-way coupling MVP
6. moving-boundary two-way coupling MVP
7. unified FSIDriver3D
8. standardized diagnostics and outputs for none, penalty, moving_boundary modes
```

Step 10 still does not mean:

```text
production-grade solver
fully validated sharp-interface FSI
strict momentum-conserving FSI
real squid geometry simulation
two-phase LBM
contact angle physics
large-grid performance readiness
```

## 2. Step 11 Objective

Step 11 turns the validated Step 1-10 engineering prototype into a documentation and writing package that can be read, reviewed, reproduced, and used as a technical-report starting point.

Create a documentation layer that covers:

```text
1. repository overview and current status
2. architecture and data flow
3. numerical method summary
4. units, grid, and timestep synchronization
5. FSI driver mode matrix
6. baseline run instructions
7. Step 10 result summary
8. known limitations and honest non-goals
9. roadmap
10. API reference
11. technical report draft
12. documentation contract test
```

This step is writing and reproducibility work. It must not change physical behavior.

## 3. Workspace And Environment

Work in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Known Python environment:

```powershell
& 'D:\working\taichi\env\python.exe' ...
```

Expected verification command:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

If a command output is saved to a log, use:

```text
logs/step11_pytest.log
```

Do not run heavy Taichi baselines unless the documentation contract exposes an actual inconsistency that requires confirming existing evidence. Step 11 should not depend on rerunning Step 10 simulations.

## 4. Strict Non-Goals

Do not implement these in Step 11:

```text
1. No new solver code.
2. No new FSI physics.
3. No new coupling mode.
4. No changes to LBMFluid3D collision, streaming, force, or bounce-back behavior.
5. No changes to MPMSolid3D mechanics or integration behavior.
6. No changes to MPMToLBMProjector3D projection math.
7. No changes to PenaltyFSICoupler3D.
8. No changes to MovingBoundaryFSICoupler3D.
9. No changes to FSIDriver3D default behavior.
10. No replacement or deletion of existing Step 6-10 artifacts.
11. No two-phase flow.
12. No contact angle physics.
13. No squid geometry.
14. No sparse storage.
15. No ReducedSquidFSI.
16. No edits to external/taichi_LBM3D.
17. No claim that the current project is production-grade.
18. No claim that strict final momentum-conserving sharp-interface FSI is complete.
19. No claim that real squid FSI is validated.
```

Allowed in Step 11:

```text
README.md
docs/*.md
paper/technical_report_draft.md
paper/figures/README.md
configs/README.md
tests/test_step11_documentation_contract.py
STEP11_WRITING_MODULE_REPORT.md
logs/step11_pytest.log
small documentation-safe edits only if needed to export or reference existing public names
```

Prefer no `src/` edits. If a `src/` edit is unavoidable, it must be documentation-only and must be explicitly justified in the Step 11 report.

## 5. Required Final Structure

Create:

```text
README.md

docs/
  00_project_status.md
  01_architecture.md
  02_numerical_methods.md
  03_units_grid_timestep.md
  04_fsi_modes.md
  05_running_baselines.md
  06_results_summary.md
  07_limitations.md
  08_roadmap.md
  09_api_reference.md

paper/
  technical_report_draft.md
  figures/
    README.md

configs/
  README.md

tests/
  test_step11_documentation_contract.py

logs/
  step11_pytest.log

STEP11_WRITING_MODULE_REPORT.md
```

No required `outputs/step11_*` directory is needed because Step 11 is documentation-oriented.

## 6. README.md Contract

Create:

```text
README.md
```

The README must be concise but complete enough for a new reader to understand what the project is and what it is not.

Required title:

```markdown
# MPM-LBM FSI Prototype
```

Required positioning:

```text
Current status: engineering prototype.
```

Required implemented list:

```text
3D single-phase LBM backend based on taichi_LBM3D
3D MPM solid backend
unified grid/unit/timestep scaffold
MPM-to-LBM projection
penalty-force two-way coupling
moving-boundary bounce-back path
moving-boundary reaction transfer to MPM
unified FSIDriver3D with modes: none, penalty, moving_boundary
```

Required not-implemented list:

```text
two-phase flow
contact angle physics
sparse storage
real squid geometry
final strict momentum-conserving sharp-interface FSI
production-grade solver readiness
```

Required quick-start commands:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_penalty_mode.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_moving_boundary_mode.py
```

Required mode table:

```markdown
| mode | LBM path | MPM reaction | cell_force | dynamic solid |
| ---- | -------- | ------------ | ---------- | ------------- |
| none | `lbm.step()` | none | zero | no |
| penalty | `lbm.step()` | `PenaltyFSICoupler3D` | nonzero | no |
| moving_boundary | `lbm.step_moving_bounceback()` | `MovingBoundaryFSICoupler3D` | zero | yes |
```

Required upstream note:

```text
The LBM backend is derived from the vendored taichi_LBM3D single-phase solver under external/taichi_LBM3D.
The external source is kept unmodified in this project workflow.
For license details, see the upstream repository and vendored license files if present.
```

Do not invent a license statement. If the license is discussed, phrase it as a pointer to upstream/license files unless the license has been explicitly inspected.

## 7. docs/00_project_status.md Contract

Create:

```text
docs/00_project_status.md
```

Must include:

```text
Completed milestones for Step 1 through Step 10.
Current validated modes: none, penalty, moving_boundary.
Current validation scale: small-scale 32^3 / 4096-particle engineering baselines.
Explicit current limitations.
Clear statement that Step 11 is documentation and reproducibility work.
```

The milestone list must include:

```text
Step 1: environment and baselines
Step 2: refactored LBMFluid3D
Step 3: MPMSolid3D
Step 4: unified units, grid, timestep
Step 5: MPM-to-LBM projection
Step 6: penalty coupling MVP
Step 7: penalty validation and stability window
Step 8: moving bounce-back scaffold
Step 9: moving-boundary reaction coupling
Step 10: unified FSI driver
```

## 8. docs/01_architecture.md Contract

Create:

```text
docs/01_architecture.md
```

Must document the role of:

```text
LBMFluid3D
MPMSolid3D
GridUnitMapper
MPMToLBMProjector3D
PenaltyFSICoupler3D
MovingBoundaryFSICoupler3D
FSIDriverConfig
FSIDriver3D
```

Must include an ASCII data-flow diagram similar to:

```text
MPMSolid3D particles
  -> MPMToLBMProjector3D
  -> LBMFluid3D solid_phi / solid_mass / solid_vel
  -> coupling mode
  -> LBM step
  -> hydro_force diagnostics or reaction
  -> MPMSolid3D grid_f_ext
```

Must explain that `FSIDriver3D` is an engineering orchestration layer, not a new physical coupling model.

## 9. docs/02_numerical_methods.md Contract

Create:

```text
docs/02_numerical_methods.md
```

Must summarize:

```text
LBM: D3Q19 MRT single-phase LBM, Guo-style forcing path for cell_force, static bounce-back, opt-in moving bounce-back.
MPM: 3D MPM solid, quadratic B-spline stencil, APIC affine velocity field, fixed-corotated elasticity.
Projection: MPM particles to LBM solid_phi, solid_mass, solid_vel.
Penalty coupling: diffuse-interface MVP using cell_force and equal/opposite reaction.
Moving-boundary coupling: opt-in moving bounce-back path and link-wise hydro_force diagnostics/reaction transfer.
```

Must include the penalty coupling expression:

```text
cell_force = beta_lbm * solid_phi * rho * (solid_vel - fluid_vel)
```

Must explicitly state:

```text
The moving-boundary reaction currently uses engineering scaling, not final strict link-area momentum integration.
The current implementation is not a strict final momentum-conserving sharp-interface FSI solver.
```

## 10. docs/03_units_grid_timestep.md Contract

Create:

```text
docs/03_units_grid_timestep.md
```

Must summarize Step 4 and include:

```text
dx_norm = 1 / n_grid
lbm_dt_phys = mpm_substeps_per_lbm_step * mpm_dt
u_lbm = u_norm * lbm_dt_phys / dx_norm
u_norm = u_lbm * dx_norm / lbm_dt_phys
a_lbm = a_norm * lbm_dt_phys^2 / dx_norm
nu_lbm = nu_norm * lbm_dt_phys / dx_norm^2
```

Must include the current default small baseline values:

```text
n_grid = 32
n_particles = 4096
mpm_dt = 4.0e-4
mpm_substeps_per_lbm_step = 10
lbm_dt_phys = 0.004
target_u_lbm around 0.02 to 0.03 in small validation cases
```

## 11. docs/04_fsi_modes.md Contract

Create:

```text
docs/04_fsi_modes.md
```

Must clearly distinguish:

```text
none
penalty
moving_boundary
```

Must include this mode table:

```markdown
| mode | Purpose | Coupler | LBM force | Solid mask | MPM reaction |
| ---- | ------- | ------- | --------- | ---------- | ------------ |
| none | baseline | none | zero | no dynamic solid | none |
| penalty | diffuse-interface MVP | `PenaltyFSICoupler3D` | `cell_force` | no dynamic solid | sampled `hydro_force` |
| moving_boundary | sharper-interface MVP | `MovingBoundaryFSICoupler3D` | zero `cell_force` | dynamic solid | link-wise `hydro_force` |
```

Must include pseudocode for each mode, matching Step 10 behavior:

```text
none:
  projector.project()
  lbm.step()
  solid.substep()

penalty:
  projector.project()
  penalty_coupler.build_penalty_force()
  lbm.step()
  penalty reaction -> MPM grid

moving_boundary:
  projector.project()
  lbm.update_dynamic_solid()
  lbm.reinitialize_new_fluid_cells()
  lbm.step_moving_bounceback()
  moving-boundary reaction -> MPM grid
```

## 12. docs/05_running_baselines.md Contract

Create:

```text
docs/05_running_baselines.md
```

Must include:

```text
basic test command
Step 10 driver baseline commands
earlier-step baseline inventory
where logs are saved
where outputs are saved
how to interpret short probes versus full acceptance baselines
```

Required commands:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_penalty_mode.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_moving_boundary_mode.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_mode_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_performance_profile.py
```

Must state that Step 11 itself does not require rerunning heavy simulations if existing Step 10 artifacts are present and tests pass.

## 13. docs/06_results_summary.md Contract

Create:

```text
docs/06_results_summary.md
```

Must summarize Step 10 results using evidence from `STEP10_FSI_DRIVER_REPORT.md`.

Required mode matrix table:

```markdown
| mode | projection_zone_ux_final | solid_vx_final | rho_min | rho_max | cell_force_max_norm | hydro_force_max_norm |
| ---- | -----------------------: | -------------: | ------: | ------: | ------------------: | -------------------: |
| none | 0.000000000e+00 | 1.562558860e-01 | 1.000000358e+00 | 1.000000358e+00 | 0.000000000e+00 | 0.000000000e+00 |
| penalty | 3.118396126e-05 | 1.536530405e-01 | 9.999890327e-01 | 1.000013232e+00 | 1.964970033e-05 | 1.964970033e-05 |
| moving_boundary | 1.293938956e-03 | 1.509043574e-01 | 9.851434231e-01 | 1.014919758e+00 | 0.000000000e+00 | 4.021631479e-01 |
```

Required trend statement:

```text
projection_zone_ux_final(moving_boundary) > projection_zone_ux_final(penalty) > projection_zone_ux_final(none)
```

Required performance table:

```markdown
| mode | total_time | projection_time | coupling_time | lbm_time | mpm_time |
| ---- | ---------: | --------------: | ------------: | -------: | -------: |
| none | 4.373437290e+01 | 8.247374999e-01 | 0.000000000e+00 | 3.809378300e+00 | 2.849920500e+00 |
| penalty | 1.652768771e+02 | 7.281521100e+00 | 5.183930000e-01 | 4.336646700e+01 | 5.827792260e+01 |
| moving_boundary | 7.204992740e+01 | 8.267775000e-01 | 6.620363001e-01 | 4.862220000e+00 | 4.369796800e+00 |
```

Must explicitly state that these are small-scale engineering baselines, not final accuracy validation.

## 14. docs/07_limitations.md Contract

Create:

```text
docs/07_limitations.md
```

Must include these limitations:

```text
single-phase fluid only
no two-phase surface tension/contact angle physics
no real squid geometry
dense grid only
moving-boundary reaction uses engineering scale
not strict final momentum-conserving sharp-interface FSI
small-scale validation only: n_grid = 32, n_particles = 4096
diagnostics often copy data to NumPy and are not production performance paths
committed logs/outputs are for reproducibility and may be large
```

Must avoid apologetic or marketing language. Keep it technical and precise.

## 15. docs/08_roadmap.md Contract

Create:

```text
docs/08_roadmap.md
```

Must include a conservative future roadmap. Suggested items:

```text
Step 12: performance and memory cleanup
Step 13: geometry ingestion / squid proxy geometry
Step 14: larger-grid validation
Step 15: moving-boundary reaction calibration and sharper momentum accounting
Step 16: optional two-phase LBM exploration
```

Must state that future steps should preserve the existing regression baselines and mode matrix before adding new physics.

## 16. docs/09_api_reference.md Contract

Create:

```text
docs/09_api_reference.md
```

Must include sections for:

```text
LBMFluid3D
MPMSolid3D
GridUnitMapper
UnifiedSimConfig
MPMToLBMProjector3D
PenaltyFSICoupler3D
MovingBoundaryFSICoupler3D
FSIDriverConfig
FSIDriver3D
FSIDiagnostics3D
```

Each section must list:

```text
purpose
main fields or config inputs
main methods
which mode or step uses it
```

This is a lightweight API reference, not full autogenerated documentation.

## 17. configs/README.md Contract

Create:

```text
configs/README.md
```

Must describe:

```text
step10_penalty_default.json
step10_moving_boundary_default.json
step10_mode_matrix.json
coupling_mode field
common grid/timestep fields
force/coupling fields
how configs are loaded by FSIDriverConfig.from_json()
```

Must warn that config values are currently tuned for small validation baselines.

## 18. paper/technical_report_draft.md Contract

Create:

```text
paper/technical_report_draft.md
```

Required title:

```markdown
# A Taichi-based Prototype for 3D MPM-LBM Fluid-Solid Coupling
```

Required sections:

```markdown
## Abstract
## 1. Introduction
## 2. System Architecture
## 3. Numerical Methods
## 4. Coupling Modes
## 5. Validation Baselines
## 6. Results
## 7. Limitations
## 8. Future Work
## Appendix A: Reproducibility Commands
## Appendix B: Configuration Examples
```

The abstract must be 150-250 words and must state:

```text
Taichi-based prototype
3D MPM solid solver
single-phase D3Q19 MRT LBM fluid solver
penalty-force mode
moving-boundary bounce-back mode
unified driver/config/diagnostics scaffold
small-scale 32^3 / 4096-particle validation
not final strict momentum-conserving sharp-interface FSI
no two-phase flow, contact-angle physics, or real squid geometry
```

The report must be honest and must not claim final validation beyond the committed baselines.

## 19. paper/figures/README.md Contract

Create:

```text
paper/figures/README.md
```

Must state:

```text
No required Step 11 figures are generated.
Future figures should be generated from committed CSV/NPZ/VTK artifacts.
Do not hand-draw or fabricate result plots.
```

## 20. Documentation Contract Test

Create:

```text
tests/test_step11_documentation_contract.py
```

The test must check required paths:

```python
required_paths = [
    "README.md",
    "docs/00_project_status.md",
    "docs/01_architecture.md",
    "docs/02_numerical_methods.md",
    "docs/03_units_grid_timestep.md",
    "docs/04_fsi_modes.md",
    "docs/05_running_baselines.md",
    "docs/06_results_summary.md",
    "docs/07_limitations.md",
    "docs/08_roadmap.md",
    "docs/09_api_reference.md",
    "configs/README.md",
    "paper/technical_report_draft.md",
    "paper/figures/README.md",
    "STEP11_WRITING_MODULE_REPORT.md",
]
```

The test must check README keywords:

```text
MPM-LBM
Taichi
engineering prototype
FSIDriver3D
none
penalty
moving_boundary
not production
two-phase flow
contact angle
squid geometry
strict momentum-conserving
```

The test must check limitations keywords:

```text
single-phase
engineering scale
not strict
no real squid geometry
dense grid
small-scale
```

The test must check API reference keywords:

```text
LBMFluid3D
MPMSolid3D
GridUnitMapper
UnifiedSimConfig
MPMToLBMProjector3D
PenaltyFSICoupler3D
MovingBoundaryFSICoupler3D
FSIDriverConfig
FSIDriver3D
FSIDiagnostics3D
```

The test must check results summary includes:

```text
projection_zone_ux_final
moving_boundary
penalty
none
1.293938956e-03
3.118396126e-05
performance
```

The test must check report acceptance checklist items are marked `[x]`.

The test must also check that Step 11 documentation does not contain overclaims such as:

```text
production-grade solver
fully validated sharp-interface FSI
real squid simulation is validated
strict momentum-conserving FSI is complete
```

Use exact string checks where possible. Keep the test lightweight and deterministic.

## 21. Step 11 Report Contract

Create:

```text
STEP11_WRITING_MODULE_REPORT.md
```

Required sections:

```markdown
# Step 11 Writing Module Report

## 1. Goal
## 2. Files Created
## 3. Documentation Scope
## 4. Explicit Non-Goals
## 5. README Summary
## 6. Technical Report Draft
## 7. Verification
## 8. GitHub Sync
## 9. Acceptance Checklist
## 10. Decision
```

The report must include:

```text
pytest command and result
README.md created
docs/ created
paper/technical_report_draft.md created
documentation contract test added
no solver code changes, or explicit justification for any documentation-only source edit
no new FSI physics
no external/taichi_LBM3D edits
final commit hash
remote branch after push
```

Acceptance checklist in the report must include all items from the Hard Acceptance Checklist and must be completed with `[x]` only after verification.

## 22. Required Execution Order

Follow this order:

```text
1. Confirm git status, branch, and remote.
2. Confirm README.md does not already exist or read it if it does.
3. Read STEP10_FSI_DRIVER_REPORT.md and Step 10 docs/tests needed for source numbers.
4. Add tests/test_step11_documentation_contract.py first.
5. Run pytest and confirm the Step 11 contract test fails because docs are missing. Record this as RED evidence.
6. Add README.md and docs/00, 01, 04, 07 first.
7. Add docs/02, 03, 05, 06, 08, 09, configs/README.md, paper/technical_report_draft.md, paper/figures/README.md.
8. Add STEP11_WRITING_MODULE_REPORT.md with unchecked checklist.
9. Run pytest -q.
10. Fix only documentation/test-contract issues.
11. Run pytest -q again and save logs/step11_pytest.log.
12. Confirm external/taichi_LBM3D is unchanged.
13. Confirm no source solver changes unless explicitly documented.
14. Update STEP11_WRITING_MODULE_REPORT.md checklist to checked.
15. Run final pytest -q.
16. Run git diff --check.
17. Commit Step 11 artifacts.
18. Push to GitHub.
19. Verify local HEAD equals origin/main.
```

Do not report a short probe as Step 11 acceptance. Step 11 acceptance is based on documentation artifacts, documentation contract test, full pytest, report completion, and GitHub push.

## 23. Verification Commands

Primary test:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Log-saving form:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q 2>&1 | Tee-Object -FilePath logs\step11_pytest.log
```

Git hygiene:

```powershell
git status --short --branch
git status --short external
git diff --check
git diff --cached --check
```

If `pytest -q` fails due to documentation contract errors, fix the documentation or the contract. Do not change solver code to make a documentation test pass.

## 24. Hard Acceptance Checklist

All must be true before Step 11 is complete:

```text
[ ] main is on the Step 11 final commit
[ ] README.md exists
[ ] README.md states current status is engineering prototype
[ ] README.md lists none / penalty / moving_boundary
[ ] README.md lists not-implemented items
[ ] README.md includes upstream taichi_LBM3D note
[ ] docs/00_project_status.md exists
[ ] docs/01_architecture.md exists
[ ] docs/02_numerical_methods.md exists
[ ] docs/03_units_grid_timestep.md exists
[ ] docs/04_fsi_modes.md exists
[ ] docs/05_running_baselines.md exists
[ ] docs/06_results_summary.md exists
[ ] docs/07_limitations.md exists
[ ] docs/08_roadmap.md exists
[ ] docs/09_api_reference.md exists
[ ] configs/README.md exists
[ ] paper/technical_report_draft.md exists
[ ] paper/figures/README.md exists
[ ] docs explain moving-boundary reaction uses engineering scale
[ ] docs state the project is not strict final momentum-conserving sharp-interface FSI
[ ] docs state there is no real squid geometry
[ ] docs state single-phase only
[ ] Step 10 mode matrix results are included in results summary
[ ] Step 10 performance profile is included in results summary
[ ] API reference includes all main classes
[ ] tests/test_step11_documentation_contract.py exists
[ ] documentation contract test passes
[ ] pytest -q passes
[ ] logs/step11_pytest.log exists
[ ] no new solver code
[ ] no new FSI physics
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] no overclaims about production-grade or fully validated sharp-interface FSI
[ ] STEP11_WRITING_MODULE_REPORT.md is complete
[ ] Step 11 artifacts are committed
[ ] Step 11 artifacts are pushed to GitHub
```

## 25. Failure Handling

If a documentation claim conflicts with actual code or committed results:

```text
The documentation must be corrected to match the code/results.
Do not change solver code in Step 11 to satisfy the documentation.
```

If a required number is missing from Step 10 reports/logs:

```text
Search committed Step 10 logs and outputs first.
If still missing, write that the value is not available in committed artifacts.
Do not fabricate numbers.
```

If pytest fails due to existing unrelated tests:

```text
Record the exact failing tests and error text.
Fix only if the failure is caused by Step 11 edits.
Do not mask or skip tests without explicit justification.
```

If GitHub push fails:

```text
Keep the local commit.
Record the exact push error.
Do not force-push unless explicitly requested.
```

## 26. Completion Definition

Step 11 is complete only when:

```text
1. all required documentation artifacts exist
2. documentation claims match existing Step 1-10 evidence
3. documentation contract test passes
4. full pytest -q passes
5. logs/step11_pytest.log is saved
6. STEP11_WRITING_MODULE_REPORT.md has a completed checklist
7. external/taichi_LBM3D remains unchanged
8. no new solver or FSI physics was added
9. final Step 11 commit is pushed to GitHub
10. local HEAD matches origin/main
```

Only after those conditions are satisfied may the report mark:

```text
Can proceed to Step 12?

- [x] Yes
- [ ] No
```
