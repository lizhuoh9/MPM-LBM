import math
import os

from step54_common import ROOT, check_row, read_json, read_text, summary_rows, write_csv_rows, write_json, write_log
from src.lbm_relaxation_semantics import (
    relaxation_semantics_summary,
    tau_from_lattice_kinematic_viscosity,
    tau_from_legacy_external_solver_parameter,
)


FIELDS = ["check", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    policy = read_json("configs/step54_lbm_relaxation_semantics_policy.json")
    source = read_text("src/lbm_fluid.py")
    summary = relaxation_semantics_summary(niu=0.1)
    rows = [
        check_row(
            "legacy_helper_formula_preserves_current_tau",
            math.isclose(tau_from_legacy_external_solver_parameter(0.1), 0.1 / 3.0 + 0.5),
            tau_from_legacy_external_solver_parameter(0.1),
            "legacy niu helper must preserve the previous default behavior",
        ),
        check_row(
            "standard_helper_formula_is_available_but_not_default",
            math.isclose(tau_from_lattice_kinematic_viscosity(0.1), 3.0 * 0.1 + 0.5),
            tau_from_lattice_kinematic_viscosity(0.1),
            "standard lattice viscosity semantics must be named separately",
        ),
        check_row(
            "lbm_fluid_uses_legacy_helper",
            "tau_from_legacy_external_solver_parameter(self.niu)" in source,
            "helper_call_present",
            "LBMFluid3D must call the explicit legacy helper",
        ),
        check_row(
            "inline_niu_tau_assignment_removed",
            "self.tau_f=self.niu/3.0+0.5" not in source and "self.tau_f = self.niu / 3.0 + 0.5" not in source,
            "inline_assignment_absent",
            "the legacy formula must not remain hidden inline",
        ),
        check_row(
            "policy_keeps_standard_viscosity_non_default",
            policy["standard_lattice_viscosity_is_default"] is False,
            policy["standard_lattice_viscosity_is_default"],
            "Step 54 names standard viscosity semantics without migrating defaults",
        ),
        check_row(
            "policy_disallows_physical_viscosity_claim",
            policy["physical_viscosity_validation_claim"] is False,
            policy["physical_viscosity_validation_claim"],
            "Step 54 must not claim physical viscosity validation",
        ),
    ]
    summary.update(
        {
            "row_count": len(rows),
            "pass_count": sum(1 for row in rows if row["pass"]),
            "standard_viscosity_validation_claim": False,
            "physical_viscosity_validation_claim": False,
        }
    )
    summary["lbm_relaxation_semantics_audit_pass"] = bool(summary["row_count"] == summary["pass_count"])
    if not summary["lbm_relaxation_semantics_audit_pass"]:
        raise RuntimeError(f"Step 54 LBM relaxation semantics audit failed: {summary}")

    out_dir = ROOT / "outputs" / "step54_lbm_relaxation_semantics_audit"
    write_csv_rows(out_dir / "lbm_relaxation_semantics.csv", rows, FIELDS)
    write_csv_rows(out_dir / "lbm_relaxation_semantics_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "lbm_relaxation_semantics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 54 LBM relaxation semantics audit finished"
    write_log("logs/step54_lbm_relaxation_semantics_audit.log", [marker, f"pass_count={summary['pass_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
