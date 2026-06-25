import os

from step110_common import ROOT
from src.mpm_lbm.evidence.step112_common import write_log
from src.mpm_lbm.evidence.step112_real_dynamics_diagnostics import build_step112_real_dynamics_diagnostics


def main():
    os.chdir(ROOT)
    component, force, structural = build_step112_real_dynamics_diagnostics(ROOT)
    if not component["real_dynamics_diagnostics_pass"] or not force["force_displacement_phase_pass"] or not structural["structural_state_pass"]:
        raise RuntimeError(f"Step112 diagnostics failed: {component} {force} {structural}")
    marker = "[OK] Step112 real dynamics diagnostics finished"
    write_log(ROOT, "logs/step112_real_dynamics_diagnostics.log", [marker])
    print(marker)


if __name__ == "__main__":
    main()
