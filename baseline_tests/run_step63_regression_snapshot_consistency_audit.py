import os

from step63_67_common import ROOT, run_audit
from src.mpm_lbm.evidence.regression_snapshot_consistency_audit import build_regression_snapshot_consistency_audit


def main():
    os.chdir(ROOT)
    run_audit(build_regression_snapshot_consistency_audit, "outputs/step63_regression_snapshot_consistency_audit", "logs/step63_regression_snapshot_consistency_audit.log", "regression_snapshot_consistency_pass", "[OK] Step 63 regression snapshot consistency audit finished", None)


if __name__ == "__main__":
    main()
