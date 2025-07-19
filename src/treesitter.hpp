#include <cstdint>
#include <string>
#include <tuple>
#include <vector>
#include <unordered_map>

struct TSParser;
struct TSTree;
struct TSNode;

using Hilight = std::tuple<uint32_t, uint32_t, uint32_t, uint32_t, int>;

class TreeSitter
{
    TSParser* parser;
    TSTree* tree;
    std::unordered_map<std::string, uint32_t> symbols;
    std::unordered_map<uint64_t, int> patterns;

    void walk_tree(TSNode node, uint64_t pattern,
                   std::vector<Hilight>& result);

    void dump_nodes(TSNode node, size_t d, std::string& result);
public:
    TreeSitter();
    void set_source_utf8(std::string const& source);
    void set_source_utf16(std::vector<uint16_t> const& source);
    void set_format(std::vector<std::pair<std::string, int>> const& format);
    std::vector<Hilight> get_highlights();
    std::string dump_tree();
};
