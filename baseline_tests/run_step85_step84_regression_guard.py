from step85_common import run_named_audit
from src.mpm_lbm.evidence.step85_step84_regression_guard import build_step85_step84_regression_guard


def main():
    run_named_audit(
        build_step85_step84_regression_guard,
        "outputs/step85_step84_regression_guard",
        "logs/step85_step84_regression_guard.log",
        "step85_step84_regression_guard_pass",
        "[OK] Step85 Step84 regression guard finished",
        "step84_regression_guard",
    )


if __name__ == "__main__":
    main()
