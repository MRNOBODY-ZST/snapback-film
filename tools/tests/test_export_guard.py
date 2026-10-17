"""Registration and hash checks, using temporary synthetic assets only."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from validate_exports import audit_registered_exports, deliverable_files
except ImportError:
    audit_registered_exports = deliverable_files = None


class ExportGuardTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def register(self, scope="TEST_FIXTURE_ONLY", relative="cad/feed_test_rig/R0_bench/base.step"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"TEST_ONLY synthetic export")
        manifest = {"mode": scope, "physical_validation": False,
                    "final_back_manufacturing_authorized": False,
                    "exports": [{"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                 "bytes": path.stat().st_size}]}
        mp = path.parent / "manifest.json"
        mp.write_text(json.dumps(manifest), encoding="utf-8")
        return {"entries": [{"scope": scope, "manifest_path": mp.relative_to(self.root).as_posix(),
                             "export_root": path.parent.relative_to(self.root).as_posix()}]}, path, mp

    def test_registered_bench_export_is_only_fixture(self):
        self.assertIsNotNone(audit_registered_exports, "Implement guard after RED")
        register, _, _ = self.register()
        result = audit_registered_exports(self.root, register, set())
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["fixture_exports"]), 1)
        self.assertEqual(result["source_reference_previews"], [])

    def test_unregistered_final_export_rejected(self):
        self.assertIsNotNone(audit_registered_exports)
        register, _, _ = self.register()
        final = self.root / "cad/final/untested.stl"
        final.parent.mkdir(parents=True)
        final.write_bytes(b"TEST_ONLY")
        result = audit_registered_exports(self.root, register, set())
        self.assertIn("cad/final/untested.stl", result["unauthorized_exports"])

    def test_changed_hash_rejected(self):
        self.assertIsNotNone(audit_registered_exports)
        register, path, _ = self.register()
        path.write_bytes(b"changed")
        self.assertTrue(audit_registered_exports(self.root, register, set())["errors"])

    def test_claim_of_physical_validation_rejected(self):
        self.assertIsNotNone(audit_registered_exports)
        register, _, mp = self.register()
        manifest = json.loads(mp.read_text())
        manifest["physical_validation"] = True
        mp.write_text(json.dumps(manifest))
        self.assertTrue(audit_registered_exports(self.root, register, set())["errors"])

    def test_fixture_scope_cannot_authorize_final_directory(self):
        self.assertIsNotNone(audit_registered_exports)
        register, _, _ = self.register(relative="cad/final/untested.step")
        self.assertTrue(audit_registered_exports(self.root, register, set())["errors"])

    def test_local_runtime_excluded(self):
        self.assertIsNotNone(deliverable_files)
        excluded = self.root / ".tools-venv/vendor/fake.step"
        excluded.parent.mkdir(parents=True)
        excluded.write_text("TEST_ONLY")
        ordinary = self.root / "README.md"
        ordinary.write_text("deliverable")
        self.assertEqual(list(deliverable_files(self.root)), [ordinary])


if __name__ == "__main__":
    unittest.main()
