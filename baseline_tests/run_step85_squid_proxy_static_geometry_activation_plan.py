from step85_common import run_named_audit
from src.mpm_lbm.evidence.step85_squid_proxy_static_geometry_activation_plan import (
    build_step85_squid_proxy_static_geometry_activation_plan,
)


def main():
    run_named_audit(
        build_step85_squid_proxy_static_geometry_activation_plan,
        "outputs/step85_squid_proxy_static_geometry_activation_plan",
        "logs/step85_squid_proxy_static_geometry_activation_plan.log",
        "step85_squid_proxy_static_geometry_activation_plan_pass",
        "[OK] Step85 squid proxy static geometry activation plan finished",
        "squid_proxy_static_geometry_activation_plan",
    )


if __name__ == "__main__":
    main()
