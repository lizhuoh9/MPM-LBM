from step86_common import run_named_audit
from src.mpm_lbm.evidence.step86_step85_regression_guard import build_step86_step85_regression_guard


def main():
    run_named_audit(
        build_step86_step85_regression_guard,
        "outputs/step86_step85_regression_guard",
        "logs/step86_step85_regression_guard.log",
        "step86_step85_regression_guard_pass",
        "[OK] Step86 Step85 regression guard finished",
        "step85_regression_guard",
    )


if __name__ == "__main__":
    main()
