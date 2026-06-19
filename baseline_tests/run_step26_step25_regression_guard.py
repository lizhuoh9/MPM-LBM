import os

from step26_common import ROOT, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    rows = [
        _check_file("step25_report_exists", "STEP25_CONTROLLED_REAL_GEOMETRY_INTAKE_REPORT.md"),
        _check_step25_manifest(),
        _check_step25_sampling(),
        _check_step25_projection(),
        _check_step25_artifact_summary("large_file_count", 0),
        _check_step25_artifact_summary("scan_data_file_count", 0),
        _check_step25_artifact_summary("raw_candidate_large_file_count", 0),
    ]
    failed = [row for row in rows if row["pass"] is not True]
    if failed:
        raise RuntimeError(f"Step 25 regression guard failed: {failed}")

    out_dir = ROOT / "outputs" / "step26_step25_regression_guard"
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "step25_manifest_row_count": _read_json("outputs/step25_candidate_manifest/candidate_manifest.json")["row_count"],
        "step25_large_file_count": _read_json("outputs/step25_artifact_manifest/artifact_summary.json")["large_file_count"],
        "step25_scan_data_file_count": _read_json("outputs/step25_artifact_manifest/artifact_summary.json")[
            "scan_data_file_count"
        ],
        "step25_raw_candidate_large_file_count": _read_json("outputs/step25_artifact_manifest/artifact_summary.json")[
            "raw_candidate_large_file_count"
        ],
    }
    write_csv_rows(out_dir / "step25_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step25_regression_guard.json", summary)
    marker = "[OK] Step 26 Step 25 regression guard finished"
    write_log("logs/step26_step25_regression_guard.log", [marker, f"row_count={len(rows)}"])
    print(f"row_count={len(rows)}")
    print(marker)


def _check_file(name, relative_path):
    return {"check": name, "pass": (ROOT / relative_path).is_file(), "value": relative_path, "notes": "required Step 25 artifact"}


def _check_step25_manifest():
    manifest = _read_json("outputs/step25_candidate_manifest/candidate_manifest.json")
    rows = manifest.get("rows", [])
    passed = int(manifest.get("row_count", 0)) == 2 and all(row.get("manifest_pass") is True for row in rows)
    return {"check": "step25_candidate_manifest", "pass": passed, "value": len(rows), "notes": "expected 2 passing rows"}


def _check_step25_sampling():
    summary = _read_json("outputs/step25_sampling_reproducibility/sampling_reproducibility.json")
    rows = summary.get("rows", [])
    passed = int(summary.get("row_count", 0)) == 2 and all(row.get("reproducibility_pass") is True for row in rows)
    return {"check": "step25_sampling_reproducibility", "pass": passed, "value": len(rows), "notes": "expected 2 passing rows"}


def _check_step25_projection():
    summary = _read_json("outputs/step25_projection_smoke/projection_smoke_results.json")
    rows = summary.get("rows", [])
    passed = int(summary.get("row_count", 0)) == 2 and all(row.get("projection_pass") is True for row in rows)
    return {"check": "step25_projection_smoke", "pass": passed, "value": len(rows), "notes": "expected 2 passing rows"}


def _check_step25_artifact_summary(key, expected):
    summary = _read_json("outputs/step25_artifact_manifest/artifact_summary.json")
    value = int(summary.get(key, -1))
    return {"check": f"step25_{key}", "pass": value == expected, "value": value, "notes": f"expected {expected}"}


def _read_json(relative_path):
    import json

    with (ROOT / relative_path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
