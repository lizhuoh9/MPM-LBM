from step82_common import run_named_audit
from src.mpm_lbm.evidence.step82_wall_velocity_solid_vel_quality_audit import (
    build_step82_wall_velocity_solid_vel_quality_audit,
)


FIELDS = ["row_name", "check", "actual", "expected", "operator", "pass"]


if __name__ == "__main__":
    run_named_audit(
        build_step82_wall_velocity_solid_vel_quality_audit,
        "outputs/step82_wall_velocity_solid_vel_quality",
        "logs/step82_wall_velocity_solid_vel_quality.log",
        "step82_wall_velocity_solid_vel_quality_pass",
        "[OK] Step82 wall velocity solid_vel quality finished",
        "wall_velocity_solid_vel_quality",
        FIELDS,
    )
