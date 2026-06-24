import os

import taichi as ti

from step105_common import ROOT, write_log
from src.mpm_lbm.evidence.step105_transient_gap_smoke_runner import (
    build_step105_transient_gap_smoke,
    write_step105_flow_development_artifacts,
    write_step105_transient_artifacts,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary, flow_rows, flow_summary = build_step105_transient_gap_smoke(ROOT)
    if not summary["step105_transient_gap_smoke_pass"]:
        raise RuntimeError(f"Step105 transient gap smoke failed: {summary}")
    if not flow_summary["flow_development_report_pass"]:
        raise RuntimeError(f"Step105 flow development failed: {flow_summary}")
    write_step105_transient_artifacts(ROOT, rows, summary)
    write_step105_flow_development_artifacts(ROOT, flow_rows, flow_summary)
    marker = "[OK] Step105 Fluent duct-flap proxy 50-step transient gap smoke finished"
    write_log(
        "logs/step105_fluent_duct_flap_proxy_50step_transient_gap_smoke.log",
        [marker, f"row_count={summary['row_count']}", f"flow_row_count={flow_summary['row_count']}"],
    )
    print(marker)


if __name__ == "__main__":
    main()
