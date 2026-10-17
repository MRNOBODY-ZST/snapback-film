"""R0 adjustable roller-alignment bench; no camera/cartridge geometry.

Run with project .tools-venv Python. Cylinders are rigid alignment gauges, not
qualified developer-contact rollers. Four bearing rings are COTS envelopes.
"""
import argparse
import json
from pathlib import Path

from fixture_contract import validate
from bench_geometry import block, cylinder_x, cylinder_z, ring_x, part, verify, derived, export

HERE = Path(__file__).resolve().parent


def build(config):
    v = validate(config)
    for key, value in v.items():
        if value <= 0:
            raise ValueError(f"{key}: positive bench dimension required")
    guide_min = v["guide_bottom_z"] + v["slider_height_z"] / 2
    guide_max = v["guide_bottom_z"] + v["guide_height_z"] - v["slider_height_z"] / 2
    upper = v["upper_center_z"]
    lower = v["lower_center_z"]
    if not guide_min <= upper <= guide_max:
        raise ValueError("upper carrier centre outside machined guide travel")
    if not v["stop_range_min"] <= v["stop_height_z"] <= v["stop_range_max"]:
        raise ValueError("stop insert outside own adjustable stock range")
    if upper - v["slider_height_z"] / 2 < v["guide_bottom_z"] + v["stop_height_z"]:
        raise ValueError("upper carrier below installed guide stop insert")
    separation = upper - lower - v["gauge_diameter"]
    if separation < 0:
        raise ValueError("rigid gauge barrels intersect; actual compliant nip remains unknown")
    clearance = (v["guide_width_y"] - v["slider_width_y"]) / 2
    if clearance <= 0:
        raise ValueError("guide lacks positive nominal side clearance")
    if v["bearing_pocket_diameter"] <= v["bearing_outer_diameter"]:
        raise ValueError("bearing pocket clearance candidate must be positive")
    if v["gauge_face_length"] / 2 >= v["frame_center_x"] - v["frame_x"] / 2:
        raise ValueError("gauge barrel intersects support frame")
    extra = v["cut_extra"]
    parts = []
    base = block(v["base_x"], v["base_y"], v["base_z"], (0, 0, v["base_z"] / 2))
    for sign in (-1, 1):
        for y in (-v["frame_bolt_y"], v["frame_bolt_y"]):
            base = base.cut(cylinder_z(v["structural_clearance_diameter"], v["base_z"] + 2 * extra,
                                      (sign * v["frame_center_x"], y, v["base_z"] / 2)))
    parts.append(part("OWN_base", base))
    frame_top = v["base_z"] + v["frame_z"]
    bearing_centre_local_x = v["frame_x"] / 2 - v["bearing_width"] / 2
    pocket_centre_local_x = v["frame_x"] / 2 - v["bearing_pocket_depth"] / 2

    def bearing_pocket(s, centre_z):
        s = s.cut(cylinder_x(v["shaft_clearance_diameter"], v["frame_x"] + 2 * extra, (0, 0, centre_z)))
        return s.cut(cylinder_x(v["bearing_pocket_diameter"], v["bearing_pocket_depth"] + extra,
                               (pocket_centre_local_x + extra / 2, 0, centre_z)))

    def cap_holes(s, centre_z, diameter, depth, centre_x):
        for y in (-v["cap_bolt_y"], v["cap_bolt_y"]):
            for dz in (-v["cap_bolt_z"], v["cap_bolt_z"]):
                s = s.cut(cylinder_x(diameter, depth, (centre_x, y, centre_z + dz)))
        return s

    for sign, side in ((-1, "L"), (1, "R")):
        frame = block(v["frame_x"], v["frame_y"], v["frame_z"],
                      (0, 0, v["base_z"] + v["frame_z"] / 2))
        frame = frame.cut(block(v["frame_x"] + 2 * extra, v["guide_width_y"], v["guide_height_z"],
                                (0, 0, v["guide_bottom_z"] + v["guide_height_z"] / 2)))
        frame = bearing_pocket(frame, lower)
        frame = cap_holes(frame, lower, v["cap_pilot_diameter"], v["cap_pilot_depth"] + extra,
                          v["frame_x"] / 2 - v["cap_pilot_depth"] / 2 + extra / 2)
        for y in (-v["frame_bolt_y"], v["frame_bolt_y"]):
            frame = frame.cut(cylinder_z(v["structural_pilot_diameter"], v["structural_pilot_depth"] + extra,
                                        (0, y, v["base_z"] + v["structural_pilot_depth"] / 2 - extra / 2)))
        for y in (-v["bridge_bolt_y"], v["bridge_bolt_y"]):
            frame = frame.cut(cylinder_z(v["structural_pilot_diameter"], v["structural_pilot_depth"] + extra,
                                        (0, y, frame_top - v["structural_pilot_depth"] / 2 + extra / 2)))
        carrier = block(v["frame_x"], v["slider_width_y"], v["slider_height_z"], (0, 0, upper))
        carrier = bearing_pocket(carrier, upper)
        carrier = cap_holes(carrier, upper, v["cap_pilot_diameter"], v["cap_pilot_depth"] + extra,
                            v["frame_x"] / 2 - v["cap_pilot_depth"] / 2 + extra / 2)
        carrier_top = upper + v["slider_height_z"] / 2
        carrier = carrier.cut(cylinder_z(v["spring_seat_diameter"], v["spring_seat_depth"] + extra,
                                          (0, 0, carrier_top - v["spring_seat_depth"] / 2 + extra / 2)))
        bridge = block(v["bridge_x"], v["bridge_y"], v["bridge_z"],
                       (0, 0, frame_top + v["bridge_z"] / 2))
        bridge = bridge.cut(cylinder_z(v["adjuster_pilot_diameter"], v["bridge_z"] + 2 * extra,
                                      (0, 0, frame_top + v["bridge_z"] / 2)))
        for y in (-v["bridge_bolt_y"], v["bridge_bolt_y"]):
            bridge = bridge.cut(cylinder_z(v["structural_clearance_diameter"], v["bridge_z"] + 2 * extra,
                                          (0, y, frame_top + v["bridge_z"] / 2)))
        stop = block(v["frame_x"], v["stop_y"], v["stop_height_z"],
                     (0, 0, v["guide_bottom_z"] + v["stop_height_z"] / 2))

        def place(s):
            if sign == -1:
                s = s.rotate((0, 0, 0), (0, 0, 1), 180)
            return s.translate((sign * v["frame_center_x"], 0, 0))

        for label, s in (("frame", frame), ("carrier", carrier), ("bridge", bridge), ("stop_insert", stop)):
            parts.append(part(f"OWN_{side}_{label}", place(s)))
        for label, z, height in (("lower", lower, v["lower_cap_z"]), ("upper", upper, v["upper_cap_z"])):
            cap_x = v["frame_x"] / 2 + v["cap_x"] / 2
            cap = block(v["cap_x"], v["cap_y"], height, (cap_x, 0, z))
            cap = cap.cut(cylinder_x(v["cap_shaft_clearance"], v["cap_x"] + 2 * extra, (cap_x, 0, z)))
            cap = cap_holes(cap, z, v["cap_clearance_diameter"], v["cap_x"] + 2 * extra, cap_x)
            parts.append(part(f"OWN_{side}_{label}_bearing_cap", place(cap)))
            bearing = ring_x(v["bearing_outer_diameter"], v["bearing_bore"], v["bearing_width"],
                             (bearing_centre_local_x, 0, z))
            parts.append(part(f"REF_COTS_B608ZZ_{side}_{label}", place(bearing), "PURCHASE_COTS_NOT_PRINT", True))
            collar = ring_x(v["collar_diameter"], v["collar_bore"], v["collar_width"],
                            (sign * v["collar_center_x"], 0, z))
            collar = collar.cut(cylinder_z(v["cap_pilot_diameter"], v["collar_diameter"] / 2 + extra,
                                           (sign * v["collar_center_x"], 0, z + v["collar_diameter"] / 4 + extra / 2)))
            parts.append(part(f"OWN_{side}_{label}_axial_collar", collar))
    for label, z in (("lower", lower), ("upper", upper)):
        gauge = cylinder_x(v["gauge_diameter"], v["gauge_face_length"], (0, 0, z)).fuse(
            cylinder_x(v["shaft_nominal_diameter"], v["shaft_length"], (0, 0, z)))
        parts.append(part(f"OWN_{label}_rigid_alignment_gauge_NOT_developer_roller", gauge))
    report = verify(parts, v["intersection_volume_tolerance"])
    if report["unintended_interferences"]:
        raise ValueError(f"Unintended nominal fixture interference: {report['unintended_interferences']}")
    report.update({"guide_side_clearance_each_mm": clearance,
                   "neutral_gauge_surface_separation_mm": separation,
                   "derived_parameters": {
                       "bare_carrier_min_z": derived(guide_min, "mm", "guide_bottom_z + slider_height_z/2"),
                       "bare_carrier_max_z": derived(guide_max, "mm", "guide_bottom_z + guide_height_z - slider_height_z/2"),
                       "bare_carrier_travel": derived(guide_max-guide_min, "mm", "guide_height_z - slider_height_z"),
                       "installed_stop_carrier_min_z": derived(guide_min+v["stop_height_z"], "mm", "bare_carrier_min_z + stop_height_z"),
                       "nominal_side_clearance_each": derived(clearance, "mm", "(guide_width_y-slider_width_y)/2"),
                       "parked_dummy_surface_separation": derived(separation, "mm", "upper_center_z-lower_center_z-gauge_diameter; NOT actual_nip_gap"),
                       "bearing_centre_local_x": derived(bearing_centre_local_x, "mm", "frame_x/2-bearing_width/2"),
                       "bearing_pocket_centre_local_x": derived(pocket_centre_local_x, "mm", "frame_x/2-bearing_pocket_depth/2"),
                       "frame_top_z": derived(frame_top, "mm", "base_z+frame_z")
                   }})
    return parts, report


def export_fixture(config, directory):
    parts, report = build(config)
    return export(parts, report, config, directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=HERE / "config.json")
    parser.add_argument("--output", type=Path, default=HERE / "exports")
    args = parser.parse_args()
    result = export_fixture(json.loads(args.config.read_text(encoding="utf-8")), args.output)
    print(json.dumps({"fixture": result["fixture"], "solid_count": result["step_roundtrip"]["solid_count"],
                      "max_bbox_error_mm": result["step_roundtrip"]["max_bbox_error_mm"],
                      "export_count": len(result["exports"]), "manifest": str(args.output / "manifest.json")}, ensure_ascii=False))
