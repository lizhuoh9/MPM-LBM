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
