import os

from step68_common import ROOT, run_audit
from src.mpm_lbm.evidence.step68_regression_guard import build_step68_step63_67_regression_guard


def main():
    os.chdir(ROOT)
    run_audit(build_step68_step63_67_regression_guard, "outputs/step68_step63_67_regression_guard", "logs/step68_step63_67_regression_guard.log", "step68_regression_guard_pass", "[OK] Step 68 Step63-67 regression guard finished")


if __name__ == "__main__":
    main()
