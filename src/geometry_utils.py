import numpy as np


def as_vec3(values, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.shape != (3,):
        raise ValueError(f"{name} must contain exactly three values")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    return array


def _as_points(points: np.ndarray) -> np.ndarray:
    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError("points must have shape (n, 3)")
    if not np.all(np.isfinite(array)):
        raise ValueError("points must be finite")
    return array


def inside_box(points: np.ndarray, box_min, box_max) -> np.ndarray:
    pts = _as_points(points)
    lo = as_vec3(box_min, "box_min")
    hi = as_vec3(box_max, "box_max")
    return np.all((pts >= lo) & (pts <= hi), axis=1)


def inside_ellipsoid(points: np.ndarray, center, radii) -> np.ndarray:
    pts = _as_points(points)
    c = as_vec3(center, "center")
    r = as_vec3(radii, "radii")
    if np.any(r <= 0.0):
        raise ValueError("radii must be positive")
    q = (pts - c) / r
    return np.einsum("ij,ij->i", q, q) <= 1.0


def distance_to_segment(points: np.ndarray, a, b) -> np.ndarray:
    pts = _as_points(points)
    start = as_vec3(a, "a")
    end = as_vec3(b, "b")
    segment = end - start
    segment_len2 = float(np.dot(segment, segment))
    if segment_len2 <= 0.0:
        return np.linalg.norm(pts - start, axis=1)

    t = np.clip(((pts - start) @ segment) / segment_len2, 0.0, 1.0)
    closest = start + t[:, None] * segment
    return np.linalg.norm(pts - closest, axis=1)


def inside_capsule(points: np.ndarray, a, b, radius: float) -> np.ndarray:
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    return distance_to_segment(points, a, b) <= float(radius)
