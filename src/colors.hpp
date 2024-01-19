#pragma once
#ifndef COLORS_HPP
#define COLORS_HPP

#include <cstdint>
#include <tuple>
#include <vector>

namespace color {

static inline constexpr uint32_t tob(double f)
{
    return static_cast<int>(f * 255);
}

inline constexpr uint32_t rgba(double r, double g, double b, double a)
{
    return (tob(r) << 24) | (tob(g) << 16) | (tob(b) << 8) | tob(a);
}

inline constexpr std::tuple<float, float, float, float> color2tuple(uint32_t color)
{
    auto r = (color >> 24) / 255.0;
    auto g = ((color >> 16) & 0xff) / 255.0;
    auto b = ((color >> 8) & 0xff) / 255.0;
    auto a = (color & 0xff) / 255.0;

    return std::make_tuple(r,g,b,a);
}


inline constexpr uint32_t blend_color(uint32_t a, uint32_t b, float d)
{
    auto [ra, ga, ba, aa] = color2tuple(a);
    auto [rb, gb, bb, ab] = color2tuple(b);
    return rgba(ra * d + rb * (1-d), ga * d + gb * (1-d),
                ba * d + bb * (1-d), aa * d + ab * (1-d));
}

inline constexpr uint32_t blend_colors(std::vector<uint32_t> const& colors, float d)
{
    auto o = colors.size() * d;
    auto i = (size_t)o;
    auto j = i+1;
    if (j >= colors.size()) { j = colors.size()-1; }
    d = o - i;

    //printf("%zu - %zu %f\n", i, j, d);
    auto [ra, ga, ba, aa] = color2tuple(colors[j]);
    auto [rb, gb, bb, ab] = color2tuple(colors[i]);
    return rgba(ra * d + rb * (1-d), ga * d + gb * (1-d),
                ba * d + bb * (1-d), aa * d + ab * (1-d));
}

inline constexpr uint32_t add_color(uint32_t a, uint32_t b)
{
    auto [ra, ga, ba, aa] = color2tuple(a);
    auto [rb, gb, bb, ab] = color2tuple(b);
    ra += rb;
    if (ra > 1.0) { ra = 1.0; }
    ga += gb;
    if (ga > 1.0) { ga = 1.0; }
    ba += bb;
    if (ba > 1.0) { ba = 1.0; }
    aa += ab;
    if (aa > 1.0) { aa = 1.0; }
    return rgba(ra, ga, ba, aa);
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
