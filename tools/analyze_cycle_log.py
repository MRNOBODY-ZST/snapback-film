"""Read measured diagnostic traces; no inferred battery current or jam limits."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import OrderedDict
from pathlib import Path


def _number(row: dict, field: str, nonnegative: bool = False) -> float:
    try:
        value = float(row[field])
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError(f"Missing or invalid {field}") from exc
    if not math.isfinite(value) or (nonnegative and value < 0):
        raise ValueError(f"Invalid {field}: finite {'nonnegative ' if nonnegative else ''}value required")
    return value


def _p99(values: list[float]) -> float:
    values = sorted(values)
    rank = .99 * (len(values) - 1)
    low, high = math.floor(rank), math.ceil(rank)
    return values[low] + (values[high] - values[low]) * (rank - low)


def analyze_rows(rows: list[dict]) -> dict:
    out = {"status": "NO_DATA" if not rows else "ANALYZED", "sample_count": len(rows),
           "cycles": [], "physical_reliability_qualified": False,
           "warning": "Sample percentiles are descriptive, not calibrated jam thresholds. Complete states alone do not prove chemical/image quality."}
    grouped = OrderedDict()
    last_time = -math.inf
    last_cycle = None
    closed_cycles = set()
    for row in rows:
        t = _number(row, "timestamp_s", nonnegative=True)
        if t < last_time:
            raise ValueError("Timestamp moved backwards; no automatic sorting")
        last_time = t
        cycle_id = str(row.get("cycle_id", ""))
        if not cycle_id:
            raise ValueError("cycle_id is required")
        if cycle_id != last_cycle:
            if cycle_id in closed_cycles:
                raise ValueError("Noncontiguous cycle_id; split runs or provide unique cycle identifiers")
            if last_cycle is not None:
                closed_cycles.add(last_cycle)
            last_cycle = cycle_id
        parsed = {"t": t, "a": _number(row, "motor_a_current_a", True),
                  "b": _number(row, "motor_b_current_a", True), "state": row.get("state", "")}
        for field in ("home", "entry", "exit", "dark_slide", "door_closed", "cartridge_present"):
            if field in row and row[field] not in ("", None) and str(row[field]) not in {"0", "1"}:
                raise ValueError(f"{field}: expected 0/1")
        voltage_present = row.get("battery_voltage_v") not in (None, "")
        current_present = row.get("battery_current_a") not in (None, "")
        parsed["battery"] = None
        if voltage_present:
            voltage = _number(row, "battery_voltage_v", True)
            if voltage <= 0:
                raise ValueError("Battery voltage must be positive")
        if current_present:
            current = _number(row, "battery_current_a")
        if voltage_present and current_present:
            parsed["battery"] = (voltage, current)
        grouped.setdefault(cycle_id, []).append(parsed)
    for cycle_id, samples in grouped.items():
        a = [s["a"] for s in samples]
        b = [s["b"] for s in samples]
        measured = all(s["battery"] is not None for s in samples) and len(samples) >= 2
        energy = charge = None
        if measured:
            energy = charge = 0.0
            for left, right in zip(samples, samples[1:]):
                dt = right["t"] - left["t"]
                vl, il = left["battery"]
                vr, ir = right["battery"]
                energy += .5 * (vl * il + vr * ir) * dt
                charge += .5 * (il + ir) * dt / 3.6
        out["cycles"].append({"cycle_id": cycle_id, "sample_count": len(samples),
            "duration_s": samples[-1]["t"] - samples[0]["t"],
            "motor_a_peak_a": max(a), "motor_b_peak_a": max(b),
            "motor_a_sample_p99_a": _p99(a), "motor_b_sample_p99_a": _p99(b),
            "states_observed": list(dict.fromkeys(s["state"] for s in samples)),
            "battery_energy_status": "INTEGRATED" if measured else "BATTERY_CURRENT_REQUIRED",
            "battery_energy_net_j": energy, "battery_charge_net_mah": charge})
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    args = parser.parse_args()
    try:
        with args.csv.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            required = {"timestamp_s", "state", "motor_a_current_a", "motor_b_current_a", "cycle_id"}
            if not reader.fieldnames or required - set(reader.fieldnames):
                raise ValueError("CSV needs timestamp_s,state,motor_a_current_a,motor_b_current_a,cycle_id")
            result = analyze_rows(list(reader))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Invalid diagnostic trace: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
