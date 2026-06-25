import os

from step108_common import ROOT, write_log
from src.mpm_lbm.evidence.step108_dimensional_mapping import build_step108_dimensional_mapping


def main():
    os.chdir(ROOT)
    mapping = build_step108_dimensional_mapping(ROOT)
    marker = "[OK] Step108 dimensional mapping finished"
    write_log(
        "logs/step108_dimensional_mapping.log",
        [
            marker,
            f"mapped_inlet_velocity_mps={mapping['mapped_inlet_velocity_mps']}",
            f"lbm_substeps_per_fsi_step={mapping['lbm_substeps_per_fsi_step']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
