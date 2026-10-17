"""Hash-register fixture and reference exports without approving a camera back."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

EXCLUDED_DIRS = {".tools-venv", ".git", ".pio", "__pycache__", ".pytest_cache", ".test-temp", "build"}
CAD_SUFFIXES = {".stl", ".step", ".stp", ".gbr", ".fcstd", ".f3d"}
SCOPES = {"SOURCE_REFERENCE_PREVIEW": ("cad/cartridge/R0_reference_only",),
          "TEST_FIXTURE_ONLY": ("cad/feed_test_rig/R0_bench", "cad/roller_test_rig/R0_bench")}


def deliverable_files(root: Path):
    """Never traverse local package runtimes or transient compiler outputs."""
    for directory, subdirs, files in os.walk(root):
        subdirs[:] = sorted(d for d in subdirs if d not in EXCLUDED_DIRS)
        for name in sorted(files):
            if not name.endswith((".pyc", ".bak")):
                yield Path(directory) / name


def audit_registered_exports(root: Path, register: dict, reference_paths: set[str]) -> dict:
    root = root.resolve()
    errors, fixture, preview = [], [], []
    allowed = set(reference_paths)
    seen_manifests = set()
    for entry in register.get("entries", []):
        scope = entry.get("scope")
        prefix = entry.get("export_root", "")
        mp = (root / entry.get("manifest_path", "")).resolve()
        directory = (root / prefix).resolve()
        permitted = scope in SCOPES and any(directory.is_relative_to((root / p).resolve()) for p in SCOPES.get(scope, ()))
        if not permitted or not mp.is_relative_to(directory) or mp in seen_manifests:
            errors.append("Invalid scope/path/duplicate export manifest: " + str(mp))
            continue
        seen_manifests.add(mp)
        try:
            manifest = json.loads(mp.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append("Unreadable export manifest: " + str(exc))
            continue
        final_guard = manifest.get("final_back_manufacturing_authorized", manifest.get("manufacturing_authorized"))
        if manifest.get("mode") != scope or manifest.get("physical_validation") is not False or final_guard is not False:
            errors.append("Export claims unverified physical/final authority: " + str(mp))
            continue
        for asset in manifest.get("exports", []):
            rel = asset.get("path", "")
            path = (root / rel).resolve()
            if not path.is_relative_to(directory) or rel in allowed or path.suffix.lower() not in CAD_SUFFIXES:
                errors.append("Invalid/outside/duplicate export: " + rel)
                continue
            try:
                data = path.read_bytes()
                valid = hashlib.sha256(data).hexdigest() == asset.get("sha256") and len(data) == asset.get("bytes")
            except OSError:
                valid = False
            if not valid:
                errors.append("Missing/changed registered export: " + rel)
                continue
            allowed.add(rel)
            (fixture if scope == "TEST_FIXTURE_ONLY" else preview).append(rel)
    unauthorized = [p.relative_to(root).as_posix() for p in deliverable_files(root)
                    if p.suffix.lower() in CAD_SUFFIXES and p.relative_to(root).as_posix() not in allowed]
    if unauthorized:
        errors.append("Unregistered CAD/manufacturing files: " + str(unauthorized))
    return {"fixture_exports": fixture, "source_reference_previews": preview,
            "unauthorized_exports": unauthorized, "errors": errors}
