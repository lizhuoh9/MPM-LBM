# Step73 Wall Velocity Activation Readiness Audit

Step73 adds a readiness audit around the wall velocity activation surface. It
does not activate wall velocity, runtime geometry, combined runtime geometry plus
wall velocity, real geometry, squid simulation, larger-grid runs, VTR output, or
particle NPY output.

The audit checks:

- canonical wall velocity imports and public symbols;
- `WallVelocityFieldConfig` and `WallVelocityApplicationConfig` schema stability
  against the Step70 frozen schema rows;
- safe field-generation and application defaults;
- `FSIDriverConfig` wall velocity gates closed by default;
- rejection of invalid wall velocity gate combinations;
- application safety for the opt-in `solid_vel` path;
- output/no-simulation policy;
- all 10 Step70 activation gates remain closed;
- Step72 runtime geometry readiness remains green.

Evidence is generated under `outputs/step73_*` and logged under `logs/step73_*`.
This step records readiness for a later activation decision only.
