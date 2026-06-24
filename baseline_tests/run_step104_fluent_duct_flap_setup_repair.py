import os

import taichi as ti

from step104_common import ROOT, write_log
from src.mpm_lbm.evidence.step104_fluent_duct_flap_setup_repair_runner import (
    build_step104_fluent_duct_flap_setup_repair,
    write_step104_setup_repair_artifacts,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary = build_step104_fluent_duct_flap_setup_repair(ROOT)
    if not summary["step104_setup_repair_pass"]:
        raise RuntimeError(f"Step104 setup repair failed: {summary}")
    write_step104_setup_repair_artifacts(ROOT, rows, summary)
    marker = "[OK] Step104 Fluent duct-flap setup repair finished"
    write_log(
        "logs/step104_fluent_duct_flap_setup_repair.log",
        [marker, f"row_count={summary['row_count']}"],
    )
    print(marker)


if __name__ == "__main__":
    main()
