#pragma once
#include "journal.hpp"
#include <algorithm>
#include <array>
#include <cstring>
#include <stdexcept>
#include <string>

inline void require(bool condition, const std::string& why) {
    if (!condition) throw std::runtime_error(why);
}
// Test utility only. Models real erased flash (0xff) and 1->0 writes;
// partial writes survive Controller/Journal object reconstruction.
class RamFlash final : public rb67::Storage {
public:
    std::array<std::array<std::uint8_t, rb67::Journal::slot_size>, 2> slots{};
    int write_budget = -1; // Byte budget; zero fails before the next byte.
    int read_budget = -1; // Call budget for fault injection.
    bool read_failure = false;
    bool erase_failure = false;
    unsigned writes = 0;
    unsigned erases = 0;
    RamFlash() { for (auto& slot : slots) slot.fill(0xff); }
    bool read(std::size_t s, std::size_t off, std::uint8_t* dst, std::size_t n) override {
        if (read_failure || read_budget==0 || s >= 2 || off+n > slots[s].size()) return false;
        if (read_budget>0) --read_budget;
        std::memcpy(dst, slots[s].data()+off, n); return true;
    }
    bool erase(std::size_t s) override {
        if (erase_failure || s >= 2) return false;
        ++erases; slots[s].fill(0xff); return true;
    }
    bool write(std::size_t s, std::size_t off, const std::uint8_t* src, std::size_t n) override {
        if (s >= 2 || off+n > slots[s].size()) return false;
        ++writes;
        for (std::size_t i=0;i<n;++i) {
            if (write_budget==0) return false;
            if (write_budget>0) --write_budget;
            if ((slots[s][off+i] & src[i]) != src[i]) return false;
            slots[s][off+i] &= src[i];
        }
        return true;
    }
};
