import os

from step96_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step96_step92_regression_guard import build_step96_step92_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step96_step92_regression_guard,
        "outputs/step96_step92_regression_guard",
        "logs/step96_step92_regression_guard.log",
        "step96_step92_regression_guard_pass",
        "[OK] Step96 Step92 regression guard finished",
        "step92_regression_guard",
    )


if __name__ == "__main__":
    main()
