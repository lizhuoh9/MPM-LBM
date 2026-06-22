from step87_common import run_named_audit
from src.mpm_lbm.evidence.step87_step82_regression_guard import build_step87_step82_regression_guard


def main():
    run_named_audit(
        build_step87_step82_regression_guard,
        "outputs/step87_step82_regression_guard",
        "logs/step87_step82_regression_guard.log",
        "step87_step82_regression_guard_pass",
        "[OK] Step87 Step82 regression guard finished",
        "step82_regression_guard",
    )


if __name__ == "__main__":
    main()
