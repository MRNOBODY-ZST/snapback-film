#include "test_storage.hpp"
#include <functional>
#include <iostream>
#include <utility>
#include <vector>
using namespace rb67;
int main() {
    std::vector<std::pair<const char*,std::function<void()>>> tests{
        {"intent survives a reconstructed journal", [] {
            RamFlash flash; Journal journal(flash); Record r;
            r.pack_session=3; r.cycle_id=7; r.kind=CycleKind::Photo;
            r.frames_remaining=10; r.cover_done=true; r.in_progress=true;
            require(journal.append(r), "intent must be durably written");
            Journal reboot(flash); const auto got=reboot.load();
            require(got.status==JournalStatus::Valid && got.has_record, "valid intent required after reboot");
            require(got.record.in_progress && got.record.frames_remaining==10 && got.record.cycle_id==7, "intent payload must survive");
        }},
        {"CRC32 standard independent check vector", [] {
            const std::uint8_t text[]={'1','2','3','4','5','6','7','8','9'};
            require(Journal::crc32(text,9)==0xcbf43926u,"CRC32 IEEE check vector mismatch");
        }},
        {"every torn completion preserves pending evidence", [] {
            for (int cut=0;cut<static_cast<int>(Journal::slot_size);++cut) {
                RamFlash flash; Journal journal(flash); Record pending;
                pending.kind=CycleKind::Photo; pending.in_progress=true; pending.cover_done=true;
                pending.frames_remaining=10; pending.cycle_id=1;
                require(journal.append(pending),"setup intent must write");
                Record complete=pending; complete.in_progress=false; complete.frames_remaining=9;
                flash.write_budget=cut;
                require(!journal.append(complete),"torn append must fail verification");
                flash.write_budget=-1; Journal reboot(flash); auto got=reboot.load();
                require(got.has_record && got.record.in_progress && got.record.frames_remaining==10,"a torn commit must never publish count 9");
            }
        }},
        {"CRC corruption cannot silently revive an older ready record", [] {
            RamFlash flash; Journal journal(flash); Record ready;
            ready.cover_done=true; ready.frames_remaining=10;
            require(journal.append(ready),"setup ready");
            Record pending=ready; pending.kind=CycleKind::Photo; pending.in_progress=true; pending.cycle_id=1;
            require(journal.append(pending),"setup pending");
            flash.slots[1][7] ^= 1;
            const auto got=journal.load();
            require(got.status==JournalStatus::Corrupt,"invalid newer slot must not silently fall back to ready");
        }},
        {"alternating commits increment sequence and keep final result", [] {
            RamFlash flash; Journal journal(flash); Record r; r.cover_done=true; r.frames_remaining=10;
            for (unsigned i=0;i<20;++i) require(journal.append(r),"append should alternate slots");
            const auto got=journal.load();
            require(got.status==JournalStatus::Valid && got.record.sequence==20 && got.record.frames_remaining==10,"latest sequence must win");
        }},
        {"storage failure never looks like blank NVM", [] {
            RamFlash flash; flash.read_failure=true; Journal journal(flash);
            require(journal.load().status==JournalStatus::IoError,"read failure is not a fresh pack");
            require(!journal.append(Record{}),"cannot append on unreadable storage");
        }},
        {"invalid count and kind are refused before write", [] {
            RamFlash flash; Journal journal(flash); Record r; r.frames_remaining=11;
            require(!journal.append(r),"count >10 must be refused");
            r.frames_remaining=10; r.in_progress=true; r.kind=CycleKind::None;
            require(!journal.append(r),"pending must identify cover/photo kind");
            require(flash.writes==0,"invalid records must not touch flash");
        }},
        {"publication marker occupies a separate eight-byte flash program unit", [] {
            class GranularFlash final : public Storage {
            public:
                RamFlash raw;
                bool read(std::size_t s,std::size_t o,std::uint8_t* b,std::size_t n) override { return raw.read(s,o,b,n); }
                bool erase(std::size_t s) override { return raw.erase(s); }
                bool write(std::size_t s,std::size_t o,const std::uint8_t* b,std::size_t n) override {
                    return o%8==0 && n%8==0 && raw.write(s,o,b,n);
                }
            } flash;
            Journal journal(flash); Record r; r.kind=CycleKind::Cover; r.in_progress=true;
            require(journal.append(r),"payload and last marker must each align to 8-byte program granules");
        }}
    };
    unsigned failed=0;
    for (const auto& test:tests) { try { test.second(); std::cout<<"PASS "<<test.first<<'\n'; }
        catch (const std::exception& e) { ++failed; std::cout<<"FAIL "<<test.first<<": "<<e.what()<<'\n'; } }
    std::cout<<tests.size()-failed<<'/'<<tests.size()<<" journal checks passed\n";
    return failed?1:0;
}
