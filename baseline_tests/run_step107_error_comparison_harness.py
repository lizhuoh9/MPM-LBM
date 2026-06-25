import os

from step107_common import ROOT, write_log
from src.mpm_lbm.evidence.step107_error_comparison_harness import build_step107_error_comparison


def main():
    os.chdir(ROOT)
    rows, summary = build_step107_error_comparison(ROOT)
    marker = "[OK] Step107 public Fluent plot error comparison finished"
    write_log(
        "logs/step107_error_comparison_harness.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"sample_count={rows[0]['sample_count']}",
            f"peak_abs_error_m={rows[0]['peak_abs_error_m']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
