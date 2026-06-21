import os

from step52_common import ROOT, feasibility_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_48_feasibility_diagnostics import mass_force_bounceback_48_envelope

    rows = feasibility_rows()
    diag_rows, summary = mass_force_bounceback_48_envelope(rows)
    if not summary["envelope_pass"]:
        raise RuntimeError(f"Step 52 mass force bounce-back envelope failed: {summary}")
    out_dir = ROOT / "outputs" / "step52_mass_force_bounceback_envelope"
    write_csv_rows(out_dir / "mass_force_bounceback_envelope.csv", diag_rows)
    write_json(out_dir / "mass_force_bounceback_envelope.json", {"summary": summary, "rows": diag_rows})
    marker = "[OK] Step 52 mass force bounce-back envelope finished"
    write_log("logs/step52_mass_force_bounceback_envelope.log", [marker, f"row_count={summary['row_count']}", f"envelope_pass={summary['envelope_pass']}"])
    print(marker)


if __name__ == "__main__":
    main()
