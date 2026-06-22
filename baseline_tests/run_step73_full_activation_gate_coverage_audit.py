import os

from step73_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.full_activation_gate_coverage_audit import build_step73_full_activation_gate_coverage_audit


def main():
    os.chdir(ROOT)
    run_named_audit(build_step73_full_activation_gate_coverage_audit, "outputs/step73_full_activation_gate_coverage_audit", "logs/step73_full_activation_gate_coverage_audit.log", "full_activation_gate_coverage_audit_pass", "[OK] Step 73 full activation gate coverage audit finished", "full_activation_gate_coverage")


if __name__ == "__main__":
    main()
