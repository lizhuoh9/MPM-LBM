import os

from step88_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step88_squid_proxy_runtime_geometry_wall_velocity_combined_activation_guard import (
    build_step88_squid_proxy_runtime_geometry_wall_velocity_combined_activation_guard,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step88_squid_proxy_runtime_geometry_wall_velocity_combined_activation_guard,
        "outputs/step88_activation_guard",
        "logs/step88_activation_guard.log",
        "step88_activation_guard_pass",
        "[OK] Step88 activation guard finished",
        "activation_guard",
    )


if __name__ == "__main__":
    main()
