import os

from step69_common import ROOT, run_audit
from src.mpm_lbm.evidence.src_init_export_refresh_audit import build_step69_src_init_export_audit


def main():
    os.chdir(ROOT)
    run_audit(build_step69_src_init_export_audit, "outputs/step69_src_init_export_audit", "logs/step69_src_init_export_audit.log", "src_init_export_audit_pass", "[OK] Step 69 src init export audit finished")


if __name__ == "__main__":
    main()
