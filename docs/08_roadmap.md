# Roadmap

The next steps should preserve the existing regression baselines and mode matrix before adding new physics.

## Current Status

Step 20 is completed as the first mesh/voxel geometry import pipeline. The next implementation step should validate imported geometry at larger scale before any real squid geometry or final strict sharp-interface FSI claims.

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
| Step 21 | proposed: imported geometry scale validation | carry Step 20 imported voxel/mesh cases to larger windows before real geometry |
| Future | stricter sharp-interface momentum accounting and real geometry ingestion | Strict link-area momentum-conserving coupling remains future work. |

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
```

New physics should be added behind explicit modes or new configs, not by silently changing validated behavior.

Step 16 does not add new FSI physics. The 64^3 moving_boundary row is a feasibility baseline. squid_proxy is procedural and not real squid validation.

Step 17 adds diagnostic-only direction-wise and link-area proxy accounting. The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. These are diagnostic proxy policies, not final surface-area reconstruction.

Step 18 adds an opt-in experimental link-area reaction transfer mode. The default moving_boundary reaction transfer remains engineering. The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. The experimental transfer uses a bounded global area_scale from Step 17 link-area proxy accounting. This is not final strict momentum-conserving sharp-interface FSI. squid_proxy is procedural and not real squid validation.

Step 19 validates the opt-in link_area_experimental transfer over longer windows and 64^3 feasibility. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. LinkAreaMovingBoundaryCoupler3D formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. The link-area transfer remains experimental and uses a bounded global area_scale. This is not final strict momentum-conserving sharp-interface FSI. squid_proxy is procedural and not real squid validation.

Step 20 adds a small synthetic mesh and voxel geometry import pipeline. Step 20 is a geometry-ingestion scaffold, not real squid validation. Imported geometry supports voxel and mesh inputs through GeometryConfig and GeometrySampler3D. The Step 20 mesh path is limited to small synthetic fixtures and is not production mesh repair. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
