import os

from step70_common import ROOT, run_audit
from src.mpm_lbm.evidence.report_consistency_freeze_audit import build_step70_report_consistency_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step70_report_consistency_audit, "outputs/step70_report_consistency_audit", "logs/step70_report_consistency_audit.log", "report_consistency_freeze_audit_pass", "[OK] Step 70 report consistency audit finished")


if __name__ == "__main__":
    main()
