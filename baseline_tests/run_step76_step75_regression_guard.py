from step76_common import run_named_audit
from src.mpm_lbm.evidence.step76_regression_guard import build_step76_step75_regression_guard


FIELDS = ["check", "artifact_path", "summary_key", "actual", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step76_step75_regression_guard,
        "outputs/step76_step75_regression_guard",
        "logs/step76_step75_regression_guard.log",
        "step76_step75_regression_guard_pass",
        "[OK] Step76 Step75 regression guard finished",
        "step75_regression_guard",
        FIELDS,
    )
