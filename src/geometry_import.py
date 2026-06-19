import math

import numpy as np

from .mesh_io import load_obj, mesh_bounds, normalize_vertices
from .voxel_io import load_voxel_geometry


class ImportedGeometrySampler3D:
    """
    Small synthetic mesh/voxel import helper for Step 20.

    This is a geometry-ingestion scaffold, not production mesh repair and not
    real squid validation. It feeds the existing MPM particle initialization
    and LBM projection paths without changing FSI coupling physics.
    """

    def __init__(self, config):
        self.config = config
        self.domain_min = _as_vec3(config.domain_min, "domain_min")
        self.domain_max = _as_vec3(config.domain_max, "domain_max")
        self.domain_span = self.domain_max - self.domain_min
        self.domain_volume = float(np.prod(self.domain_span))

        self.voxel_geometry = None
        self.mesh_vertices = None
        self.mesh_faces = None
        self.source_stats = {}

        if config.geometry_type == "voxel":
            self.voxel_geometry = load_voxel_geometry(
                config.geometry_file,
                metadata_path=config.metadata_file,
                threshold=config.voxel_threshold,
            )
            self.source_stats = dict(self.voxel_geometry.stats)
        elif config.geometry_type == "mesh":
            vertices, faces = load_obj(config.geometry_file)
            if config.normalize_to_domain:
                vertices = normalize_vertices(
                    vertices,
                    domain_min=config.domain_min,
                    domain_max=config.domain_max,
                    padding=config.padding,
                    preserve_aspect_ratio=config.preserve_aspect_ratio,
                )
            self.mesh_vertices = vertices
            self.mesh_faces = faces
            bmin, bmax = mesh_bounds(vertices)
            self.source_stats = {
                "vertices_count": int(len(vertices)),
                "faces_count": int(len(faces)),
                "bounds_min": [float(v) for v in bmin],
                "bounds_max": [float(v) for v in bmax],
                "mesh_inside_method": config.mesh_inside_method,
            }
        else:
            raise ValueError(f"unsupported imported geometry_type: {config.geometry_type}")

    def inside(self, points):
        pts = np.asarray(points, dtype=np.float64)
        if pts.ndim != 2 or pts.shape[1] != 3:
            raise ValueError("points must have shape (n, 3)")
        if not np.all(np.isfinite(pts)):
            raise ValueError("points must be finite")
        if self.config.geometry_type == "voxel":
            return self._inside_voxel(pts)
        if self.config.geometry_type == "mesh":
            return self._inside_mesh(pts)
        raise ValueError(f"unsupported imported geometry_type: {self.config.geometry_type}")

    def sample_particles(self):
        candidates, inside_mask, resolution = self._find_inside_candidates()
        inside_points = candidates[inside_mask]
        selected = self._select_deterministic_subset(inside_points, self.config.n_particles)

        geometry_volume = self._estimate_volume(int(np.count_nonzero(inside_mask)), resolution)
        vol0 = np.full(self.config.n_particles, geometry_volume / self.config.n_particles, dtype=np.float32)
        mass = vol0 * np.float32(self.config.p_rho)

        stats = self.get_stats()
        stats.update(
            {
                "candidate_resolution": int(resolution),
                "candidate_count": int(len(candidates)),
                "accepted_count": int(len(inside_points)),
                "particle_count": int(len(selected)),
                "geometry_volume": float(geometry_volume),
                "deterministic": bool(self.config.deterministic),
                "imported_geometry_note": (
                    "Step 20 synthetic imported geometry scaffold, not real squid validation "
                    "and not production mesh repair"
                ),
            }
        )

        return {
            "x": selected.astype(np.float32),
            "vol0": vol0,
            "mass": mass.astype(np.float32),
            "geometry_volume": float(geometry_volume),
            "sampling_stats": stats,
        }

    def voxelize(self, n_grid):
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

    def get_stats(self):
        stats = {
            "geometry_type": self.config.geometry_type,
            "source_file": self.config.geometry_file,
        }
        stats.update(self.source_stats)
        return stats

    def _inside_voxel(self, points):
        occupancy = self.voxel_geometry.occupancy
        shape = np.asarray(occupancy.shape, dtype=np.float64)
        normalized = (points - self.domain_min[None, :]) / self.domain_span[None, :]
        domain_mask = np.all((normalized >= 0.0) & (normalized <= 1.0), axis=1)
        clipped = np.clip(normalized, 0.0, np.nextafter(1.0, 0.0))
        idx = np.floor(clipped * shape[None, :]).astype(np.int64)
        inside = occupancy[idx[:, 0], idx[:, 1], idx[:, 2]]
        return inside & domain_mask

    def _inside_mesh(self, points):
        if self.config.mesh_inside_method == "voxelized":
            return self._inside_mesh_ray_cast(points)
        if self.config.mesh_inside_method == "ray_cast":
            return self._inside_mesh_ray_cast(points)
        raise ValueError(f"unsupported mesh_inside_method: {self.config.mesh_inside_method}")

    def _inside_mesh_ray_cast(self, points):
        vertices = self.mesh_vertices
        faces = self.mesh_faces
        direction = np.array([1.0, 0.0, 0.0], dtype=np.float64)
        unique_hits = [[] for _ in range(len(points))]
        eps = 1.0e-9

        for face in faces:
            tri = vertices[face]
            edge1 = tri[1] - tri[0]
            edge2 = tri[2] - tri[0]
            h = np.cross(direction, edge2)
            a = float(np.dot(edge1, h))
            if abs(a) < eps:
                continue
            f = 1.0 / a
            s = points - tri[0][None, :]
            u = f * np.einsum("ij,j->i", s, h)
            q = np.cross(s, edge1)
            v = f * np.einsum("j,ij->i", direction, q)
            t = f * np.einsum("j,ij->i", edge2, q)
            mask = (u >= -eps) & (v >= -eps) & ((u + v) <= 1.0 + eps) & (t > eps)
            for idx in np.nonzero(mask)[0]:
                value = float(t[idx])
                hits = unique_hits[idx]
                if not any(abs(value - existing) <= 1.0e-7 for existing in hits):
                    hits.append(value)

        return np.asarray([len(hits) % 2 == 1 for hits in unique_hits], dtype=bool)

    def _find_inside_candidates(self):
        min_fraction = 0.015
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

    def _candidate_points(self, resolution):
        coords = self.domain_min + (np.arange(resolution, dtype=np.float64) + 0.5)[:, None] * (
            self.domain_span / float(resolution)
        )
        x, y, z = np.meshgrid(coords[:, 0], coords[:, 1], coords[:, 2], indexing="ij")
        return np.column_stack((x.ravel(), y.ravel(), z.ravel()))

    def _select_deterministic_subset(self, points, count):
        if len(points) < count:
            raise RuntimeError(f"not enough inside points: have {len(points)}, need {count}")
        if len(points) == count:
            return points.copy()
        indices = np.linspace(0, len(points) - 1, count, dtype=np.int64)
        return points[indices].copy()

    def _estimate_volume(self, accepted_count, resolution):
        return self.domain_volume * float(accepted_count) / float(resolution**3)


def _as_vec3(values, name):
    arr = np.asarray(values, dtype=np.float64)
    if arr.shape != (3,) or not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must contain three finite values")
    return arr
