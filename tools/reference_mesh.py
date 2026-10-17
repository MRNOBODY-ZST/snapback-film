"""Preserve source mesh geometry for CAD reference; never qualify physical dimensions."""
from __future__ import annotations

import math
import struct
from collections import Counter
from pathlib import Path


def read_binary_stl(path: Path) -> list:
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError("STL header is incomplete")
    count = struct.unpack_from("<I", data, 80)[0]
    if not count or len(data) != 84 + count * 50:
        raise ValueError("Expected complete binary STL")
    triangles = []
    for i in range(count):
        face = struct.unpack_from("<12fH", data, 84 + 50 * i)
        triangles.append((face[3:6], face[6:9], face[9:12]))
    return triangles


def validate_closed_mesh(triangles: list) -> dict:
    if not triangles:
        raise ValueError("No source triangles")
    directed, undirected = Counter(), Counter()
    pts, volume6 = [], 0.0
    for triangle in triangles:
        if len(triangle) != 3:
            raise ValueError("Triangle must have three vertices")
        vertices = [tuple(p) for p in triangle]
        if any(len(p) != 3 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in p) for p in vertices):
            raise ValueError("Finite XYZ coordinates are required")
        p, q, r = vertices
        a = [q[k] - p[k] for k in range(3)]
        b = [r[k] - p[k] for k in range(3)]
        normal = (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
        if sum(v*v for v in normal) == 0:
            raise ValueError("Degenerate source triangle")
        for k in range(3):
            u, v = vertices[k], vertices[(k+1) % 3]
            directed[(u, v)] += 1
            undirected[tuple(sorted((u, v)))] += 1
        volume6 += p[0]*(q[1]*r[2]-q[2]*r[1]) - p[1]*(q[0]*r[2]-q[2]*r[0]) + p[2]*(q[0]*r[1]-q[1]*r[0])
        pts.extend(vertices)
    if any(n != 2 for n in undirected.values()) or any(directed[(v, u)] != n for (u, v), n in directed.items()):
        raise ValueError("Source mesh must be closed with consistent triangle winding")
    if volume6 == 0 or not math.isfinite(volume6):
        raise ValueError("Source mesh has no finite enclosed volume")
    lo = [min(p[k] for p in pts) for k in range(3)]
    hi = [max(p[k] for p in pts) for k in range(3)]
    return {"triangle_count": len(triangles), "min_xyz": lo, "max_xyz": hi,
            "extents_xyz": [hi[k]-lo[k] for k in range(3)],
            "signed_volume_model_units_cubed": volume6/6, "physical_validation": False,
            "unit": "source model coordinate; STL has no unit metadata"}


def transform_mesh(triangles: list, scale_xyz: list, translation_xyz: list) -> list:
    if len(scale_xyz) != 3 or len(translation_xyz) != 3:
        raise ValueError("Explicit XYZ scale and translation required")
    for value in scale_xyz:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError("Reference scale must be known, finite and positive")
    for value in translation_xyz:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("Reference translation must be known and finite")
    return [tuple(tuple(p[k]*scale_xyz[k]+translation_xyz[k] for k in range(3)) for p in tri) for tri in triangles]


def make_cadquery_solid(triangles: list):
    """Faceted BREP of the source reference; CAD kernel assumes mm interpretation."""
    import cadquery as cq
    validate_closed_mesh(triangles)
    faces = [cq.Face.makeFromWires(cq.Wire.makePolygon(list(tri), close=True)) for tri in triangles]
    solid = cq.Solid.makeSolid(cq.Shell.makeShell(faces))
    if not solid.isValid() or solid.Volume() <= 0:
        raise ValueError("Reference source cannot form a valid positive-volume CAD solid")
    return solid
