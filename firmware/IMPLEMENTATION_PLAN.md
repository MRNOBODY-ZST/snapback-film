# R0 host controller implementation plan

**Goal:** Build and actually run a platform independent C++17 dual-motor transport core against the existing [behavior contract](../docs/firmware.md), with no claim of hardware calibration or successful film development.

**Architecture:** A bounded `tick(uint64_t milliseconds, Inputs)` processes sensor transitions and deadlines without sleeps. It returns signed A/B duty commands and independent ARM outputs. A separately testable two-slot CRC journal writes an intent before any motion, a reverse-used intent before a permitted rollback, and a completion only after exit plus home evidence. The default configuration is incomplete and cannot enable a bridge.

**Execution:** The user explicitly requested implementation of this already-defined design. Implement in this delegated task with test-first host checks; do not edit the root contract, root parameter register, or audit. Four concurrent agent slots are occupied, so this task cannot spawn a fifth worker.

## Files and responsibilities

- `src/journal.hpp/.cpp`: explicit little-endian record format, CRC32, two independently erasable slots, final validity marker, verified writes, corruption reporting.
- `src/controller.hpp/.cpp`: logical sensor input, debounce, independent current guards, timeouts, transport evidence, one safe bounded A rollback followed by latched JAM, no automatic forward retry.
- `tests/journal_tests.cpp`, `tests/controller_tests.cpp`: actual host execution, deliberate write tears/corruption/power cycles, positive transport traces and injected faults.
- `host/sim.cpp`: TEST_ONLY CSV trace using explicit amperes, volts, milliseconds internally and seconds in CSV.
- `build-host.ps1`, `README.md`: reproducible local build and boundaries of HAL/bench use.
- `../electronics/pcb/R0_bench-interface.md/.json/.svg`: independent OWN_DESIGN bench carrier geometry, fixed logical connector order, no final back fit, no Gerber.

## Test-first tasks

- [x] Write journal behavior tests and watch them fail against safe non-writing stubs; implement persistence and run them green.
- [x] Write controller traces before motion implementation; watch positive traces and relevant state checks fail; implement the bounded state machine and run all checks green.
- [x] Add uncovered edges as failing regressions before correction, including independent reviewer probes for raw startup signals, coast pulses and exact deadline completion.
- [x] Build and run the host simulator; validate CSV fields and trace count against the same transport core.
- [x] Create and structurally validate the separate bench interface JSON/SVG; render and inspect the diagram.
- [x] Run the complete host suite with compiler warnings treated as errors; leave product firmware, physical calibration and bench validation explicitly outstanding.

No motor thresholds, timing or mechanical geometry become measured values through passing a synthetic test. The host TEST_ONLY configuration must be rejected in Hardware mode.
