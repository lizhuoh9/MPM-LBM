# Controlled Real Geometry Intake

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

## Scope

Step 25 adds a controlled candidate intake layer before any future real-geometry solver exercise. It validates candidate descriptors, fingerprints source files with SHA-256 and exact byte size, records normalization reports, checks deterministic sampling reproducibility, and runs projection-only smoke diagnostics.

The projection smoke path initializes LBM, MPM, and `MPMToLBMProjector3D` only to verify that imported candidate particles can be projected to `solid_phi`, `solid_mass`, and `solid_vel` without NaN or Inf values. It does not run `FSIDriver3D` as a validation matrix.

## Inputs

Committed Step 25 descriptors:

- `configs/step25_candidate_smoke_mesh_descriptor.json`
- `configs/step25_candidate_smoke_voxel_descriptor.json`
- `configs/step25_intake_policy.json`

The mesh descriptor points at `data/geometry_fixtures/step25_real_candidate_smoke_mesh.obj`, a small synthetic closed cube. The voxel descriptor points at the existing small synthetic `data/geometry_fixtures/voxel_sphere.npy` fixture.

Local candidate payloads belong under `data/real_geometry_candidates/`; `.gitignore` excludes raw candidate files by default while allowing README, `.gitkeep`, and descriptor files.

## APIs

Step 25 adds:

- `src/geometry_fingerprint.py`: deterministic SHA-256, exact byte-size, and path-redacted fingerprint reporting.
- `src/geometry_candidate_manifest.py`: strict descriptor validation and manifest row generation.
- `src/geometry_normalization.py`: mesh and voxel normalization reports without source mutation, repair, or remeshing.
- `src/geometry_intake.py`: intake orchestration, strict quality checks, deterministic sampling reproducibility, and projection-only smoke diagnostics.

## Baselines

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_candidate_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_real_geometry_intake_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_mesh_candidate_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_voxel_candidate_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_normalization_reports.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_sampling_reproducibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_projection_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_step24_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_artifact_manifest.py
```

Primary outputs:

- `outputs/step25_candidate_manifest/candidate_manifest.csv`
- `outputs/step25_real_geometry_intake_smoke/intake_smoke_summary.csv`
- `outputs/step25_mesh_candidate_quality/mesh_candidate_quality.csv`
- `outputs/step25_voxel_candidate_quality/voxel_candidate_quality.csv`
- `outputs/step25_normalization_reports/normalization_summary.csv`
- `outputs/step25_sampling_reproducibility/sampling_reproducibility.csv`
- `outputs/step25_projection_smoke/projection_smoke_results.csv`
- `outputs/step25_step24_regression_guard/step24_regression_guard.csv`
- `outputs/step25_artifact_manifest/artifact_summary.json`

## Limitations

- no squid swimming;
- no squid actuation;
- no new FSI physics;
- no production sharp-interface FSI validation;
- no production mesh repair;
- no automatic remeshing;
- no two-phase flow;
- no contact angle physics;
- no raw large real geometry committed.

## Decision For Step 26

If Step 25 passes, Step 26 should remain conservative: controlled real geometry projection-only diagnostics and optional very short driver feasibility. It should not claim swimming, actuation, production sharp-interface FSI, or final readiness.
