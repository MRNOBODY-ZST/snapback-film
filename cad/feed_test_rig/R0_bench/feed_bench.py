"""Open observation fixture with replaceable blank; never a matched pickup claw."""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "roller_test_rig" / "R0_bench"))
from fixture_contract import validate
from bench_geometry import block, cylinder_x, cylinder_z, slot_z, part, verify, derived, export


def build(config):
    v = validate(config)
    for key, value in v.items():
        if key not in ("carriage_x", "carriage_min_x", "carriage_max_x", "rail_center_x", "rail_bolt_front_x") and value <= 0:
            raise ValueError(f"{key}: positive fixture size required")
    if not v["carriage_min_x"] <= v["carriage_x"] <= v["carriage_max_x"]:
        raise ValueError("carriage outside nominal admissible travel")
    if not v["fence_min_y"] <= v["fence_center_y"] <= v["fence_max_y"]:
        raise ValueError("fence outside nominal clamping slot range")
    if v["fence_center_y"] <= v["fence_y"] / 2:
        raise ValueError("fence opening must remain positive")
    if not v["head_min_z"] <= v["head_bottom_z"] <= v["head_max_z"]:
        raise ValueError("head outside vertical slot range")
    if (v["carriage_min_x"]-v["carriage_length"]/2 < v["rail_center_x"]-v["rail_x"]/2
            or v["carriage_max_x"]+v["carriage_length"]/2 > v["rail_center_x"]+v["rail_x"]/2):
        raise ValueError("carriage travel exceeds guide rail support")
    extra = v["cut_extra"]
    parts = []
    base_top = v["base_z"]
    rail_top = base_top + v["rail_z"]
    carriage_top = rail_top + v["carriage_thickness"]
    table_top = base_top + v["table_z"]
    pad_top = table_top + v["pad_z"]
    beam_start_x = v["carriage_x"] + v["stage_offset_x"] + v["stage_x"] / 2
    beam_z = v["head_bottom_z"] + v["beam_z"] / 2
    blank_bottom = v["head_bottom_z"] + v["beam_z"]
    slot_min_z = v["head_min_z"] + v["beam_z"] / 2
    slot_max_z = v["head_max_z"] + v["beam_z"] / 2
    base = block(v["base_x"], v["base_y"], v["base_z"], (0, 0, base_top / 2))
    mount_points = []
    for sign in (-1, 1):
        mount_points.extend([(x, sign * v["rail_center_y"]) for x in (v["rail_bolt_front_x"], v["rail_bolt_rear_x"])])
        mount_points.append((v["post_center_x"], sign * v["post_center_y"]))
    for x, y in mount_points:
        base = base.cut(cylinder_z(v["mount_clearance_diameter"], v["base_z"] + 2 * extra, (x, y, base_top / 2)))
    # Table screws enter a blind base pilot from above; table heads must be
    # flush/recessed after machining. Thread form and actual hardware omitted.
    for x in (v["table_center_x"] - v["table_bolt_x_offset"], v["table_center_x"] + v["table_bolt_x_offset"]):
        for y in (-v["table_bolt_y"], v["table_bolt_y"]):
            base = base.cut(cylinder_z(v["mount_pilot_diameter"], v["mount_pilot_depth"] + extra,
                                       (x, y, base_top - v["mount_pilot_depth"] / 2 + extra / 2)))
    parts.append(part("OWN_base", base))
    for sign, side in ((-1, "L"), (1, "R")):
        y = sign * v["rail_center_y"]
        rail = block(v["rail_x"], v["rail_y"], v["rail_z"], (v["rail_center_x"], y, base_top + v["rail_z"] / 2))
        # Captive square-head clearance provision below each X guide slot.
        centre_x = (v["carriage_min_x"] + v["carriage_max_x"]) / 2
        length = v["carriage_max_x"] - v["carriage_min_x"]
        slot = block(length, v["guide_slot_width"], v["rail_z"] + 2 * extra,
                     (centre_x, y, base_top + v["rail_z"] / 2))
        for x in (v["carriage_min_x"], v["carriage_max_x"]):
            slot = slot.fuse(cylinder_z(v["guide_slot_width"], v["rail_z"] + 2 * extra,
                                       (x, y, base_top + v["rail_z"] / 2)))
        head_channel = block(length + v["guide_slot_width"], v["guide_head_channel_width"],
                              v["guide_head_channel_depth"] + extra,
                              (centre_x, y, base_top + v["guide_head_channel_depth"] / 2 - extra / 2))
        rail = rail.cut(slot.fuse(head_channel))
        for x in (v["rail_bolt_front_x"], v["rail_bolt_rear_x"]):
            rail = rail.cut(cylinder_z(v["mount_pilot_diameter"], v["mount_pilot_depth"] + extra,
                                       (x, y, base_top + v["mount_pilot_depth"] / 2 - extra / 2)))
        parts.append(part(f"OWN_{side}_machined_slotted_rail", rail))
    carriage = block(v["carriage_length"], v["carriage_width"], v["carriage_thickness"],
                     (v["carriage_x"], 0, rail_top + v["carriage_thickness"] / 2))
    for sign in (-1, 1):
        carriage = carriage.cut(cylinder_z(v["guide_slot_width"], v["carriage_thickness"] + 2 * extra,
                                           (v["carriage_x"], sign * v["rail_center_y"], rail_top + v["carriage_thickness"] / 2)))
        for dx in (-v["stage_bolt_x_offset"], v["stage_bolt_x_offset"]):
            carriage = carriage.cut(cylinder_z(v["stage_mount_clearance"], v["carriage_thickness"] + 2 * extra,
                                               (v["carriage_x"] + v["stage_offset_x"] + dx,
                                                sign * v["stage_center_y"], rail_top + v["carriage_thickness"] / 2)))
    parts.append(part("OWN_hand_advance_carriage", carriage))
    for sign, side in ((-1, "L"), (1, "R")):
        stage_x = v["carriage_x"] + v["stage_offset_x"]
        stage_y = sign * v["stage_center_y"]
        stage = block(v["stage_x"], v["stage_y"], v["stage_z"],
                      (stage_x, stage_y, carriage_top + v["stage_z"] / 2))
        slot = block(v["stage_x"] + 2 * extra, v["stage_slot_width"], slot_max_z-slot_min_z,
                     (stage_x, stage_y, (slot_min_z+slot_max_z)/2))
        for z in (slot_min_z, slot_max_z):
            slot = slot.fuse(cylinder_x(v["stage_slot_width"], v["stage_x"] + 2 * extra, (stage_x, stage_y, z)))
        stage = stage.cut(slot)
        for dx in (-v["stage_bolt_x_offset"], v["stage_bolt_x_offset"]):
            stage = stage.cut(cylinder_z(v["stage_mount_pilot"], v["stage_mount_pilot_depth"] + extra,
                                         (stage_x + dx, stage_y, carriage_top + v["stage_mount_pilot_depth"]/2-extra/2)))
        parts.append(part(f"OWN_{side}_vertical_slotted_stage", stage))
    beam = block(v["beam_x"], v["beam_y"], v["beam_z"], (beam_start_x + v["beam_x"]/2, 0, beam_z))
    for sign in (-1, 1):
        beam = beam.cut(cylinder_x(v["blank_pilot_diameter"], v["side_clamp_pilot_depth"] + extra,
                                   (beam_start_x+v["side_clamp_pilot_depth"]/2-extra/2, sign*v["stage_center_y"], beam_z)))
        beam = beam.cut(cylinder_z(v["blank_pilot_diameter"], v["beam_z"]+extra,
                                   (beam_start_x+v["beam_x"]/2, sign*v["blank_hole_y"], beam_z+extra/2)))
    parts.append(part("OWN_height_adjustable_blank_support_beam", beam))
    blank = block(v["blank_x"], v["blank_y"], v["blank_z"], (beam_start_x + v["blank_x"]/2, 0, blank_bottom + v["blank_z"]/2))
    for y in (-v["blank_hole_y"], v["blank_hole_y"]):
        blank = blank.cut(cylinder_z(v["blank_clearance_diameter"], v["blank_z"]+2*extra,
                                     (beam_start_x+v["beam_x"]/2, y, blank_bottom+v["blank_z"]/2)))
    parts.append(part("OWN_replaceable_BLANK_end_plate_NO_pickup_tip", blank))
    table = block(v["table_x"], v["table_y"], v["table_z"], (v["table_center_x"], 0, base_top+v["table_z"]/2))
    for x in (v["fence_bolt_front_x"], v["fence_bolt_rear_x"]):
        table = table.cut(slot_z(v["fence_bolt_clearance"], -v["fence_max_y"], v["fence_max_y"],
                                x, v["table_z"]+2*extra, base_top-extra))
    for x in (v["table_center_x"]-v["table_bolt_x_offset"], v["table_center_x"]+v["table_bolt_x_offset"]):
        for y in (-v["table_bolt_y"], v["table_bolt_y"]):
            table = table.cut(cylinder_z(v["mount_clearance_diameter"], v["table_z"]+2*extra,
                                         (x, y, base_top+v["table_z"]/2)))
            table = table.cut(cylinder_z(v["table_head_recess_diameter"], v["table_head_recess_depth"]+extra,
                                         (x, y, table_top-v["table_head_recess_depth"]/2+extra/2)))
    parts.append(part("OWN_open_observation_table", table))
    for label, x, y in (("front_L", v["pad_front_x"], -v["pad_front_y"]),
                        ("front_R", v["pad_front_x"], v["pad_front_y"]),
                        ("rear", v["pad_rear_x"], 0)):
        parts.append(part(f"OWN_generic_support_pad_{label}", cylinder_z(v["pad_diameter"], v["pad_z"], (x, y, table_top+v["pad_z"]/2))))
    for sign, side in ((-1,"L"), (1,"R")):
        fence = block(v["fence_x"], v["fence_y"], v["fence_z"],
                      (v["fence_center_x"], sign*v["fence_center_y"], table_top+v["fence_z"]/2))
        for x in (v["fence_bolt_front_x"], v["fence_bolt_rear_x"]):
            fence = fence.cut(cylinder_z(v["fence_bolt_clearance"], v["fence_z"]+2*extra,
                                         (x, sign*v["fence_center_y"], table_top+v["fence_z"]/2)))
        parts.append(part(f"OWN_{side}_generic_adjustable_fence", fence))
        post = block(v["post_x"], v["post_y"], v["post_z"],
                     (v["post_center_x"], sign*v["post_center_y"], base_top+v["post_z"]/2))
        for z in (base_top+v["mount_pilot_depth"]/2-extra/2,
                  base_top+v["post_z"]-v["mount_pilot_depth"]/2+extra/2):
            post = post.cut(cylinder_z(v["mount_pilot_diameter"], v["mount_pilot_depth"]+extra,
                                       (v["post_center_x"], sign*v["post_center_y"], z)))
        parts.append(part(f"OWN_{side}_future_pressure_bridge_post", post))
    bridge_bottom = base_top+v["post_z"]
    bridge = block(v["post_x"], v["pressure_bridge_y"], v["pressure_bridge_z"],
                   (v["post_center_x"], 0, bridge_bottom+v["pressure_bridge_z"]/2))
    for y, diameter in ((-v["post_center_y"],v["mount_clearance_diameter"]),
                        (v["post_center_y"],v["mount_clearance_diameter"]), (0,v["adjuster_pilot_diameter"])):
        bridge = bridge.cut(cylinder_z(diameter,v["pressure_bridge_z"]+2*extra,
                                       (v["post_center_x"],y,bridge_bottom+v["pressure_bridge_z"]/2)))
    parts.append(part("OWN_future_pressure_adjustment_bridge_NO_spring",bridge))
    report = verify(parts, v["intersection_volume_tolerance"])
    if report["unintended_interferences"]:
        raise ValueError(f"Unintended nominal fixture interference: {report['unintended_interferences']}")
    report.update({"x_travel_mm":v["carriage_max_x"]-v["carriage_min_x"],
                   "generic_fence_clear_width_mm":2*v["fence_center_y"]-v["fence_y"],
                   "blank_to_table_clearance_mm":blank_bottom-pad_top,
                   "derived_parameters":{
                       "carriage_top_z":derived(carriage_top,"mm","base_z+rail_z+carriage_thickness"),
                       "nominal_carriage_travel":derived(v["carriage_max_x"]-v["carriage_min_x"],"mm","carriage_max_x-carriage_min_x; slot arc centres, real hardware stop needs calibration"),
                       "vertical_head_travel":derived(v["head_max_z"]-v["head_min_z"],"mm","head_max_z-head_min_z"),
                       "generic_fence_width_min":derived(2*v["fence_min_y"]-v["fence_y"],"mm","2*fence_min_y-fence_y; NOT cartridge width"),
                       "generic_fence_width_max":derived(2*v["fence_max_y"]-v["fence_y"],"mm","2*fence_max_y-fence_y; NOT cartridge width"),
                       "generic_support_top_z":derived(pad_top,"mm","base_z+table_z+pad_z"),
                       "blank_bottom_z":derived(blank_bottom,"mm","head_bottom_z+beam_z"),
                       "parked_blank_to_support_clearance":derived(blank_bottom-pad_top,"mm","head_bottom_z+beam_z-(base_z+table_z+pad_z); NO actual pickup selected"),
                       "beam_start_x":derived(beam_start_x,"mm","carriage_x+stage_offset_x+stage_x/2"),
                       "slot_min_z":derived(slot_min_z,"mm","head_min_z+beam_z/2"),
                       "slot_max_z":derived(slot_max_z,"mm","head_max_z+beam_z/2")
                   }})
    return parts, report


def export_fixture(config, directory):
    parts, report = build(config)
    return export(parts, report, config, directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",type=Path,default=HERE/"config.json")
    parser.add_argument("--output",type=Path,default=HERE/"exports")
    args=parser.parse_args()
    result=export_fixture(json.loads(args.config.read_text(encoding="utf-8")),args.output)
    print(json.dumps({"fixture":result["fixture"],"solid_count":result["step_roundtrip"]["solid_count"],
                      "max_bbox_error_mm":result["step_roundtrip"]["max_bbox_error_mm"],
                      "export_count":len(result["exports"]),"manifest":str(args.output/"manifest.json")},ensure_ascii=False))
