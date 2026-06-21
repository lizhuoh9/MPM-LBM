import os

import numpy as np


def load_obj(path):
    resolved = _resolve_path(path)
    vertices = []
    faces = []
    with open(resolved, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if parts[0] == "v":
                if len(parts) < 4:
                    raise ValueError(f"invalid OBJ vertex line: {raw_line!r}")
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif parts[0] == "f":
                indices = [_parse_face_index(token) for token in parts[1:]]
                if len(indices) < 3:
                    raise ValueError(f"invalid OBJ face line: {raw_line!r}")
                for k in range(1, len(indices) - 1):
                    faces.append([indices[0], indices[k], indices[k + 1]])

    vertices = np.asarray(vertices, dtype=np.float64)
    faces = np.asarray(faces, dtype=np.int64)
    _validate_mesh(vertices, faces)
    return vertices, faces


def write_obj(path, vertices, faces):
    vertices = np.asarray(vertices, dtype=np.float64)
    faces = np.asarray(faces, dtype=np.int64)
    _validate_mesh(vertices, faces)
    resolved = _resolve_path(path)
    os.makedirs(os.path.dirname(resolved), exist_ok=True)
    with open(resolved, "w", encoding="utf-8") as f:
        f.write("# Generated synthetic Step 20 fixture\n")
        for vertex in vertices:
            f.write(f"v {vertex[0]:.9g} {vertex[1]:.9g} {vertex[2]:.9g}\n")
        for face in faces:
            a, b, c = face + 1
            f.write(f"f {a} {b} {c}\n")


def mesh_bounds(vertices):
    vertices = np.asarray(vertices, dtype=np.float64)
    if vertices.ndim != 2 or vertices.shape[1] != 3 or len(vertices) == 0:
        raise ValueError("vertices must have shape (n, 3)")
    if not np.all(np.isfinite(vertices)):
        raise ValueError("vertices must be finite")
    return vertices.min(axis=0), vertices.max(axis=0)


def normalize_vertices(
    vertices,
    domain_min=(0, 0, 0),
    domain_max=(1, 1, 1),
    padding=0.05,
    preserve_aspect_ratio=True,
):
    vertices = np.asarray(vertices, dtype=np.float64)
    bounds_min, bounds_max = mesh_bounds(vertices)
    domain_min = _as_vec3(domain_min, "domain_min")
    domain_max = _as_vec3(domain_max, "domain_max")
    padding = float(padding)
    if padding < 0.0 or padding >= 0.5:
        raise ValueError("padding must satisfy 0 <= padding < 0.5")
    if np.any(domain_min >= domain_max):
        raise ValueError("domain_min must be smaller than domain_max")

    src_span = bounds_max - bounds_min
    if np.any(src_span <= 0.0):
        raise ValueError("mesh bounds must have positive span")

    dst_span = domain_max - domain_min
    inner_min = domain_min + padding * dst_span
    inner_max = domain_max - padding * dst_span
    inner_span = inner_max - inner_min
    if np.any(inner_span <= 0.0):
        raise ValueError("padding leaves no interior domain")

    if preserve_aspect_ratio:
        scale = float(np.min(inner_span / src_span))
        scaled = (vertices - bounds_min[None, :]) * scale
        used_span = src_span * scale
        offset = inner_min + 0.5 * (inner_span - used_span)
        normalized = offset[None, :] + scaled
    else:
        normalized = inner_min[None, :] + (vertices - bounds_min[None, :]) * (inner_span / src_span)[None, :]

    if not np.all(np.isfinite(normalized)):
        raise ValueError("normalized vertices must be finite")
    if np.min(normalized) < -1.0e-8 or np.max(normalized) > 1.0 + 1.0e-8:
        raise ValueError("normalized vertices must stay inside [0, 1]^3")
    return normalized.astype(np.float64)


def _parse_face_index(token):
    head = token.split("/")[0]
    index = int(head)
    if index <= 0:
        raise ValueError("Step 20 OBJ parser supports positive 1-based indices only")
    return index - 1


def _validate_mesh(vertices, faces):
    if vertices.ndim != 2 or vertices.shape[1] != 3 or len(vertices) <= 0:
        raise ValueError("vertices must have shape (n, 3)")
    if faces.ndim != 2 or faces.shape[1] != 3 or len(faces) <= 0:
        raise ValueError("faces must have shape (m, 3)")
    if not np.all(np.isfinite(vertices)):
        raise ValueError("vertices must be finite")
    if np.min(faces) < 0 or np.max(faces) >= len(vertices):
        raise ValueError("face indices must be in range")


def _as_vec3(values, name):
    arr = np.asarray(values, dtype=np.float64)
    if arr.shape != (3,) or not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must contain three finite values")
    return arr


def _resolve_path(path):
    text = os.fspath(path)
    if os.path.isabs(text):
        return text
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    return os.path.join(root, text)
