
#pragma once

#include "system.hpp"

#include "../treesitter.hpp"
#include "tree_sitter/api.h"

#include <optional>
#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

inline void add_treesitter_module(py::module_ const& mod)
{
    using namespace pybind11::literals;

    py::class_<TSNode>(mod, "TSNode")
        .def_property_readonly("parent",
                               [](TSNode node) -> std::optional<TSNode> {
                                   auto parent = ts_node_parent(node);
                                   if (ts_node_is_null(parent)) {
                                       return std::nullopt;
                                   }
                                   return parent;
                               })
        .def_property_readonly("type",
                               [](TSNode node) { return ts_node_type(node); })
        .def_property_readonly("start",
                               [](TSNode node) {
                                   auto start = ts_node_start_point(node);
                                   return std::make_pair(start.column,
                                                         start.row);
                               })
        .def_property_readonly("end",
                               [](TSNode node) {
                                   auto start = ts_node_end_point(node);
                                   return std::make_pair(start.column,
                                                         start.row);
                               })
        .def_property_readonly(
            "symbol", [](TSNode node) { return ts_node_symbol(node); });

    auto ts =
        py::class_<TreeSitter, std::shared_ptr<TreeSitter>>(mod, "TreeSitter")
            .def(py::init<>(), "Create an empty treesitter object.")
            .def("set_source", &TreeSitter::set_source_utf8)
            .def("set_source_utf16", &TreeSitter::set_source_utf16)
            .def("set_format", &TreeSitter::set_format)
            .def("dump_tree", &TreeSitter::dump_tree)
            .def("find_node", &TreeSitter::find_node)
            .def("get_highlights", &TreeSitter::get_highlights);
}
