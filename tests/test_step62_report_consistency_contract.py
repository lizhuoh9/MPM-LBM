import json
from pathlib import Path

from src.mpm_lbm.evidence.report_consistency_guard import build_report_consistency_guard


ROOT = Path(__file__).resolve().parents[1]


def test_step62_report_consistency_guard_passes_current_reports():
    rows, summary = build_report_consistency_guard(ROOT)
    assert summary["report_consistency_guard_pass"] is True
    assert summary["step61_report_consistency_issue_fixed"] is True
    assert summary["step62_report_consistency_checked"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 4
    assert all(row["pass"] is True for row in rows)


def test_step62_report_consistency_artifact_passes():
    payload = read_json("outputs/step62_report_consistency_guard/report_consistency_guard.json")
    summary = payload["summary"]
    assert summary["report_consistency_guard_pass"] is True
    assert summary["step61_report_consistency_issue_fixed"] is True
    assert summary["step62_report_consistency_checked"] is True
    assert int(summary["fail_count"]) == 0
    assert all(row["pass"] is True for row in payload["rows"])


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
