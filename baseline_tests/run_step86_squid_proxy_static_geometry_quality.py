from step86_common import run_named_audit
from src.mpm_lbm.evidence.step86_squid_proxy_static_geometry_quality_audit import (
    build_step86_squid_proxy_static_geometry_quality_audit,
)


def main():
    run_named_audit(
        build_step86_squid_proxy_static_geometry_quality_audit,
        "outputs/step86_squid_proxy_static_geometry_quality",
        "logs/step86_squid_proxy_static_geometry_quality.log",
        "step86_squid_proxy_static_geometry_quality_pass",
        "[OK] Step86 squid proxy static geometry quality audit finished",
        "squid_proxy_static_geometry_quality",
    )


if __name__ == "__main__":
    main()
