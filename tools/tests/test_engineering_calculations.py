"""TEST_ONLY numerical fixtures; no camera or film measurements."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import engineering_calculations as calc
except ModuleNotFoundError:
    calc = None


def q(value, unit, tolerance=0.0):
    return {"value": value, "unit": unit, "tolerance": tolerance,
            "provenance": "UNKNOWN" if value is None else "ESTIMATED",
            "source": "TEST_ONLY synthetic input"}


class CalculationTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(calc, "Engineering calculations have not been implemented")

    def film_input(self):
        return {"rb67_effective_plane_z": q(-4, "mm", .05),
                "cartridge_effective_offset": q(6, "mm", .1),
                "cartridge_surface_offset": q(0, "mm", .05),
                "adapter_limit_z": q(-11, "mm", .1)}

    def motor_input(self):
        return {"roller_torque": q(.01, "N*m"), "pod_torque": q(.02, "N*m"),
                "transport_torque": q(.01, "N*m"), "friction_torque": q(.01, "N*m"),
                "external_ratio": q(3, "ratio"), "external_efficiency": q(.8, "ratio"),
                "safety_factor": q(2, "ratio"), "roller_diameter": q(10, "mm"),
                "film_speed": q(20, "mm/s")}

    def test_missing_emulsion_offset_stays_unknown(self):
        data = self.film_input()
        data["cartridge_effective_offset"] = q(None, "mm", None)
        result = calc.film_plane_screen(data)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIn("cartridge_effective_offset", result["unknowns"])
        self.assertIsNone(result["nominal_clearance_mm"])

    def test_signed_film_plane_and_worst_case_tolerance(self):
        result = calc.film_plane_screen(self.film_input())
        self.assertEqual(result["status"], "AXIAL_SCREEN_CLEAR")
        self.assertAlmostEqual(result["required_cartridge_datum_z_mm"], -10)
        self.assertAlmostEqual(result["nominal_clearance_mm"], 1)
        self.assertAlmostEqual(result["clearance_interval_mm"][0], .7)
        self.assertAlmostEqual(result["clearance_interval_mm"][1], 1.3)
        self.assertFalse(result["manufacturing_authorized"])

    def test_front_projection_can_make_axial_interference(self):
        data = self.film_input()
        data["cartridge_surface_offset"] = q(-2, "mm", .05)
        result = calc.film_plane_screen(data)
        self.assertEqual(result["status"], "AXIAL_INTERFERENCE")
        self.assertAlmostEqual(result["clearance_interval_mm"][1], -.7)

    def test_missing_tolerance_prevents_clearance_qualification(self):
        data = self.film_input()
        data["rb67_effective_plane_z"]["tolerance"] = None
        result = calc.film_plane_screen(data)
        self.assertEqual(result["status"], "TOLERANCE_REQUIRED")
        self.assertIsNone(result["clearance_interval_mm"])

    def test_tolerance_crossing_zero_is_uncertain(self):
        data = self.film_input()
        data["adapter_limit_z"] = q(-10.1, "mm", .1)
        self.assertEqual(calc.film_plane_screen(data)["status"], "AXIAL_SCREEN_UNCERTAIN")

    def test_millimetre_input_cannot_be_supplied_in_metres(self):
        data = self.film_input()
        data["adapter_limit_z"]["unit"] = "m"
        with self.assertRaises(ValueError):
            calc.film_plane_screen(data)

    def test_unknown_provenance_cannot_hide_a_fixed_dimension(self):
        data = self.film_input()
        data["adapter_limit_z"]["provenance"] = "UNKNOWN"
        with self.assertRaises(ValueError):
            calc.film_plane_screen(data)

    def test_nonfinite_dimension_is_rejected(self):
        data = self.film_input()
        data["adapter_limit_z"]["value"] = math.nan
        with self.assertRaises(ValueError):
            calc.film_plane_screen(data)

    def test_motor_torque_referred_through_reduction_and_efficiency(self):
        result = calc.motor_requirements(self.motor_input())
        self.assertEqual(result["status"], "CALCULATED")
        self.assertAlmostEqual(result["roller_load_torque_nm"], .05)
        self.assertAlmostEqual(result["required_motor_output_torque_nm"], .0416666666666667)
        self.assertAlmostEqual(result["required_motor_output_rpm"], 114.591559026165)

    def test_motor_safety_factor_below_two_is_rejected(self):
        data = self.motor_input()
        data["safety_factor"] = q(1.9, "ratio")
        with self.assertRaises(ValueError):
            calc.motor_requirements(data)

    def test_unmeasured_pod_torque_blocks_motor_selection(self):
        data = self.motor_input()
        data["pod_torque"] = q(None, "N*m")
        self.assertEqual(calc.motor_requirements(data)["status"], "UNKNOWN")

    def test_impossible_gear_efficiency_is_rejected(self):
        data = self.motor_input()
        data["external_efficiency"] = q(1.01, "ratio")
        with self.assertRaises(ValueError):
            calc.motor_requirements(data)

    def test_cam_peak_torque_uses_radians_and_actual_rise_angle(self):
        data = {"pickup_force": q(5, "N"), "stroke": q(10, "mm"),
                "rise_angle": q(180, "deg"), "cam_rpm": q(30, "rev/min"),
                "external_ratio": q(2, "ratio"), "external_efficiency": q(.8, "ratio"),
                "safety_factor": q(2, "ratio")}
        result = calc.cam_requirements(data)
        self.assertAlmostEqual(result["peak_cam_torque_nm"], .025)
        self.assertAlmostEqual(result["required_motor_output_torque_nm"], .03125)
        self.assertAlmostEqual(result["peak_pickup_speed_mm_s"], 15.707963267949)

    def test_both_roller_springs_contribute_to_preload(self):
        result = calc.roller_preload({"left_rate": q(3, "N/mm"),
                 "right_rate": q(3, "N/mm"), "left_compression": q(2, "mm"),
                 "right_compression": q(1.5, "mm"), "active_width": q(70, "mm")})
        self.assertAlmostEqual(result["total_preload_n"], 10.5)
        self.assertAlmostEqual(result["force_imbalance_n"], 1.5)
        self.assertAlmostEqual(result["mean_line_load_n_per_mm"], .15)
        self.assertNotIn("nip_pressure_pa", result)

    def test_gear_pitch_geometry_uses_module_and_both_tooth_counts(self):
        data = {"module": q(1, "mm"), "driver_teeth": q(20, "teeth"),
                "driven_teeth": q(60, "teeth"), "pressure_angle": q(20, "deg")}
        result = calc.gear_geometry(data)
        self.assertAlmostEqual(result["center_distance_mm"], 40)
        self.assertEqual(result["reduction_ratio"], 3)
        self.assertAlmostEqual(result["driver_pitch_diameter_mm"], 20)

    def test_fractional_tooth_count_is_rejected(self):
        data = {"module": q(1, "mm"), "driver_teeth": q(20.5, "teeth"),
                "driven_teeth": q(60, "teeth"), "pressure_angle": q(20, "deg")}
        with self.assertRaises(ValueError):
            calc.gear_geometry(data)

    def test_one_cam_rotation_may_not_eject_whole_sheet(self):
        result = calc.synchronized_capacity({"roller_diameter": q(10, "mm"),
                 "roller_revs_per_cam_rev": q(3, "ratio"), "capture_angle": q(180, "deg"),
                 "slip_fraction": q(.1, "ratio"), "distance_after_capture": q(60, "mm"),
                 "margin": q(5, "mm")})
        self.assertEqual(result["status"], "INSUFFICIENT_DISTANCE")
        self.assertAlmostEqual(result["available_distance_mm"], 42.4115008234622)
        self.assertAlmostEqual(result["required_distance_mm"], 65)


if __name__ == "__main__":
    unittest.main()
