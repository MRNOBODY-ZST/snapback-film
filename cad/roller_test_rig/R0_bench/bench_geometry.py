"""Deterministic CadQuery export and nominal solid-intersection verification.

All input dimensions live in configs. Derived geometry is OWN_DESIGN/DERIVED.
Export bounding boxes are model coordinates, never measured real interfaces.
"""
import hashlib
import json
import platform
from pathlib import Path

import cadquery as cq


def block(x, y, z, centre):
    return cq.Workplane("XY").box(x, y, z).val().translate(centre)


def cylinder_x(diameter, length, centre):
    return cq.Workplane("YZ").circle(diameter / 2).extrude(length).val().translate(
        (centre[0] - length / 2, centre[1], centre[2]))


def cylinder_z(diameter, length, centre):
    return cq.Workplane("XY").circle(diameter / 2).extrude(length).val().translate(
        (centre[0], centre[1], centre[2] - length / 2))


def ring_x(outer, inner, length, centre):
    return cylinder_x(outer, length, centre).cut(cylinder_x(inner, length, centre))


def slot_z(width, centre_min, centre_max, x, height, bottom):
    """Y capsule slot: explicitly specified arc-centre coordinates."""
    middle = block(width, centre_max - centre_min, height,
                   (x, (centre_min + centre_max) / 2, bottom + height / 2))
    return middle.fuse(cylinder_z(width, height, (x, centre_min, bottom + height / 2)),
                       cylinder_z(width, height, (x, centre_max, bottom + height / 2)))


def part(name, shape, method="CNC_MACHINING_REQUIRED", reference=False):
    return {"name": name, "shape": shape, "manufacturing_method": method,
            "is_cots_envelope_reference": reference,
            "fdm_authorized_for_loaded_or_film_contact_use": False}


def bbox(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


def verify(parts, tolerance):
    issues, checks = [], []
    for p in parts:
        s = p["shape"]
        if not s.isValid() or len(s.Solids()) != 1 or s.Volume() <= 0:
            raise ValueError(f"{p['name']}: invalid/non-single/nonpositive solid")
        checks.append({"name": p["name"], "valid": True, "solid_count": 1,
                       "volume_mm3": s.Volume(), "model_bbox_mm": bbox(s)})
    for i, a in enumerate(parts):
        ba = bbox(a["shape"])
        for b in parts[i + 1:]:
            bb = bbox(b["shape"])
            if any(min(ba[k+3], bb[k+3]) <= max(ba[k], bb[k]) for k in range(3)):
                continue
            volume = a["shape"].intersect(b["shape"]).Volume()
            if volume > tolerance:
                issues.append({"a": a["name"], "b": b["name"], "volume_mm3": volume})
    return {"unintended_interferences": issues, "parts": checks,
            "checked_pairs": len(parts) * (len(parts) - 1) // 2,
            "scope": "RIGID_NOMINAL_CAD_ONLY; no real material, bolt, spring or film validation"}


def derived(value, unit, formula):
    return {"value": value, "unit": unit, "status": "DERIVED", "source": "OWN_DESIGN",
            "scope": "BENCH", "formula": formula}


def export(parts, report, config, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    compound = cq.Compound.makeCompound([p["shape"] for p in parts])
    step_path = directory / (config["fixture"] + "_R0_fixture_only.step")
    cq.exporters.export(compound, str(step_path))
    paths = [(step_path, "INDEPENDENT_FIXTURE_ASSEMBLY")]
    linear = config["parameters"]["stl_linear_tolerance"]["value"]
    angular = config["parameters"]["stl_angular_tolerance"]["value"]
    for p in parts:
        path = directory / (p["name"] + ".stl")
        cq.exporters.export(p["shape"], str(path), tolerance=linear, angularTolerance=angular)
        paths.append((path, "COTS_ENVELOPE_REFERENCE_NOT_FOR_MANUFACTURE" if
                      p["is_cots_envelope_reference"] else "FIXTURE_PART_MACHINING_REFERENCE"))
    restored = cq.importers.importStep(str(step_path)).val()
    error = max(abs(a-b) for a, b in zip(bbox(compound), bbox(restored)))
    if len(restored.Solids()) != len(parts) or error >= 0.001 or not restored.isValid():
        raise ValueError("STEP roundtrip changed solids or envelope")
    exports = []
    for path, role in paths:
        raw = path.read_bytes()
        project_root = Path(__file__).resolve().parents[3]
        try:
            relative_path = path.resolve().relative_to(project_root).as_posix()
        except ValueError:
            relative_path = path.resolve().as_posix()
        exports.append({"path": relative_path, "role": role, "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest(), "units": "mm"})
    manifest = {
        "mode": "TEST_FIXTURE_ONLY", "revision": "R0_BENCH",
        "scope": "INDEPENDENT_TEST_FIXTURE", "fixture": config["fixture"],
        "asset_path_base": "PROJECT_ROOT" if directory.resolve().is_relative_to(project_root) else "ABSOLUTE_PATHS",
        "manufacturing_status": "R0_FIXTURE_ONLY_PROTOTYPE",
        "physical_validation": False, "physical_camera_fit_validated": False,
        "physical_cartridge_fit_validated": False,
        "final_back_manufacturing_authorized": False,
        "fixture_manufacturing_authorized": True,
        "manufacturing_conditions": "Independent bench only; CNC load path, no FDM precision/contact surfaces; verify pilots/threads, actual fits and assembly against README before powered tests.",
        "software": {"python": platform.python_version(), "cadquery": cq.__version__},
        "input_parameters": config["parameters"],
        "coordinate_system": config["coordinate_system"],
        "derived_parameters": report["derived_parameters"],
        "geometry_checks": report,
        "step_roundtrip": {"valid": restored.isValid(), "solid_count": len(restored.Solids()),
                           "max_bbox_error_mm": error, "model_bbox_mm": bbox(restored)},
        "parts": [{k: v for k, v in p.items() if k != "shape"} for p in parts],
        "exports": exports
    }
    (directory / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest
