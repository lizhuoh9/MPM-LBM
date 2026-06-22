import os

import taichi as ti

from step86_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.step86_squid_proxy_static_geometry_smoke_runner import (
    STEP86_SMOKE_FIELDS,
    build_step86_squid_proxy_static_geometry_smoke_matrix,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary = build_step86_squid_proxy_static_geometry_smoke_matrix(ROOT)
    if not summary["step86_squid_proxy_static_geometry_smoke_matrix_pass"]:
        raise RuntimeError(f"Step86 squid proxy static geometry smoke matrix failed: {summary}")
    out_dir = ROOT / "outputs" / "step86_squid_proxy_static_geometry_smoke_matrix"
    write_csv_rows(out_dir / "squid_proxy_static_geometry_smoke_matrix.csv", rows, STEP86_SMOKE_FIELDS)
    write_csv_rows(out_dir / "squid_proxy_static_geometry_smoke_matrix_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "squid_proxy_static_geometry_smoke_matrix.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step86 squid proxy static geometry canonical driver smoke matrix finished"
    write_log(
        "logs/step86_squid_proxy_static_geometry_smoke_matrix.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"stable_count={summary['stable_count']}",
            f"total_elapsed_seconds={summary['total_elapsed_seconds']}",
            f"slowest_row_name={summary['slowest_row_name']}",
            f"slowest_elapsed_seconds={summary['slowest_elapsed_seconds']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
