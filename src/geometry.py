import math

import numpy as np

from .geometry_config import GeometryConfig
from .geometry_import import ImportedGeometrySampler3D
from .geometry_utils import as_vec3, inside_box, inside_capsule, inside_ellipsoid


class GeometrySampler3D:
    def __init__(self, config: GeometryConfig):
        self.config = config
        self.domain_min = as_vec3(config.domain_min, "domain_min")
        self.domain_max = as_vec3(config.domain_max, "domain_max")
        self.domain_span = self.domain_max - self.domain_min
        self.domain_volume = float(np.prod(self.domain_span))
        self.imported = ImportedGeometrySampler3D(config) if config.geometry_type in {"voxel", "mesh"} else None

    def inside(self, points: np.ndarray) -> np.ndarray:
        if self.imported is not None:
            return self.imported.inside(points)
        if self.config.geometry_type == "box":
            return inside_box(points, self.config.box_min, self.config.box_max)
        if self.config.geometry_type == "ellipsoid":
            return inside_ellipsoid(points, self.config.center, self.config.ellipsoid_radii)
        if self.config.geometry_type == "squid_proxy":
            masks = self.component_masks(points)
            union = np.zeros(len(points), dtype=bool)
            for mask in masks.values():
                union |= mask
            return union
        raise ValueError(f"unsupported geometry_type: {self.config.geometry_type}")

    def component_masks(self, points: np.ndarray) -> dict:
        if self.config.geometry_type != "squid_proxy":
            return {self.config.geometry_type: self.inside(points)}

        pts = np.asarray(points, dtype=np.float64)
        mantle = inside_ellipsoid(pts, self.config.mantle_center, self.config.mantle_radii)
        head = inside_ellipsoid(pts, self.config.head_center, self.config.head_radii)

        mantle_center = as_vec3(self.config.mantle_center, "mantle_center")
        mantle_radii = as_vec3(self.config.mantle_radii, "mantle_radii")
        fin_radii = np.array([self.config.fin_radius, 0.055, 0.030], dtype=np.float64)
        left_fin_center = mantle_center + np.array([-mantle_radii[0] * 0.88, 0.025, 0.0])
        right_fin_center = mantle_center + np.array([mantle_radii[0] * 0.88, 0.025, 0.0])
        left_fin = inside_ellipsoid(pts, left_fin_center, fin_radii)
        right_fin = inside_ellipsoid(pts, right_fin_center, fin_radii)

        head_center = as_vec3(self.config.head_center, "head_center")
        arm_starts = self._arm_start_points(head_center)
        arm_ends = self._arm_end_points(head_center)
        arms = np.zeros(len(pts), dtype=bool)
        for start, end in zip(arm_starts, arm_ends):
            arms |= inside_capsule(pts, start, end, self.config.arm_radius)

        return {
            "mantle": mantle,
            "head": head,
            "left_fin": left_fin,
            "right_fin": right_fin,
            "arms": arms,
        }

    def sample_particles(self) -> dict:
        if self.imported is not None:
            return self.imported.sample_particles()
        candidates, inside_mask, resolution = self._find_inside_candidates()
        inside_points = candidates[inside_mask]
        selected = self._select_deterministic_subset(inside_points, self.config.n_particles)

        geometry_volume = self._estimate_volume(int(np.count_nonzero(inside_mask)), resolution)
        vol0 = np.full(self.config.n_particles, geometry_volume / self.config.n_particles, dtype=np.float32)
        mass = vol0 * np.float32(self.config.p_rho)

        stats = {
            "geometry_type": self.config.geometry_type,
            "candidate_resolution": int(resolution),
            "candidate_count": int(len(candidates)),
            "accepted_count": int(len(inside_points)),
            "particle_count": int(len(selected)),
            "geometry_volume": float(geometry_volume),
            "deterministic": bool(self.config.deterministic),
        }
        if self.config.geometry_type == "squid_proxy":
            masks = self.component_masks(selected)
            stats.update({f"{name}_particle_count": int(np.count_nonzero(mask)) for name, mask in masks.items()})
            stats["scope_note"] = "procedural squid proxy geometry, not anatomical or validated squid geometry"

        return {
            "x": selected.astype(np.float32),
            "vol0": vol0,
            "mass": mass.astype(np.float32),
            "geometry_volume": float(geometry_volume),
            "sampling_stats": stats,
        }

    def voxelize(self, n_grid: int) -> dict:
        if self.imported is not None:
            return self.imported.voxelize(n_grid)
        if n_grid <= 0:
            raise ValueError("n_grid must be positive")
        coords_1d = (np.arange(n_grid, dtype=np.float64) + 0.5) / float(n_grid)
        grid = np.stack(np.meshgrid(coords_1d, coords_1d, coords_1d, indexing="ij"), axis=-1)
        points = grid.reshape(-1, 3)
        mask = self.inside(points).reshape(n_grid, n_grid, n_grid)
        occupancy = mask.astype(np.int8)
        occupied_count = int(np.count_nonzero(occupancy))
        cell_volume = self.domain_volume / float(n_grid**3)
        return {
            "occupancy": occupancy,
            "phi": occupancy.astype(np.float32),
            "occupied_count": occupied_count,
            "geometry_volume_estimate": float(occupied_count * cell_volume),
        }

    def _find_inside_candidates(self):
        min_fraction = 0.015 if self.config.geometry_type != "box" else 0.025
        resolution = max(
            int(self.config.particles_per_axis_hint),
            int(math.ceil((self.config.n_particles / min_fraction) ** (1.0 / 3.0))),
        )
        resolution = max(resolution, 16)

        for _ in range(8):
            candidates = self._candidate_points(resolution)
            inside_mask = self.inside(candidates)
            if int(np.count_nonzero(inside_mask)) >= self.config.n_particles:
                return candidates, inside_mask, resolution
            resolution = int(math.ceil(resolution * 1.35))

        accepted = int(np.count_nonzero(inside_mask))
        raise RuntimeError(
            f"geometry_type={self.config.geometry_type} produced only {accepted} "
            f"inside candidates for {self.config.n_particles} particles"
        )

    def _candidate_points(self, resolution: int) -> np.ndarray:
        coords = self.domain_min + (np.arange(resolution, dtype=np.float64) + 0.5)[:, None] * (
            self.domain_span / float(resolution)
        )
        x, y, z = np.meshgrid(coords[:, 0], coords[:, 1], coords[:, 2], indexing="ij")
        return np.column_stack((x.ravel(), y.ravel(), z.ravel()))

    def _select_deterministic_subset(self, points: np.ndarray, count: int) -> np.ndarray:
        if len(points) < count:
            raise RuntimeError(f"not enough inside points: have {len(points)}, need {count}")
        if len(points) == count:
            return points.copy()
        indices = np.linspace(0, len(points) - 1, count, dtype=np.int64)
        return points[indices].copy()

    def _estimate_volume(self, accepted_count: int, resolution: int) -> float:
        return self.domain_volume * float(accepted_count) / float(resolution**3)

    def _arm_start_points(self, head_center):
        offsets = [
            (-0.055, 0.000),
            (-0.035, -0.035),
            (-0.015, 0.035),
            (0.015, -0.035),
            (0.035, 0.035),
            (0.055, 0.000),
        ]
        return [head_center + np.array([dx, -0.055, dz], dtype=np.float64) for dx, dz in offsets]

    def _arm_end_points(self, head_center):
        offsets = [
            (-0.090, 0.000),
            (-0.060, -0.060),
            (-0.025, 0.060),
            (0.025, -0.060),
            (0.060, 0.060),
            (0.090, 0.000),
        ]
        return [head_center + np.array([dx, -self.config.arm_length, dz], dtype=np.float64) for dx, dz in offsets]
