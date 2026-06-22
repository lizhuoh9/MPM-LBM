import os

from step88_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality_audit import (
    build_step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality_audit,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality_audit,
        "outputs/step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality",
        "logs/step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality.log",
        "step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality_pass",
        "[OK] Step88 squid_proxy runtime geometry wall velocity combined quality audit finished",
        "squid_proxy_runtime_geometry_wall_velocity_combined_quality",
    )


if __name__ == "__main__":
    main()
