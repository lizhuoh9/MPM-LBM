import os

from step71_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.config_schema_delta_audit import build_step71_config_schema_delta_audit


def main():
    os.chdir(ROOT)
    run_named_audit(build_step71_config_schema_delta_audit, "outputs/step71_config_schema_delta_audit", "logs/step71_config_schema_delta_audit.log", "config_schema_delta_audit_pass", "[OK] Step 71 config schema delta audit finished", "config_schema_delta")


if __name__ == "__main__":
    main()
