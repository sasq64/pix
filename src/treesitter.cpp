#include "treesitter.hpp"
#include <tree_sitter/api.h>

#include <cstdio>
#include <cstring>
#include <tuple>
#include <unordered_map>
#include <vector>

extern "C"
{
    const TSLanguage* tree_sitter_python(void);
}

static std::vector<std::pair<std::string, int>> format = {
    {"default", 1},
    {"def", 3},
    {"while", 3},
    {"if", 3},
    {"pass", 3},
    {"for", 3},
    {"from", 3},
    {"else", 3},
    {"import", 3},
    {"class", 3},
    {"string_content", 8},
    {"call.identifier", 2},
    {"decorator.identifier", 4},
    {"keyword_argument.identifier", 7},
    {"call.attribute.identifier", 2},
    {"function_definition.parameters.identifier", 6},
    {"typed_parameter.type", 7},
    {"type.identifier", 7},
    {"integer", 8},
    {"float", 8},
    {"comment", 6}};

/*
std::unordered_map<std::string, TSSymbol> symbols;
std::unordered_map<uint64_t, int> patterns;

void make_map()
{
    for (auto [pattern, color] : format) {
        uint64_t id = 0;
        size_t start_pos = 0;
        while (true) {
            auto pos = pattern.find_first_of('.', start_pos);
            if (pos != std::string::npos) {
                auto part = pattern.substr(start_pos, pos - start_pos);

                auto sym = symbols[part];
                id = (id << 16) | sym;

                printf("%s (%d). ", part.c_str(), sym);
                start_pos = pos + 1;
            } else {
                auto part = pattern.substr(start_pos);
                auto sym = symbols[part];
                id = (id << 16) | sym;
                printf("%s (%d)", part.c_str(), sym);
                break;
            }
        }
        puts("");
        printf("%s -> %llx\n", pattern.c_str(), id);
        patterns[id] = color;
    }
}
*/
void TreeSitter::walk_tree(TSNode node, int d, uint64_t pattern,
                           std::vector<Hilight>& result)
{
    static const char* spaces =
        "                                                                         ";

    auto n = ts_node_child_count(node);

    auto sym = ts_node_symbol(node);
    pattern = (pattern << 16) | (uint64_t)sym;

    uint64_t mask = 0xffff'ffff'ffff;
    int color = -1;
    while (mask != 0) {
        auto it = patterns.find(mask & pattern);
        if (it != patterns.end()) {
            color = it->second;
            break;
        }
        mask >>= 16;
    }
    printf("%s%s -- ", &spaces[strlen(spaces) - d * 2], ts_node_type(node));
    //printf("%llx -> COLOR %d\n", pattern, color);
    if (color >= 0) {
        TSPoint start = ts_node_start_point(node);
        TSPoint end = ts_node_end_point(node);
        printf("%d,%d\n", start.column, start.row);
        result.emplace_back(start.column, start.row, end.column, end.row,
                            color);
    }
    for (uint32_t i = 0; i < n; i++) {
        walk_tree(ts_node_child(node, i), d + 1, pattern, result);
    }
}

std::vector<Hilight> TreeSitter::get_highlights()
{
    std::vector<Hilight> result;
    auto root_node = ts_tree_root_node(tree);
    walk_tree(root_node, 0, 0, result);
    return result;
}

/*
int init_treesitter()
{
    // Create a parser.
    TSParser* parser = ts_parser_new();
    auto* lang = tree_sitter_python();
    ts_parser_set_language(parser, lang);

    uint32_t count = ts_language_symbol_count(lang);
    for (TSSymbol s = 0; s < count; s++) {
        const char* sym_name = ts_language_symbol_name(lang, s);
        symbols[sym_name] = s;
    }

    make_map();

    printf("%p %p\n", (void*)parser, (void*)lang);
    const char* source_code = "def test(x):\n    pass\n";
    auto* tree = ts_parser_parse_string(parser, nullptr, source_code,
                                        strlen(source_code));

    printf("tree %p\n", (void*)tree);
    auto root_node = ts_tree_root_node(tree);

    std::vector<Hilight> result;
    walk_tree(root_node, 0, 0, result);
    return 0;
}
*/

TreeSitter::TreeSitter()
{
    parser = ts_parser_new();
    auto* lang = tree_sitter_python();
    ts_parser_set_language(parser, lang);

    uint32_t count = ts_language_symbol_count(lang);
    for (TSSymbol s = 0; s < count; s++) {
        const char* sym_name = ts_language_symbol_name(lang, s);
        symbols[sym_name] = s;
    }
    set_format(format);
}

void TreeSitter::set_source_utf8(std::string const& source)
{
    tree =
        ts_parser_parse_string(parser, nullptr, source.data(), source.size());
}

void TreeSitter::set_format(
    std::vector<std::pair<std::string, int>> const& format)
{
    for (auto [pattern, color] : format) {
        uint64_t id = 0;
        size_t start_pos = 0;
        while (true) {
            auto pos = pattern.find_first_of('.', start_pos);
            if (pos != std::string::npos) {
                auto part = pattern.substr(start_pos, pos - start_pos);

                auto sym = symbols[part];
                id = (id << 16) | sym;

                printf("%s (%d). ", part.c_str(), sym);
                start_pos = pos + 1;
            } else {
                auto part = pattern.substr(start_pos);
                auto sym = symbols[part];
                id = (id << 16) | sym;
                printf("%s (%d)", part.c_str(), sym);
                break;
            }
        }
        puts("");
        //printf("%s -> %llx\n", pattern.c_str(), id);
        patterns[id] = color;
    }
}
