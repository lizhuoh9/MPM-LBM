from step79_common import run_named_audit
from src.mpm_lbm.evidence.step79_step78_regression_guard import build_step79_step78_regression_guard


FIELDS = ["artifact_path", "summary_key", "check", "actual", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step79_step78_regression_guard,
        "outputs/step79_step78_regression_guard",
        "logs/step79_step78_regression_guard.log",
        "step79_step78_regression_guard_pass",
        "[OK] Step79 Step78 regression guard finished",
        "step78_regression_guard",
        FIELDS,
    )
