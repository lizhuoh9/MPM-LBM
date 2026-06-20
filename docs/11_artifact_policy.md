# Artifact Policy

Step reports, selected logs, and selected outputs are committed for reproducibility. Ad-hoc files should stay in scratch locations unless they become part of a documented step baseline.

## Committed Artifacts

Committed artifacts may include:

- `STEP*_REPORT.md`
- `logs/step*.log`
- `outputs/step*/` files required by contract tests
- documentation under `docs/`
- report drafts under `paper/`
- reproducibility configs under `configs/`

These files support review and regression checks.

## Scratch Artifacts

Use these paths for local scratch files:

```text
outputs/tmp/
outputs/scratch/
logs/tmp/
logs/scratch/
```

They are ignored by git and should not be cited as acceptance evidence.

## Heavy Experiments

Use these paths for ad-hoc large runs:

```text
outputs/experiments/
logs/experiments/
```

Do not commit ad-hoc large outputs unless they are documented step baselines.

## Manifest Fields

The Step 12 artifact manifest records:

```text
path
kind
extension
size_bytes
size_mb
is_large
```

The large-file threshold is:

```text
size_mb >= 5.0
```

The manifest is an audit aid. It does not delete or compress artifacts.

## Geometry Outputs

Step 13 adds small committed geometry baselines:

- particle clouds under `outputs/step13_*`
- voxel masks such as `geometry_occupancy.npy`
- projection diagnostics such as `solid_phi.npy`
- driver mode diagnostics for `squid_proxy`

Geometry particle clouds, voxel masks, and VTK files can grow quickly. Small Step 13 baseline outputs may be committed because they are part of the reproducibility contract. Large ad-hoc geometry experiments should go under `outputs/experiments/` or `outputs/scratch/`.

## Step 25 Candidate Intake Artifacts

Step 25 commits small descriptor, CSV, JSON, Markdown, and log artifacts only. Step 25 does not write `.vtr` outputs or particle `.npy` outputs.

Step 25 is controlled real geometry intake, not real squid validation.
Step 25 performs geometry QA, normalization, fingerprinting, sampling reproducibility, and projection-only smoke diagnostics.
Candidate intake does not perform production mesh repair or automatic remeshing.
Raw large real geometry files and scan data are not committed.

The `data/real_geometry_candidates/` directory is ignored by default except for `README.md`, `.gitkeep`, and `*_descriptor.json`. Local raw real geometry, scan data, private anatomy, and proprietary CAD should stay out of committed artifacts.

## Step 26 Short Feasibility Artifacts

Step 26 commits small config, CSV, JSON, NPZ, Markdown, and log artifacts only. Step 26 does not write `.vtr` outputs or particle `.npy` outputs.

Step 26 is controlled real geometry projection-only and short driver feasibility.
Step 26 is not real squid validation.
Step 26 does not implement squid actuation.
Step 26 does not implement squid swimming.
Step 26 does not implement new FSI physics.
Step 26 does not validate production sharp-interface FSI.

The Step 26 artifact manifest requires `large_file_count == 0`, no raw candidate large files, no scan data, no private absolute paths in committed outputs, and exactly 8 driver `geometry_quality_report.json` files.

## Step 27 64 Short Driver Artifacts

Step 27 commits small config, CSV, JSON, NPZ, Markdown, and log artifacts only. Step 27 does not write `.vtr` outputs or particle `.npy` outputs.

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

The Step 27 artifact manifest requires `large_file_count == 0`, no raw candidate large files, no scan data, no private absolute paths in committed outputs, and exactly 6 driver `geometry_quality_report.json` files.

## Step 28 Transfer Diagnostics Artifacts

Step 28 commits small config, CSV, JSON, NPZ, Markdown, and log artifacts only. Step 28 does not write `.vtr` outputs or particle `.npy` outputs.

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

The Step 28 artifact manifest requires `large_file_count == 0`, no raw candidate large files, no scan data, no private absolute paths in committed outputs, and exactly 4 driver `geometry_quality_report.json` files.

## Step 29 Stability Envelope Artifacts

Step 29 commits small config, CSV, JSON, NPZ, Markdown, and log artifacts only. Step 29 does not write `.vtr` outputs or particle `.npy` outputs.

Step 29 is controlled real geometry 64^3 short-window stability envelope.
Step 29 extends Step 28 transfer diagnostics conservatively.
Step 29 is not real squid validation.
Step 29 does not implement squid actuation.
Step 29 does not implement squid swimming.
Step 29 does not implement new FSI physics.
Step 29 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

The Step 29 artifact manifest requires `large_file_count == 0`, no raw candidate large files, no scan data, no private absolute paths in committed outputs, and exactly 4 driver `geometry_quality_report.json` files.

## Step 30 Squid Proxy Region Geometry Artifacts

Step 30 commits small config, CSV, JSON, Markdown, and log artifacts only. Step 30 does not write `.vtr` outputs or particle `.npy` outputs.

Step 30 is controlled squid proxy region geometry.
Step 30 defines squid-like region semantics only.
Step 30 is not real squid validation.
Step 30 does not implement squid actuation.
Step 30 does not implement squid swimming.
Step 30 does not implement mantle contraction.
Step 30 does not implement funnel actuation.
Step 30 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

The Step 30 artifact manifest requires `large_file_count == 0`, Step 30 total size below 5 MB, repository total size below 180 MB, no raw candidate large files, no scan data, no private absolute paths, no Step 30 `.vtr`, and no Step 30 particle `.npy` files.

## Step 31 Squid Proxy Region Static Driver Artifacts

Step 31 commits small config, CSV, JSON, NPZ, Markdown, and log artifacts only. Step 31 does not write `.vtr` outputs or particle `.npy` outputs.

Step 31 is controlled squid proxy region projection and static driver smoke.
Step 31 uses static squid proxy region semantics only.
Step 31 is not real squid validation.
Step 31 does not implement squid actuation.
Step 31 does not implement squid swimming.
Step 31 does not implement mantle contraction.
Step 31 does not implement funnel actuation.
Step 31 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

The Step 31 artifact manifest requires `large_file_count == 0`, Step 31 total size below 10 MB, repository total size below 185 MB, no raw candidate large files, no scan data, no private absolute paths, no Step 31 `.vtr`, and no Step 31 particle `.npy` files.
