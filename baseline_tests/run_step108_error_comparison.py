import os

from step108_common import ROOT, write_log
from src.mpm_lbm.evidence.step108_error_comparison import build_step108_error_comparison


def main():
    os.chdir(ROOT)
    rows, summary = build_step108_error_comparison(ROOT)
    if not summary["step108_error_comparison_pass"]:
        raise RuntimeError(f"Step108 error comparison failed: {summary}")
    row = rows[0]
    marker = "[OK] Step108 error comparison finished"
    write_log(
        "logs/step108_error_comparison.log",
        [
            marker,
            f"sample_count={row['sample_count']}",
            f"peak_solver_m={row['peak_solver_m']}",
            f"normalized_rms_error={row['normalized_rms_error']}",
            f"shape_correlation={row['shape_correlation']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
