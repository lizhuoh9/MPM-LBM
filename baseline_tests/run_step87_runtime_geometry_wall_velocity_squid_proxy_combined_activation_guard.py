from step87_common import run_named_audit
from src.mpm_lbm.evidence.step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard import (
    build_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard,
)


def main():
    run_named_audit(
        build_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard,
        "outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard",
        "logs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard.log",
        "step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard_pass",
        "[OK] Step87 runtime geometry wall velocity squid proxy combined activation guard finished",
        "runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard",
    )


if __name__ == "__main__":
    main()
