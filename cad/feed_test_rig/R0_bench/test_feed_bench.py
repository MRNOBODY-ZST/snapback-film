"""Breaks caught: accidental pickup selection, overtravel and head/fixture collisions."""
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
CORE = HERE.parents[1] / "roller_test_rig" / "R0_bench"
sys.path.insert(0, str(CORE))
sys.path.insert(0, str(HERE))
import fixture_contract as contract


def configuration():
    return json.loads((HERE / "config.json").read_text(encoding="utf-8"))


def test_unknown_pickup_depth_cannot_be_filled_with_zero():
    cfg = configuration()
    cfg["parameters"]["actual_pickup_depth"]["value"] = 0
    with pytest.raises(ValueError, match="actual_pickup_depth"):
        contract.validate(cfg)


def test_null_cartridge_envelope_cannot_drive_geometry():
    with pytest.raises(ValueError, match="MEASUREMENT_REQUIRED"):
        contract.require_measured(configuration(), "cartridge_external_width")


def test_unbounded_feed_carriage_is_rejected():
    import feed_bench
    cfg = configuration()
    cfg["parameters"]["carriage_x"]["value"] = 40
    with pytest.raises(ValueError, match="travel"):
        feed_bench.build(cfg)


def test_fences_cannot_be_positioned_inside_each_other():
    import feed_bench
    cfg = configuration()
    cfg["parameters"]["fence_center_y"]["value"] = 4
    with pytest.raises(ValueError, match="fence"):
        feed_bench.build(cfg)


def test_open_observation_fixture_has_no_claw_or_solid_collision():
    import feed_bench
    parts, report = feed_bench.build(configuration())
    assert report["unintended_interferences"] == []
    assert report["x_travel_mm"] == pytest.approx(60.0)
    assert report["generic_fence_clear_width_mm"] == pytest.approx(100.0)
    assert report["blank_to_table_clearance_mm"] == pytest.approx(37.0)
    assert all(p["shape"].isValid() and p["shape"].Volume() > 0 for p in parts)
    assert all("claw" not in p["name"] and "cartridge" not in p["name"] for p in parts)


def test_step_roundtrip_preserves_fixture_components(tmp_path):
    import feed_bench
    manifest = feed_bench.export_fixture(configuration(), tmp_path)
    assert manifest["manufacturing_status"] == "R0_FIXTURE_ONLY_PROTOTYPE"
    # Independent BOM: base 1, rails 2, carriage 1, stages 2, beam 1,
    # blank 1, table 1, pads 3, fences 2, posts 2, pressure bridge 1.
    assert manifest["step_roundtrip"]["solid_count"] == 17
    assert manifest["step_roundtrip"]["max_bbox_error_mm"] < 0.001
    assert manifest["physical_cartridge_fit_validated"] is False
    assert all((HERE.parents[2] / f["path"]).is_file() for f in manifest["exports"])
    assert manifest["mode"] == "TEST_FIXTURE_ONLY"
    assert manifest["physical_validation"] is False
    assert manifest["final_back_manufacturing_authorized"] is False


@pytest.mark.parametrize("x,z,y", [(-60,30,57), (0,30,57), (-60,80,62), (0,80,62), (0,50,20)])
def test_reachable_adjustment_endpoints_have_clear_nominal_solids(x,z,y):
    import feed_bench
    cfg = configuration()
    for name, value in (("carriage_x",x), ("head_bottom_z",z), ("fence_center_y",y)):
        cfg["parameters"][name]["value"] = value
    _, report = feed_bench.build(cfg)
    assert report["unintended_interferences"] == []


def test_narrow_fences_and_lowered_blank_collision_is_rejected():
    import feed_bench
    cfg = configuration()
    for name, value in (("carriage_x",0), ("head_bottom_z",30), ("fence_center_y",20)):
        cfg["parameters"][name]["value"] = value
    with pytest.raises(ValueError, match="interference"):
        feed_bench.build(cfg)
