from step77_common import run_named_audit
from src.mpm_lbm.evidence.step77_regression_guard import build_step77_step76_regression_guard


FIELDS = ["check", "artifact_path", "summary_key", "actual", "expected", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step77_step76_regression_guard,
        "outputs/step77_step76_regression_guard",
        "logs/step77_step76_regression_guard.log",
        "step77_step76_regression_guard_pass",
        "[OK] Step77 Step76 regression guard finished",
        "step76_regression_guard",
        FIELDS,
    )
