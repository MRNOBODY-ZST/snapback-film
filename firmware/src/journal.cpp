#include "journal.hpp"
#include <algorithm>
#include <limits>
namespace rb67 {
namespace {
constexpr std::uint32_t magic=0x52304a31u, marker=0xa55aa55au;
using Bytes=std::array<std::uint8_t,Journal::slot_size>;
void put(Bytes& b,std::size_t o,std::uint32_t v) { for(unsigned i=0;i<4;++i) b[o+i]=static_cast<std::uint8_t>(v>>(8*i)); }
std::uint32_t get(const Bytes& b,std::size_t o) { std::uint32_t v=0; for(unsigned i=0;i<4;++i) v|=std::uint32_t(b[o+i])<<(8*i); return v; }
bool sensible(const Record& r) {
    return r.frames_remaining<=10 && static_cast<unsigned>(r.kind)<=2 &&
        (!r.in_progress || r.kind!=CycleKind::None) && (!r.reverse_used || r.in_progress);
}
bool decode(const Bytes& b,Record& r) {
    if(get(b,0)!=magic || b[4]!=1 || (b[6]&0xf8u)!=0 || get(b,20)!=0 || get(b,28)!=0 ||
       get(b,32)!=marker || get(b,36)!=~marker || get(b,24)!=Journal::crc32(b.data(),24)) return false;
    r.kind=static_cast<CycleKind>(b[5]); r.frames_remaining=b[7];
    r.in_progress=(b[6]&1u)!=0; r.cover_done=(b[6]&2u)!=0; r.reverse_used=(b[6]&4u)!=0;
    r.sequence=get(b,8); r.pack_session=get(b,12); r.cycle_id=get(b,16);
    return r.sequence!=0 && sensible(r);
}
Bytes encode(const Record& r) {
    Bytes b{}; put(b,0,magic); b[4]=1; b[5]=static_cast<std::uint8_t>(r.kind);
    b[6]=static_cast<std::uint8_t>((r.in_progress?1:0)|(r.cover_done?2:0)|(r.reverse_used?4:0));
    b[7]=r.frames_remaining; put(b,8,r.sequence); put(b,12,r.pack_session); put(b,16,r.cycle_id);
    put(b,24,Journal::crc32(b.data(),24)); put(b,32,marker); put(b,36,~marker); return b;
}
}
std::uint32_t Journal::crc32(const std::uint8_t* bytes,std::size_t n) {
    std::uint32_t crc=0xffffffffu;
    for(std::size_t i=0;i<n;++i) { crc^=bytes[i]; for(unsigned j=0;j<8;++j) crc=(crc>>1)^((crc&1u)?0xedb88320u:0u); }
    return crc^0xffffffffu;
}
JournalLoad Journal::load() {
    JournalLoad result; bool bad=false;
    for(std::size_t slot=0;slot<2;++slot) {
        Bytes bytes{};
        if(!storage_.read(slot,0,bytes.data(),bytes.size())) { result.status=JournalStatus::IoError; return result; }
        if(std::all_of(bytes.begin(),bytes.end(),[](std::uint8_t v){return v==0xff;})) continue;
        Record r;
        if(!decode(bytes,r)) { bad=true; continue; }
        if(result.has_record && r.sequence==result.record.sequence) bad=true;
        if(!result.has_record || r.sequence>result.record.sequence) { result.record=r; result.has_record=true; }
    }
    result.status=bad?JournalStatus::Corrupt:(result.has_record?JournalStatus::Valid:JournalStatus::Empty);
    return result;
}
bool Journal::append(const Record& desired) {
    if(!sensible(desired)) return false;
    const auto old=load();
    if(old.status==JournalStatus::Corrupt || old.status==JournalStatus::IoError ||
       (old.has_record && old.record.sequence==std::numeric_limits<std::uint32_t>::max())) return false;
    Record next=desired; next.sequence=old.has_record?old.record.sequence+1:1;
    const std::size_t target=(next.sequence-1)%2;
    const auto bytes=encode(next); Bytes check{};
    if(!storage_.erase(target) || !storage_.write(target,0,bytes.data(),32) ||
       !storage_.read(target,0,check.data(),32) || !std::equal(bytes.begin(),bytes.begin()+32,check.begin())) return false;
    // A separate final marker write publishes the record only after payload verification.
    if(!storage_.write(target,32,bytes.data()+32,8) || !storage_.read(target,0,check.data(),check.size())) return false;
    Record decoded;
    return check==bytes && decode(check,decoded);
}
} // namespace rb67
