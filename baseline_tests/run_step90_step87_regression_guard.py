from step90_common import run_named_audit
from src.mpm_lbm.evidence.step90_step87_regression_guard import build_step90_step87_regression_guard


def main():
    run_named_audit(
        build_step90_step87_regression_guard,
        "outputs/step90_step87_regression_guard",
        "logs/step90_step87_regression_guard.log",
        "step90_step87_regression_guard_pass",
        "[OK] Step90 Step87 regression guard finished",
        "step87_regression_guard",
    )


if __name__ == "__main__":
    main()
