#pragma once
#include "system.hpp"
#include "context.hpp"
#include "screen.hpp"

#include <functional>
#include <memory>
#include <vector>

struct Machine
{
    std::shared_ptr<System> sys{};
    //std::shared_ptr<Display> display{};
    //uint32_t frame_counter = 0;
    static Machine& get_instance();
};
