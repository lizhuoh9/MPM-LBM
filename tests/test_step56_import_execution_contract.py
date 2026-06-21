import json
from pathlib import Path

from src.mpm_lbm.evidence.import_execution_audit import build_import_execution_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step56_import_execution_audit_passes_current_runtime_imports():
    rows, summary = build_import_execution_audit(ROOT)
    assert summary["import_execution_audit_pass"] is True
    assert int(summary["row_count"]) == 9
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert int(summary["same_object_count"]) == 9
    assert summary["output_snapshot_unchanged"] is True
    assert summary["solver_run"] is False
    assert summary["runtime_object_construction_required"] is False
    assert all(row["same_object"] is True for row in rows)


def test_step56_import_execution_artifact_passes():
    payload = read_json("outputs/step56_import_execution_audit/import_execution_audit.json")
    summary = payload["summary"]
    assert summary["import_execution_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 9
    assert int(summary["same_object_count"]) == 9
    assert all(row["pass"] is True for row in payload["rows"])


def test_step56_required_canonical_and_legacy_imports_resolve_to_same_objects():
    from src.coupling import PenaltyFSICoupler3D as LegacyPenaltyFSICoupler3D
    from src.lbm_config import LBMConfig as LegacyLBMConfig
    from src.lbm_fluid import LBMFluid3D as LegacyLBMFluid3D
    from src.moving_boundary_coupling import MovingBoundaryFSICoupler3D as LegacyMovingBoundaryFSICoupler3D
    from src.mpm_config import MPMConfig as LegacyMPMConfig
    from src.mpm_solid import MPMSolid3D as LegacyMPMSolid3D
    from src.projection import MPMToLBMProjector3D as LegacyMPMToLBMProjector3D
    from src.units import GridUnitMapper as LegacyGridUnitMapper
    from src.mpm_lbm.sim.coupling.moving_boundary import MovingBoundaryFSICoupler3D
    from src.mpm_lbm.sim.coupling.penalty import PenaltyFSICoupler3D
    from src.mpm_lbm.sim.coupling.projection import MPMToLBMProjector3D
    from src.mpm_lbm.sim.lbm.config import LBMConfig
    from src.mpm_lbm.sim.lbm.fluid import LBMFluid3D
    from src.mpm_lbm.sim.mpm.config import MPMConfig
    from src.mpm_lbm.sim.mpm.solid import MPMSolid3D
    from src.mpm_lbm.sim.units.mapper import GridUnitMapper

    assert LegacyLBMConfig is LBMConfig
    assert LegacyLBMFluid3D is LBMFluid3D
    assert LegacyMPMConfig is MPMConfig
    assert LegacyMPMSolid3D is MPMSolid3D
    assert LegacyGridUnitMapper is GridUnitMapper
    assert LegacyMPMToLBMProjector3D is MPMToLBMProjector3D
    assert LegacyPenaltyFSICoupler3D is PenaltyFSICoupler3D
    assert LegacyMovingBoundaryFSICoupler3D is MovingBoundaryFSICoupler3D


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
