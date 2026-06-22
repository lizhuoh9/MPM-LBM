from step80_common import run_named_audit
from src.mpm_lbm.evidence.step80_runtime_geometry_diagnostic_only_activation_guard import (
    build_step80_runtime_geometry_diagnostic_only_activation_guard,
)


FIELDS = ["row_name", "check", "actual", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step80_runtime_geometry_diagnostic_only_activation_guard,
        "outputs/step80_activation_guard",
        "logs/step80_activation_guard.log",
        "step80_runtime_geometry_diagnostic_only_activation_guard_pass",
        "[OK] Step80 activation guard finished",
        "activation_guard",
        FIELDS,
    )
