
#pragma once

#include "system.hpp"

#include "../treesitter.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

inline void add_treesitter_module(py::module_ const& mod)
{
    using namespace pybind11::literals;

    auto ts = py::class_<TreeSitter, std::shared_ptr<TreeSitter>>(mod, "TreeSitter")
            .def(py::init<>(), "Create an empty treesitter object.")
            .def("set_source", &TreeSitter::set_source_utf8)
            .def("set_source_utf16", &TreeSitter::set_source_utf16)
            .def("set_format", &TreeSitter::set_format)
            .def("dump_tree", &TreeSitter::dump_tree)
            .def("get_highlights", &TreeSitter::get_highlights);
}
