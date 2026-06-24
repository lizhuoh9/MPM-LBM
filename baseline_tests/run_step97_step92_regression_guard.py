import os

from step97_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step97_step92_regression_guard import build_step97_step92_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step97_step92_regression_guard,
        "outputs/step97_step92_regression_guard",
        "logs/step97_step92_regression_guard.log",
        "step97_step92_regression_guard_pass",
        "[OK] Step97 Step92 regression guard finished",
        "step92_regression_guard",
    )


if __name__ == "__main__":
    main()
