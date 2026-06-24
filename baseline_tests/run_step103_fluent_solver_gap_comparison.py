import os

from step103_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step103_fluent_solver_gap_comparison import build_step103_fluent_solver_gap_comparison


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step103_fluent_solver_gap_comparison,
        "outputs/step103_fluent_comparison",
        "logs/step103_fluent_solver_gap_comparison.log",
        "step103_fluent_solver_gap_comparison_pass",
        "[OK] Step103 Fluent solver gap comparison finished",
        "fluent_solver_gap_comparison",
    )


if __name__ == "__main__":
    main()
