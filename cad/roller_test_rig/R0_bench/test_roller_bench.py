"""Breaks caught: substituted unknowns, impossible guide travel, part collision,
and exports that lose/merge solids or change size on STEP round-trip."""
import copy
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fixture_contract as contract


def configuration():
    return json.loads((HERE / "config.json").read_text(encoding="utf-8"))


def test_unknown_gap_cannot_be_silently_replaced_with_zero():
    cfg = configuration()
    cfg["parameters"]["actual_nip_gap"]["value"] = 0
    with pytest.raises(ValueError, match="actual_nip_gap"):
        contract.validate(cfg)


def test_unknown_physical_measurement_cannot_drive_geometry():
    cfg = configuration()
    with pytest.raises(ValueError, match="MEASUREMENT_REQUIRED"):
        contract.require_measured(cfg, "actual_nip_gap")


def test_unproven_gap_is_excluded_from_fixture_dimensions():
    values = contract.validate(configuration())
    assert "actual_nip_gap" not in values
    assert "cartridge_external_width" not in values


def test_missing_provenance_is_rejected_before_export():
    cfg = configuration()
    cfg["parameters"]["base_x"].pop("source")
    with pytest.raises(ValueError, match="base_x"):
        contract.validate(cfg)


def test_wrong_units_are_rejected_before_export():
    cfg = configuration()
    cfg["units"] = "inch"
    with pytest.raises(ValueError, match="mm"):
        contract.validate(cfg)


def test_slider_outside_machined_guide_is_rejected():
    import roller_bench
    cfg = configuration()
    cfg["parameters"]["upper_center_z"]["value"] = 120
    with pytest.raises(ValueError, match="guide"):
        roller_bench.build(cfg)


def test_rigid_gauge_rollers_cannot_intersect():
    import roller_bench
    cfg = configuration()
    cfg["parameters"]["gauge_diameter"]["value"] = 60
    with pytest.raises(ValueError, match="gauge"):
        roller_bench.build(cfg)


def test_nominal_assembly_has_no_unintended_solid_overlap():
    import roller_bench
    parts, report = roller_bench.build(configuration())
    assert len(parts) >= 15
    assert report["unintended_interferences"] == []
    assert report["guide_side_clearance_each_mm"] == pytest.approx(0.2)
    assert report["neutral_gauge_surface_separation_mm"] == pytest.approx(10.0)
    assert all(p["shape"].isValid() and p["shape"].Volume() > 0 for p in parts)


def test_step_roundtrip_preserves_all_fixture_components(tmp_path):
    import roller_bench
    manifest = roller_bench.export_fixture(configuration(), tmp_path)
    assert manifest["manufacturing_status"] == "R0_FIXTURE_ONLY_PROTOTYPE"
    # Independent BOM: base 1, frames 2, sliders 2, caps 4, reference
    # bearings 4, gauges 2, collars 4, bridges 2, stop inserts 2.
    assert manifest["step_roundtrip"]["solid_count"] == 23
    assert manifest["step_roundtrip"]["max_bbox_error_mm"] < 0.001
    assert manifest["physical_camera_fit_validated"] is False
    assert all((HERE.parents[2] / f["path"]).is_file() for f in manifest["exports"])
    assert manifest["mode"] == "TEST_FIXTURE_ONLY"
    assert manifest["physical_validation"] is False
    assert manifest["final_back_manufacturing_authorized"] is False


@pytest.mark.parametrize("z", [59, 75, 92])
def test_installed_stop_and_guide_endpoints_remain_clear(z):
    import roller_bench
    cfg = configuration()
    cfg["parameters"]["upper_center_z"]["value"] = z
    _, report = roller_bench.build(cfg)
    assert report["unintended_interferences"] == []
