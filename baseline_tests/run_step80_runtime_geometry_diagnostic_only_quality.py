from step80_common import run_named_audit
from src.mpm_lbm.evidence.step80_runtime_geometry_diagnostic_only_quality_audit import (
    build_step80_runtime_geometry_diagnostic_only_quality_audit,
)


FIELDS = ["row_name", "check", "actual", "expected", "operator", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step80_runtime_geometry_diagnostic_only_quality_audit,
        "outputs/step80_runtime_geometry_diagnostic_only_quality",
        "logs/step80_runtime_geometry_diagnostic_only_quality.log",
        "step80_runtime_geometry_diagnostic_only_quality_pass",
        "[OK] Step80 runtime geometry diagnostic-only quality finished",
        "runtime_geometry_diagnostic_only_quality",
        FIELDS,
    )
