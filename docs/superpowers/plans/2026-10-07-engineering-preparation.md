# R0 Engineering Preparation Implementation Plan

> For agentic workers: use task ownership below and test-driven-development for executable changes. This plan is authorized for execution by the user's request to complete the work we can do now.

**Goal:** Complete useful engineering preparation without substituting guessed measurements for the RB67 film plane, cartridge interface or instant-film processing parameters.

**Architecture:** Three independent workers own reference retrieval, bench fixture CAD and the two-motor controller. The main worker owns calculations, trace analysis, integration and verification. Camera integration remains behind the existing physical gates.

**Tech Stack:** Python 3.10+ standard library; C++17 host controller; scriptable CAD with an isolated project dependency environment.

**Spec:** [requirements.md](../../requirements.md), [film-plane.md](../../film-plane.md), [transport.md](../../transport.md), [firmware.md](../../firmware.md).

## Global Constraints

- Preserve the appropriate original RB67 rotating adapter; no donor instant-camera parts or proprietary development module.
- Physical UNKNOWN values stay null and carry MEASUREMENT_REQUIRED; source mesh dimensions are separate nominal geometry.
- Bench design choices may have explicit OWN_DESIGN provenance. They do not establish camera fit, roller performance or gate passage.
- No final enclosure, PCB/Gerber or claimed functioning back before mechanical/optical validation.
- All example traces and test inputs are TEST_ONLY, separate from physical experimental records.

## Review Focus

- Missing or incorrectly labelled dimensional inputs must not become zero or yield PASS.
- Motor torque is referred through the external gear ratio and efficiency; stall torque is not a continuous rating.
- Logging cannot infer battery current by summing PWM motor current channels.
- Power loss, an open door and incomplete exit/home events must not trigger a second sheet or commit the counter.
- Existing CAD asset and prototype export provenance must remain separate from final manufacturing authorization.

## Task 1 — Reference assets (transport worker)

Files: cad/reference source assets, source-manifest.json and geometry-report.json.
Consumes: previously verified creator pages and licences.
Produces: unchanged, hash-registered source assets; explicit status for remaining inaccessible files.

- [x] Use normal authorized public downloads for the cartridge STL and editable source files.
- [x] Verify format, creator, licence and hash; preserve original files.
- [x] Regenerate the read-only geometry inspection report and report unresolved access limitations.

## Task 2 — Engineering calculations (main worker)

Files: tools/engineering_calculations.py, tools/run_engineering.py, tools/tests/test_engineering_calculations.py, tools/calculation-inputs.json.
Interface: film_plane_screen(data), motor_requirements(data), cam_requirements(data), roller_preload(data), gear_geometry(data), synchronized_capacity(data), calculate_all(config); dictionaries in/out, explicit units and provenance.

- [x] Write and observe failing tests for UNKNOWN, units, tolerance intervals, gear torque direction, SF >= 2, cam derivative and transport-distance sufficiency.
- [x] Implement pure calculations and a JSON CLI with no fixed unknown defaults.
- [x] Run tests and the real null-valued configuration; confirm that no physical PASS is produced.

## Task 3 — Trace analysis (main worker)

Files: tools/analyze_cycle_log.py, tools/tests/test_cycle_log.py, tools/tests/fixtures/synthetic.TEST_ONLY.csv, experiments/transport/diagnostic-log.csv.
Interface: analyze_rows(rows); CSV records with timestamp_s, state, motor_a_current_a, motor_b_current_a and optional independently measured battery_current_a/battery_voltage_v.

- [x] Write and observe failing tests for backward/nonfinite time, missing battery-current channels, independent battery energy and cycle grouping.
- [x] Implement data validation, per-cycle duration/current summaries and optional battery-energy integration.
- [x] Run tests, the empty real log and labelled synthetic fixture. No jam threshold or reliability result is inferred from synthetic data.

## Task 4 — Bench fixtures (film-plane worker)

Files: cad/feed_test_rig/R0_bench and cad/roller_test_rig/R0_bench source/config/exports/manifests.
Consumes: defined bench choices and commodity part drawings; no fixed cartridge or camera dimensions.
Produces: editable open fixture source, prototype STEP/STL, dimensions/provenance and machining/assembly limits.

- [x] Test parameter guards and geometry assumptions before generation.
- [x] Build adjustable pickup mounting/observation and removable adjustable roller supports.
- [x] Execute CAD export and check geometry. Keep the unknown pickup tip and developer processing settings unqualified.

## Task 5 — Controller and PCB bench handoff (electronics worker)

Files: firmware/src, firmware/tests/build instructions; electronics/pcb/R0_bench-interface.md and JSON/SVG.
Consumes: existing safety/state/persistence contracts and measured calibration provided later.
Produces: compiled host core with tests; explicit independent bench board geometry and logical connector pin order.

- [x] Test black cover/counting, exit/home completion, interlocks, jam recovery, timeouts, corrupt/torn persistence and calibration-disabled startup.
- [x] Implement nonblocking two-motor core and CRC-protected intent/commit journal.
- [x] Define bench board outline/holes/connector zones with OWN_DESIGN provenance; keep integrated PCB placement unknown.

## Task 6 — Integration and verification (main worker)

Files: README.md, docs/preparation-status.md, tools/audit_feasibility.py and prototype export register.

- [x] Inspect all worker results and add an independent cross-review of the controller and fixture safety assumptions.
- [x] Permit only registered prototype fixtures/reference assets in the audit; keep final back exports locked.
- [x] Run the complete relevant Python/C++/CAD checks and record exact outcomes and limitations.
- [x] Synchronize to the desktop project while preserving user-modified files; verify hashes.

## Execution ledger

2026-10-07: Tasks 1, 4 and 5 delegated to the existing independent owners. Main worker implements tasks 2, 3 and 6. This directory is a standalone project, not a Git worktree; no branch, push or repository publication is required. User's current instruction authorizes continuing without a new plan-approval pause.

2026-10-07 completion: 36 Python tool tests, 8 journal checks, 29 controller checks, 24 bench CAD tests; 19 original assets and 42 fixture exports plus 2 reference previews registered. Desktop source files copied and verified by SHA-256. Physical gates remain open; no final camera-back release.
