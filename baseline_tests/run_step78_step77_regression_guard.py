from step78_common import run_named_audit
from src.mpm_lbm.evidence.step78_regression_guard import build_step78_step77_regression_guard


FIELDS = ["check", "artifact_path", "summary_key", "actual", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step78_step77_regression_guard,
        "outputs/step78_step77_regression_guard",
        "logs/step78_step77_regression_guard.log",
        "step78_step77_regression_guard_pass",
        "[OK] Step78 Step77 regression guard finished",
        "step77_regression_guard",
        FIELDS,
    )
