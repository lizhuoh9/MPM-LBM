import os

from step101_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step101_step99_regression_guard import build_step101_step99_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step101_step99_regression_guard,
        "outputs/step101_step99_regression_guard",
        "logs/step101_step99_regression_guard.log",
        "step101_step99_regression_guard_pass",
        "[OK] Step101 Step99 regression guard finished",
        "step99_regression_guard",
    )


if __name__ == "__main__":
    main()
