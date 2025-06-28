#pragma once
#include "system.hpp"
#include "context.hpp"
#include "screen.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <functional>
#include <memory>
#include <vector>

struct Machine
{
    int in_pix = 0;
    std::shared_ptr<System> sys{};
    std::vector<pybind11::object> events;
    int counter = 0;
    using Listener = std::function<bool(pybind11::object)>;
    std::unordered_map<int, Listener> listeners;
    //std::shared_ptr<Display> display{};
    //uint32_t frame_counter = 0;
    static Machine& get_instance();
};
