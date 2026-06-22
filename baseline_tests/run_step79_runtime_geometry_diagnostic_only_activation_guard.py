from step79_common import run_named_audit
from src.mpm_lbm.evidence.step79_runtime_geometry_diagnostic_only_activation_guard import (
    build_step79_runtime_geometry_diagnostic_only_activation_guard,
)


FIELDS = ["row_name", "check", "actual", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step79_runtime_geometry_diagnostic_only_activation_guard,
        "outputs/step79_runtime_geometry_diagnostic_only_activation_guard",
        "logs/step79_runtime_geometry_diagnostic_only_activation_guard.log",
        "step79_runtime_geometry_diagnostic_only_activation_guard_pass",
        "[OK] Step79 runtime geometry diagnostic-only activation guard finished",
        "runtime_geometry_diagnostic_only_activation_guard",
        FIELDS,
    )
