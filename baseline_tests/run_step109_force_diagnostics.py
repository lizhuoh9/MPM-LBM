import os

from step109_common import ROOT, write_log
from src.mpm_lbm.evidence.step109_force_diagnostics import build_step109_force_and_structural_diagnostics


def main():
    os.chdir(ROOT)
    force, structural = build_step109_force_and_structural_diagnostics(ROOT)
    marker = "[OK] Step109 force and structural diagnostics finished"
    write_log(
        "logs/step109_force_diagnostics.log",
        [
            marker,
            f"force_rows={force['summary']['row_count']}",
            f"structural_rows={structural['summary']['structural_row_count']}",
            f"best_peak_solver_m={force['summary']['best_peak_solver_m']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
