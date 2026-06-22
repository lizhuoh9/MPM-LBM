from step87_common import run_named_audit
from src.mpm_lbm.evidence.step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan import (
    build_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan,
)


def main():
    run_named_audit(
        build_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan,
        "outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan",
        "logs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan.log",
        "step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_pass",
        "[OK] Step87 runtime geometry wall velocity squid proxy combined activation plan finished",
        "runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan",
    )


if __name__ == "__main__":
    main()
