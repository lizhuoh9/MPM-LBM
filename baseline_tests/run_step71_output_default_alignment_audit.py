import os

from step71_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.output_default_alignment_audit import build_step71_output_default_alignment_audit


def main():
    os.chdir(ROOT)
    run_named_audit(build_step71_output_default_alignment_audit, "outputs/step71_output_default_alignment_audit", "logs/step71_output_default_alignment_audit.log", "output_default_alignment_audit_pass", "[OK] Step 71 output default alignment audit finished", "output_default_alignment")


if __name__ == "__main__":
    main()
