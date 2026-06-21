import os

from step63_67_common import ROOT, run_audit
from src.mpm_lbm.evidence.solver_completion_roadmap_audit import build_solver_completion_roadmap_audit


def main():
    os.chdir(ROOT)
    run_audit(build_solver_completion_roadmap_audit, "outputs/step63_solver_completion_roadmap_audit", "logs/step63_solver_completion_roadmap_audit.log", "solver_completion_roadmap_pass", "[OK] Step 63 solver completion roadmap audit finished", None)


if __name__ == "__main__":
    main()
