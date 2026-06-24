import os

from step102_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step102_fluent_official_2way_fsi_benchmark_intake import (
    build_step102_fluent_official_2way_fsi_benchmark_intake,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step102_fluent_official_2way_fsi_benchmark_intake,
        "outputs/step102_fluent_official_2way_fsi_benchmark_intake",
        "logs/step102_fluent_official_2way_fsi_benchmark_intake.log",
        "step102_fluent_official_2way_fsi_benchmark_intake_pass",
        "[OK] Step102 Fluent official two-way FSI benchmark intake finished",
        "fluent_official_2way_fsi_benchmark_intake",
    )


if __name__ == "__main__":
    main()
