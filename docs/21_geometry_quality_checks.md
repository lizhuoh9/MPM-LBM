# Geometry Quality Checks

Step 22 adds diagnostic quality checks for imported mesh and voxel geometry.
Step 22 is a geometry QA and import robustness layer, not real squid validation.

The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 22 mesh path is not production mesh repair or automatic remeshing.

## Scope

Step 22 adds CPU/NumPy diagnostics around the existing Step 20/21 imported geometry path. It does not add new FSI physics, change solver formulas, change coupling formulas, add squid actuation, validate squid swimming, add two-phase flow, add contact angle physics, add sparse storage, or edit `external/taichi_LBM3D`.

The quality layer is intended to catch obvious fixture and import mistakes before a geometry is sampled into MPM particles or projected to the LBM grid. It reports problems; it does not repair meshes, remesh inputs, or convert a bad geometry into a valid one.

## APIs

Step 22 adds:

- `src/mesh_quality.py`: `analyze_mesh(vertices, faces, eps=1.0e-12)`.
- `src/voxel_quality.py`: `analyze_voxel_occupancy(occupancy, metadata=None)`.
- `src/geometry_quality.py`: `analyze_geometry_config(config)` and `GeometryQualityGate`.

`GeometryConfig` and `FSIDriverConfig` now include:

```text
quality_check_enabled: bool = False
quality_check_strict: bool = False
quality_report_path: Optional[str] = None
```

The defaults preserve prior Step 20 and Step 21 behavior. When the driver quality check is enabled, `FSIDriver3D` writes `geometry_quality_report.json` before imported-geometry sampling. When strict mode is enabled and the gate fails, the driver raises a clear `ValueError`.

## Mesh Diagnostics

Mesh quality reports include:

- vertex and face counts;
- finite vertex and face-index validity flags;
- duplicate vertex count;
- degenerate and zero-area face counts;
- boundary and non-manifold edge counts;
- watertightness proxy;
- surface area;
- signed and absolute volume proxies;
- Euler characteristic;
- diagnostic notes.

Signed volume, watertightness, and edge counts are diagnostic proxies. They are useful for small synthetic fixtures, but they are not a production mesh repair pipeline.

## Voxel Diagnostics

Voxel quality reports include:

- occupancy shape;
- occupied count and occupied fraction;
- empty occupancy flag;
- occupied bounding box;
- domain-boundary contact flag;
- 6-neighbor connected component count;
- largest component size and fraction;
- surface and interior voxel counts.

Empty voxel occupancy is handled deterministically and can be used as an expected-failure fixture.

## Quality Gate

`GeometryQualityGate(strict=False)` reports warnings for suspicious geometry while allowing the diagnostic run to continue. `GeometryQualityGate(strict=True)` rejects the required bad fixtures:

| fixture | expected strict result | reason |
| ------- | ---------------------- | ------ |
| `bad_nonwatertight.obj` | fail | boundary edges |
| `bad_degenerate.obj` | fail | degenerate face, boundary edges, nonmanifold edge |
| `bad_empty_voxel.npy` | fail | empty voxel occupancy |

Good Step 22 imported geometry driver smoke cases use non-strict quality checks, write reports, and then continue through the existing FSI driver paths.

## Baselines

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_mesh_quality_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_voxel_quality_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_bad_geometry_failure_checks.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_sampling_resolution_sensitivity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_driver_quality_gate_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_artifact_manifest.py
```

Primary outputs:

- `outputs/step22_mesh_quality_sanity/mesh_quality_results.csv`
- `outputs/step22_voxel_quality_sanity/voxel_quality_results.csv`
- `outputs/step22_bad_geometry_failure_checks/bad_geometry_results.csv`
- `outputs/step22_sampling_resolution_sensitivity/resolution_sensitivity.csv`
- `outputs/step22_driver_quality_gate_smoke/quality_gate_driver_results.csv`
- `outputs/step22_artifact_manifest/artifact_summary.json`

## Results

| case | geometry_type | quality_kind | pass | severity | key result |
| ---- | ------------- | ------------ | ---- | -------- | ---------- |
| mesh_cube | mesh | mesh | true | ok | 8 vertices, 12 faces, 0 boundary edges |
| mesh_ellipsoid | mesh | mesh | true | ok | 114 vertices, 224 faces, 0 boundary edges |
| voxel_sphere | voxel | voxel | true | ok | 3016 occupied voxels, 1 connected component |
| bad_nonwatertight | mesh | mesh | false | error | strict gate rejects boundary edges |
| bad_degenerate | mesh | mesh | false | error | strict gate rejects degenerate and nonmanifold geometry |
| bad_empty_voxel | voxel | voxel | false | error | strict gate rejects empty occupancy |

The driver quality gate smoke keeps output small with VTK and particle export disabled. The penalty voxel row and moving-boundary mesh row both finish with stable density and positive MPM volume.

## Step 23 Quality-Gated Scale Validation

Step 23 repeats imported geometry scale validation with quality_check_enabled=true.
Step 23 uses quality_check_strict=false for scale validation.
Step 23 is quality-gated synthetic imported geometry validation, not real squid validation.

The default quality_check_enabled remains false. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 23 mesh path is not production mesh repair or automatic remeshing.

Step 23 uses the Step 22 non-strict quality gate across the Step 21 48^3 and 64^3 imported geometry scale matrix, aggregates all quality reports, and compares Step 21 ungated rows with Step 23 quality-gated rows.

## Limitations

- no real squid geometry validation;
- no squid actuation;
- no swimming validation;
- no production mesh repair;
- no automatic remeshing;
- no two-phase flow;
- no contact angle physics;
- no sparse storage;
- no new FSI physics.
