import os

from step33_common import ROOT, make_motion_rows, motion_hashes, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value_first", "value_second", "notes"]


def main():
    os.chdir(ROOT)
    rows_first = make_motion_rows()
    rows_second = make_motion_rows()
    hashes_first = motion_hashes(rows_first)
    hashes_second = motion_hashes(rows_second)
    summary = {
        "row_count_first": len(rows_first),
        "row_count_second": len(rows_second),
        "motion_hash_first": hashes_first["motion_hash"],
        "motion_hash_second": hashes_second["motion_hash"],
        "mantle_motion_hash_first": hashes_first["mantle_motion_hash"],
        "mantle_motion_hash_second": hashes_second["mantle_motion_hash"],
        "cavity_motion_hash_first": hashes_first["cavity_motion_hash"],
        "cavity_motion_hash_second": hashes_second["cavity_motion_hash"],
        "funnel_motion_hash_first": hashes_first["funnel_motion_hash"],
        "funnel_motion_hash_second": hashes_second["funnel_motion_hash"],
    }
    summary["repeatability_pass"] = bool(
        summary["row_count_first"] == summary["row_count_second"]
        and summary["motion_hash_first"] == summary["motion_hash_second"]
        and summary["mantle_motion_hash_first"] == summary["mantle_motion_hash_second"]
        and summary["cavity_motion_hash_first"] == summary["cavity_motion_hash_second"]
        and summary["funnel_motion_hash_first"] == summary["funnel_motion_hash_second"]
    )
    if not summary["repeatability_pass"]:
        raise RuntimeError(f"Step 33 motion repeatability failed: {summary}")
    rows = [
        _row("row_count", summary["row_count_first"] == summary["row_count_second"], summary["row_count_first"], summary["row_count_second"], "row counts must match"),
        _row("motion_hash", summary["motion_hash_first"] == summary["motion_hash_second"], summary["motion_hash_first"], summary["motion_hash_second"], "full motion hash must repeat"),
        _row(
            "mantle_motion_hash",
            summary["mantle_motion_hash_first"] == summary["mantle_motion_hash_second"],
            summary["mantle_motion_hash_first"],
            summary["mantle_motion_hash_second"],
            "mantle motion hash must repeat",
        ),
        _row(
            "cavity_motion_hash",
            summary["cavity_motion_hash_first"] == summary["cavity_motion_hash_second"],
            summary["cavity_motion_hash_first"],
            summary["cavity_motion_hash_second"],
            "cavity motion hash must repeat",
        ),
        _row(
            "funnel_motion_hash",
            summary["funnel_motion_hash_first"] == summary["funnel_motion_hash_second"],
            summary["funnel_motion_hash_first"],
            summary["funnel_motion_hash_second"],
            "funnel motion hash must repeat",
        ),
        _row("repeatability_pass", summary["repeatability_pass"], summary["repeatability_pass"], summary["repeatability_pass"], "all repeatability checks must pass"),
    ]

    out_dir = ROOT / "outputs" / "step33_motion_repeatability"
    write_csv_rows(out_dir / "motion_repeatability.csv", rows, FIELDS)
    write_json(out_dir / "motion_repeatability.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 33 motion repeatability finished"
    write_log("logs/step33_motion_repeatability.log", [marker, f"row_count={len(rows_first)}"])
    print(f"row_count={len(rows_first)}")
    print(marker)


def _row(check, passed, first, second, notes):
    return {"check": check, "pass": bool(passed), "value_first": first, "value_second": second, "notes": notes}


if __name__ == "__main__":
    main()
