"""Parameterized source-reference preview, not a measured cartridge engineering model.

Geometry is derived from Jocelyn Girard's LGPL-2.1 source STL. Preview exports
retain that source attribution/license; the original STL remains unchanged.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from reference_mesh import read_binary_stl, transform_mesh, validate_closed_mesh, make_cadquery_solid


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true", help="Write reference-only faceted STEP/STL; never a manufacturing release")
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("instax_square_cartridge.reference-config.json"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config.get("manufacturing_authorized") is not False:
        raise ValueError("This reference workflow cannot authorize manufacturing")
    manifest = json.loads((ROOT / "cad/reference/source-manifest.json").read_text(encoding="utf-8"))
    asset = next(a for a in manifest["assets"] if a["source_id"] == "C01" and a["path"].lower().endswith(".stl"))
    path = ROOT / asset["path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != asset["sha256"]:
        raise ValueError("Source reference hash mismatch")
    tris = transform_mesh(read_binary_stl(path), config["reference_scale_xyz"], config["reference_translation_xyz"])
    report = {"mode": "SOURCE_REFERENCE_PREVIEW", "source_path": asset["path"],
              "source_sha256": asset["sha256"], "source_page": asset["source_page"],
              "license": asset["license"], "manufacturing_authorized": False,
              "physical_validation": False, "geometry": validate_closed_mesh(tris),
              "mm_interpretation": "ESTIMATED from original printing context; not verified physical scale",
              "coordinate_registration_to_R": None, "coordinate_registration_to_P": None,
              "effective_emulsion_plane": "UNKNOWN — MEASUREMENT_REQUIRED", "exports": []}
    if args.preview:
        import cadquery as cq
        solid = make_cadquery_solid(tris)
        out_dir = ROOT / "cad/cartridge/R0_reference_only"
        out_dir.mkdir(parents=True, exist_ok=True)
        for ext in ("step", "stl"):
            out = out_dir / f"instax_square_cartridge.SOURCE_REFERENCE.{ext}"
            cq.exporters.export(solid, str(out))
            report["exports"].append({"path": out.relative_to(ROOT).as_posix(),
                                      "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
                                      "bytes": out.stat().st_size})
        report["cad_kernel_validation"] = {"valid_nominal_solid": solid.isValid(), "nominal_volume_under_mm_assumption_mm3": solid.Volume()}
        (out_dir / "preview-manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
