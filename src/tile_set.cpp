#include "tile_set.hpp"

static constexpr int align(int val, int a)
{
    return (val + (a - 1)) & (~(a - 1));
}

void TileSet::add_char(char32_t c)
{
    auto pos = alloc_char(c);

    // Render character into texture
    auto [fw, fh] = font_ptr->get_size();
    std::vector<uint32_t> temp(fw * fh * 2);
    font_ptr->render_char(c, temp.data(), 0xffffff00, fw, fw, fh);
    auto ox = (char_width - fw) / 2;
    auto oy = (char_height - fh) / 2;
    tile_texture->update(pos.first + ox, pos.second + oy, fw, fh, temp.data());
}

std::pair<int, int> TileSet::alloc_char(char32_t c)
{
    if (next_pos.second >= (texture_height - char_height - gap)) {
        throw font_exception("No room left in tileset");
    }
    auto cw = char_width + gap;
    auto fx = texture_width / 256;
    auto fy = texture_height / 256;
    int x = next_pos.first / fx;
    int y = next_pos.second / fy;
    auto uv = x | (y << 8);
    char_uvs[c] = uv;
    reverse_chars[uv] = c;
    if (c <= 0xffff) { char_array[c] = uv; }

    auto res = next_pos;
    next_pos.first += align(char_width + gap, 4);
    if (next_pos.first >= (texture_width - cw - gap)) {
        next_pos.first = 0;
        next_pos.second += align(char_height + gap, 4);
    }
    return res;
}
char32_t TileSet::get_char_from_uv(uint32_t uv)
{
    return reverse_chars[uv];
}

TileSet::TileSet(std::string const& font_file, int size,
                 std::pair<int, int> tsize)
    : font_ptr{std::make_shared<FreetypeFont>(font_file.c_str(), size)},
      char_array{0xffffffff}, char_width{tsize.first}, char_height{tsize.second}
{
    init();
}

TileSet::TileSet(std::shared_ptr<FreetypeFont> freetype_font,
                 std::pair<int, int> tsize)
    : font_ptr{std::move(freetype_font)}, char_array{0xffffffff},
      char_width{tsize.first}, char_height{tsize.second}
{
    init();
}

TileSet::TileSet(std::pair<int, int> tile_size)
    : char_array{0xffffffff}, char_width(tile_size.first),
      char_height(tile_size.second)
{
    init();
}

void TileSet::init()
{
    std::vector<uint32_t> data;
    data.resize(texture_width * texture_height);
    if (char_width <= 0) {
        std::tie(char_width, char_height) = font_ptr->get_size();
    }

    std::fill(data.begin(), data.end(), 0);

    tile_texture =
        std::make_shared<gl::Texture>(texture_width, texture_height, data);
    std::fill(char_array.begin(), char_array.end(), 0xffffffff);
    if (font_ptr) {
        for (char32_t c = 0x20; c <= 0x7f; c++) {
            add_char(c);
        }
    }
    std::fill(data.begin(), data.end(), 0xff);
    tile_texture->bind(0);
}

std::pair<float, float> TileSet::get_uvscale() const
{
    return std::pair{
        static_cast<float>(char_width) / static_cast<float>(texture_width),
        static_cast<float>(char_height) / static_cast<float>(texture_height)};
}

uint32_t TileSet::get_offset(char32_t c)
{
    if (c <= 0xffff) {
        auto res = char_array[c];
        if (res == 0xffffffff) {
            add_char(c);
            res = char_array[c];
        }
        return res;
    }
    auto it = char_uvs.find(c);
    if (it == char_uvs.end()) {
        add_char(c);
        it = char_uvs.find(c);
    }
    return it->second;
}
std::pair<int, int> TileSet::get_size() const
{
    return font_ptr->get_size();
}

gl::TexRef TileSet::get_texture_for_char(char32_t c)
{
    auto fx = texture_width / 256;
    auto fy = texture_height / 256;

    std::pair<int, int> pos;
    auto it = char_uvs.find(c);
    if (it == char_uvs.end()) {
        pos = alloc_char(c);
    } else {
        auto cx = (it->second & 0xff) * fx;
        auto cy = (it->second >> 8) * fy;
        pos = {cx, cy};
    }

    auto dx = 1.0 / texture_width;
    auto dy = 1.0 / texture_height;

    auto u = static_cast<float>(pos.first * dx);
    auto v = static_cast<float>(pos.second * dy);
    auto du = static_cast<float>(char_width * dx);
    auto dv = static_cast<float>(char_height * dy);

    gl::TexRef tr{tile_texture,
                       std::array{u, v, u + du, v, u + du, v + dv, u, v + dv}};
    return tr;
}

void TileSet::render_chars(pix::Context* context, std::string const& text, Vec2f pos, Vec2f size)
{
    auto us = utf8::utf8_decode(text);
    render_tiles(context, (int32_t*)us.data(), us.length(), pos, size);
}
void TileSet::render_chars(pix::Context* context, std::string const& text, std::vector<Vec2f> const& points)
{
    auto us = utf8::utf8_decode(text);
    render_tiles(context, (int32_t*)us.data(), points);

}
void TileSet::render_tiles(pix::Context* context, int32_t const* tiles, size_t count, Vec2f pos, Vec2f size)
{
    context->set_target();
    if (size == Vec2f{0,0}) {
        size = Vec2f(char_width, char_height);
    }

    tile_texture->bind();
    for(size_t i = 0; i<count; i++) {
        auto c = tiles[i];
        auto img = get_texture_for_char(c);
        auto vdata = context->generate_quad_with_uvs(pos, size);
        std::copy(img.uvs().begin(), img.uvs().end(), vdata.begin() + 8);
        context->draw_textured(vdata, gl::Primitive::TriangleFan);
        pos.x += size.x;
    }
}

void TileSet::render_tiles(pix::Context* context, int32_t const* tiles, std::vector<Vec2f> const& points)
{
    context->set_target();

    tile_texture->bind();
    auto size = Vec2f(char_width, char_height);
    int n = points.size();
    for(int i = 0; i<n; i++) {
        auto c = tiles[i];
        auto img = get_texture_for_char(c);
        auto vdata = context->generate_quad_with_uvs(points[i], size);
        std::copy(img.uvs().begin(), img.uvs().end(), vdata.begin() + 8);
        context->draw_textured(vdata, gl::Primitive::TriangleFan);
    }
}
