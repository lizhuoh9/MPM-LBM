import os

from step73_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.wall_velocity_readiness_audit import build_step73_wall_velocity_readiness_audit


def main():
    os.chdir(ROOT)
    run_named_audit(build_step73_wall_velocity_readiness_audit, "outputs/step73_wall_velocity_readiness_audit", "logs/step73_wall_velocity_readiness_audit.log", "wall_velocity_readiness_audit_pass", "[OK] Step 73 wall velocity readiness audit finished", "wall_velocity_readiness")


if __name__ == "__main__":
    main()
