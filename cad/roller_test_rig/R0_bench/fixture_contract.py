"""Shared R0 fixture contract: unresolved real interfaces never drive bench CAD."""
import math


def validate(config):
    if config.get("units") != "mm":
        raise ValueError("Fixture geometry must explicitly use mm")
    if config.get("manufacturing_status") != "R0_FIXTURE_ONLY_PROTOTYPE":
        raise ValueError("Only R0_FIXTURE_ONLY_PROTOTYPE may be exported")
    result = {}
    for name, p in config["parameters"].items():
        for key in ("value", "unit", "status", "source", "scope", "rationale"):
            if key not in p or (key != "value" and not p[key]):
                raise ValueError(f"{name}: missing {key}")
        if p["status"] == "UNKNOWN" or p["scope"] == "PHYSICAL_INTERFACE":
            if not (p["status"] == "UNKNOWN" and p["source"] == "MEASUREMENT_REQUIRED"
                    and p["value"] is None and p["scope"] == "PHYSICAL_INTERFACE"):
                raise ValueError(f"{name}: MEASUREMENT_REQUIRED must remain UNKNOWN/null")
            continue
        if p["scope"] not in ("BENCH", "COTS_TRIAL"):
            raise ValueError(f"{name}: invalid fixture scope")
        if p["source"] == "OWN_DESIGN":
            if p["status"] not in ("ESTIMATED", "DERIVED"):
                raise ValueError(f"{name}: own design is not a measured interface")
        elif p["source"] == "MANUFACTURER_DATASHEET":
            if p["status"] != "MANUFACTURER_SPEC" or not p.get("source_url"):
                raise ValueError(f"{name}: manufacturer source URL is required")
        else:
            raise ValueError(f"{name}: unapproved provenance")
        value = p["value"]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name}: finite numeric bench dimension required")
        result[name] = value
    return result


def require_measured(config, name):
    p = config["parameters"][name]
    if p["value"] is None or p["status"] != "VERIFIED_MEASUREMENT":
        raise ValueError(f"{name}: MEASUREMENT_REQUIRED; real interface has not been measured")
    return p["value"]
