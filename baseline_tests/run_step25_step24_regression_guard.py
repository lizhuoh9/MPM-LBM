import os

from step25_common import ROOT, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]
FORBIDDEN_CLAIMS = [
    "real squid simulation is validated",
    "validated squid swimming",
    "production mesh repair is complete",
    "automatic remeshing is implemented",
    "production-ready mesh import",
    "production-ready sharp-interface FSI",
    "strict momentum-conserving FSI is complete",
    "implements two_phase",
    "implements contact_angle",
]


def main():
    os.chdir(ROOT)
    rows = [
        _check_file("step24_report_exists", "STEP24_STRICT_QUALITY_GATED_IMPORTED_GEOMETRY_LONG_RUN_REPORT.md"),
        _check_file("step24_quality_aggregation_exists", "outputs/step24_quality_report_aggregation/quality_report_summary.json"),
        _check_step24_quality_count(),
        _check_step24_large_file_count(),
        _check_file("step24_pytest_log_exists", "logs/step24_pytest.log"),
        _check_step24_docs_no_forbidden_claims(),
    ]
    failed = [row for row in rows if row["pass"] is not True]
    if failed:
        raise RuntimeError(f"Step 24 regression guard failed: {failed}")

    out_dir = ROOT / "outputs" / "step25_step24_regression_guard"
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "quality_report_count": _read_json("outputs/step24_quality_report_aggregation/quality_report_summary.json")[
            "quality_report_count"
        ],
        "large_file_count": _read_json("outputs/step24_artifact_manifest/artifact_summary.json")["large_file_count"],
    }
    write_csv_rows(out_dir / "step24_regression_guard.csv", rows, FIELDS)
    write_json(out_dir / "step24_regression_guard.json", summary)
    marker = "[OK] Step 25 Step 24 regression guard finished"
    write_log("logs/step25_step24_regression_guard.log", [marker, f"row_count={len(rows)}"])
    print(f"row_count={len(rows)}")
    print(marker)


def _check_file(name, relative_path):
    path = ROOT / relative_path
    return {"check": name, "pass": path.is_file(), "value": relative_path, "notes": "required Step 24 artifact"}


def _check_step24_quality_count():
    summary = _read_json("outputs/step24_quality_report_aggregation/quality_report_summary.json")
    value = int(summary.get("quality_report_count", -1))
    return {"check": "step24_quality_report_count", "pass": value == 9, "value": value, "notes": "expected 9"}


def _check_step24_large_file_count():
    summary = _read_json("outputs/step24_artifact_manifest/artifact_summary.json")
    value = int(summary.get("large_file_count", -1))
    return {"check": "step24_large_file_count", "pass": value == 0, "value": value, "notes": "expected 0"}


def _check_step24_docs_no_forbidden_claims():
    paths = [
        "README.md",
        "docs/23_strict_quality_gated_imported_geometry_long_run.md",
        "STEP24_STRICT_QUALITY_GATED_IMPORTED_GEOMETRY_LONG_RUN_REPORT.md",
    ]
    combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in paths)
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    return {
        "check": "step24_docs_no_forbidden_claims",
        "pass": offenders == [],
        "value": ",".join(offenders),
        "notes": "Step 24 docs remain scoped away from real validation claims",
    }


def _read_json(relative_path):
    import json

    with (ROOT / relative_path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
