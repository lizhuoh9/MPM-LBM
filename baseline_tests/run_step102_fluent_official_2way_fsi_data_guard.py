import os

from step102_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step102_fluent_official_2way_fsi_data_guard import (
    build_step102_fluent_official_2way_fsi_data_guard,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step102_fluent_official_2way_fsi_data_guard,
        "outputs/step102_fluent_official_2way_fsi_data_guard",
        "logs/step102_fluent_official_2way_fsi_data_guard.log",
        "step102_fluent_official_2way_fsi_data_guard_pass",
        "[OK] Step102 Fluent official two-way FSI data guard finished",
        "fluent_official_2way_fsi_data_guard",
    )


if __name__ == "__main__":
    main()
