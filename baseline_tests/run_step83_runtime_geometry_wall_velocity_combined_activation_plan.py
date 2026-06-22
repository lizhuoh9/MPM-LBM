import os

from step83_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step83_runtime_geometry_wall_velocity_combined_activation_plan import (
    build_step83_runtime_geometry_wall_velocity_combined_activation_plan,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step83_runtime_geometry_wall_velocity_combined_activation_plan,
        "outputs/step83_runtime_geometry_wall_velocity_combined_activation_plan",
        "logs/step83_runtime_geometry_wall_velocity_combined_activation_plan.log",
        "step83_runtime_geometry_wall_velocity_combined_activation_plan_pass",
        "[OK] Step83 runtime geometry wall velocity combined activation plan finished",
        "runtime_geometry_wall_velocity_combined_activation_plan",
    )


if __name__ == "__main__":
    main()
