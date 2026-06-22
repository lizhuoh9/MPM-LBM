import os

from step73_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step73_regression_guard import build_step73_step72_regression_guard


def main():
    os.chdir(ROOT)
    run_named_audit(build_step73_step72_regression_guard, "outputs/step73_step72_regression_guard", "logs/step73_step72_regression_guard.log", "step73_step72_regression_guard_pass", "[OK] Step 73 Step72 regression guard finished", "step72_regression_guard")


if __name__ == "__main__":
    main()
