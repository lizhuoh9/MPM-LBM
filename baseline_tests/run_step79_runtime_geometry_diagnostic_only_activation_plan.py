from step79_common import run_named_audit
from src.mpm_lbm.evidence.step79_runtime_geometry_diagnostic_only_activation_plan import (
    build_step79_runtime_geometry_diagnostic_only_activation_plan,
)


FIELDS = ["row_name", "check", "actual", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step79_runtime_geometry_diagnostic_only_activation_plan,
        "outputs/step79_runtime_geometry_diagnostic_only_activation_plan",
        "logs/step79_runtime_geometry_diagnostic_only_activation_plan.log",
        "step79_runtime_geometry_diagnostic_only_activation_plan_pass",
        "[OK] Step79 runtime geometry diagnostic-only activation plan finished",
        "runtime_geometry_diagnostic_only_activation_plan",
        FIELDS,
    )
