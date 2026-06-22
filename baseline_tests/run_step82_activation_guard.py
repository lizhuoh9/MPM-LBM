import os

from step82_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step82_wall_velocity_solid_vel_activation_guard import (
    build_step82_wall_velocity_solid_vel_activation_guard,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step82_wall_velocity_solid_vel_activation_guard,
        "outputs/step82_activation_guard",
        "logs/step82_activation_guard.log",
        "step82_activation_guard_pass",
        "[OK] Step82 activation guard finished",
        "activation_guard",
    )


if __name__ == "__main__":
    main()
