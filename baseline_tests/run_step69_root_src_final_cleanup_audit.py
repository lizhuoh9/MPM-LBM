import os

from step69_common import ROOT, run_audit
from src.mpm_lbm.evidence.root_src_final_cleanup_audit import build_step69_root_src_final_cleanup_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step69_root_src_final_cleanup_audit, "outputs/step69_root_src_final_cleanup_audit", "logs/step69_root_src_final_cleanup_audit.log", "step69_root_src_final_cleanup_audit_pass", "[OK] Step 69 root src final cleanup audit finished")


if __name__ == "__main__":
    main()
