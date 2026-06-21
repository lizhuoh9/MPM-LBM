import os

from step51_common import ROOT, transfer_comparison_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_transfer_diagnostics import mass_force_bounceback_transfer_envelope

    rows = transfer_comparison_rows()
    diag_rows, summary = mass_force_bounceback_transfer_envelope(rows)
    if not summary["envelope_pass"]:
        raise RuntimeError(f"Step 51 mass force bounce-back transfer envelope failed: {summary}")
    out_dir = ROOT / "outputs" / "step51_mass_force_bounceback_transfer_envelope"
    write_csv_rows(out_dir / "mass_force_bounceback_transfer_envelope.csv", diag_rows)
    write_json(out_dir / "mass_force_bounceback_transfer_envelope.json", {"summary": summary, "rows": diag_rows})
    marker = "[OK] Step 51 mass force bounce-back transfer envelope finished"
    write_log("logs/step51_mass_force_bounceback_transfer_envelope.log", [marker, f"row_count={summary['row_count']}", f"envelope_pass={summary['envelope_pass']}"])
    print(marker)


if __name__ == "__main__":
    main()
