import os

from step102_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step102_fluent_official_2way_fsi_mapping_guard import (
    build_step102_fluent_official_2way_fsi_mapping_guard,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step102_fluent_official_2way_fsi_mapping_guard,
        "outputs/step102_fluent_official_2way_fsi_mapping_guard",
        "logs/step102_fluent_official_2way_fsi_mapping_guard.log",
        "step102_fluent_official_2way_fsi_mapping_guard_pass",
        "[OK] Step102 Fluent official two-way FSI mapping guard finished",
        "fluent_official_2way_fsi_mapping_guard",
    )


if __name__ == "__main__":
    main()
