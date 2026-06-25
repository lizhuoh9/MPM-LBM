import os

from step110_common import ROOT, write_log
from src.mpm_lbm.evidence.step110_curve_shape_diagnostics import build_step110_curve_shape_diagnostics


def main():
    os.chdir(ROOT)
    _, summary = build_step110_curve_shape_diagnostics(ROOT)
    marker = "[OK] Step110 curve shape diagnostics finished"
    write_log("logs/step110_curve_shape_diagnostics.log", [marker, f"diagnostic_row_count={summary['diagnostic_row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()

