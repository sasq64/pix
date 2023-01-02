#pragma once

#include <algorithm>
#include <cmath>
#include <string>
#include <tuple>
#include <type_traits>

template <typename T> struct Vec2
{
    T x = 0;
    T y = 0;

    constexpr Vec2() = default;

    constexpr Vec2(std::pair<T, T> const& p)
        : x{p.first}, y{p.second} {} // NOLINT
    constexpr Vec2(T _x, T _y) : x{_x}, y{_y} {}

    constexpr T& operator[](size_t i) { return i == 0 ? x : y; }
    constexpr T const& operator[](size_t i) const { return i == 0 ? x : y; }

    bool operator==(const Vec2& other) const
    {
        return other.x == x && other.y == y;
    };
    bool operator!=(const Vec2& other) const
    {
        return other.x != x || other.y != y;
    };

    constexpr Vec2 clamp(Vec2 low, Vec2 hi) const
    {
        return {std::clamp(x, low.x, hi.x), std::clamp(y, low.y, hi.y)};
    }

    constexpr explicit operator std::pair<T, T>() { return {x, y}; }

    // template<class S = T, typename
    // std::enable_if<std::is_floating_point<S>::value>::type>
    explicit operator Vec2<int32_t>()
    {
        return {static_cast<int32_t>(x), static_cast<int32_t>(y)};
    }

    operator Vec2<double>() // NOLINT
    {
        return {static_cast<double>(x), static_cast<double>(y)};
    }

    // compare to low/hi bounds. Return -1 or 1 depending on if it is inside
    // or outside
    Vec2 clip(Vec2 low, Vec2 hi) const
    {
        return {x < low.x ? x - low.x : (x >= hi.x ? x - hi.x : 0.0F),
                y < low.y ? y - low.y : (y >= hi.y ? y - hi.y : 0.0F)};
    }

    Vec2 cossin() const { return {cos(x), sin(y)}; }

    Vec2 sign()
    {
        return {x < 0 ? T(-1) : (x > 0 ? T(1) : T(0)),
                y < 0 ? T(-1) : (y > 0 ? T(1) : T(0))};
    }
    T mag() const { return std::sqrt(x * x + y * y); }
    T mag2() const { return (x * x + y * y); }

    Vec2 norm() const
    {
        auto m = mag();
        return {x / m, y / m};
    }

    Vec2 floor() const
    {
        return Vec2{std::floor(x), std::floor(y)};
    }

    float angle() const { return norm().angle_n(); }

    float angle_n() const
    {
        if (x == 0)
            return (y > 0) ? M_PI / 2 : (y == 0) ? 0 : M_PI * 3 / 2;
        else if (y == 0)
            return (x >= 0) ? 0 : M_PI;
        auto ret = atanf(y / x);
        if (x < 0 && y < 0)
            ret = M_PI + ret;
        else if (x < 0)
            ret = M_PI + ret;
        else if (y < 0)
            ret = 2 * M_PI + ret;

        return ret;
    }

    // add
    constexpr Vec2 add(Vec2 v) const { return {v.x + x, v.y + y}; }
    constexpr Vec2 operator+(Vec2 v) const { return add(v); }

    constexpr Vec2& iadd(Vec2 v)
    {
        x += v.x;
        y += v.y;
        return *this;
    }
    constexpr Vec2 operator+=(Vec2 v) { return iadd(v); }

    constexpr Vec2 adds(T v) const { return {v + x, v + y}; }
    constexpr Vec2 operator+(T v) const { return adds(v); }

    constexpr Vec2& iadds(T v)
    {
        x += v;
        y += v;
        return *this;
    }
    constexpr Vec2 operator+=(T v) { return iadds(v); }

    // sub
    constexpr Vec2 sub(Vec2 v) const { return {x - v.x, y - v.y}; }
    constexpr Vec2 operator-(Vec2 v) const { return sub(v); }

    constexpr Vec2& isub(Vec2 v)
    {
        x -= v.x;
        y -= v.y;
        return *this;
    }
    constexpr Vec2 operator-=(Vec2 v) const { return isub(v); }

    constexpr Vec2 subs(T s) const { return {x - s, y - s}; }
    constexpr Vec2 operator-(T v) const { return subs(v); }

    constexpr Vec2& isubs(T v)
    {
        x -= v;
        y -= v;
        return *this;
    }
    constexpr Vec2 operator-=(T v) { return isubs(v); }

    // mul

    constexpr Vec2 mul(Vec2 v) const { return {v.x * x, v.y * y}; }
    constexpr Vec2 operator*(Vec2 v) const { return mul(v); }

    constexpr Vec2& imul(Vec2 v)
    {
        x *= v.x;
        y *= v.y;
        return *this;
    }
    constexpr Vec2 operator*=(Vec2 v) const { return imul(v); }

    // scalar mul
    constexpr Vec2 muls(T s) const { return {s * x, s * y}; }
    constexpr Vec2 operator*(T v) const { return muls(v); }

    template <typename S> constexpr Vec2& imuls(S s)
    {
        x *= s;
        y *= s;
        return *this;
    }
    template <typename S> constexpr Vec2 operator*=(S v) const
    {
        return imul(v);
    }

    // div
    constexpr Vec2 div(Vec2 v) const { return {x / v.x, y / v.y}; }
    constexpr Vec2 operator/(Vec2 v) const { return div(v); }

    constexpr Vec2& idiv(Vec2 v)
    {
        x /= v.x;
        y /= v.y;
        return *this;
    }
    constexpr Vec2 operator/=(Vec2 v) const { return idiv(v); }

    constexpr Vec2 divs(T v) const { return {x / v, y / v}; }
    constexpr Vec2 operator/(T v) const { return divs(v); }

    constexpr Vec2 fdiv(Vec2 v) const
    {
        if constexpr (std::is_integral<T>::value) {
            return {x / v.x, y / v.y};
        } else {
            return {floorf(x / v.x), floorf(y / v.y)};
        }
    }

    constexpr Vec2 fdivs(T v) const
    {
        if constexpr (std::is_integral<T>::value) {
            return {x / v, y / v};
        } else {
            return {floorf(x / v), floorf(y / v)};
        }
    }

    constexpr std::size_t len() { return 2; }

    constexpr static inline Vec2 from_angle(double a)
    {
        return {cos(a), sin(a)};
    }

    std::string repr()
    {
        if constexpr (std::is_integral<T>::value) {
            return "Vec2i(" + std::to_string(x) + ", " + std::to_string(y) +
                   ")";
        } else {
            return "Vec2(" + std::to_string(x) + ", " + std::to_string(y) + ")";
        }
    }
};

using Vec2f = Vec2<double>;
using Vec2i = Vec2<int32_t>;
