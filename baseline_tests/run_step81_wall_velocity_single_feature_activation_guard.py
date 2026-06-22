import os

from step81_common import ROOT, run_named_audit

from src.mpm_lbm.evidence.step81_wall_velocity_single_feature_activation_guard import (
    build_step81_wall_velocity_single_feature_activation_guard,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step81_wall_velocity_single_feature_activation_guard,
        "outputs/step81_wall_velocity_single_feature_activation_guard",
        "logs/step81_wall_velocity_single_feature_activation_guard.log",
        "step81_wall_velocity_single_feature_activation_guard_pass",
        "[OK] Step81 wall velocity single-feature activation guard finished",
        "wall_velocity_single_feature_activation_guard",
    )


if __name__ == "__main__":
    main()
