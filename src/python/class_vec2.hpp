#pragma once

#include "../vec2.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <tuple>

namespace py = pybind11;

static inline Vec2f vec2_one{1, 1};
static inline Vec2f vec2_zero{0, 0};

static inline Vec2i vec2i_one{1, 1};
static inline Vec2i vec2i_zero{0, 0};

template <typename Vec2>
py::class_<Vec2> add_common(py::module_& mod, const char* name)
{
    auto vd =
        py::class_<Vec2>(mod, name)
            .def(py::init<int, int>(), py::arg("x") = 0, py::arg("y") = 0)
            .def(py::init<int, double>(), py::arg("x") = 0, py::arg("y") = 0)
            .def(py::init<double, int>(), py::arg("x") = 0, py::arg("y") = 0)
            .def(py::init<double, double>(), py::arg("x") = 0, py::arg("y") = 0)
            .def("__len__", &Vec2::len)
            .def("clamp", &Vec2::clamp, py::arg("low"), py::arg("high"),
                 "Separately clamp the x and y component between the "
                 "corresponding components in the given arguments.")
            .def("sign", &Vec2::sign)
            .def_readonly("x", &Vec2::x)
            .def_readonly("y", &Vec2::y)
            .def_property_readonly("yx",
                                   [](Vec2 self) {
                                       return Vec2{self.y, self.x};
                                   })
            .def_property_readonly("with_y0",
                                   [](Vec2 self) {
                                       return Vec2{self.x, 0};
                                   })
            .def_property_readonly("with_x0",
                                   [](Vec2 self) {
                                       return Vec2{0, self.y};
                                   })
            .def("__eq__",
                 [](const Vec2& a, Vec2 const& b) { return a == b; })
            .def("__ne__",
                 [](const Vec2& a, Vec2 const& b) { return a != b; })
            .def("__lt__",
                 [](const Vec2& a, Vec2 const& b) {
                     return a.x < b.x && a.y < b.y;
                 })
            .def("__le__",
                 [](const Vec2& a, Vec2 const& b) {
                     return a.x <= b.x && a.y <= b.y;
                 })
            .def("__gt__",
                 [](const Vec2& a, Vec2 const& b) {
                     return a.x > b.x && a.y > b.y;
                 })
            .def("__ge__",
                 [](const Vec2 a, Vec2 const& b) {
                     return a.x >= b.x && a.y >= b.y;
                 })
            .def("__getitem__",
                 [](Vec2 const& v, size_t i) {
                     if (i > 1) { throw pybind11::index_error(); }
                     return v[i];
                 })
            .def(
                "__iter__",
                [](Vec2 const& v) {
                    return py::make_iterator(&v.x, &v.y + 1);
                },
                py::keep_alive<0, 1>());

    return vd;
}

inline void add_vec2_class(py::module_& mod)
{
    auto vi = add_common<Vec2i>(mod, "Int2");
    auto vd = add_common<Vec2f>(mod, "Float2");

    vd.def(py::init<std::pair<double, double>>())
        .def(
            "toi",
            [](Vec2f self) {
                return Vec2i{static_cast<int>(self.x),
                             static_cast<int>(self.y)};
            },
            "Convert a `Float2` to an `Int2`")
        .def("random",
             [](Vec2f self) {
                 double rm = RAND_MAX;
                 return Vec2f{rand() / rm * self.x, rand() / rm * self.y};
             }, "Returns Float2(rnd(x), rnd(y)) where rnd(n) returns a random number between 0 and n.")
        .def("__repr__",
             [](Vec2f self) {
                 return "Float2(" + std::to_string(self.x) + ", " +
                        std::to_string(self.y) + ")";
             })
        .def("__truediv__", &Vec2f::div)
        .def("__truediv__",
             [](Vec2f self, Vec2i other) { return self / Vec2f{other}; })
        .def("__truediv__", &Vec2f::divs)
        .def("__floordiv__", &Vec2f::fdiv)
        .def("__floordiv__",
             [](Vec2f self, Vec2i other) {
                 return (self / Vec2f{other}).floor();
             })
        .def("__floordiv__", &Vec2f::fdivs)
        .def("__mul__", &Vec2f::mul)
        .def("__mul__",
             [](Vec2f self, Vec2i other) { return self * Vec2f{other}; })
        .def("__mul__", &Vec2f::muls)
        .def("__add__", &Vec2f::add)
        .def("__add__",
             [](Vec2f self, Vec2i other) { return self + Vec2f{other}; })
        .def("__add__", &Vec2f::adds)
        .def("__sub__", &Vec2f::sub)
        .def("__sub__",
             [](Vec2f self, Vec2i other) { return self - Vec2f{other}; })
        .def("__sub__", &Vec2f::subs)
        .def_static("from_angle", &Vec2f::from_angle, "From angle")
        .def("clip", &Vec2f::clip, py::arg("low"), py::arg("high"),
             "Compare the point against the bounding box defined by low/high. Returns (0,0) if point is inside the box, or a negative or positive distance to the edge if outside.")
        .def("floor", &Vec2f::floor)
        .def("ceil", &Vec2f::ceil)
        .def("round", &Vec2f::round)
        .def("mag", &Vec2f::mag, "Get magnitude (length) of vector")
        .def("mag2", &Vec2f::mag2, "Get the squared magnitude")
        .def("norm", &Vec2f::norm, "Get the normalized vector.")
        .def("angle", &Vec2f::angle, "Get the angle between the vector and (1,0).")
        .def("cossin", &Vec2f::cossin, "Returns (cos(x), sin(y)).")
        .def_readonly_static("ONE", &vec2_one, "Constant (1,1)")
        .def_readonly_static("ZERO", &vec2_zero, "Constant (0,0)")
        .def("inside_polygon", &Vec2f::inside_polygon, py::arg("points"),
             "Check if the `point` is inside the polygon formed by `points`.");
    vd.doc() = "Represents an floating pont coordinate or size";

    vi.def(py::init<std::pair<int, int>>())
        .def(
            "tof",
            [](Vec2i self) {
              return Vec2f{static_cast<double>(self.x),
                           static_cast<double>(self.y)};
            },
            "Convert an `Int2` to a `Float2`")
        .def("random",
             [](Vec2i self) {
                 return Vec2i{rand() % self.x, rand() % self.y};
             }, "Returns Int2(rnd(x), rnd(y)) where rnd(n) returns a random number between 0 and n.")
        .def("__repr__",
             [](Vec2i self) {
                 return "Int2(" + std::to_string(self.x) + ", " +
                        std::to_string(self.y) + ")";
             })
        .def("__truediv__", &Vec2i::div)
        .def("__truediv__",
             [](Vec2i self, Vec2f other) { return Vec2f{self} / other; })
        .def("__truediv__", &Vec2i::divs)
        .def("__truediv__",
             [](Vec2i self, double other) { return Vec2f{self} / other; })
        .def("__floordiv__", &Vec2i::fdiv)
        .def("__floordiv__",
             [](Vec2i self, Vec2f other) {
                 return (Vec2f{self} / other).floor();
             })
        .def("__floordiv__", &Vec2i::fdivs)
        .def("__floordiv__",
             [](Vec2i self, double other) {
                 return (Vec2f{self} / other).floor();
             })
        .def("__mul__", &Vec2i::mul)
        .def("__mul__",
             [](Vec2i self, Vec2f other) { return Vec2f{self} * other; })
        .def("__mul__", &Vec2i::muls)
        .def("__mul__",
             [](Vec2i self, double other) { return Vec2f{self} * other; })
        .def("__add__", &Vec2i::add)
        .def("__add__",
             [](Vec2i self, Vec2f other) { return Vec2f{self} + other; })
        .def("__add__", &Vec2i::adds)
        .def("__add__",
             [](Vec2i self, double other) { return Vec2f{self} + other; })
        .def("__sub__", &Vec2i::sub)
        .def("__sub__",
             [](Vec2i self, Vec2f other) { return Vec2f{self} - other; })
        .def("__sub__", &Vec2i::subs)
        .def("__sub__",
             [](Vec2i self, double other) { return Vec2f{self} - other; })
        .def_readonly_static("ONE", &vec2i_one, "Constant (1,1)")
        .def_readonly_static("ZERO", &vec2i_zero, "Constant (0,0)");
    vi.doc() = "Represents an integer coordinate or size";
}
