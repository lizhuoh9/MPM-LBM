import os

import numpy as np

from .sampler import GeometrySampler3D
from .mesh_io import load_obj, normalize_vertices
from .mesh_quality import analyze_mesh
from .voxel_io import load_voxel_geometry
from .voxel_quality import analyze_voxel_occupancy


def analyze_geometry_config(config) -> dict:
    if config.geometry_type == "mesh":
        vertices, faces = load_obj(config.geometry_file)
        if config.normalize_to_domain:
            vertices = normalize_vertices(
                vertices,
                domain_min=config.domain_min,
                domain_max=config.domain_max,
                padding=config.padding,
                preserve_aspect_ratio=config.preserve_aspect_ratio,
            )
        report = analyze_mesh(vertices, faces)
        report.update(
            {
                "geometry_type": config.geometry_type,
                "quality_kind": "mesh",
                "source_file": config.geometry_file,
                "scope_note": "diagnostic mesh quality proxy; not production mesh repair or automatic remeshing",
            }
        )
        return report

    if config.geometry_type == "voxel":
        try:
            voxel_geometry = load_voxel_geometry(
                config.geometry_file,
                metadata_path=config.metadata_file,
                threshold=config.voxel_threshold,
            )
            occupancy = voxel_geometry.occupancy
            metadata = voxel_geometry.metadata
            loader_error = ""
        except ValueError as exc:
            if "occupied voxel" not in str(exc):
                raise
            raw = np.load(_resolve_path(config.geometry_file))
            occupancy = raw.astype(bool)
            metadata = {}
            loader_error = str(exc)

        report = analyze_voxel_occupancy(occupancy, metadata=metadata)
        report.update(
            {
                "geometry_type": config.geometry_type,
                "quality_kind": "voxel",
                "source_file": config.geometry_file,
                "loader_error": loader_error,
                "scope_note": "diagnostic voxel quality report; not real squid validation",
            }
        )
        return report

    sampler = GeometrySampler3D(config)
    voxelized = sampler.voxelize(32)
    report = analyze_voxel_occupancy(voxelized["occupancy"])
    report.update(
        {
            "geometry_type": config.geometry_type,
            "quality_kind": "procedural_voxelized",
            "source_file": config.geometry_type,
            "allow_disconnected_components": config.geometry_type == "squid_proxy",
            "component_semantics": _procedural_component_semantics(config.geometry_type),
            "scope_note": "procedural diagnostic voxelization only",
        }
    )
    return report


class GeometryQualityGate:
    def __init__(self, strict=False):
        self.strict = bool(strict)

    def evaluate(self, report) -> dict:
        kind = str(report.get("quality_kind", ""))
        reasons = []
        warnings = []

        if kind == "mesh":
            self._evaluate_mesh(report, reasons, warnings)
        elif kind == "voxel":
            self._evaluate_voxel(report, reasons, warnings)
        else:
            self._evaluate_voxel(report, reasons, warnings)

        passed = len(reasons) == 0
        severity = "ok"
        if reasons:
            severity = "error"
        elif warnings:
            severity = "warning"

        return {
            "pass": bool(passed),
            "severity": severity,
            "reasons": reasons,
            "warnings": warnings,
            "strict": self.strict,
        }

    def _evaluate_mesh(self, report, reasons, warnings):
        if int(report.get("vertices_count", 0)) <= 0:
            reasons.append("mesh has no vertices")
        if int(report.get("faces_count", 0)) <= 0:
            reasons.append("mesh has no faces")
        if not bool(report.get("has_valid_face_indices", False)):
            reasons.append("mesh has invalid face indices")

        degenerate = int(report.get("degenerate_face_count", 0))
        boundary = int(report.get("boundary_edge_count", 0))
        nonmanifold = int(report.get("nonmanifold_edge_count", 0))
        duplicate = int(report.get("duplicate_vertex_count", 0))
        volume_abs = float(report.get("volume_abs", 0.0))

        if self.strict:
            if degenerate > 0:
                reasons.append("mesh has degenerate faces")
            if boundary > 0:
                reasons.append("mesh has boundary edges")
            if nonmanifold > 0:
                reasons.append("mesh has nonmanifold edges")
        else:
            if degenerate > 0:
                warnings.append("mesh has degenerate faces")
            if boundary > 0:
                warnings.append("mesh has boundary edges")
            if nonmanifold > 0:
                warnings.append("mesh has nonmanifold edges")

        if duplicate > 0:
            warnings.append("mesh has duplicate vertices")
        if volume_abs <= 0.0:
            warnings.append("mesh volume proxy is non-positive")

    def _evaluate_voxel(self, report, reasons, warnings):
        occupied = int(report.get("occupied_count", 0))
        components = int(report.get("connected_component_count", 0))
        if occupied == 0:
            reasons.append("voxel occupancy is empty")
        if components == 0:
            reasons.append("voxel occupancy has no connected components")

        if components > 1 and not bool(report.get("allow_disconnected_components", False)):
            warnings.append("voxel occupancy has multiple connected components")
        if bool(report.get("touches_domain_boundary", False)):
            warnings.append("voxel occupancy touches domain boundary")

        fraction = float(report.get("occupied_fraction", 0.0))
        if fraction < 1.0e-4 or fraction > 0.95:
            warnings.append("voxel occupied fraction is outside the recommended diagnostic range")


def _resolve_path(path):
    text = os.fspath(path)
    if os.path.isabs(text):
        return text
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    return os.path.join(root, text)


def _procedural_component_semantics(geometry_type: str) -> str:
    if geometry_type == "squid_proxy":
        return "static squid proxy appendage and fin components may be disconnected in coarse diagnostic voxelization"
    return ""
