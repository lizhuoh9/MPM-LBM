# Roadmap

The next steps should preserve the existing regression baselines and mode matrix before adding new physics.

## Current Status

Step 27 is controlled real geometry 64^3 short driver feasibility. It preserves Step 25 intake evidence and Step 26 projection/short-driver evidence while adding a six-row 64^3 coupling subset before any actuation, swimming, or production sharp-interface FSI claims.

## Proposed Steps

| step | focus | boundary |
| ---- | ----- | -------- |
| Step 12 | completed: performance and memory cleanup | preserve Step 10 mode matrix |
| Step 13 | completed: geometry ingestion / squid proxy geometry | squid_proxy is procedural and not real squid validation |
| Step 14 | completed: larger-grid validation | 48^3 engineering scale baseline and 64^3 feasibility checks |
| Step 15 | completed: moving-boundary reaction calibration and sharper momentum accounting | keep engineering-scale MVP path available for comparison |
| Step 16 | completed: long-run validation and 64^3 moving_boundary feasibility | preserve Step 10 mode matrix, Step 13 geometry contracts, and Step 14 scale baselines |
| Step 17 | completed: diagnostic-only direction-wise and link-area proxy accounting | no new FSI mode and no solver physics change |
| Step 18 | completed: experimental link-area reaction transfer mode | opt-in only; do not replace the engineering-scale moving_boundary path |
| Step 19 | completed: experimental link-area transfer long-run and 64^3 feasibility | preserve Step 18 comparison evidence before increasing scale |
| Step 20 | completed: mesh/voxel geometry import pipeline | synthetic fixtures only; do not claim real squid validation |
| Step 21 | completed: imported geometry scale validation | synthetic fixtures only; 48^3 mode validation and 64^3 feasibility before real geometry |
| Step 22 | completed: geometry quality checks and import robustness | diagnostic QA only; no production mesh repair or automatic remeshing |
| Step 23 | completed: quality-gated imported geometry scale validation | non-strict quality reports for synthetic scale baselines |
| Step 24 | completed: strict quality-gated imported geometry long-run validation | strict gate for selected synthetic imported geometry rows only |
| Step 25 | controlled real geometry intake | manifest, fingerprinting, QA, normalization, deterministic sampling, and projection-only smoke only |
| Step 26 | controlled real geometry projection-only and short driver feasibility | no squid actuation, swimming, production sharp-interface FSI, or final readiness claim |
| Step 27 | controlled real geometry 64^3 short driver feasibility | six coupling rows only; no squid actuation, swimming, production sharp-interface FSI, or final readiness claim |

## Regression Rule

Every future step should keep these checks available:

```text
pytest -q
Step 10 penalty driver baseline
Step 10 moving_boundary driver baseline
Step 10 mode matrix baseline
Step 10 performance profile baseline
Step 12 resource and artifact checks
Step 13 geometry ingestion contracts
Step 14 larger-grid validation contracts
Step 15 moving-boundary calibration contracts
Step 16 long-run validation contracts
Step 17 link-area momentum accounting contracts
Step 18 experimental link-area transfer contracts
Step 19 link-area long-run validation contracts
Step 20 geometry import contracts
Step 21 imported geometry scale validation contracts
Step 22 geometry quality and import robustness contracts
Step 23 quality-gated imported geometry scale validation contracts
Step 24 strict quality-gated imported geometry long-run contracts
Step 25 controlled real geometry intake contracts
Step 26 controlled real geometry projection-only and short driver feasibility contracts
Step 27 controlled real geometry 64^3 short driver feasibility contracts
```

New physics should be added behind explicit modes or new configs, not by silently changing validated behavior.

Step 16 does not add new FSI physics. The 64^3 moving_boundary row is a feasibility baseline. squid_proxy is procedural and not real squid validation.

Step 17 adds diagnostic-only direction-wise and link-area proxy accounting. The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. These are diagnostic proxy policies, not final surface-area reconstruction.

Step 18 adds an opt-in experimental link-area reaction transfer mode. The default moving_boundary reaction transfer remains engineering. The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. The experimental transfer uses a bounded global area_scale from Step 17 link-area proxy accounting. This is not final strict momentum-conserving sharp-interface FSI. squid_proxy is procedural and not real squid validation.

Step 19 validates the opt-in link_area_experimental transfer over longer windows and 64^3 feasibility. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. LinkAreaMovingBoundaryCoupler3D formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. The link-area transfer remains experimental and uses a bounded global area_scale. This is not final strict momentum-conserving sharp-interface FSI. squid_proxy is procedural and not real squid validation.

Step 20 adds a small synthetic mesh and voxel geometry import pipeline. Step 20 is a geometry-ingestion scaffold, not real squid validation. Imported geometry supports voxel and mesh inputs through GeometryConfig and GeometrySampler3D. The Step 20 mesh path is limited to small synthetic fixtures and is not production mesh repair. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 21 carries Step 20 synthetic imported voxel and mesh geometries to 48^3 mode validation and 64^3 feasibility. Step 21 is synthetic imported geometry scale validation, not real squid validation. Imported geometry remains limited to small synthetic voxel and mesh fixtures. The Step 21 mesh path is not production mesh repair. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 22 adds diagnostic quality checks for imported mesh and voxel geometry. Step 22 is a geometry QA and import robustness layer, not real squid validation. Imported geometry remains limited to small synthetic voxel and mesh fixtures. The Step 22 mesh path is not production mesh repair or automatic remeshing. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 23 repeats imported geometry scale validation with quality_check_enabled=true. Step 23 uses quality_check_strict=false for scale validation. Step 23 is quality-gated synthetic imported geometry validation, not real squid validation. The default quality_check_enabled remains false. Imported geometry remains limited to small synthetic voxel and mesh fixtures. The Step 23 mesh path is not production mesh repair or automatic remeshing. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 24 runs strict quality-gated synthetic imported geometry long-run validation. Step 24 uses quality_check_enabled=true and quality_check_strict=true for selected imported geometry rows. Step 24 is not real squid validation. Step 24 does not implement new FSI physics. The default quality_check_enabled remains false. The default quality_check_strict remains false. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged. Imported geometry remains limited to small synthetic voxel and mesh fixtures. The Step 24 mesh path is not production mesh repair or automatic remeshing. Step 25 should be a controlled real geometry intake contract, starting with geometry QA, normalization, and sampling reproducibility only.

Step 25 is controlled real geometry intake, not real squid validation. Step 25 performs geometry QA, normalization, fingerprinting, sampling reproducibility, and projection-only smoke diagnostics. Step 25 does not implement squid swimming. Step 25 does not implement squid actuation. Step 25 does not implement new FSI physics. Step 25 does not validate production sharp-interface FSI. The default quality_check_enabled remains false. The default quality_check_strict remains false. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged. Candidate intake does not perform production mesh repair or automatic remeshing. Raw large real geometry files and scan data are not committed.

Step 26 is controlled real geometry projection-only and short driver feasibility. Step 26 is not real squid validation. Step 26 does not implement squid actuation. Step 26 does not implement squid swimming. Step 26 does not implement new FSI physics. Step 26 does not validate production sharp-interface FSI. The default quality_check_enabled remains false. The default quality_check_strict remains false. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 27 is controlled real geometry 64^3 short driver feasibility. Step 27 is not real squid validation. Step 27 does not implement squid actuation. Step 27 does not implement squid swimming. Step 27 does not implement new FSI physics. Step 27 does not validate production sharp-interface FSI. The default quality_check_enabled remains false. The default quality_check_strict remains false. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
