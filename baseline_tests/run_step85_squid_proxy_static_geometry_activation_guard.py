from step85_common import run_named_audit
from src.mpm_lbm.evidence.step85_squid_proxy_static_geometry_activation_guard import (
    build_step85_squid_proxy_static_geometry_activation_guard,
)


def main():
    run_named_audit(
        build_step85_squid_proxy_static_geometry_activation_guard,
        "outputs/step85_squid_proxy_static_geometry_activation_guard",
        "logs/step85_squid_proxy_static_geometry_activation_guard.log",
        "step85_squid_proxy_static_geometry_activation_guard_pass",
        "[OK] Step85 squid proxy static geometry activation guard finished",
        "squid_proxy_static_geometry_activation_guard",
    )


if __name__ == "__main__":
    main()
