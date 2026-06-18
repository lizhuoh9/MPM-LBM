from dataclasses import asdict, dataclass
import json
from typing import Tuple


VALID_GEOMETRY_TYPES = ("box", "ellipsoid", "squid_proxy")


def _as_float_tuple(values, name):
    if len(values) != 3:
        raise ValueError(f"{name} must contain exactly three values")
    out = tuple(float(v) for v in values)
    if any(not (value == value) for value in out):
        raise ValueError(f"{name} must be finite")
    return out


def _validate_bounds(lo, hi, lo_name, hi_name):
    if any(a >= b for a, b in zip(lo, hi)):
        raise ValueError(f"{lo_name} must be smaller than {hi_name} in every dimension")


def _validate_positive(values, name):
    if any(value <= 0.0 for value in values):
        raise ValueError(f"{name} values must be positive")


@dataclass(frozen=True)
class GeometryConfig:
    geometry_type: str = "box"
    n_particles: int = 4096

    domain_min: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    domain_max: Tuple[float, float, float] = (1.0, 1.0, 1.0)

    center: Tuple[float, float, float] = (0.5, 0.5, 0.5)
    scale: Tuple[float, float, float] = (0.3, 0.3, 0.3)

    box_min: Tuple[float, float, float] = (0.25, 0.35, 0.25)
    box_max: Tuple[float, float, float] = (0.55, 0.65, 0.55)

    ellipsoid_radii: Tuple[float, float, float] = (0.15, 0.20, 0.12)

    mantle_center: Tuple[float, float, float] = (0.50, 0.58, 0.50)
    mantle_radii: Tuple[float, float, float] = (0.16, 0.24, 0.12)
    head_center: Tuple[float, float, float] = (0.50, 0.36, 0.50)
    head_radii: Tuple[float, float, float] = (0.11, 0.10, 0.09)
    arm_length: float = 0.22
    arm_radius: float = 0.018
    fin_radius: float = 0.07

    p_rho: float = 1.0
    particles_per_axis_hint: int = 32
    deterministic: bool = True

    def __post_init__(self):
        if self.geometry_type not in VALID_GEOMETRY_TYPES:
            raise ValueError(f"geometry_type must be one of {VALID_GEOMETRY_TYPES}")
        if self.n_particles <= 0:
            raise ValueError("n_particles must be positive")
        if self.particles_per_axis_hint <= 0:
            raise ValueError("particles_per_axis_hint must be positive")
        if self.p_rho <= 0.0:
            raise ValueError("p_rho must be positive")
        if self.arm_length <= 0.0:
            raise ValueError("arm_length must be positive")
        if self.arm_radius <= 0.0:
            raise ValueError("arm_radius must be positive")
        if self.fin_radius <= 0.0:
            raise ValueError("fin_radius must be positive")

        for name in (
            "domain_min",
            "domain_max",
            "center",
            "scale",
            "box_min",
            "box_max",
            "ellipsoid_radii",
            "mantle_center",
            "mantle_radii",
            "head_center",
            "head_radii",
        ):
            object.__setattr__(self, name, _as_float_tuple(getattr(self, name), name))

        _validate_bounds(self.domain_min, self.domain_max, "domain_min", "domain_max")
        _validate_bounds(self.box_min, self.box_max, "box_min", "box_max")
        _validate_positive(self.scale, "scale")
        _validate_positive(self.ellipsoid_radii, "ellipsoid_radii")
        _validate_positive(self.mantle_radii, "mantle_radii")
        _validate_positive(self.head_radii, "head_radii")

    @classmethod
    def from_json(cls, path: str) -> "GeometryConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def to_dict(self) -> dict:
        data = asdict(self)
        tuple_fields = [
            "domain_min",
            "domain_max",
            "center",
            "scale",
            "box_min",
            "box_max",
            "ellipsoid_radii",
            "mantle_center",
            "mantle_radii",
            "head_center",
            "head_radii",
        ]
        for key in tuple_fields:
            data[key] = list(data[key])
        return data
