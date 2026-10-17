#pragma once
#include <array>
#include <cstddef>
#include <cstdint>

namespace rb67 {
enum class CycleKind : std::uint8_t { None = 0, Cover = 1, Photo = 2 };
struct Record {
    std::uint32_t sequence = 0;
    std::uint32_t pack_session = 0;
    std::uint32_t cycle_id = 0;
    std::uint8_t frames_remaining = 0;
    CycleKind kind = CycleKind::None;
    bool in_progress = false;
    bool cover_done = false;
    bool reverse_used = false;
};
class Storage {
public:
    virtual ~Storage() = default;
    // Two distinct erase units; never erase both to append one record.
    virtual bool read(std::size_t slot, std::size_t offset, std::uint8_t* dst, std::size_t n) = 0;
    virtual bool erase(std::size_t slot) = 0;
    virtual bool write(std::size_t slot, std::size_t offset, const std::uint8_t* src, std::size_t n) = 0;
};
enum class JournalStatus { Empty, Valid, Corrupt, IoError };
struct JournalLoad { JournalStatus status = JournalStatus::Empty; Record record{}; bool has_record = false; };
class Journal {
public:
    static constexpr std::size_t slot_size = 40; // 32-byte body + independent 8-byte publication unit.
    explicit Journal(Storage& storage) : storage_(storage) {}
    JournalLoad load();
    bool append(const Record& desired);
    static std::uint32_t crc32(const std::uint8_t* bytes, std::size_t n);
private:
    Storage& storage_;
};
} // namespace rb67
