#include "controller.hpp"
#include "../tests/synthetic_fixture.hpp"
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>

// A deterministic event script, not a physical film model. Currents and voltage are synthetic.
int main(int argc,char** argv) {
    try {
        std::ofstream file;
        if(argc>2) throw std::runtime_error("usage: host_sim [output.csv]");
        if(argc==2) { file.open(argv[1]); if(!file) throw std::runtime_error("cannot open CSV output"); }
        std::ostream& out=argc==2?file:std::cout;
        Fixture f;
        out<<"timestamp_s,state,motor_a_current_a,motor_b_current_a,home,entry,exit,dark_slide,door_closed,cartridge_present,battery_voltage_v,frames_remaining,cycle_id,transport_phase,count_known,pending,fault,a_duty,b_duty,configuration_origin\n";
        const auto row=[&] {
            const auto s=f.core.snapshot(); const auto& o=f.core.outputs();
            out<<std::fixed<<std::setprecision(3)<<f.time/1000.0<<','<<stateName(s.state)<<','
               <<f.in.motor_a_current_a<<','<<f.in.motor_b_current_a<<','<<f.in.pickup_home<<','
               <<f.in.roller_entry<<','<<f.in.film_exit<<','<<f.in.dark_slide_inserted<<','<<f.in.door_closed<<','
               <<f.in.pack_present<<','<<f.in.battery_voltage_v<<','<<unsigned(s.frames_remaining)<<','<<s.cycle_id<<','
               <<phaseName(s.phase)<<','<<s.count_known<<','<<s.pending<<','<<faultName(s.fault)<<','
               <<o.a_duty<<','<<o.b_duty<<",TEST_ONLY_SYNTHETIC\n";
        };
        const auto tick=[&] { f.step(); row(); };
        tick(); tick(); tick();
        if(!f.core.confirmNewPack(true)) throw std::runtime_error("fresh pack confirmation failed");
        row();
        const auto cycle=[&](bool cover) {
            f.in.load_button=cover; f.in.eject_button=!cover; tick();
            f.in.load_button=f.in.eject_button=false; tick(); tick();
            if(!f.core.outputs().a_arm) throw std::runtime_error("synthetic cycle did not start");
            f.in.pickup_home=false; tick(); tick();
            f.in.roller_entry=true; tick(); tick();
            f.in.capture_confirmed=true; tick();
            f.in.film_exit=true; tick(); tick();
            f.in.roller_entry=false; tick(); tick();
            f.in.film_exit=false; tick(); tick();
            f.in.pickup_home=true; tick(); tick();
            f.in.capture_confirmed=false; tick(); tick();
        };
        cycle(true); cycle(false);
        if(f.core.snapshot().frames_remaining!=9 || f.core.snapshot().state!=rb67::State::Ready)
            throw std::runtime_error("synthetic cover + photo result mismatch");
        return 0;
    } catch(const std::exception& e) { std::cerr<<"simulation failed: "<<e.what()<<'\n'; return 1; }
}
