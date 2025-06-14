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

    void set_format(std::vector<std::pair<std::string, int>> const& format);
    void walk_tree(TSNode node, int d, uint64_t pattern,
                   std::vector<Hilight>& result);

public:
    TreeSitter();
    void set_source_utf8(std::string const& source);

    std::vector<Hilight> get_highlights();
};
