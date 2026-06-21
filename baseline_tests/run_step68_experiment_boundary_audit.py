import os

from step68_common import ROOT, run_audit
from src.mpm_lbm.evidence.experiment_boundary_audit import build_step68_experiment_boundary_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step68_experiment_boundary_audit, "outputs/step68_experiment_boundary_audit", "logs/step68_experiment_boundary_audit.log", "experiment_boundary_audit_pass", "[OK] Step 68 experiment boundary audit finished")


if __name__ == "__main__":
    main()
