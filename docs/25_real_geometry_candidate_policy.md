# Real Geometry Candidate Policy

Step 25 is controlled real geometry intake, not real squid validation.
Step 25 performs geometry QA, normalization, fingerprinting, sampling reproducibility, and projection-only smoke diagnostics.
Candidate intake does not perform production mesh repair or automatic remeshing.
Raw large real geometry files and scan data are not committed.

## Directory Policy

Use:

```text
data/real_geometry_candidates/
```

for local candidate descriptors and local-only raw candidate files.

Committed files in this directory are limited to:

- `README.md`
- `.gitkeep`
- `*_descriptor.json`

Raw mesh, voxel, scan, CAD, and anatomy files stay local unless they are intentionally tiny controlled smoke fixtures under `data/geometry_fixtures/` and are clearly not anatomical validation assets.

## Descriptor Policy

Descriptors must use:

```text
validation_scope = intake_qa_normalization_sampling_projection_only
quality_check_enabled = true
quality_check_strict = true
```

Allowed `commit_policy` values:

- `small_controlled_fixture_allowed`
- `do_not_commit_large_raw_geometry`
- `local_candidate_only`

Source paths in committed manifests must be repo-relative or redacted. Private absolute local paths are not committed in manifest outputs.

## Artifact Policy

Step 25 artifacts are CSV, JSON, Markdown, and small log files. Step 25 does not write `.vtr` outputs or particle `.npy` outputs. The artifact manifest checks Step 25 output size, repository size, large-file count, and local candidate payload policy.

## Solver Boundary

Step 25 does not implement squid swimming.
Step 25 does not implement squid actuation.
Step 25 does not implement new FSI physics.
Step 25 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

## Step 26 Candidate Reuse

Step 26 is controlled real geometry projection-only and short driver feasibility.
Step 26 is not real squid validation.
Step 26 does not implement squid actuation.
Step 26 does not implement squid swimming.
Step 26 does not implement new FSI physics.
Step 26 does not validate production sharp-interface FSI.

Step 26 reuses the accepted Step 25 descriptors only after fingerprint comparison against the Step 25 manifest. Generated Step 26 configs must keep strict quality gates enabled and must keep VTK and particle outputs disabled.

## Step 27 Candidate Reuse

Step 27 is controlled real geometry 64^3 short driver feasibility.
Step 27 is not real squid validation.
Step 27 does not implement squid actuation.
Step 27 does not implement squid swimming.
Step 27 does not implement new FSI physics.
Step 27 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 27 reuses the accepted Step 25 descriptors and Step 26 driver-ready geometry configs only after fingerprint comparison. Generated Step 27 driver configs must keep strict quality gates enabled and must keep VTK and particle outputs disabled.

## Step 28 Candidate Policy

Step 28 is controlled real geometry 64^3 transfer diagnostics.
Step 28 compares engineering and link_area_experimental transfer diagnostically.
Step 28 is not real squid validation.
Step 28 does not implement squid actuation.
Step 28 does not implement squid swimming.
Step 28 does not implement new FSI physics.
Step 28 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 28 continues to use only the accepted mesh and voxel smoke candidates. The candidate fingerprint guard must pass before the 64^3 transfer-pair driver rows are accepted.
