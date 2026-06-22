import os

from step81_common import ROOT, run_named_audit

from src.mpm_lbm.evidence.step81_step80_regression_guard import build_step81_step80_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step81_step80_regression_guard,
        "outputs/step81_step80_regression_guard",
        "logs/step81_step80_regression_guard.log",
        "step81_step80_regression_guard_pass",
        "[OK] Step81 Step80 regression guard finished",
        "step80_regression_guard",
    )


if __name__ == "__main__":
    main()
