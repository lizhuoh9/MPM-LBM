from step75_common import run_named_audit
from src.mpm_lbm.evidence.step75_regression_guard import build_step75_step74_regression_guard


if __name__ == "__main__":
    run_named_audit(
        build_step75_step74_regression_guard,
        "outputs/step75_step74_regression_guard",
        "logs/step75_step74_regression_guard.log",
        "step75_step74_regression_guard_pass",
        "[OK] Step 75 Step74 regression guard finished",
        "step74_regression_guard",
    )
