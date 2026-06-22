# Config Schema Freeze

Step70 records schema snapshots and hashes for required config classes.

```text
config_schema_freeze_audit_pass = true
schema_row_count = 14
required_config_class_count = 14
missing_config_class_count = 0
schema_hash_count = 14
from_json_available_count = 11
```

Snapshot artifacts:

```text
outputs/step70_config_schema_freeze_audit/config_schema_freeze.json
outputs/step70_config_schema_freeze_audit/config_schema_freeze.csv
```

Step71 supersedes one field-default part of the Step70 snapshot:

```text
changed_schema_classes = ["FSIDriverConfig"]
FSIDriverConfig.write_vtk: True -> False
FSIDriverConfig.write_particles: True -> False
```

This is an output-persistence default change only. Step71 does not change
solver formulas, LBM tau numerical behavior, MPM behavior, projection, runtime
geometry activation, wall velocity activation, or physical validation status.
The Step71 schema delta artifact is:

```text
outputs/step71_config_schema_delta_audit/config_schema_delta.json
```

Frozen classes:

```text
FSIDriverConfig
UnifiedSimConfig
LBMConfig
MPMConfig
GeometryConfig
BoundaryMotionInterfaceConfig
GeometryMotionInterfaceConfig
WallVelocityApplicationConfig
WallVelocityFieldConfig
RuntimeGeometryProjectionIntegrationConfig
GeometryDisplacementConfig
SquidProxyRegionConfig
SquidKinematicsScheduleConfig
SquidMotionMappingConfig
```
