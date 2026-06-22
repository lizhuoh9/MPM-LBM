import json
from pathlib import Path

from src.mpm_lbm.evidence.post_gate_3step_rebaseline_quality_audit import (
    build_step77_post_gate_3step_rebaseline_quality_audit,
)


ROOT = Path(__file__).resolve().parents[1]


def test_step77_3step_quality_audit_passes():
    rows, summary = build_step77_post_gate_3step_rebaseline_quality_audit(ROOT)
    assert rows
    assert summary["post_gate_3step_rebaseline_quality_pass"] is True
    assert summary["source_matrix_row_count"] == 1
    assert summary["pass_count"] == summary["row_count"]
    assert summary["finite_max_grid_reaction_norm_count"] == 1


def test_step77_3step_quality_artifact_passes():
    payload = read_json("outputs/step77_post_gate_3step_rebaseline_quality/post_gate_3step_rebaseline_quality.json")
    assert payload["rows"]
    assert payload["summary"]["post_gate_3step_rebaseline_quality_pass"] is True
    assert payload["summary"]["pass_count"] == payload["summary"]["row_count"]


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
