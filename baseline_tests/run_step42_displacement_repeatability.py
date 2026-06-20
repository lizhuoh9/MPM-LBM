import os

from step42_common import ROOT, make_displacement_rows, write_csv_rows, write_json, write_log
from src.geometry_displacement_field import displacement_hashes


FIELDS = ["check", "pass", "value_first", "value_second", "notes"]


def main():
    os.chdir(ROOT)
    rows_first = make_displacement_rows()
    rows_second = make_displacement_rows()
    hashes_first = displacement_hashes(rows_first)
    hashes_second = displacement_hashes(rows_second)
    summary = {
        "row_count_first": len(rows_first),
        "row_count_second": len(rows_second),
        "displacement_hash_first": hashes_first["displacement_hash"],
        "displacement_hash_second": hashes_second["displacement_hash"],
        "mantle_displacement_hash_first": hashes_first["mantle_displacement_hash"],
        "mantle_displacement_hash_second": hashes_second["mantle_displacement_hash"],
        "cavity_displacement_hash_first": hashes_first["cavity_displacement_hash"],
        "cavity_displacement_hash_second": hashes_second["cavity_displacement_hash"],
        "funnel_displacement_hash_first": hashes_first["funnel_displacement_hash"],
        "funnel_displacement_hash_second": hashes_second["funnel_displacement_hash"],
    }
    summary["repeatability_pass"] = bool(
        summary["row_count_first"] == summary["row_count_second"]
        and summary["displacement_hash_first"] == summary["displacement_hash_second"]
        and summary["mantle_displacement_hash_first"] == summary["mantle_displacement_hash_second"]
        and summary["cavity_displacement_hash_first"] == summary["cavity_displacement_hash_second"]
        and summary["funnel_displacement_hash_first"] == summary["funnel_displacement_hash_second"]
    )
    if not summary["repeatability_pass"]:
        raise RuntimeError(f"Step 42 displacement repeatability failed: {summary}")
    rows = [
        _row("row_count", summary["row_count_first"] == summary["row_count_second"], summary["row_count_first"], summary["row_count_second"], "row counts must match"),
        _row("displacement_hash", summary["displacement_hash_first"] == summary["displacement_hash_second"], summary["displacement_hash_first"], summary["displacement_hash_second"], "full displacement hash must repeat"),
        _row("mantle_displacement_hash", summary["mantle_displacement_hash_first"] == summary["mantle_displacement_hash_second"], summary["mantle_displacement_hash_first"], summary["mantle_displacement_hash_second"], "mantle hash must repeat"),
        _row("cavity_displacement_hash", summary["cavity_displacement_hash_first"] == summary["cavity_displacement_hash_second"], summary["cavity_displacement_hash_first"], summary["cavity_displacement_hash_second"], "cavity hash must repeat"),
        _row("funnel_displacement_hash", summary["funnel_displacement_hash_first"] == summary["funnel_displacement_hash_second"], summary["funnel_displacement_hash_first"], summary["funnel_displacement_hash_second"], "funnel hash must repeat"),
        _row("repeatability_pass", summary["repeatability_pass"], summary["repeatability_pass"], summary["repeatability_pass"], "all repeatability checks must pass"),
    ]

    out_dir = ROOT / "outputs" / "step42_displacement_repeatability"
    write_csv_rows(out_dir / "displacement_repeatability.csv", rows, FIELDS)
    write_json(out_dir / "displacement_repeatability.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 42 displacement repeatability finished"
    write_log("logs/step42_displacement_repeatability.log", [marker, f"row_count={len(rows_first)}"])
    print(f"row_count={len(rows_first)}")
    print(marker)


def _row(check, passed, first, second, notes):
    return {"check": check, "pass": bool(passed), "value_first": first, "value_second": second, "notes": notes}


if __name__ == "__main__":
    main()
