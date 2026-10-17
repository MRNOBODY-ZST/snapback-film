#include "controller.hpp"
#include <cmath>
#include <limits>
namespace rb67 {
namespace {
bool positive(double v) { return std::isfinite(v) && v>0; }
bool duty(double v) { return positive(v) && v<=1; }
bool latched(State s) { return s==State::Jam || s==State::Fault || s==State::CycleUncertain || s==State::Service; }
}
bool Config::valid(Mode mode) const {
    if(calibration==Calibration::Unverified || (mode==Mode::Hardware && calibration!=Calibration::Measured)) return false;
    const std::uint32_t times[]={debounce_ms,self_test_ms,charge_pause_max_ms,motor_settle_ms,leave_home_max_ms,
        entry_max_ms,capture_max_ms,exit_enter_max_ms,exit_clear_max_ms,entry_clear_max_ms,return_home_max_ms,
        total_max_ms,sample_gap_max_ms,startup_blank_ms,jam_dwell_ms,coast_ms,coast_max_ms,reverse_max_ms};
    for(auto t:times) if(t==0 || t>3600000) return false;
    return duty(a_forward_duty) && duty(b_forward_duty) && duty(a_reverse_duty) &&
        positive(start_battery_v) && positive(abort_battery_v) && start_battery_v>=abort_battery_v &&
        positive(jam_a_current_a) && positive(jam_b_current_a) && positive(hard_a_current_a) && positive(hard_b_current_a) &&
        positive(stopped_current_max_a) && hard_a_current_a>jam_a_current_a && hard_b_current_a>jam_b_current_a &&
        stopped_current_max_a<jam_a_current_a && stopped_current_max_a<jam_b_current_a &&
        startup_blank_ms<leave_home_max_ms && startup_blank_ms<entry_max_ms && coast_ms<=coast_max_ms &&
        motor_settle_ms<charge_pause_max_ms && sample_gap_max_ms<total_max_ms;
}
Controller::Controller(const Config& c,Journal& j,Mode m):cfg_(c),journal_(j),mode_(m) {}
void Controller::Debounced::update(bool value,std::uint64_t now,std::uint32_t delay) {
    if(!initialized) { initialized=true; stable=candidate=value; since=now; return; }
    if(value!=candidate) { candidate=value; since=now; }
    if(candidate!=stable && now-since>=delay) stable=candidate;
}
void Controller::stop() { output_.a_duty=output_.b_duty=0; output_.a_arm=output_.b_arm=false; }
void Controller::drive(double a,double b) {
    if(a!=0 && output_.a_duty==0) a_started_=now_;
    if(b!=0 && output_.b_duty==0) b_started_=now_;
    output_.a_duty=a; output_.b_duty=b; output_.a_arm=a!=0; output_.b_arm=b!=0;
}
bool Controller::moving() const { return output_.a_arm || output_.b_arm; }
bool Controller::analogHealthy() const {
    return input_.analog_valid && std::isfinite(input_.battery_voltage_v) && input_.battery_voltage_v>0 &&
        std::isfinite(input_.motor_a_current_a) && input_.motor_a_current_a>=0 &&
        std::isfinite(input_.motor_b_current_a) && input_.motor_b_current_a>=0;
}
bool Controller::safeToStart() const {
    return cfg_.valid(mode_) && input_.sensor_valid_mask==0x3f && analogHealthy() && input_.rail_good &&
        !input_.bridge_fault_a && !input_.bridge_fault_b && input_.pack_present && input_.door_closed &&
        !input_.dark_slide_inserted && sensors_[0].stable && sensors_[1].stable && !sensors_[2].stable &&
        input_.pickup_home && sensors_[3].stable && !sensors_[4].stable && !sensors_[5].stable &&
        !input_.roller_entry && !input_.film_exit && input_.battery_voltage_v>=cfg_.start_battery_v &&
        !input_.capture_confirmed &&
        input_.motor_a_current_a<=cfg_.stopped_current_max_a && input_.motor_b_current_a<=cfg_.stopped_current_max_a;
}
bool Controller::safeToReverse() const {
    return cfg_.reverse_path_verified && input_.reverse_position_valid && !input_.reverse_limit_reached &&
        home_left_ && !sensors_[3].stable && !input_.pickup_home && !entry_seen_ && !exit_seen_ && !captured_ && !input_.capture_confirmed &&
        !record_.reverse_used && input_.sensor_valid_mask==0x3f && input_.pack_present && input_.door_closed &&
        !input_.dark_slide_inserted && !sensors_[2].stable && !input_.roller_entry && !input_.film_exit &&
        !sensors_[4].stable && !sensors_[5].stable && analogHealthy() && input_.rail_good &&
        !input_.bridge_fault_a && !input_.bridge_fault_b && input_.battery_voltage_v>=cfg_.start_battery_v &&
        input_.motor_a_current_a<=cfg_.stopped_current_max_a && input_.motor_b_current_a<=cfg_.stopped_current_max_a;
}
void Controller::fail(State state,Fault fault) {
    stop(); state_=state; phase_=Phase::Latched; fault_=fault; output_.request_kill_latch=true; output_.charge_pause=true;
    if(record_.in_progress) count_known_=false;
}
void Controller::idle() {
    stop(); phase_=Phase::None; output_.charge_pause=false;
    if(!input_.pack_present || !sensors_[0].stable) { state_=State::NoCartridge; return; }
    if(!input_.door_closed || !sensors_[1].stable) { state_=State::DoorOpen; return; }
    if(input_.dark_slide_inserted || sensors_[2].stable) { state_=State::DarkSlide; return; }
    if(input_.battery_voltage_v<cfg_.start_battery_v) { state_=State::LowBattery; return; }
    if(!sensors_[3].stable || sensors_[4].stable || sensors_[5].stable) { fail(State::Fault,Fault::SensorSequence); return; }
    if(!record_valid_ || !record_.cover_done) state_=State::LoadPending;
    else state_=record_.frames_remaining?State::Ready:State::Empty;
}
bool Controller::confirmNewPack(bool confirmed) {
    if(!confirmed || !booted_ || !cfg_.valid(mode_) || record_.in_progress || latched(state_) || moving() ||
       state_==State::SelfTest || !analogHealthy() || input_.sensor_valid_mask!=0x3f ||
       !input_.pack_present || !input_.door_closed || !sensors_[3].stable || sensors_[4].stable || sensors_[5].stable ||
       !input_.rail_good || input_.bridge_fault_a || input_.bridge_fault_b ||
       record_.pack_session==std::numeric_limits<std::uint32_t>::max()) return false;
    Record fresh; fresh.pack_session=record_.pack_session+1; fresh.cycle_id=record_.cycle_id;
    if(!persist(fresh)) { fail(State::Fault,Fault::Storage); return false; }
    record_valid_=count_known_=true; fault_=Fault::None; idle(); return true;
}
bool Controller::persist(const Record& next) {
    if(!journal_.append(next)) return false;
    const auto got=journal_.load();
    if(got.status!=JournalStatus::Valid || !got.has_record || got.record.pack_session!=next.pack_session ||
       got.record.cycle_id!=next.cycle_id || got.record.frames_remaining!=next.frames_remaining ||
       got.record.kind!=next.kind || got.record.in_progress!=next.in_progress ||
       got.record.cover_done!=next.cover_done || got.record.reverse_used!=next.reverse_used) return false;
    record_=got.record; return true;
}
void Controller::enterService() {
    stop(); state_=State::Service; phase_=Phase::Latched; output_.request_kill_latch=true; output_.charge_pause=true;
    if(record_.in_progress) count_known_=false;
}
void Controller::start(CycleKind kind) {
    if(!safeToStart() || !record_valid_ || record_.in_progress || record_.cycle_id==std::numeric_limits<std::uint32_t>::max()) return;
    Record next=record_; next.in_progress=true; next.kind=kind; next.reverse_used=false; ++next.cycle_id;
    // Intent is synchronous, bounded by the Storage HAL contract, with both bridges stopped.
    stop();
    if(!persist(next)) { count_known_=false; fail(State::Fault,Fault::Storage); return; }
    home_left_=home_returned_=entry_seen_=entry_cleared_=exit_seen_=exit_cleared_=captured_=false;
    jam_a_timing_=jam_b_timing_=false;
    cycle_start_=phase_at_=now_; state_=State::EjectStart; phase_=Phase::ChargePause; output_.charge_pause=true;
}
void Controller::beginJam(Fault fault) {
    stop(); fault_=fault; count_known_=false; state_=State::Jam; phase_=Phase::RecoveryStop; phase_at_=now_;
    jam_a_timing_=jam_b_timing_=false;
}
void Controller::recovery() {
    if(now_-motion_start_>=cfg_.total_max_ms) { fail(State::Jam,Fault::Timeout); return; }
    if(phase_==Phase::RecoveryStop) {
        stop();
        // Raw proof observed during coast permanently ends recovery, even if the signal is brief.
        if(input_.capture_confirmed || input_.roller_entry || input_.film_exit || input_.pickup_home ||
           input_.dark_slide_inserted || !input_.reverse_position_valid || input_.reverse_limit_reached) {
            fail(State::Jam,fault_); return;
        }
        // Even an eligible rollback must include a stopped tick and a bounded coast interval.
        if(now_-phase_at_<cfg_.coast_ms) return;
        if(safeToReverse()) {
            Record next=record_; next.reverse_used=true;
            if(!persist(next)) { fail(State::Jam,Fault::Storage); return; }
            phase_=Phase::Reverse; phase_at_=now_;
            drive(-cfg_.a_reverse_duty,0); return;
        }
        if(entry_seen_ || exit_seen_ || captured_ || input_.capture_confirmed || !input_.reverse_position_valid || !cfg_.reverse_path_verified ||
           !input_.pack_present || !input_.door_closed || input_.dark_slide_inserted || sensors_[3].stable ||
           input_.roller_entry || input_.film_exit || now_-phase_at_>=cfg_.coast_max_ms) fail(State::Jam,fault_);
        return;
    }
    if(phase_==Phase::Reverse) {
        // Reverse_position_valid must be continuously observed, not inferred from motor time.
        if(!input_.reverse_position_valid || input_.reverse_limit_reached || input_.capture_confirmed || input_.pickup_home ||
           input_.roller_entry || input_.film_exit || input_.dark_slide_inserted ||
           input_.motor_a_current_a>cfg_.jam_a_current_a || now_-phase_at_>=cfg_.reverse_max_ms) { fail(State::Jam,fault_); return; }
        drive(-cfg_.a_reverse_duty,0);
    }
}
void Controller::commit() {
    stop(); Record next=record_; next.in_progress=false; next.reverse_used=false;
    if(next.kind==CycleKind::Cover) { next.cover_done=true; next.frames_remaining=10; }
    else if(next.kind==CycleKind::Photo && next.cover_done && next.frames_remaining>0) --next.frames_remaining;
    else { fail(State::CycleUncertain,Fault::SensorSequence); return; }
    if(!persist(next)) { fail(State::CycleUncertain,Fault::Storage); return; }
    count_known_=true; state_=State::Complete; phase_=Phase::None;
}
void Controller::motion() {
    // Absolute deadlines win over a new event on the same tick; no late edge may commit a count.
    if(now_-motion_start_>=cfg_.total_max_ms || (!home_left_ && now_-motion_start_>=cfg_.leave_home_max_ms) ||
       (entry_seen_ && !captured_ && now_-entry_at_>=cfg_.capture_max_ms) ||
       (captured_ && !exit_seen_ && now_-capture_at_>=cfg_.exit_enter_max_ms) ||
       (entry_seen_ && !entry_cleared_ && now_-entry_at_>=cfg_.entry_clear_max_ms) ||
       (exit_seen_ && !exit_cleared_ && now_-exit_at_>=cfg_.exit_clear_max_ms) ||
       (captured_ && !home_returned_ && now_-capture_at_>=cfg_.return_home_max_ms)) {
        fail(State::CycleUncertain,Fault::Timeout); return;
    }
    if(!entry_seen_ && now_-motion_start_>=cfg_.entry_max_ms) { beginJam(Fault::Timeout); return; }
    const bool home=sensors_[3].stable,entry=sensors_[4].stable,exit=sensors_[5].stable;
    if(input_.capture_confirmed && !entry_seen_ && !entry) { fail(State::CycleUncertain,Fault::SensorSequence); return; }
    if(!home && !home_left_) { home_left_=true; progress_at_=now_; }
    if(home && home_left_ && !home_returned_) {
        if(!captured_) { fail(State::CycleUncertain,Fault::SensorSequence); return; }
        home_returned_=true; progress_at_=now_;
    }
    if(entry && !entry_seen_) {
        if(!home_left_ || home || exit_seen_) { fail(State::CycleUncertain,Fault::SensorSequence); return; }
        entry_seen_=true; entry_at_=progress_at_=now_; phase_=Phase::Capture;
    }
    if(entry_seen_ && !entry && !entry_cleared_) { entry_cleared_=true; progress_at_=now_; }
    if(entry_seen_ && input_.capture_confirmed && !captured_) { captured_=true; capture_at_=progress_at_=now_; phase_=Phase::Transport; }
    if(exit && !exit_seen_) {
        if(!entry_seen_ || !captured_) { fail(State::CycleUncertain,Fault::SensorSequence); return; }
        exit_seen_=true; exit_at_=progress_at_=now_;
    }
    if(exit_seen_ && !exit && !exit_cleared_) { exit_cleared_=true; progress_at_=now_; }
    if((entry_cleared_ && entry) || (exit_cleared_ && exit) || (home_returned_ && !home)) {
        fail(State::CycleUncertain,Fault::SensorSequence); return;
    }
    if(home_returned_ && entry_seen_ && entry_cleared_ && exit_seen_ && exit_cleared_ && !entry && !exit) { commit(); return; }
    const auto over=[this](bool enabled,double current,double limit,std::uint64_t started,bool& timing,std::uint64_t& since) {
        if(!enabled || now_-started<cfg_.startup_blank_ms || current<=limit) { timing=false; return false; }
        if(!timing) { timing=true; since=now_; }
        return now_-since>=cfg_.jam_dwell_ms && now_-progress_at_>=cfg_.jam_dwell_ms;
    };
    if(over(output_.a_arm,input_.motor_a_current_a,cfg_.jam_a_current_a,a_started_,jam_a_timing_,jam_a_since_)) { beginJam(Fault::JamCurrentA); return; }
    if(over(output_.b_arm,input_.motor_b_current_a,cfg_.jam_b_current_a,b_started_,jam_b_timing_,jam_b_since_)) { beginJam(Fault::JamCurrentB); return; }
    const double a=(!entry_seen_ || (captured_ && !home_returned_))?cfg_.a_forward_duty:0;
    const double b=exit_cleared_?0:cfg_.b_forward_duty;
    drive(a,b);
    if(exit_cleared_ && !home_returned_) phase_=Phase::AwaitHome;
    else if(captured_) phase_=Phase::Transport;
    else if(entry_seen_) phase_=Phase::Capture;
    else phase_=Phase::Pickup;
    if(record_.kind==CycleKind::Cover) state_=State::LoadBlackCover;
    else if(phase_==Phase::Pickup) state_=State::Pickup;
    else if(phase_==Phase::Capture) state_=State::RollerCapture;
    else if(phase_==Phase::AwaitHome) state_=State::ReturnHome;
    else state_=State::Ejecting;
}
void Controller::tick(std::uint64_t now,const Inputs& input) {
    if(clock_seen_ && now<last_tick_) { fail(State::CycleUncertain,Fault::Clock); return; }
    const auto gap=clock_seen_?now-last_tick_:0;
    now_=now; last_tick_=now; clock_seen_=true; input_=input;
    const bool eject_edge=input.eject_button && !last_eject_,load_edge=input.load_button && !last_load_;
    last_eject_=input.eject_button; last_load_=input.load_button;
    const bool bits[]={input.pack_present,input.door_closed,input.dark_slide_inserted,input.pickup_home,input.roller_entry,input.film_exit};
    for(unsigned n=0;n<6;++n) sensors_[n].update(bits[n],now,cfg_.debounce_ms);
    if(!booted_) {
        booted_=true; boot_at_=now; stop();
        const auto load=journal_.load(); record_=load.record; record_valid_=load.has_record;
        count_known_=load.status==JournalStatus::Valid && !record_.in_progress;
        if(!cfg_.valid(mode_)) { fail(State::Service,Fault::Configuration); return; }
        if(load.status==JournalStatus::IoError || load.status==JournalStatus::Corrupt) { fail(State::CycleUncertain,Fault::Storage); return; }
        if(record_.in_progress) { fail(State::CycleUncertain,Fault::PendingCycle); return; }
        state_=State::SelfTest; return; // startup-held buttons cannot become a new edge.
    }
    if((latched(state_) && !(state_==State::Jam && (phase_==Phase::RecoveryStop || phase_==Phase::Reverse))) ||
       (state_==State::LowBattery && fault_!=Fault::None)) { stop(); return; }
    if(input.sensor_valid_mask!=0x3f) { fail(State::CycleUncertain,Fault::SensorHealth); return; }
    if(!analogHealthy()) { fail(State::CycleUncertain,Fault::AnalogHealth); return; }
    if(!input.rail_good || input.bridge_fault_a || input.bridge_fault_b) { fail(State::CycleUncertain,Fault::Bridge); return; }
    if(input.motor_a_current_a>=cfg_.hard_a_current_a || input.motor_b_current_a>=cfg_.hard_b_current_a) { fail(State::CycleUncertain,Fault::HardCurrent); return; }
    if(record_.in_progress) {
        if(!input.door_closed) { fail(State::CycleUncertain,Fault::DoorOpened); return; }
        if(!input.pack_present) { fail(State::CycleUncertain,Fault::PackRemoved); return; }
        if(input.battery_voltage_v<cfg_.abort_battery_v) { fail(State::LowBattery,Fault::LowVoltage); return; }
        if(state_!=State::EjectStart && !input.charge_pause_ack) { fail(State::CycleUncertain,Fault::ChargePauseLost); return; }
        if(gap>cfg_.sample_gap_max_ms) { fail(State::CycleUncertain,Fault::Scheduler); return; }
    }
    if(state_==State::SelfTest) {
        if(now-boot_at_<cfg_.self_test_ms) return;
        if(input.motor_a_current_a>cfg_.stopped_current_max_a || input.motor_b_current_a>cfg_.stopped_current_max_a) { fail(State::Fault,Fault::AnalogHealth); return; }
        idle(); return;
    }
    if(state_==State::Jam) { recovery(); return; }
    if(state_==State::EjectStart) {
        stop();
        if(input.dark_slide_inserted || sensors_[2].stable || !input.pickup_home || input.roller_entry || input.film_exit ||
           !sensors_[3].stable || sensors_[4].stable || sensors_[5].stable || input.capture_confirmed) { fail(State::CycleUncertain,Fault::SensorSequence); return; }
        if(now-cycle_start_>=cfg_.charge_pause_max_ms) { fail(State::CycleUncertain,Fault::Timeout); return; }
        if(!input.charge_pause_ack || now-cycle_start_<cfg_.motor_settle_ms) return;
        motion_start_=progress_at_=phase_at_=now; phase_=Phase::Pickup;
        state_=record_.kind==CycleKind::Cover?State::LoadBlackCover:State::Pickup;
        drive(cfg_.a_forward_duty,cfg_.b_forward_duty); return;
    }
    if(record_.in_progress) { motion(); return; }
    if(state_==State::Complete) { idle(); return; }
    idle();
    if(state_==State::Ready && eject_edge && !load_edge) start(CycleKind::Photo);
    else if(state_==State::LoadPending && record_valid_ && load_edge && !eject_edge) start(CycleKind::Cover);
}
Snapshot Controller::snapshot() const {
    return {state_,phase_,fault_,record_.frames_remaining,count_known_,record_.cover_done,record_.in_progress,
        record_.reverse_used,record_.cycle_id,record_.pack_session};
}
const char* stateName(State s) {
    switch(s) {
    case State::PowerOff:return "POWER_OFF"; case State::Boot:return "BOOT"; case State::SelfTest:return "SELF_TEST";
    case State::DarkSlide:return "DARK_SLIDE"; case State::Ready:return "READY"; case State::EjectStart:return "EJECT_START";
    case State::Pickup:return "PICKUP"; case State::RollerCapture:return "ROLLER_CAPTURE"; case State::Ejecting:return "EJECTING";
    case State::ReturnHome:return "RETURN_HOME"; case State::Complete:return "COMPLETE"; case State::Empty:return "EMPTY";
    case State::Jam:return "JAM"; case State::LowBattery:return "LOW_BATTERY"; case State::Service:return "SERVICE";
    case State::NoCartridge:return "NO_CARTRIDGE"; case State::DoorOpen:return "DOOR_OPEN"; case State::LoadPending:return "LOAD_PENDING";
    case State::LoadBlackCover:return "LOAD_BLACK_COVER"; case State::CycleUncertain:return "CYCLE_UNCERTAIN"; case State::Fault:return "FAULT";
    } return "INVALID";
}
const char* phaseName(Phase p) {
    switch(p) { case Phase::None:return "NONE"; case Phase::ChargePause:return "CHARGE_PAUSE"; case Phase::Pickup:return "PICKUP";
    case Phase::Capture:return "CAPTURE"; case Phase::Transport:return "TRANSPORT"; case Phase::AwaitHome:return "AWAIT_HOME";
    case Phase::RecoveryStop:return "RECOVERY_STOP"; case Phase::Reverse:return "REVERSE"; case Phase::Latched:return "LATCHED"; }
    return "INVALID";
}
const char* faultName(Fault f) {
    switch(f) { case Fault::None:return "NONE"; case Fault::Configuration:return "CONFIGURATION"; case Fault::Storage:return "STORAGE";
    case Fault::PendingCycle:return "PENDING_CYCLE"; case Fault::SensorHealth:return "SENSOR_HEALTH"; case Fault::AnalogHealth:return "ANALOG_HEALTH";
    case Fault::SensorSequence:return "SENSOR_SEQUENCE"; case Fault::DoorOpened:return "DOOR_OPENED"; case Fault::PackRemoved:return "PACK_REMOVED";
    case Fault::Bridge:return "BRIDGE"; case Fault::LowVoltage:return "LOW_VOLTAGE"; case Fault::HardCurrent:return "HARD_CURRENT";
    case Fault::JamCurrentA:return "JAM_CURRENT_A"; case Fault::JamCurrentB:return "JAM_CURRENT_B"; case Fault::Timeout:return "TIMEOUT";
    case Fault::Scheduler:return "SCHEDULER"; case Fault::Clock:return "CLOCK"; case Fault::ChargePauseLost:return "CHARGE_PAUSE_LOST"; } return "INVALID";
}
} // namespace rb67
