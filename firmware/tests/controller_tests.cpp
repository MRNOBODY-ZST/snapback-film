#include "synthetic_fixture.hpp"
#include <functional>
#include <iostream>
#include <limits>
#include <vector>
using namespace rb67;
int main() {
    std::vector<std::pair<const char*,std::function<void()>>> tests{
        {"unknown calibration and TEST_ONLY hardware config fail closed", [] {
            RamFlash f; Journal j(f); Controller unknown(Config{},j); auto i=syntheticInputs();
            unknown.tick(1,i); unknown.tick(10,i); i.load_button=true; unknown.tick(12,i);
            require(unknown.snapshot().fault==Fault::Configuration && !unknown.outputs().a_arm,"unknown config must report failure and inhibit");
            require(unknown.outputs().charge_pause,"unconfigured startup must retain charger pause request");
            Controller hardware(syntheticConfig(),j,Mode::Hardware); hardware.tick(1,i); hardware.tick(10,i);
            require(hardware.snapshot().fault==Fault::Configuration && !hardware.outputs().b_arm,"test config forbidden on hardware");
        }},
        {"cover writes intent before motion and publishes ten only after exit plus home", [] {
            Fixture f; f.bootFresh(); f.in.load_button=true; f.step();
            require(f.stopped() && f.core.snapshot().state==State::EjectStart,"intent stage must stay stopped");
            const auto r=f.journal.load(); require(r.has_record && r.record.in_progress && r.record.kind==CycleKind::Cover,"durable cover intent before ARM");
            f.in.load_button=false; f.step(); f.step(); require(f.core.outputs().a_arm,"load drives A after preflight");
            f.leaveHome(); f.enter(); f.capture(); f.exitRise(); f.clearEntry(); f.clearExit();
            require(f.core.snapshot().frames_remaining==0 && f.core.snapshot().pending,"exit alone cannot mark cover done");
            f.home(); f.step(); require(f.core.snapshot().frames_remaining==10 && f.core.snapshot().cover_done && !f.core.snapshot().pending,"cover completion publishes ten");
        }},
        {"photo exit plus home decrements once and busy button edges are not queued", [] {
            Fixture f; f.cover(); f.press(false); f.in.eject_button=true; f.step(); f.leaveHome();
            f.enter(); f.capture(); f.exitRise(); f.clearEntry(); f.clearExit();
            require(f.core.snapshot().frames_remaining==10,"no early decrement"); f.home(); f.step(); f.step();
            require(f.core.snapshot().frames_remaining==9 && f.core.snapshot().state==State::Ready,"one full photo consumes one");
            for(int k=0;k<8;++k) f.step();
            require(f.stopped() && f.core.snapshot().cycle_id==2,"held button must not retrigger");
        }},
        {"startup door pack dark slide and low battery gates", [] {
            Fixture f; f.cover(); const auto cycle=f.core.snapshot().cycle_id;
            for(int gate=0;gate<4;++gate) {
                f.in=syntheticInputs(); if(gate==0) f.in.door_closed=false; if(gate==1) f.in.pack_present=false;
                if(gate==2) f.in.dark_slide_inserted=true;
                if(gate==3) f.in.battery_voltage_v=3.3;
                f.step(); f.step(); f.in.eject_button=true; f.step();
                require(f.stopped() && f.core.snapshot().cycle_id==cycle,"interlock must reject cycle");
                f.in.eject_button=false; f.step();
            }
            Fixture cover; cover.bootFresh(); cover.in.dark_slide_inserted=true; cover.step(); cover.step(); cover.press(true);
            require(cover.stopped() && !cover.core.snapshot().pending,"dark slide also prohibits black cover LOAD");
        }},
        {"charge pause acknowledgement is required before motor enable", [] {
            Fixture f; f.bootFresh(); f.in.charge_pause_ack=false; f.press(true);
            require(f.stopped() && f.core.outputs().charge_pause,"charger pause requested while stopped");
            for(int k=0;k<22;++k) f.step();
            require(f.stopped() && f.core.snapshot().fault==Fault::Timeout,"unacknowledged charging must timeout stopped");
        }},
        {"home departure entry capture exit ordering rejects impossible edges", [] {
            Fixture f; f.cover(); f.press(false); f.in.roller_entry=true; f.step(); f.step();
            require(f.stopped() && f.core.snapshot().fault==Fault::SensorSequence,"entry before home departure rejected");
            Fixture g; g.cover(); g.press(false); g.leaveHome(); g.in.film_exit=true; g.step(); g.step();
            require(g.stopped() && g.core.snapshot().fault==Fault::SensorSequence,"exit before entry rejected");
            Fixture h; h.cover(); h.press(false); h.leaveHome(); h.enter(); h.home();
            require(h.stopped() && h.core.snapshot().fault==Fault::SensorSequence,"home return before independent capture rejected");
        }},
        {"S4 alone does not authorize cam return or count", [] {
            Fixture f; f.cover(); f.press(false); f.leaveHome(); f.enter();
            require(!f.core.outputs().a_arm && f.core.outputs().b_arm,"A waits for capture proof while B transports");
            f.exitRise(); require(f.stopped() && f.core.snapshot().fault==Fault::SensorSequence,"exit without capture proof is not success");
        }},
        {"both motor current jams stop then single safe A reverse then latched JAM", [] {
            for(int motor=0;motor<2;++motor) {
                Fixture f; f.cover(); f.press(false); f.leaveHome();
                if(motor==0) f.in.motor_a_current_a=1.0; else f.in.motor_b_current_a=1.1;
                for(int k=0;k<10 && f.core.snapshot().phase!=Phase::RecoveryStop;++k) f.step();
                require(f.stopped() && f.core.snapshot().phase==Phase::RecoveryStop,"jam must first stop both");
                f.in.motor_a_current_a=f.in.motor_b_current_a=0; f.step(); f.step();
                require(f.core.outputs().a_duty<0 && !f.core.outputs().b_arm && f.core.snapshot().reverse_used,"only A reverses once");
                require(f.journal.load().record.reverse_used,"reverse intent is persistent before ARM");
                f.in.reverse_limit_reached=true; f.step();
                require(f.stopped() && f.core.snapshot().state==State::Jam,"bounded reverse ends in latched JAM");
                f.in.reverse_limit_reached=false; f.in.eject_button=true; for(int k=0;k<20;++k) f.step();
                require(f.stopped() && f.core.snapshot().state==State::Jam,"no automatic or button forward retry");
            }
        }},
        {"after entry/pod capture a jam never reverses", [] {
            Fixture f; f.cover(); f.press(false); f.leaveHome(); f.enter(); f.capture(); f.in.motor_b_current_a=1.1;
            for(int k=0;k<12;++k) f.step();
            require(f.stopped() && f.core.snapshot().state==State::Jam && !f.core.snapshot().reverse_used,"captured sheet cannot be reversed");
        }},
        {"door opens during motion stop immediately and preserve uncertain intent", [] {
            Fixture f; f.cover(); f.press(false); f.in.door_closed=false; f.step();
            require(f.stopped() && f.core.snapshot().fault==Fault::DoorOpened && f.core.snapshot().pending && !f.core.snapshot().count_known,"raw door kills before debounce");
            f.in.door_closed=true; f.step(); f.step(); require(f.stopped(),"reclosing cannot restart");
        }},
        {"sensor and ADC failures and hard current stop without reverse", [] {
            for(int failure=0;failure<3;++failure) {
                Fixture f; f.cover(); f.press(false); f.leaveHome();
                if(failure==0) f.in.sensor_valid_mask &= ~0x10u;
                if(failure==1) f.in.motor_a_current_a=std::numeric_limits<double>::quiet_NaN();
                if(failure==2) f.in.motor_b_current_a=2.1;
                f.step(); require(f.stopped() && !f.core.snapshot().reverse_used && !f.core.snapshot().count_known,"unsafe health fault cannot rollback");
            }
        }},
        {"missing home departure times out stopped", [] {
            Fixture f; f.cover(); f.press(false); for(int k=0;k<30;++k) f.step();
            require(f.stopped() && f.core.snapshot().fault==Fault::Timeout,"stuck home has a bounded deadline");
        }},
        {"scheduler gap and clock reversal cannot leave motors enabled", [] {
            Fixture f; f.cover(); f.press(false); f.step(30);
            require(f.stopped() && f.core.snapshot().fault==Fault::Scheduler,"late scheduler stop");
            Fixture g; g.cover(); g.press(false); g.core.tick(g.time-1,g.in);
            require(g.stopped() && g.core.snapshot().fault==Fault::Clock,"backward clock stop");
        }},
        {"pending NVM reboot is uncertain even with clear sensors and ignores buttons", [] {
            Fixture f; f.cover(); f.press(false);
            Journal rebootJournal(f.flash); Controller reboot(f.config,rebootJournal,Mode::HostSimulation);
            auto i=syntheticInputs(); reboot.tick(1,i); reboot.tick(5,i);
            require(reboot.snapshot().state==State::CycleUncertain && !reboot.snapshot().count_known,"pending reset must not restore Ready");
            i.eject_button=i.load_button=true; reboot.tick(7,i); reboot.enterService(); reboot.tick(9,i);
            require(!reboot.outputs().a_arm && !reboot.outputs().b_arm && reboot.snapshot().pending,"service cannot resend pending sheet");
            require(!reboot.confirmNewPack(true),"pack reset cannot hide pending sheet");
        }},
        {"intent NVM failure prevents enable and completion failure does not publish count", [] {
            Fixture f; f.cover(); f.flash.write_budget=0; f.press(false);
            require(f.stopped() && f.core.snapshot().fault==Fault::Storage,"failed intent never enables");
            Fixture g; g.cover(); g.press(false); g.leaveHome(); g.enter(); g.capture(); g.home();
            g.exitRise(); g.clearEntry(); g.flash.write_budget=7; g.clearExit(); g.step();
            require(g.stopped() && !g.core.snapshot().count_known && g.core.snapshot().frames_remaining==10,"unverified commit cannot publish nine");
        }},
        {"dark slide insertion midcycle inhibits next start without arbitrary abrupt stop", [] {
            Fixture f; f.cover(); f.press(false); f.in.dark_slide_inserted=true; f.step();
            require(f.core.outputs().a_arm,"S2 is a start interlock, midcycle policy retains bounded forward motion");
            f.completeTransport(); require(f.core.snapshot().frames_remaining==9 && f.core.snapshot().state==State::DarkSlide,"completed current sheet then dark slide interlock");
        }},
        {"readback failure after durable intent still cannot authorize motion", [] {
            Fixture f; f.cover(); f.flash.read_budget=4; f.press(false);
            require(f.stopped() && f.core.snapshot().fault==Fault::Storage && !f.core.snapshot().count_known,"failed post-intent reload must fail closed");
            f.flash.read_budget=-1; Controller reboot(f.config,f.journal,Mode::HostSimulation); reboot.tick(1,syntheticInputs());
            require(reboot.snapshot().pending && reboot.snapshot().state==State::CycleUncertain,"durable intent still blocks after reboot");
        }},
        {"stale capture signal cannot authorize next sheet", [] {
            Fixture f; f.cover(); f.in.capture_confirmed=true; f.press(false);
            require(f.stopped() && !f.core.snapshot().pending,"stuck capture proof prohibits startup");
            Fixture g; g.cover(); g.press(false); g.leaveHome(); g.in.capture_confirmed=true; g.step();
            require(g.stopped() && g.core.snapshot().fault==Fault::SensorSequence,"capture before entry is an impossible sequence");
        }},
        {"loss of charger pause acknowledgement during motion stops", [] {
            Fixture f; f.cover(); f.press(false); f.in.charge_pause_ack=false; f.step();
            require(f.stopped() && !f.core.snapshot().count_known,"motion must retain charger isolation acknowledgement");
        }},
        {"every transport waiting phase has a finite stop deadline", [] {
            for(int stage=0;stage<5;++stage) {
                Fixture f; f.cover(); f.press(false); f.leaveHome();
                if(stage>0) f.enter();
                if(stage>1) f.capture();
                if(stage==3) { f.home(); f.exitRise(); f.clearEntry(); }
                if(stage==4) { f.exitRise(); f.clearEntry(); f.clearExit(); }
                for(int k=0;k<100;++k) f.step();
                require(f.stopped() && f.core.snapshot().pending && !f.core.snapshot().count_known,"entry/capture/exit/home missing evidence must stop");
            }
        }},
        {"reverse duration and missing position observation are bounded", [] {
            for(int limit=0;limit<2;++limit) {
                Fixture f; f.cover(); f.press(false); f.leaveHome(); f.in.motor_a_current_a=1;
                for(int k=0;k<10 && f.core.snapshot().phase!=Phase::RecoveryStop;++k) f.step();
                f.in.motor_a_current_a=0; if(limit==0) f.in.reverse_position_valid=false;
                for(int k=0;k<20;++k) f.step();
                require(f.stopped() && f.core.snapshot().state==State::Jam,"position failure or duration ends latched JAM");
                require(f.core.snapshot().reverse_used==(limit==1),"reverse forbidden without position observation");
            }
        }},
        {"brownout during rollback cannot perform a second rollback", [] {
            Fixture f; f.cover(); f.press(false); f.leaveHome(); f.in.motor_a_current_a=1;
            for(int k=0;k<10 && f.core.snapshot().phase!=Phase::RecoveryStop;++k) f.step();
            f.in.motor_a_current_a=0; f.step(); f.step(); require(f.core.snapshot().reverse_used,"fixture must reverse once");
            Controller reboot(f.config,f.journal,Mode::HostSimulation); auto i=syntheticInputs(); i.pickup_home=false;
            reboot.tick(1,i); reboot.tick(3,i); i.eject_button=i.load_button=true; reboot.tick(5,i);
            require(reboot.snapshot().reverse_used && reboot.snapshot().state==State::CycleUncertain && !reboot.outputs().a_arm,"pending reverse survives and cannot restart");
        }},
        {"ten photos finish EMPTY without underflow", [] {
            Fixture f; f.cover();
            for(int n=9;n>=0;--n) { f.press(false); f.completeTransport(); require(f.core.snapshot().frames_remaining==n,"each full transport decrements exactly once"); }
            require(f.core.snapshot().state==State::Empty,"zero remaining is EMPTY");
            const auto cycle=f.core.snapshot().cycle_id; f.press(false);
            require(f.stopped() && f.core.snapshot().cycle_id==cycle,"EMPTY prohibits another EJECT");
        }},
        {"service entered during motion stops without legitimizing count", [] {
            Fixture f; f.cover(); f.press(false); f.core.enterService(); f.step();
            require(f.stopped() && f.core.snapshot().pending && !f.core.snapshot().count_known,"service cannot certify an interrupted cycle");
        }},
        {"late raw capture evidence prohibits or immediately stops reverse", [] {
            for(int late=0;late<2;++late) {
                Fixture f; f.cover(); f.press(false); f.leaveHome(); f.in.motor_a_current_a=1;
                for(int k=0;k<10 && f.core.snapshot().phase!=Phase::RecoveryStop;++k) f.step();
                f.in.motor_a_current_a=0;
                if(late==1) { f.step(); f.step(); require(f.core.outputs().a_duty<0,"fixture must already reverse"); }
                f.in.capture_confirmed=true; f.step(); f.step();
                require(f.stopped() && f.core.snapshot().state==State::Jam && f.core.snapshot().phase==Phase::Latched,"new raw capture evidence forbids any further reverse");
                require(f.core.snapshot().reverse_used==(late==1),"pre-reverse capture must never authorize rollback");
            }
        }},
        {"last ARM gate checks raw home entry and exit before debounce", [] {
            for(int signal=0;signal<3;++signal) {
                RamFlash flash; Journal journal(flash); Record ready; ready.cover_done=true; ready.frames_remaining=10;
                require(journal.append(ready),"ready journal setup"); auto c=syntheticConfig(); c.debounce_ms=10;
                Controller core(c,journal,Mode::HostSimulation); auto i=syntheticInputs();
                core.tick(1,i); core.tick(3,i); i.eject_button=true; core.tick(5,i);
                require(core.snapshot().state==State::EjectStart,"preflight intent setup");
                if(signal==0) i.pickup_home=false;
                if(signal==1) i.roller_entry=true;
                if(signal==2) i.film_exit=true;
                core.tick(7,i);
                require(!core.outputs().a_arm && !core.outputs().b_arm && core.snapshot().fault==Fault::SensorSequence,"raw unsafe position must prevent first ARM");
            }
        }},
        {"total motion deadline also covers stopped recovery and rollback", [] {
            RamFlash flash; Journal journal(flash); Record ready; ready.cover_done=true; ready.frames_remaining=10;
            require(journal.append(ready),"ready setup"); auto c=syntheticConfig();
            c.entry_max_ms=490; c.coast_ms=20; c.coast_max_ms=30;
            Controller core(c,journal,Mode::HostSimulation); auto i=syntheticInputs();
            core.tick(1,i); core.tick(3,i); i.eject_button=true; core.tick(5,i); core.tick(7,i);
            i.pickup_home=false; i.eject_button=false;
            for(std::uint64_t t=9;t<=509;t+=2) core.tick(t,i);
            require(core.snapshot().state==State::Jam && core.snapshot().phase==Phase::Latched && !core.outputs().a_arm,"total deadline must stop recovery before it can reverse");
            require(!core.snapshot().reverse_used,"expired total deadline prohibits reverse intent");
        }},
        {"exit clear exactly at its deadline cannot publish completion", [] {
            Fixture f; f.cover(); f.press(false); f.leaveHome(); f.enter(); f.capture(); f.home(); f.exitRise();
            const auto exit_at=f.time; f.clearEntry();
            while(f.time<exit_at+96) f.step();
            f.in.film_exit=false; f.step(); f.step();
            require(f.stopped() && f.core.snapshot().fault==Fault::Timeout && f.core.snapshot().frames_remaining==10,"deadline takes precedence over a same-tick completion edge");
        }},
        {"a brief capture entry exit or home pulse during coast permanently prohibits rollback", [] {
            for(int signal=0;signal<4;++signal) {
                RamFlash flash; Journal journal(flash); Record ready; ready.cover_done=true; ready.frames_remaining=10;
                require(journal.append(ready),"ready setup"); auto c=syntheticConfig(); c.coast_ms=20; c.coast_max_ms=30;
                Controller core(c,journal,Mode::HostSimulation); auto i=syntheticInputs();
                core.tick(1,i); core.tick(3,i); i.eject_button=true; core.tick(5,i); core.tick(7,i);
                i.pickup_home=false; i.motor_a_current_a=1; std::uint64_t t=9;
                for(;t<60 && core.snapshot().phase!=Phase::RecoveryStop;t+=2) core.tick(t,i);
                require(core.snapshot().phase==Phase::RecoveryStop,"coast setup"); i.motor_a_current_a=0;
                if(signal==0) i.capture_confirmed=true;
                if(signal==1) i.roller_entry=true;
                if(signal==2) i.film_exit=true;
                if(signal==3) i.pickup_home=true;
                core.tick(t,i); t+=2; i.capture_confirmed=i.roller_entry=i.film_exit=i.pickup_home=false;
                for(int k=0;k<20;++k,t+=2) core.tick(t,i);
                require(core.snapshot().phase==Phase::Latched && !core.snapshot().reverse_used && !core.outputs().a_arm,"observed unsafe pulse cannot disappear into a later reverse");
            }
        }}
    };
    unsigned failed=0;
    for(const auto& test:tests) { try { test.second(); std::cout<<"PASS "<<test.first<<'\n'; }
        catch(const std::exception& e) { ++failed; std::cout<<"FAIL "<<test.first<<": "<<e.what()<<'\n'; } }
    std::cout<<tests.size()-failed<<'/'<<tests.size()<<" controller checks passed\n";
    return failed?1:0;
}
