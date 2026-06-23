from step91_common import run_named_audit
from src.mpm_lbm.evidence.step91_step90_regression_guard import build_step91_step90_regression_guard


def main():
    run_named_audit(
        build_step91_step90_regression_guard,
        "outputs/step91_step90_regression_guard",
        "logs/step91_step90_regression_guard.log",
        "step91_step90_regression_guard_pass",
        "[OK] Step91 Step90 regression guard finished",
        "step90_regression_guard",
    )


if __name__ == "__main__":
    main()
