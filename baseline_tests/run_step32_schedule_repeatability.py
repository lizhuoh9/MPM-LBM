import os

from step32_common import ROOT, load_sampling_config, make_schedule_rows, schedule_hashes, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value_first", "value_second", "notes"]


def main():
    os.chdir(ROOT)
    sampling = load_sampling_config()
    precision = int(sampling.get("hash_numeric_precision", 12))
    first = make_schedule_rows()
    second = make_schedule_rows()
    first_hashes = schedule_hashes(first, precision=precision)
    second_hashes = schedule_hashes(second, precision=precision)
    summary = {
        "row_count_first": len(first),
        "row_count_second": len(second),
        "schedule_hash_first": first_hashes["schedule_hash"],
        "schedule_hash_second": second_hashes["schedule_hash"],
        "mantle_hash_first": first_hashes["mantle_hash"],
        "mantle_hash_second": second_hashes["mantle_hash"],
        "cavity_hash_first": first_hashes["cavity_hash"],
        "cavity_hash_second": second_hashes["cavity_hash"],
        "funnel_hash_first": first_hashes["funnel_hash"],
        "funnel_hash_second": second_hashes["funnel_hash"],
    }
    summary["repeatability_pass"] = bool(
        summary["row_count_first"] == summary["row_count_second"]
        and summary["schedule_hash_first"] == summary["schedule_hash_second"]
        and summary["mantle_hash_first"] == summary["mantle_hash_second"]
        and summary["cavity_hash_first"] == summary["cavity_hash_second"]
        and summary["funnel_hash_first"] == summary["funnel_hash_second"]
    )
    if not summary["repeatability_pass"]:
        raise RuntimeError(f"Step 32 schedule repeatability failed: {summary}")
    rows = [
        _row("row_count", summary["row_count_first"] == summary["row_count_second"], summary["row_count_first"], summary["row_count_second"], "row counts must match"),
        _row("schedule_hash", summary["schedule_hash_first"] == summary["schedule_hash_second"], summary["schedule_hash_first"], summary["schedule_hash_second"], "full schedule hash must repeat"),
        _row("mantle_hash", summary["mantle_hash_first"] == summary["mantle_hash_second"], summary["mantle_hash_first"], summary["mantle_hash_second"], "mantle schedule hash must repeat"),
        _row("cavity_hash", summary["cavity_hash_first"] == summary["cavity_hash_second"], summary["cavity_hash_first"], summary["cavity_hash_second"], "cavity schedule hash must repeat"),
        _row("funnel_hash", summary["funnel_hash_first"] == summary["funnel_hash_second"], summary["funnel_hash_first"], summary["funnel_hash_second"], "funnel schedule hash must repeat"),
        _row("repeatability_pass", summary["repeatability_pass"], summary["repeatability_pass"], summary["repeatability_pass"], "all repeatability checks must pass"),
    ]

    out_dir = ROOT / "outputs" / "step32_schedule_repeatability"
    write_csv_rows(out_dir / "schedule_repeatability.csv", rows, FIELDS)
    write_json(out_dir / "schedule_repeatability.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 32 schedule repeatability finished"
    write_log(
        "logs/step32_schedule_repeatability.log",
        [marker, f"row_count={summary['row_count_first']}", f"schedule_hash={summary['schedule_hash_first']}"],
    )
    print(f"row_count={summary['row_count_first']}")
    print(marker)


def _row(check, passed, first, second, notes):
    return {"check": check, "pass": bool(passed), "value_first": first, "value_second": second, "notes": notes}


if __name__ == "__main__":
    main()
