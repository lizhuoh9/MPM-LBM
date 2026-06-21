from collections import Counter

import numpy as np


def analyze_mesh(vertices, faces, eps=1.0e-12) -> dict:
    """
    Diagnostic-only mesh quality report.

    This is not production mesh repair. It records simple topology and
    geometry proxies for small synthetic fixtures before imported-geometry
    sampling.
    """
    vertices = np.asarray(vertices, dtype=np.float64)
    faces = np.asarray(faces, dtype=np.int64)
    eps = float(eps)

    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError("vertices must have shape (n, 3)")
    if faces.ndim != 2 or faces.shape[1] != 3:
        raise ValueError("faces must have shape (m, 3)")

    vertices_count = int(len(vertices))
    faces_count = int(len(faces))
    has_finite_vertices = bool(vertices_count > 0 and np.all(np.isfinite(vertices)))
    if not has_finite_vertices:
        raise ValueError("mesh vertices must be finite and non-empty")

    has_faces = faces_count > 0
    has_valid_face_indices = bool(has_faces and np.min(faces) >= 0 and np.max(faces) < vertices_count)

    bounds_min = vertices.min(axis=0)
    bounds_max = vertices.max(axis=0)
    bounds_span = bounds_max - bounds_min
    duplicate_vertex_count = int(vertices_count - len(np.unique(vertices, axis=0)))

    edge_counter = Counter()
    zero_area_face_count = 0
    repeated_index_count = 0
    surface_area = 0.0
    volume_terms = []

    if has_valid_face_indices:
        for face in faces:
            if len(set(int(i) for i in face)) < 3:
                repeated_index_count += 1

            tri = vertices[face]
            area = 0.5 * float(np.linalg.norm(np.cross(tri[1] - tri[0], tri[2] - tri[0])))
            if area <= eps:
                zero_area_face_count += 1
            surface_area += area

            volume_term = float(np.dot(tri[0], np.cross(tri[1], tri[2])) / 6.0)
            volume_terms.append(volume_term)

            for a, b in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
                edge_counter[tuple(sorted((int(a), int(b))))] += 1

    degenerate_face_count = int(max(zero_area_face_count, repeated_index_count))
    boundary_edge_count = int(sum(1 for count in edge_counter.values() if count == 1))
    nonmanifold_edge_count = int(sum(1 for count in edge_counter.values() if count > 2))
    unique_edge_count = int(len(edge_counter))
    is_watertight_proxy = bool(boundary_edge_count == 0 and nonmanifold_edge_count == 0 and has_valid_face_indices)
    volume_signed = float(sum(volume_terms))
    volume_abs = float(sum(abs(value) for value in volume_terms))
    orientation_consistent_proxy = bool(volume_abs > eps and abs(volume_signed) / volume_abs > 0.5)
    euler_characteristic = int(vertices_count - unique_edge_count + faces_count)
    stable = bool(has_valid_face_indices and degenerate_face_count == 0 and surface_area > 0.0)

    report = {
        "vertices_count": vertices_count,
        "faces_count": faces_count,
        "bounds_min_x": float(bounds_min[0]),
        "bounds_min_y": float(bounds_min[1]),
        "bounds_min_z": float(bounds_min[2]),
        "bounds_max_x": float(bounds_max[0]),
        "bounds_max_y": float(bounds_max[1]),
        "bounds_max_z": float(bounds_max[2]),
        "bounds_span_x": float(bounds_span[0]),
        "bounds_span_y": float(bounds_span[1]),
        "bounds_span_z": float(bounds_span[2]),
        "has_finite_vertices": has_finite_vertices,
        "has_valid_face_indices": has_valid_face_indices,
        "duplicate_vertex_count": duplicate_vertex_count,
        "degenerate_face_count": degenerate_face_count,
        "zero_area_face_count": int(zero_area_face_count),
        "boundary_edge_count": boundary_edge_count,
        "nonmanifold_edge_count": nonmanifold_edge_count,
        "is_watertight_proxy": is_watertight_proxy,
        "surface_area": float(surface_area),
        "volume_signed": volume_signed,
        "volume_abs": volume_abs,
        "orientation_consistent_proxy": orientation_consistent_proxy,
        "euler_characteristic": euler_characteristic,
        "stable": stable,
        "notes": "diagnostic proxy only; no production mesh repair or automatic remeshing",
    }
    return report
