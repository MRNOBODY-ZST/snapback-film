#pragma once
#include "journal.hpp"
#include <cstdint>

namespace rb67 {
enum class Mode { Hardware, HostSimulation };
enum class Calibration { Unverified, TestOnly, Measured };
enum class State {
    PowerOff, Boot, SelfTest, DarkSlide, Ready, EjectStart, Pickup, RollerCapture,
    Ejecting, ReturnHome, Complete, Empty, Jam, LowBattery, Service,
    NoCartridge, DoorOpen, LoadPending, LoadBlackCover, CycleUncertain, Fault
};
enum class Phase { None, ChargePause, Pickup, Capture, Transport, AwaitHome, RecoveryStop, Reverse, Latched };
enum class Fault { None, Configuration, Storage, PendingCycle, SensorHealth, AnalogHealth,
    SensorSequence, DoorOpened, PackRemoved, Bridge, LowVoltage, HardCurrent,
    JamCurrentA, JamCurrentB, Timeout, Scheduler, Clock, ChargePauseLost };
struct Config {
    Calibration calibration=Calibration::Unverified;
    bool reverse_path_verified=false;
    std::uint32_t debounce_ms=0, self_test_ms=0, charge_pause_max_ms=0, motor_settle_ms=0;
    std::uint32_t leave_home_max_ms=0, entry_max_ms=0, capture_max_ms=0;
    std::uint32_t exit_enter_max_ms=0, exit_clear_max_ms=0, entry_clear_max_ms=0;
    std::uint32_t return_home_max_ms=0, total_max_ms=0, sample_gap_max_ms=0;
    std::uint32_t startup_blank_ms=0, jam_dwell_ms=0, coast_ms=0, coast_max_ms=0, reverse_max_ms=0;
    double a_forward_duty=0, b_forward_duty=0, a_reverse_duty=0;
    double start_battery_v=0, abort_battery_v=0;
    double jam_a_current_a=0, jam_b_current_a=0, hard_a_current_a=0, hard_b_current_a=0;
    double stopped_current_max_a=0;
    bool valid(Mode mode) const;
};
struct Inputs {
    bool pack_present=false, door_closed=false, dark_slide_inserted=true;
    bool pickup_home=false, roller_entry=false, film_exit=false;
    std::uint8_t sensor_valid_mask=0; // bits 0..5: independently diagnosed logical S0..S5.
    double motor_a_current_a=0, motor_b_current_a=0, battery_voltage_v=0;
    bool analog_valid=false, bridge_fault_a=false, bridge_fault_b=false, rail_good=false;
    bool capture_confirmed=false; // calibrated evidence separate from S4 edge.
    bool reverse_position_valid=false, reverse_limit_reached=false;
    bool charge_pause_ack=false, eject_button=false, load_button=false;
};
struct Outputs {
    double a_duty=0, b_duty=0; // signed; positive forward, negative reverse.
    bool a_arm=false, b_arm=false, charge_pause=true, request_kill_latch=false;
};
struct Snapshot {
    State state=State::Boot; Phase phase=Phase::None; Fault fault=Fault::None;
    std::uint8_t frames_remaining=0; bool count_known=false;
    bool cover_done=false, pending=false, reverse_used=false;
    std::uint32_t cycle_id=0, pack_session=0;
};
class Controller {
public:
    Controller(const Config& config,Journal& journal,Mode mode=Mode::Hardware);
    void tick(std::uint64_t now_ms,const Inputs& input);
    bool confirmNewPack(bool user_confirms_fresh_pack);
    void enterService(); // stopped diagnostics only; never clears a pending cycle/JAM.
    const Outputs& outputs() const { return output_; }
    Snapshot snapshot() const;
private:
    struct Debounced { bool initialized=false,stable=false,candidate=false; std::uint64_t since=0;
        void update(bool value,std::uint64_t now,std::uint32_t delay); };
    Config cfg_; Journal& journal_; Mode mode_; Outputs output_{}; State state_=State::Boot;
    Phase phase_=Phase::None; Fault fault_=Fault::None; Record record_{};
    Inputs input_{}; Debounced sensors_[6]{};
    bool booted_=false, clock_seen_=false, count_known_=false, record_valid_=false;
    bool last_eject_=false,last_load_=false, home_left_=false,home_returned_=false;
    bool entry_seen_=false,entry_cleared_=false,exit_seen_=false,exit_cleared_=false,captured_=false;
    bool jam_a_timing_=false,jam_b_timing_=false;
    std::uint64_t now_=0,last_tick_=0,boot_at_=0,cycle_start_=0,motion_start_=0,phase_at_=0;
    std::uint64_t entry_at_=0,exit_at_=0,capture_at_=0,progress_at_=0;
    std::uint64_t jam_a_since_=0,jam_b_since_=0,a_started_=0,b_started_=0;
    void stop(); void drive(double a,double b); bool moving() const;
    bool analogHealthy() const; bool safeToStart() const; bool safeToReverse() const;
    void idle(); void fail(State state,Fault fault); void start(CycleKind kind);
    void beginJam(Fault fault); void recovery(); void motion(); void commit();
    bool persist(const Record& next);
};
const char* stateName(State state);
const char* phaseName(Phase phase);
const char* faultName(Fault fault);
} // namespace rb67
