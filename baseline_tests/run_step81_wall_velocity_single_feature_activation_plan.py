import os

from step81_common import ROOT, run_named_audit

from src.mpm_lbm.evidence.step81_wall_velocity_single_feature_activation_plan import (
    build_step81_wall_velocity_single_feature_activation_plan,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step81_wall_velocity_single_feature_activation_plan,
        "outputs/step81_wall_velocity_single_feature_activation_plan",
        "logs/step81_wall_velocity_single_feature_activation_plan.log",
        "step81_wall_velocity_single_feature_activation_plan_pass",
        "[OK] Step81 wall velocity single-feature activation plan finished",
        "wall_velocity_single_feature_activation_plan",
    )


if __name__ == "__main__":
    main()
