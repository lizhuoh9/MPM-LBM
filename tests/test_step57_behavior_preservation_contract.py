import json
from pathlib import Path

import numpy as np

from src.mpm_lbm.evidence.driver_support_behavior_preservation_audit import (
    build_driver_support_behavior_preservation_audit,
)


ROOT = Path(__file__).resolve().parents[1]


def test_step57_behavior_preservation_audit_passes_current_source():
    rows, summary = build_driver_support_behavior_preservation_audit(ROOT)
    assert summary["driver_support_behavior_preservation_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 10
    assert summary["solver_behavior_changed"] is False
    assert summary["physics_feature_expansion"] is False
    assert summary["solver_object_construction_required"] is False
    assert all(row["pass"] is True for row in rows)


def test_step57_behavior_preservation_artifact_passes():
    payload = read_json("outputs/step57_behavior_preservation_audit/behavior_preservation_audit.json")
    summary = payload["summary"]
    assert summary["driver_support_behavior_preservation_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 10
    assert all(row["pass"] is True for row in payload["rows"])


def test_step57_driver_support_semantics_are_unchanged_by_import_path():
    from src.mpm_lbm.sim.geometry.config import GeometryConfig
    from src.mpm_lbm.sim.geometry.sampler import GeometrySampler3D
    from src.mpm_lbm.sim.geometry.quality import GeometryQualityGate

    config = GeometryConfig(n_particles=8, particles_per_axis_hint=8)
    first = GeometrySampler3D(config).sample_particles()
    second = GeometrySampler3D(config).sample_particles()
    assert np.array_equal(first["x"], second["x"])
    assert np.array_equal(first["vol0"], second["vol0"])
    assert np.array_equal(first["mass"], second["mass"])

    report = {
        "quality_kind": "mesh",
        "vertices_count": 8,
        "faces_count": 12,
        "has_valid_face_indices": True,
        "degenerate_face_count": 1,
        "boundary_edge_count": 1,
        "nonmanifold_edge_count": 0,
        "duplicate_vertex_count": 0,
        "volume_abs": 1.0,
    }
    assert GeometryQualityGate(strict=False).evaluate(report)["pass"] is True
    assert GeometryQualityGate(strict=True).evaluate(report)["pass"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
