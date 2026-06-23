from step89_common import run_named_audit
from src.mpm_lbm.evidence.step89_step87_regression_guard import build_step89_step87_regression_guard


def main():
    run_named_audit(
        build_step89_step87_regression_guard,
        "outputs/step89_step87_regression_guard",
        "logs/step89_step87_regression_guard.log",
        "step89_step87_regression_guard_pass",
        "[OK] Step89 Step87 regression guard finished",
        "step87_regression_guard",
    )


if __name__ == "__main__":
    main()
