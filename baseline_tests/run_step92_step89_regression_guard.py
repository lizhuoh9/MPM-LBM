from step92_common import run_named_audit
from src.mpm_lbm.evidence.step92_step89_regression_guard import build_step92_step89_regression_guard


def main():
    run_named_audit(
        build_step92_step89_regression_guard,
        "outputs/step92_step89_regression_guard",
        "logs/step92_step89_regression_guard.log",
        "step92_step89_regression_guard_pass",
        "[OK] Step92 Step89 regression guard finished",
        "step89_regression_guard",
    )


if __name__ == "__main__":
    main()
