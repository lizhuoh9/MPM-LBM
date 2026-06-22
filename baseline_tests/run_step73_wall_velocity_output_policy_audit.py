import os

from step73_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.wall_velocity_output_policy_audit import build_step73_wall_velocity_output_policy_audit


def main():
    os.chdir(ROOT)
    run_named_audit(build_step73_wall_velocity_output_policy_audit, "outputs/step73_wall_velocity_output_policy_audit", "logs/step73_wall_velocity_output_policy_audit.log", "wall_velocity_output_policy_audit_pass", "[OK] Step 73 wall velocity output policy audit finished", "wall_velocity_output_policy")


if __name__ == "__main__":
    main()
