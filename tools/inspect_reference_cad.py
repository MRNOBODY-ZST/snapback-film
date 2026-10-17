"""Inspect archived reference files only; never promote source CAD into measurements."""
from __future__ import annotations
import hashlib
import json
import math
import re
import struct
import sys
import zipfile
from pathlib import Path

def inspect_file(path: Path) -> dict:
    data = path.read_bytes()
    result = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
              "physical_validation": False, "manufacturing_authorized": False}
    ext = path.suffix.lower()
    if ext == ".stl":
        triangles = []
        if len(data) >= 84:
            count = struct.unpack_from("<I", data, 80)[0]
        else:
            count = 0
        if len(data) == 84 + 50 * count and count > 0:
            result["format"] = "binary STL"
            for i in range(count):
                face = struct.unpack_from("<12fH", data, 84 + 50*i)
                triangles.append([face[3:6], face[6:9], face[9:12]])
        else:
            result["format"] = "ASCII STL"
            vertices = [tuple(float(v) for v in match) for match in re.findall(
                r"vertex\s+([-+\d.eE]+)\s+([-+\d.eE]+)\s+([-+\d.eE]+)",
                data.decode("ascii"))]
            if not vertices or len(vertices) % 3:
                raise ValueError(f"Invalid STL structure: {path}")
            triangles = [vertices[i:i+3] for i in range(0, len(vertices), 3)]
        pts = [p for face in triangles for p in face]
        if not all(math.isfinite(v) for p in pts for v in p):
            raise ValueError(f"Non-finite STL vertex: {path}")
        lo = [min(p[k] for p in pts) for k in range(3)]
        hi = [max(p[k] for p in pts) for k in range(3)]
        result.update(triangles=len(triangles), min_xyz=lo, max_xyz=hi,
                      extents_xyz=[hi[k]-lo[k] for k in range(3)],
                      unit="unitless model coordinates",
                      intended_unit="mm assumed from creator printing context; verify before use",
                      quantity_provenance="DERIVED", physical_applicability="ESTIMATED",
                      coordinate_registration_to_project=None)
    elif ext in {".step", ".stp"}:
        text = data.decode("utf-8", errors="replace")
        if not text.startswith("ISO-10303-21;") or not text.rstrip().endswith("END-ISO-10303-21;"):
            raise ValueError(f"Invalid STEP envelope: {path}")
        result.update(format="STEP Part 21 envelope",
                      entity_count=len(re.findall(r"(?m)^#\d+\s*=", text)),
                      declared_si_units=re.findall(r"SI_UNIT\([^;]*", text),
                      solids_not_imported_or_validated=True)
    elif ext == ".f3d":
        with zipfile.ZipFile(path) as archive:
            if sum(i.file_size for i in archive.infolist()) > 256*1024*1024:
                raise ValueError("Unexpectedly large archive")
            failed = archive.testzip()
            if failed:
                raise ValueError(f"Invalid F3D ZIP member: {failed}")
            result.update(format="Fusion archive", member_count=len(archive.infolist()),
                          native_geometry_not_evaluated=True)
    else:
        result["format"] = "source notice"
    return result

def inspect_archive(root: Path) -> dict:
    ref = root / "cad/reference"
    manifest = json.loads((ref / "source-manifest.json").read_text(encoding="utf-8"))
    rows = []
    for asset in manifest["assets"]:
        path = (root / asset["path"]).resolve()
        if not path.is_relative_to(ref.resolve()):
            raise ValueError("Reference path outside archive")
        row = dict(asset)
        row["inspection"] = inspect_file(path)
        if row["inspection"]["sha256"] != asset["sha256"]:
            raise ValueError(f"Reference hash mismatch: {asset['path']}")
        rows.append(row)
    return {"scope": "Reference file integrity and nominal model geometry; no physical verification",
            "date": "2026-10-07", "assets": rows,
            "feasibility_result": "UNCERTAIN — MEASUREMENT REQUIRED"}

if __name__ == "__main__":
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    print(json.dumps(inspect_archive(root), ensure_ascii=False, indent=2))
