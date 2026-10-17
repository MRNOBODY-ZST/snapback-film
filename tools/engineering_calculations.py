"""Unit-checked engineering screens; no physical PASS or manufacturing release."""
from __future__ import annotations

import math

PROVENANCE = {"VERIFIED_MEASUREMENT", "MANUFACTURER_SPEC", "RELIABLE_SOURCE",
              "DERIVED", "ESTIMATED", "UNKNOWN"}


def _inputs(data: dict, units: dict[str, str]) -> tuple[dict, dict]:
    values, unknowns, unverified = {}, [], []
    for name, unit in units.items():
        item = data.get(name, {"value": None, "unit": unit, "tolerance": None,
                              "provenance": "UNKNOWN", "source": "MEASUREMENT_REQUIRED"})
        if not isinstance(item, dict) or item.get("unit") != unit:
            raise ValueError(f"{name}: expected explicit unit {unit}")
        provenance = item.get("provenance")
        if provenance not in PROVENANCE or not isinstance(item.get("source"), str) or not item["source"].strip():
            raise ValueError(f"{name}: provenance and source are required")
        value = item.get("value")
        if provenance == "UNKNOWN" and value is not None:
            raise ValueError(f"{name}: UNKNOWN cannot contain a fixed value")
        if value is None:
            unknowns.append(name)
        elif isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name}: finite numeric value required")
        else:
            values[name] = float(value)
            if provenance != "VERIFIED_MEASUREMENT":
                unverified.append(name)
        tolerance = item.get("tolerance")
        if tolerance is not None and (isinstance(tolerance, bool) or not isinstance(tolerance, (int, float))
                                      or not math.isfinite(tolerance) or tolerance < 0):
            raise ValueError(f"{name}: tolerance must be nonnegative or null")
    result = {"status": "UNKNOWN" if unknowns else "CALCULATED", "unknowns": unknowns,
              "unverified_against_prototype": unverified, "manufacturing_authorized": False,
              "scope": "DERIVED from declared inputs; not physical validation"}
    return values, result


def _positive(v: dict, *names: str) -> None:
    if any(v[name] <= 0 for name in names):
        raise ValueError("Positive values required: " + ", ".join(names))


def _nonnegative(v: dict, *names: str) -> None:
    if any(v[name] < 0 for name in names):
        raise ValueError("Nonnegative values required: " + ", ".join(names))


def _drive(v: dict) -> None:
    _positive(v, "external_ratio")
    if not 0 < v["external_efficiency"] <= 1:
        raise ValueError("External gear efficiency must be in (0, 1]")
    if v["safety_factor"] < 2:
        raise ValueError("Motor torque safety factor must be at least 2")


def film_plane_screen(data: dict) -> dict:
    """One coincident XY sample: signed Z offsets relative to a defined datum.

    The cartridge surface and adapter limiting surface MUST refer to the same
    candidate overlap region. Positive clearance means the cartridge surface
    stays behind that limit. Full footprint/aperture/rotation testing is separate.
    """
    units = {name: "mm" for name in ("rb67_effective_plane_z", "cartridge_effective_offset",
                                     "cartridge_surface_offset", "adapter_limit_z")}
    v, out = _inputs(data, units)
    out.update(required_cartridge_datum_z_mm=None, nominal_clearance_mm=None,
               clearance_interval_mm=None, warning="Only a defined axial overlap sample; not a full 3D feasibility result")
    if out["unknowns"]:
        return out
    z_datum = v["rb67_effective_plane_z"] - v["cartridge_effective_offset"]
    clearance = z_datum + v["cartridge_surface_offset"] - v["adapter_limit_z"]
    out.update(required_cartridge_datum_z_mm=z_datum, nominal_clearance_mm=clearance)
    missing_tolerances = [name for name in units if data[name].get("tolerance") is None]
    if missing_tolerances:
        out.update(status="TOLERANCE_REQUIRED", tolerance_required=missing_tolerances)
        return out
    worst_error = sum(data[name]["tolerance"] for name in units)
    low, high = clearance - worst_error, clearance + worst_error
    out["clearance_interval_mm"] = [low, high]
    out["status"] = "AXIAL_SCREEN_CLEAR" if low > 0 else "AXIAL_INTERFERENCE" if high < 0 else "AXIAL_SCREEN_UNCERTAIN"
    return out


def motor_requirements(data: dict) -> dict:
    """Torque components referred to the roller; external ratio = motor/roller rpm.

    Components must be non-overlapping. A measured total processing torque must
    not be supplied again as separate pod/transport/friction components.
    """
    units = {name: "N*m" for name in ("roller_torque", "pod_torque", "transport_torque", "friction_torque")}
    units.update(external_ratio="ratio", external_efficiency="ratio", safety_factor="ratio",
                 roller_diameter="mm", film_speed="mm/s")
    v, out = _inputs(data, units)
    if out["unknowns"]:
        return out
    _drive(v)
    _positive(v, "roller_diameter", "film_speed")
    _nonnegative(v, "roller_torque", "pod_torque", "transport_torque", "friction_torque")
    load = sum(v[name] for name in ("roller_torque", "pod_torque", "transport_torque", "friction_torque"))
    rpm = 60 * v["film_speed"] / (math.pi * v["roller_diameter"])
    torque = load * v["safety_factor"] / (v["external_ratio"] * v["external_efficiency"])
    out.update(roller_load_torque_nm=load, roller_rpm=rpm,
               required_motor_output_torque_nm=torque,
               required_motor_output_rpm=rpm * v["external_ratio"],
               warning="Compare to qualified continuous/peak output capability, not stall torque alone; acceleration and low-voltage startup remain to measure")
    return out


def cam_requirements(data: dict) -> dict:
    """Simple-harmonic rise screen. It is not a complete cam or follower design."""
    units = dict(pickup_force="N", stroke="mm", rise_angle="deg", cam_rpm="rev/min",
                 external_ratio="ratio", external_efficiency="ratio", safety_factor="ratio")
    v, out = _inputs(data, units)
    if out["unknowns"]:
        return out
    _drive(v)
    _positive(v, "stroke", "cam_rpm")
    _nonnegative(v, "pickup_force")
    if not 0 < v["rise_angle"] < 360:
        raise ValueError("Rise angle must leave a nonzero return interval")
    beta = math.radians(v["rise_angle"])
    derivative = v["stroke"] * math.pi / (2 * beta)
    torque = v["pickup_force"] * derivative / 1000
    out.update(profile="simple_harmonic_rise", peak_displacement_derivative_mm_per_rad=derivative,
               peak_cam_torque_nm=torque,
               required_motor_output_torque_nm=torque * v["safety_factor"] / (v["external_ratio"] * v["external_efficiency"]),
               required_motor_output_rpm=v["cam_rpm"] * v["external_ratio"],
               peak_pickup_speed_mm_s=derivative * v["cam_rpm"] * 2 * math.pi / 60,
               warning="Needs measured F(x), follower friction, acceleration, pressure-angle and return/home analysis")
    return out


def roller_preload(data: dict) -> dict:
    units = dict(left_rate="N/mm", right_rate="N/mm", left_compression="mm",
                 right_compression="mm", active_width="mm")
    v, out = _inputs(data, units)
    if out["unknowns"]:
        return out
    _positive(v, "left_rate", "right_rate", "active_width")
    _nonnegative(v, "left_compression", "right_compression")
    left = v["left_rate"] * v["left_compression"]
    right = v["right_rate"] * v["right_compression"]
    out.update(left_force_n=left, right_force_n=right, total_preload_n=left + right,
               force_imbalance_n=abs(left - right), mean_line_load_n_per_mm=(left + right) / v["active_width"],
               warning="Mean line load is not nip contact pressure or a verified pod-rupture requirement. Include initial spring load separately if present.")
    return out


def gear_geometry(data: dict) -> dict:
    units = dict(module="mm", driver_teeth="teeth", driven_teeth="teeth", pressure_angle="deg")
    v, out = _inputs(data, units)
    if out["unknowns"]:
        return out
    _positive(v, "module", "driver_teeth", "driven_teeth")
    if any(not v[n].is_integer() for n in ("driver_teeth", "driven_teeth")):
        raise ValueError("Tooth counts must be integers")
    if not 0 < v["pressure_angle"] < 90:
        raise ValueError("Pressure angle must be in (0, 90) degrees")
    d1 = v["module"] * v["driver_teeth"]
    d2 = v["module"] * v["driven_teeth"]
    out.update(driver_pitch_diameter_mm=d1, driven_pitch_diameter_mm=d2,
               driver_base_diameter_mm=d1 * math.cos(math.radians(v["pressure_angle"])),
               driven_base_diameter_mm=d2 * math.cos(math.radians(v["pressure_angle"])),
               center_distance_mm=(d1 + d2) / 2, reduction_ratio=v["driven_teeth"] / v["driver_teeth"],
               warning="Nominal unshifted spur geometry only; undercut, contact ratio, backlash, strength and tolerances require separate checks")
    return out


def synchronized_capacity(data: dict) -> dict:
    units = dict(roller_diameter="mm", roller_revs_per_cam_rev="ratio", capture_angle="deg",
                 slip_fraction="ratio", distance_after_capture="mm", margin="mm")
    v, out = _inputs(data, units)
    if out["unknowns"]:
        return out
    _positive(v, "roller_diameter", "roller_revs_per_cam_rev")
    _nonnegative(v, "distance_after_capture", "margin")
    if not 0 <= v["capture_angle"] < 360 or not 0 <= v["slip_fraction"] < 1:
        raise ValueError("Capture angle/slip leave no valid transport interval")
    per_ratio = math.pi * v["roller_diameter"] * (360 - v["capture_angle"]) / 360 * (1 - v["slip_fraction"])
    available = per_ratio * v["roller_revs_per_cam_rev"]
    required = v["distance_after_capture"] + v["margin"]
    out.update(status="DISTANCE_SCREEN_CLEAR" if available >= required else "INSUFFICIENT_DISTANCE",
               available_distance_mm=available, required_distance_mm=required,
               minimum_roller_revs_per_cam_rev=required / per_ratio,
               warning="Capacity alone does not validate single-sheet separation, capture or stopping at home")
    return out


CALCULATORS = {"film_plane": film_plane_screen, "motor": motor_requirements,
               "cam": cam_requirements, "roller_preload": roller_preload,
               "gear": gear_geometry, "single_motor_cycle": synchronized_capacity}


def calculate_all(config: dict) -> dict:
    return {"scope": "Engineering calculations only; physical gates remain open",
            "feasibility_result": "UNCERTAIN — MEASUREMENT REQUIRED",
            "manufacturing_authorized": False,
            "calculations": {key: fn(config.get(key, {})) for key, fn in CALCULATORS.items()}}
