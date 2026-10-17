#pragma once
#include "controller.hpp"
#include "test_storage.hpp"
// TEST_ONLY arbitrary values for deterministic host event tests. NEVER hardware calibration.
inline rb67::Config syntheticConfig() {
    rb67::Config c; c.calibration=rb67::Calibration::TestOnly; c.reverse_path_verified=true;
    c.debounce_ms=1; c.self_test_ms=2; c.charge_pause_max_ms=40; c.motor_settle_ms=2;
    c.leave_home_max_ms=50; c.entry_max_ms=100; c.capture_max_ms=50;
    c.exit_enter_max_ms=150; c.exit_clear_max_ms=100; c.entry_clear_max_ms=150;
    c.return_home_max_ms=120; c.total_max_ms=500; c.sample_gap_max_ms=20;
    c.startup_blank_ms=5; c.jam_dwell_ms=10; c.coast_ms=2; c.coast_max_ms=20; c.reverse_max_ms=10;
    c.a_forward_duty=.4; c.b_forward_duty=.5; c.a_reverse_duty=.1;
    c.start_battery_v=3.5; c.abort_battery_v=3.1;
    c.jam_a_current_a=.8; c.jam_b_current_a=.9; c.hard_a_current_a=2; c.hard_b_current_a=2;
    c.stopped_current_max_a=.1; return c;
}
inline rb67::Inputs syntheticInputs() {
    rb67::Inputs i; i.pack_present=i.door_closed=i.pickup_home=true; i.dark_slide_inserted=false;
    i.sensor_valid_mask=0x3f; i.analog_valid=i.rail_good=i.charge_pause_ack=i.reverse_position_valid=true;
    i.battery_voltage_v=3.8; return i;
}
struct Fixture {
    RamFlash flash; rb67::Journal journal{flash}; rb67::Config config=syntheticConfig();
    rb67::Controller core{config,journal,rb67::Mode::HostSimulation}; rb67::Inputs in=syntheticInputs();
    std::uint64_t time=0;
    void step(std::uint64_t dt=2) { time+=dt; core.tick(time,in); }
    void settle() { step(); step(); step(); }
    void bootFresh() { settle(); require(core.confirmNewPack(true),"fresh pack explicit confirmation must succeed"); }
    void press(bool cover) { if(cover) in.load_button=true; else in.eject_button=true; step();
        in.load_button=in.eject_button=false; step(); step(); }
    void leaveHome() { in.pickup_home=false; step(); step(); }
    void enter() { in.roller_entry=true; step(); step(); }
    void capture() { in.capture_confirmed=true; step(); }
    void home() { in.pickup_home=true; step(); step(); }
    void exitRise() { in.film_exit=true; step(); step(); }
    void clearEntry() { in.roller_entry=false; step(); step(); }
    void clearExit() { in.film_exit=false; step(); step(); }
    void completeTransport(bool home_before_exit=true) {
        leaveHome(); enter(); capture(); if(home_before_exit) home();
        exitRise(); clearEntry(); clearExit(); if(!home_before_exit) home();
        step(); in.capture_confirmed=false; step();
    }
    void cover() { bootFresh(); press(true); require(core.outputs().a_arm,"positive load fixture must actually drive");
        completeTransport(); require(core.snapshot().frames_remaining==10 && core.snapshot().state==rb67::State::Ready,"cover fixture must finish with 10 READY"); }
    bool stopped() const { return !core.outputs().a_arm && !core.outputs().b_arm && core.outputs().a_duty==0 && core.outputs().b_duty==0; }
};
