from step86_common import run_named_audit
from src.mpm_lbm.evidence.step86_squid_proxy_static_geometry_activation_guard import (
    build_step86_squid_proxy_static_geometry_activation_guard,
)


def main():
    run_named_audit(
        build_step86_squid_proxy_static_geometry_activation_guard,
        "outputs/step86_activation_guard",
        "logs/step86_activation_guard.log",
        "step86_activation_guard_pass",
        "[OK] Step86 activation guard finished",
        "activation_guard",
    )


if __name__ == "__main__":
    main()
