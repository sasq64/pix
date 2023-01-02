#pragma once
#include "system.hpp"
#include "context.hpp"

struct Machine
{
    std::shared_ptr<System> sys{};
    std::shared_ptr<Screen> screen{};
    std::shared_ptr<pix::Context> context{};
    uint32_t frame_counter = 0;
    static Machine& get_instance();
};
