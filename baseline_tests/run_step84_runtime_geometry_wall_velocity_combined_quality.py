import os

from step84_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step84_runtime_geometry_wall_velocity_combined_quality_audit import (
    build_step84_runtime_geometry_wall_velocity_combined_quality_audit,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step84_runtime_geometry_wall_velocity_combined_quality_audit,
        "outputs/step84_runtime_geometry_wall_velocity_combined_quality",
        "logs/step84_runtime_geometry_wall_velocity_combined_quality.log",
        "step84_runtime_geometry_wall_velocity_combined_quality_pass",
        "[OK] Step84 runtime geometry plus wall velocity combined quality audit finished",
        "runtime_geometry_wall_velocity_combined_quality",
    )


if __name__ == "__main__":
    main()
