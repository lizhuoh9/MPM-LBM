# Step72 Runtime Geometry Activation Readiness Audit

Step72 adds a readiness audit around the runtime geometry activation surface. It
does not activate runtime geometry, wall velocity, real geometry, squid proxy
simulation, VTR output, particle NPY output, or dense displacement output.

The audit checks:

- canonical runtime geometry imports and public symbols;
- `RuntimeGeometryProjectionIntegrationConfig` schema stability against the
  Step70 frozen schema row;
- safe runtime geometry mutation and persistence defaults;
- `FSIDriverConfig` runtime geometry gates closed by default;
- rejection of invalid runtime geometry gate combinations;
- state guard source invariants for non-persistent transient projection;
- Step70 activation gates remain closed;
- Step71 output defaults and tau convention evidence remain green.

Evidence is generated under `outputs/step72_*` and logged under `logs/step72_*`.
The Step72 artifact manifest keeps this as a small, committable, audit-only
change set.
