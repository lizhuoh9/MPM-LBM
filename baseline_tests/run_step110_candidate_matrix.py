import os

from step110_common import ROOT, write_log
from src.mpm_lbm.evidence.step110_candidate_matrix_runner import build_step110_candidate_matrix


def main():
    os.chdir(ROOT)
    _, summary = build_step110_candidate_matrix(ROOT)
    marker = "[OK] Step110 candidate matrix finished"
    write_log(
        "logs/step110_candidate_matrix.log",
        [
            marker,
            f"best_candidate={summary['best_candidate_row_name']}",
            f"best_candidate_normalized_rms_error={summary['best_candidate_normalized_rms_error']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()

