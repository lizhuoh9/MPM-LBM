from step74_common import run_named_audit
from src.mpm_lbm.evidence.step74_regression_guard import build_step74_step73_regression_guard


if __name__ == "__main__":
    run_named_audit(
        build_step74_step73_regression_guard,
        "outputs/step74_step73_regression_guard",
        "logs/step74_step73_regression_guard.log",
        "step74_step73_regression_guard_pass",
        "[OK] Step 74 Step73 regression guard finished",
        "step73_regression_guard",
    )
