import os

from step98_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step98_step94_regression_guard import build_step98_step94_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step98_step94_regression_guard,
        "outputs/step98_step94_regression_guard",
        "logs/step98_step94_regression_guard.log",
        "step98_step94_regression_guard_pass",
        "[OK] Step98 Step94 regression guard finished",
        "step94_regression_guard",
    )


if __name__ == "__main__":
    main()
