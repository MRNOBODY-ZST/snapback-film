"""Synthetic diagnostics; these tests are not film transport evidence."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import analyze_cycle_log as logs
except ModuleNotFoundError:
    logs = None


def row(t, a=.2, b=.4, cycle="1", battery_current=None):
    item = {"timestamp_s": t, "state": "EJECTING", "motor_a_current_a": a,
            "motor_b_current_a": b, "cycle_id": cycle, "battery_voltage_v": 3.7}
    if battery_current is not None:
        item["battery_current_a"] = battery_current
    return item


class CycleLogTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(logs, "Cycle-log analyzer has not been implemented")

    def test_empty_log_does_not_manufacture_cycles(self):
        result = logs.analyze_rows([])
        self.assertEqual(result["status"], "NO_DATA")
        self.assertEqual(result["cycles"], [])

    def test_backwards_time_is_not_silently_sorted(self):
        with self.assertRaises(ValueError):
            logs.analyze_rows([row(2), row(1)])

    def test_nonfinite_current_is_rejected(self):
        with self.assertRaises(ValueError):
            logs.analyze_rows([row(0, a=float("nan"))])

    def test_missing_battery_current_does_not_sum_motor_currents(self):
        result = logs.analyze_rows([row(0), row(2, a=.6, b=.8)])
        cycle = result["cycles"][0]
        self.assertIsNone(cycle["battery_energy_net_j"])
        self.assertEqual(cycle["battery_energy_status"], "BATTERY_CURRENT_REQUIRED")
        self.assertEqual(cycle["motor_a_peak_a"], .6)
        self.assertEqual(cycle["motor_b_peak_a"], .8)
        self.assertEqual(cycle["duration_s"], 2)

    def test_battery_energy_uses_independent_measured_channel(self):
        result = logs.analyze_rows([row(0, battery_current=.5), row(2, battery_current=.5)])
        cycle = result["cycles"][0]
        self.assertAlmostEqual(cycle["battery_energy_net_j"], 3.7)
        self.assertAlmostEqual(cycle["battery_charge_net_mah"], .277777777777778)

    def test_partial_battery_channel_does_not_estimate_missing_sample(self):
        result = logs.analyze_rows([row(0, battery_current=.5), row(2)])
        self.assertIsNone(result["cycles"][0]["battery_energy_net_j"])

    def test_separate_cycles_have_separate_duration(self):
        result = logs.analyze_rows([row(0), row(2), row(3, cycle="2"), row(4, cycle="2")])
        self.assertEqual([r["duration_s"] for r in result["cycles"]], [2, 1])

    def test_negative_magnitude_channel_is_rejected(self):
        with self.assertRaises(ValueError):
            logs.analyze_rows([row(0, a=-.1)])


if __name__ == "__main__":
    unittest.main()
