from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SupportScalingAuditConfig:
    audit_id: str
    reference_artifacts_config_path: str
    metric_semantics_policy_path: str
    step51_combined_row_name: str
    step52_combined_row_name: str
    step52_static_row_name: str
    step51_grid: int
    step52_grid: int
    phase_count: int
    phase_sequence: tuple[float, ...]
    diagnostic_only: bool
    post_processing_only: bool
    requires_new_solver_rows: bool
    introduces_new_transfer_mode: bool
    rerun_physics_matrix: bool
    allow_48_link_area: bool
    allow_multi_cycle: bool
    allow_64_grid: bool
    modify_solver_formulas: bool
    modify_default_behavior: bool
    write_vtk: bool
    write_particles: bool
    write_dense_displacement_field: bool
    write_displaced_particles: bool
    persist_projected_state: bool
    persist_displaced_geometry: bool
    persist_lbm_solid_vel: bool

    @classmethod
    def from_json(cls, path: str | Path) -> "SupportScalingAuditConfig":
        payload = _read_json(path)
        return cls(
            audit_id=str(payload["audit_id"]),
            reference_artifacts_config_path=str(payload["reference_artifacts_config_path"]),
            metric_semantics_policy_path=str(payload["metric_semantics_policy_path"]),
            step51_combined_row_name=str(payload["step51_combined_row_name"]),
            step52_combined_row_name=str(payload["step52_combined_row_name"]),
            step52_static_row_name=str(payload["step52_static_row_name"]),
            step51_grid=int(payload["step51_grid"]),
            step52_grid=int(payload["step52_grid"]),
            phase_count=int(payload["phase_count"]),
            phase_sequence=tuple(float(value) for value in payload["phase_sequence"]),
            diagnostic_only=bool(payload["diagnostic_only"]),
            post_processing_only=bool(payload["post_processing_only"]),
            requires_new_solver_rows=bool(payload["requires_new_solver_rows"]),
            introduces_new_transfer_mode=bool(payload["introduces_new_transfer_mode"]),
            rerun_physics_matrix=bool(payload["rerun_physics_matrix"]),
            allow_48_link_area=bool(payload["allow_48_link_area"]),
            allow_multi_cycle=bool(payload["allow_multi_cycle"]),
            allow_64_grid=bool(payload["allow_64_grid"]),
            modify_solver_formulas=bool(payload["modify_solver_formulas"]),
            modify_default_behavior=bool(payload["modify_default_behavior"]),
            write_vtk=bool(payload["write_vtk"]),
            write_particles=bool(payload["write_particles"]),
            write_dense_displacement_field=bool(payload["write_dense_displacement_field"]),
            write_displaced_particles=bool(payload["write_displaced_particles"]),
            persist_projected_state=bool(payload["persist_projected_state"]),
            persist_displaced_geometry=bool(payload["persist_displaced_geometry"]),
            persist_lbm_solid_vel=bool(payload["persist_lbm_solid_vel"]),
        )

    def mutation_flags_false(self) -> bool:
        return not any(
            [
                self.requires_new_solver_rows,
                self.introduces_new_transfer_mode,
                self.rerun_physics_matrix,
                self.allow_48_link_area,
                self.allow_multi_cycle,
                self.allow_64_grid,
                self.modify_solver_formulas,
                self.modify_default_behavior,
                self.write_vtk,
                self.write_particles,
                self.write_dense_displacement_field,
                self.write_displaced_particles,
                self.persist_projected_state,
                self.persist_displaced_geometry,
                self.persist_lbm_solid_vel,
            ]
        )


def load_reference_artifacts_config(root: Path, config: SupportScalingAuditConfig) -> dict:
    return _read_json(root / config.reference_artifacts_config_path)


def load_metric_semantics_policy(root: Path, config: SupportScalingAuditConfig) -> dict:
    return _read_json(root / config.metric_semantics_policy_path)


def _read_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)
