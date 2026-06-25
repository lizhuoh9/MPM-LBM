import os

from step110_common import ROOT
from src.mpm_lbm.evidence.step111_common import write_log
from src.mpm_lbm.evidence.step111_error_comparison import build_step111_error_comparison


def main():
    os.chdir(ROOT)
    rows, summary = build_step111_error_comparison(ROOT)
    row = rows[0]
    marker = "[OK] Step111 error comparison finished"
    write_log(
        ROOT,
        "logs/step111_error_comparison.log",
        [
            marker,
            f"step111_error_comparison_pass={summary['step111_error_comparison_pass']}",
            f"normalized_rms_error={row['normalized_rms_error']}",
            f"shape_correlation={row['shape_correlation']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
