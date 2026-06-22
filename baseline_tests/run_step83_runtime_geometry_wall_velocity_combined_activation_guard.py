import os

from step83_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step83_runtime_geometry_wall_velocity_combined_activation_guard import (
    build_step83_runtime_geometry_wall_velocity_combined_activation_guard,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step83_runtime_geometry_wall_velocity_combined_activation_guard,
        "outputs/step83_runtime_geometry_wall_velocity_combined_activation_guard",
        "logs/step83_runtime_geometry_wall_velocity_combined_activation_guard.log",
        "step83_runtime_geometry_wall_velocity_combined_activation_guard_pass",
        "[OK] Step83 runtime geometry wall velocity combined activation guard finished",
        "runtime_geometry_wall_velocity_combined_activation_guard",
    )


if __name__ == "__main__":
    main()
