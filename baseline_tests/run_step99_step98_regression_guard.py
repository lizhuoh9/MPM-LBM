import os

from step99_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step99_step98_regression_guard import build_step99_step98_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step99_step98_regression_guard,
        "outputs/step99_step98_regression_guard",
        "logs/step99_step98_regression_guard.log",
        "step99_step98_regression_guard_pass",
        "[OK] Step99 Step98 regression guard finished",
        "step98_regression_guard",
    )


if __name__ == "__main__":
    main()
