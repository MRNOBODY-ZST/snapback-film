"""Closed-source-mesh guards using a synthetic tetrahedron, not film geometry."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import reference_mesh as meshes
except ModuleNotFoundError:
    meshes = None

TETRA = [((0, 0, 0), (0, 1, 0), (1, 0, 0)),
         ((0, 0, 0), (1, 0, 0), (0, 0, 1)),
         ((0, 0, 0), (0, 0, 1), (0, 1, 0)),
         ((1, 0, 0), (0, 1, 0), (0, 0, 1))]


class ReferenceMeshTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(meshes, "Reference mesh guards have not been implemented")

    def test_closed_mesh_reports_positive_nominal_volume(self):
        result = meshes.validate_closed_mesh(TETRA)
        self.assertEqual(result["triangle_count"], 4)
        self.assertAlmostEqual(result["signed_volume_model_units_cubed"], .166666666666667)
        self.assertFalse(result["physical_validation"])

    def test_missing_face_cannot_be_exported_as_solid(self):
        with self.assertRaises(ValueError):
            meshes.validate_closed_mesh(TETRA[:-1])

    def test_inconsistent_triangle_winding_is_rejected(self):
        wrong = list(TETRA)
        wrong[0] = tuple(reversed(wrong[0]))
        with self.assertRaises(ValueError):
            meshes.validate_closed_mesh(wrong)

    def test_source_axes_can_be_scaled_for_reference_only(self):
        result = meshes.validate_closed_mesh(meshes.transform_mesh(TETRA, [2, 3, 4], [10, -2, 5]))
        self.assertEqual(result["min_xyz"], [10, -2, 5])
        self.assertEqual(result["max_xyz"], [12, 1, 9])
        self.assertAlmostEqual(result["signed_volume_model_units_cubed"], 4)

    def test_missing_or_negative_scale_does_not_become_default(self):
        for scale in ([None, 1, 1], [-1, 1, 1], [0, 1, 1]):
            with self.assertRaises(ValueError):
                meshes.transform_mesh(TETRA, scale, [0, 0, 0])


if __name__ == "__main__":
    unittest.main()
