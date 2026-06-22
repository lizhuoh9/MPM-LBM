from step80_common import run_named_audit
from src.mpm_lbm.evidence.step80_step79_regression_guard import build_step80_step79_regression_guard


FIELDS = ["artifact_path", "summary_key", "check", "actual", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step80_step79_regression_guard,
        "outputs/step80_step79_regression_guard",
        "logs/step80_step79_regression_guard.log",
        "step80_step79_regression_guard_pass",
        "[OK] Step80 Step79 regression guard finished",
        "step79_regression_guard",
        FIELDS,
    )
