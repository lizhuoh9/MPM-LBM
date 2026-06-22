import os

from step73_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.wall_velocity_config_schema_audit import build_step73_wall_velocity_config_schema_audit


def main():
    os.chdir(ROOT)
    run_named_audit(build_step73_wall_velocity_config_schema_audit, "outputs/step73_wall_velocity_config_schema_audit", "logs/step73_wall_velocity_config_schema_audit.log", "wall_velocity_config_schema_audit_pass", "[OK] Step 73 wall velocity config schema audit finished", "wall_velocity_config_schema")


if __name__ == "__main__":
    main()
