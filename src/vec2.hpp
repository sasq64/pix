#pragma once

#include <algorithm>
#include <cmath>
#include <string>
#include <tuple>
#include <type_traits>

template <typename T> struct V2Iterator
{
    T start;
    T current;
    T limit;

    using value_type = T;

    V2Iterator(T const& c, T const& l)
    {
        start = current = c;
        limit = l;

    }

    auto operator++()
    {
        current.x++;
        if (current.x == limit.x) {
            current.y++;
            if (current.y < limit.y) { current.x = start.x; }
        }
        return *this;
    }

    bool operator==(V2Iterator<T> const& other) const
    {
        return other.current == current;
    }

    bool operator!=(V2Iterator<T> const& other) const
    {
        return other.current != current;
    }

    T operator*() const
    {
        return current;
    }

};

template <typename T> struct Vec2Range
{
    T a;
    T b;
    Vec2Range(T a_, T b_) : a{a_}, b{b_} {}

    [[nodiscard]] V2Iterator<T> begin() const
    {
        return {a, b};

    }

    [[nodiscard]] V2Iterator<T> end() const
    {
        return {b, b};
    }

};

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

    Vec2Range<Vec2<T>> grid_coordinates() {
        return Vec2Range<Vec2<T>>(Vec2<T>(0,0), *this);
    }


    [[nodiscard]] V2Iterator<Vec2<T>> begin() const
    {
        return {{0,0}, *this};

    }

    [[nodiscard]] V2Iterator<Vec2<T>> end() const
    {
        return {*this, *this};
    }

    bool operator==(const Vec2& other) const
    {
        return other.x == x && other.y == y;
    };
    bool operator!=(const Vec2& other) const
    {
        return other.x != x || other.y != y;
    };

    [[nodiscard]] constexpr Vec2 clamp(Vec2 low, Vec2 hi) const
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


    [[nodiscard]] Vec2 ceil() const
    {
        return { std::ceil(x), std::ceil(y) };
    }
    [[nodiscard]] Vec2 round() const
    {
        return { std::round(x), std::round(y) };
    }

    // compare to low/hi bounds. Return -1 or 1 depending on if it is inside
    // or outside
    [[nodiscard]] Vec2 clip(Vec2 low, Vec2 hi) const
    {
        return {x < low.x ? x - low.x : (x >= hi.x ? x - hi.x : 0.0F),
                y < low.y ? y - low.y : (y >= hi.y ? y - hi.y : 0.0F)};
    }

    [[nodiscard]] Vec2 cossin() const { return {cos(x), sin(y)}; }

    [[nodiscard]] Vec2 sign() const
    {
        return {x < 0 ? T(-1) : (x > 0 ? T(1) : T(0)),
                y < 0 ? T(-1) : (y > 0 ? T(1) : T(0))};
    }
    [[nodiscard]] T mag() const { return std::sqrt(x * x + y * y); }
    [[nodiscard]] T mag2() const { return (x * x + y * y); }

    [[nodiscard]] Vec2 norm() const
    {
        auto m = mag();
        return {x / m, y / m};
    }

    [[nodiscard]] Vec2 floor() const
    {
        return Vec2{std::floor(x), std::floor(y)};
    }

    [[nodiscard]] float angle() const { return norm().angle_n(); }

    [[nodiscard]] float angle_n() const
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
    [[nodiscard]] constexpr Vec2 add(Vec2 v) const { return {v.x + x, v.y + y}; }
    [[nodiscard]] constexpr Vec2 operator+(Vec2 v) const { return add(v); }

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

    static inline bool instersects(Vec2 v11, Vec2 v12, Vec2 v21, Vec2 v22)
    {
        double d1, d2;
        double a1, a2, b1, b2, c1, c2;

        // Convert vector 1 to a line (line 1) of infinite length.
        // We want the line in linear equation standard form: A*x + B*y + C = 0
        // See: http://en.wikipedia.org/wiki/Linear_equation
        a1 = v12.y - v11.y;
        b1 = v11.x - v12.x;
        c1 = (v12.x * v11.y) - (v11.x * v12.y);

        // Every point (x,y), that solves the equation above, is on the line,
        // every point that does not solve it, is not. The equation will have a
        // positive result if it is on one side of the line and a negative one
        // if is on the other side of it. We insert (x1,y1) and (x2,y2) of vector
        // 2 into the equation above.
        d1 = (a1 * v21.x) + (b1 * v21.y) + c1;
        d2 = (a1 * v22.x) + (b1 * v22.y) + c1;

        // If d1 and d2 both have the same sign, they are both on the same side
        // of our line 1 and in that case no intersection is possible. Careful,
        // 0 is a special case, that's why we don't test ">=" and "<=",
        // but "<" and ">".
        if (d1 > 0 && d2 > 0) return false;
        if (d1 < 0 && d2 < 0) return false;

        // The fact that vector 2 intersected the infinite line 1 above doesn't
        // mean it also intersects the vector 1. Vector 1 is only a subset of that
        // infinite line 1, so it may have intersected that line before the vector
        // started or after it ended. To know for sure, we have to repeat the
        // the same test the other way round. We start by calculating the
        // infinite line 2 in linear equation standard form.
        a2 = v22.y - v21.y;
        b2 = v21.x - v22.x;
        c2 = (v22.x * v21.y) - (v21.x * v22.y);

        // Calculate d1 and d2 again, this time using points of vector 1.
        d1 = (a2 * v11.x) + (b2 * v11.y) + c2;
        d2 = (a2 * v12.x) + (b2 * v12.y) + c2;

        // Again, if both have the same sign (and neither one is 0),
        // no intersection is possible.
        if (d1 > 0 && d2 > 0) return false;
        if (d1 < 0 && d2 < 0) return false;

        // If we get here, only two possibilities are left. Either the two
        // vectors intersect in exactly one point or they are collinear, which
        // means they intersect in any number of points from zero to infinite.
        //if ((a1 * b2) - (a2 * b1) == 0.0f) return COLLINEAR;

        // If they are not collinear, they must intersect in exactly one point.
        return true;
    }

    inline bool inside_polygon(std::vector<Vec2> const& points) {
        Vec2 s = *this + Vec2{10000, 0};
        int count = 0;
        for(size_t i=0; i<points.size()-1; i++) {

            auto&& a = points[i];
            auto&& b = points[i+1];
            if (instersects(*this, s, a, b)) {
                count++;
            }
        }
        auto&& a = points[points.size()-1];
        auto&& b = points[0];
        if (instersects(*this, s, a, b)) {
            count++;
        }
        return (count & 1) == 1;
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
