"""Read-only R0 documentation audit. Does not validate a physical camera back."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote
from validate_exports import audit_registered_exports, deliverable_files


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors: list[str] = []
    core = ["research", "measurements", "architecture", "film-plane", "transport", "roller-development", "patents-and-prior-art"]
    for stem in core:
        path = root / "docs" / f"{stem}.md"
        if not path.is_file() or path.stat().st_size < 200:
            errors.append(f"Missing/empty core document: {path}")

    register = json.loads((root / "cad/parameters.json").read_text(encoding="utf-8"))
    params = register["parameters"]
    ids = [p["id"] for p in params]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate parameter IDs")
    classifications = {"VERIFIED_MEASUREMENT", "MANUFACTURER_SPEC", "RELIABLE_SOURCE", "DERIVED", "ESTIMATED", "UNKNOWN"}
    for p in params:
        if p["provenance"] not in classifications or not p["source"] or not p["unit"]:
            errors.append(f"Invalid provenance/source/unit: {p['id']}")
        if p["provenance"] == "UNKNOWN":
            if p["value"] is not None or not p["measurement_required"] or not p["measurement_id"]:
                errors.append(f"Unknown dimension not guarded: {p['id']}")
        if p["role"] == "design_target" and p["provenance"] == "VERIFIED_MEASUREMENT":
            errors.append(f"Target incorrectly called a measurement: {p['id']}")
    if register["manufacturing_export_authorized"] or register["feasibility_result"] != "UNCERTAIN — MEASUREMENT REQUIRED":
        errors.append("R0 result/export guard mismatch")
    cartridge = json.loads((root / "cad/source/instax_square_cartridge.measurement.json").read_text(encoding="utf-8"))
    if cartridge["entity_model_available"] or cartridge["manufacturing_export_authorized"]:
        errors.append("Unmeasured cartridge falsely presented as an entity model")
    if set(cartridge["required_parameters"]) - set(ids):
        errors.append("Cartridge refers to absent parameters")

    links_checked = 0
    for md in (p for p in deliverable_files(root) if p.suffix.lower() == ".md"):
        content = md.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", content):
            target = target.strip().strip("<>")
            if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            resolved = (md.parent / target).resolve()
            links_checked += 1
            if not resolved.exists() or not resolved.is_relative_to(root):
                errors.append(f"Broken/outside local link: {md.relative_to(root)} -> {target}")
    for svg in (p for p in deliverable_files(root) if p.suffix.lower() == ".svg"):
        ET.parse(svg)

    states = ["POWER_OFF", "BOOT", "SELF_TEST", "DARK_SLIDE", "READY", "EJECT_START", "PICKUP", "ROLLER_CAPTURE", "EJECTING", "RETURN_HOME", "COMPLETE", "EMPTY", "JAM", "LOW_BATTERY", "SERVICE"]
    firmware_contract = (root / "docs/firmware.md").read_text(encoding="utf-8")
    for state in states:
        if not re.search(rf"\|\s*{state}\s*\|", firmware_contract):
            errors.append(f"Missing required firmware state: {state}")
    pcb = (root / "electronics/pcb/interface-contract.md").read_text(encoding="utf-8")
    for i in range(6):
        if f"S{i}" not in pcb:
            errors.append(f"Missing sensor S{i}")

    weights = [25, 20, 15, 15, 10, 5, 5, 5]
    scores = {"A": [3,3,4,3,2,2,4,4], "B": [4,4,2,3,4,4,3,3], "C": [2,4,3,3,3,3,2,3]}
    totals = {k: sum(w*s for w,s in zip(weights,v))/5 for k,v in scores.items()}
    if sum(weights) != 100 or totals != {"A":62.0,"B":69.0,"C":58.0}:
        errors.append("Weighted score arithmetic error")
    architecture = (root / "docs/architecture.md").read_text(encoding="utf-8")
    if not re.search(r"\*\*Weighted total /100\*\*.*\*\*62\*\*.*\*\*69\*\*.*\*\*58\*\*", architecture):
        errors.append("Published score totals differ from calculation")
    budget = {"prototype_low":sum([30,30,12,10,20,12,15,30,40]),"prototype_high":sum([60,90,30,30,45,30,30,80,100]),"final_low":sum([20,15,8,5,10,6,10,15]),"final_high":sum([50,40,15,12,20,15,20,30])}
    if list(budget.values()) != [199,495,89,202]:
        errors.append("Budget arithmetic error")

    recorded_rows = 0
    for path in (root / "experiments").rglob("*.csv"):
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames:
                errors.append(f"Missing CSV headers: {path}")
            recorded_rows += sum(1 for row in reader if any(v for v in row.values()))
    reference_manifest_path = root / "cad/reference/source-manifest.json"
    reference_assets = []
    reference_paths = set()
    if reference_manifest_path.is_file():
        reference_manifest = json.loads(reference_manifest_path.read_text(encoding="utf-8"))
        reference_assets = reference_manifest["assets"]
        for asset in reference_assets:
            rel = asset["path"]
            path = (root / rel).resolve()
            if not path.is_relative_to((root / "cad/reference").resolve()) or rel in reference_paths:
                errors.append("Invalid/duplicate reference archive path: " + rel)
                continue
            reference_paths.add(rel)
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != asset["sha256"]:
                errors.append("Missing/changed reference asset: " + rel)
            if not asset["source_page"] or not asset["license"] or asset["modified"] or asset["physical_validation"] or asset["manufacturing_authorized"]:
                errors.append("Invalid reference provenance/guard: " + rel)
    preparation_register = json.loads((root / "cad/preparation-export-register.json").read_text(encoding="utf-8"))
    export_audit = audit_registered_exports(root, preparation_register, reference_paths)
    errors.extend(export_audit["errors"])
    manufactured = export_audit["unauthorized_exports"]

    result = {"scope":"Documentation/provenance/link/arithmetic audit only; no physical validation", "core_documents":len(core),"parameter_count":len(params),"unknown_parameters":sum(p["provenance"]=="UNKNOWN" for p in params),"verified_measurements":sum(p["provenance"]=="VERIFIED_MEASUREMENT" for p in params),"local_links_checked":links_checked,"required_states":len(states),"weighted_scores":totals,"estimated_budget_USD":budget,"zero_failure_cycles_needed_for_99_5_at_one_sided_95_percent":math.ceil(math.log(.05)/math.log(.995)),"experimental_data_rows":recorded_rows,"archived_reference_assets":len(reference_assets),"manufacturing_exports":manufactured,"errors":errors,"passed":not errors}
    result.update({"source_reference_previews": len(export_audit["source_reference_previews"]),
                   "prototype_fixture_exports": len(export_audit["fixture_exports"]),
                   "final_back_manufacturing_authorized": False})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
