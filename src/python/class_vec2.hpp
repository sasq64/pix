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

inline void add_vec2_class(py::module_& mod)
{
    auto vi =
        py::class_<Vec2i>(mod, "Int2")
            .def(py::init<int, int>(), py::arg("x") = 0, py::arg("y") = 0)
            .def(py::init<int, double>(), py::arg("x") = 0, py::arg("y") = 0)
            .def(py::init<double, int>(), py::arg("x") = 0, py::arg("y") = 0)
            .def(py::init<double, double>(), py::arg("x") = 0, py::arg("y") = 0)
            .def(py::init<std::pair<int, int>>());
        vi.doc() = "Represents an integer coordinate or size";

    auto vd =
        py::class_<Vec2f>(mod, "Float2")
            .def(py::init<int, int>(), py::arg("x") = 0, py::arg("y") = 0)
            .def(py::init<int, double>(), py::arg("x") = 0, py::arg("y") = 0)
            .def(py::init<double, int>(), py::arg("x") = 0, py::arg("y") = 0)
            .def(py::init<double, double>(), py::arg("x") = 0, py::arg("y") = 0)
            .def(py::init<std::pair<double, double>>())
            .def(
                "toi",
                [](Vec2f self) {
                    return Vec2i{static_cast<int>(self.x),
                                 static_cast<int>(self.y)};
                },
                "Convert a `Float2` to an `Int2`")
            .def("__len__", &Vec2f::len)
            .def("clamp", &Vec2f::clamp, py::arg("low"), py::arg("high"),
                 "Separately clamp the x and y component between the "
                 "corresponding components in the given arguments.")
            .def("sign", &Vec2f::sign)
            .def_readonly("x", &Vec2f::x)
            .def_readonly("y", &Vec2f::y)
            .def("random",
                 [](Vec2f self) {
                     double rm = RAND_MAX;
                     return Vec2f{rand() / rm * self.x, rand() / rm * self.y};
                 })
            .def("__eq__",
                 [](const Vec2f& a, Vec2f const& b) { return a == b; })
            .def("__ne__",
                 [](const Vec2f& a, Vec2f const& b) { return a != b; })
            .def("__getitem__",
                 [](Vec2f const& v, size_t i) {
                     if (i > 1) { throw pybind11::index_error(); }
                     return v[i];
                 })
            .def(
                "__iter__",
                [](Vec2f const& v) {
                    return py::make_iterator(&v.x, &v.y + 1);
                },
                py::keep_alive<0, 1>())
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
            .def("clip", &Vec2f::clip, py::arg("low"), py::arg("high"))
            .def("mag", &Vec2f::mag, "Get magnitude (length) of vector")
            .def("mag2", &Vec2f::mag2, "Get the squared magnitude")
            .def("norm", &Vec2f::norm, "Get the normalized vector.")
            .def("angle", &Vec2f::angle,
                 "Get the angle between the vector and (1,0).")
            .def("cossin", &Vec2f::cossin)
            .def_readonly_static("ONE", &vec2_one, "Constant (1,1)")
            .def_readonly_static("ZERO", &vec2_zero, "Constant (0,0)");

    vd.doc() = "Represents an floating pont coordinate or size";

    vi.def("__len__", &Vec2i::len)
        .def("clamp", &Vec2i::clamp, py::arg("low"), py::arg("high"))
        .def("sign", &Vec2i::sign)
        .def(
            "tof",
            [](Vec2f self) {
                return Vec2f{self.x, self.y};
            },
            "Convert a `Int2` to an `Float2`. Convenience function, since it "
            "converts automatically.")
        .def_readonly("x", &Vec2i::x)
        .def_readonly("y", &Vec2i::y)
        .def("random",
             [](Vec2i self) {
                 return Vec2i{rand() % self.x, rand() % self.y};
             })
        .def("__eq__", [](const Vec2i& a, Vec2i const& b) { return a == b; })
        .def("__ne__", [](const Vec2i& a, Vec2i const& b) { return a != b; })
        .def("__getitem__",
             [](Vec2i const& v, size_t i) {
                 if (i > 1) { throw pybind11::index_error(); }
                 return v[i];
             })
        .def(
            "__iter__",
            [](Vec2i const& v) { return py::make_iterator(&v.x, &v.y + 1); },
            py::keep_alive<0, 1>())
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
}
