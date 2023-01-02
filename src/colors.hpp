#pragma once
#ifndef COLORS_HPP
#define COLORS_HPP

#include <cstdint>

namespace color {

static inline constexpr uint32_t tob(double f)
{
    return static_cast<int>(f * 255);
}

inline constexpr uint32_t rgba(double r, double g, double b, double a)
{
    return (tob(r) << 24) | (tob(g) << 16) | (tob(b) << 8) | tob(a);
}

const uint32_t black = rgba(0.0, 0.0, 0.0, 1.0);
const uint32_t white = rgba(1.0, 1.0, 1.0, 1.0);
const uint32_t red = rgba(0.533, 0.0, 0.0, 1.0);
const uint32_t cyan = rgba(0.667, 1.0, 0.933, 1.0);
const uint32_t purple = rgba(0.8, 0.267, 0.8, 1.0);
const uint32_t green = rgba(0.0, 0.8, 0.333, 1.0);
const uint32_t blue = rgba(0.0, 0.0, 0.667, 1.0);
const uint32_t yellow = rgba(0.933, 0.933, 0.467, 1.0);
const uint32_t orange = rgba(0.867, 0.533, 0.333, 1.0);
const uint32_t brown = rgba(0.4, 0.267, 0.0, 1.0);
const uint32_t light_red = rgba(1.0, 0.467, 0.467, 1.0);
const uint32_t dark_grey = rgba(0.2, 0.2, 0.2, 1.0);
const uint32_t grey = rgba(0.467, 0.467, 0.467, 1.0);
const uint32_t light_green = rgba(0.667, 1.0, 0.4, 1.0);
const uint32_t light_blue = rgba(0.0, 0.533, 1.0, 1.0);
const uint32_t light_grey = rgba(0.733, 0.733, 0.733, 1.0);
const uint32_t transp = rgba(0.0, 0.0, 0.0, 0.0);
} // namespace color
#endif