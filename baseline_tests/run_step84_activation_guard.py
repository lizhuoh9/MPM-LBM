import os

from step84_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step84_runtime_geometry_wall_velocity_combined_activation_guard import (
    build_step84_runtime_geometry_wall_velocity_combined_activation_guard,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step84_runtime_geometry_wall_velocity_combined_activation_guard,
        "outputs/step84_activation_guard",
        "logs/step84_activation_guard.log",
        "step84_activation_guard_pass",
        "[OK] Step84 activation guard finished",
        "activation_guard",
    )


if __name__ == "__main__":
    main()
