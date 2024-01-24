#include "pixel_console.hpp"

#include "gl/buffer.hpp"
#include "gl/program_cache.hpp"

#include <algorithm>

std::string PixConsole::vertex_shader{R"gl(
    #ifdef GL_ES
        precision mediump float;
    #endif
        attribute vec2 in_pos;
        attribute vec2 in_uv;
        varying vec2 out_uv;
        void main() {
            vec4 v = vec4(in_pos, 0, 1);
            gl_Position = vec4( v.x, v.y, 0, 1 );
            out_uv = in_uv;
        })gl"};

std::string PixConsole::fragment_shader{R"gl(
    #ifdef GL_ES
        precision mediump float;
    #endif
        uniform sampler2D in_tex;
        uniform sampler2D uv_tex;
        uniform sampler2D col_tex;

        uniform vec2 console_size;
        uniform vec2 uv_scale;
        varying vec2 out_uv;

        void main() {
              vec4 up = texture2D(uv_tex, out_uv);
              vec4 color = texture2D(col_tex, out_uv);
              vec3 fg_color = vec3(up.wz, color.a);
              vec3 bg_color = color.rgb;
              vec2 ux = (up.xy * 255.0) / 256.0;
              vec2 uvf = fract(out_uv * console_size);
              vec2 uv = ux + uvf * uv_scale;
              vec4 col = texture2D(in_tex, uv);
              gl_FragColor = vec4(fg_color * col.rgb * col.a + bg_color * (1.0 - col.a), col.a);
        })gl"};
/*
PixConsole::PixConsole(int w, int h, std::string const& font_file, int size)
    : font_ptr{std::make_shared<TileSet>(font_file, size)}, font{*font_ptr},
      cols(w), rows(h)
{
    init();
}

PixConsole::PixConsole(int w, int h, FreetypeFont& ftfont)
    : font_ptr{std::make_shared<TileSet>(ftfont)}, font{*font_ptr}, cols(w),
      rows(h)

{
    init();
}
*/
PixConsole::PixConsole(int _cols, int _rows, std::shared_ptr<TileSet> const& _tile_set)
    : tile_set{_tile_set},  cols{_cols}, rows{_rows}
{
    init();
}

void PixConsole::init()
{
    uvdata.resize(cols * rows);
    coldata.resize(cols * rows);
    fill(0xffffffff, 0);
    uv_texture = gl::Texture{cols, rows, uvdata};
    col_texture = gl::Texture{cols, rows, coldata};

    col_texture.bind(2);
    uv_texture.bind(1);

    program = gl::Program(gl::VertexShader{vertex_shader},
                          gl::FragmentShader{fragment_shader});

    program.setUniform("in_tex", 0);
    program.setUniform("uv_tex", 1);
    program.setUniform("col_tex", 2);

    program.setUniform("console_size", std::pair<float, float>(cols, rows));
    program.setUniform("uv_scale", tile_set->get_uvscale());

    uv_texture.update(uvdata.data());
    col_texture.update(coldata.data());
}

template <typename T> std::pair<T, T> PixConsole::get_char_size() const
{
    return {static_cast<T>(tile_set->char_width), static_cast<T>(tile_set->char_height)};
}

template std::pair<float, float> PixConsole::get_char_size() const;
template std::pair<int, int> PixConsole::get_char_size() const;


std::pair<int, int> PixConsole::text(int x, int y, std::string const& t,
                                     uint32_t fg, uint32_t bg)
{
    auto text32 = utf8::utf8_decode(t);
    return text(x, y, text32, fg, bg);
}

std::pair<int, int> PixConsole::text(std::pair<int, int> pos,
                                     std::u32string const& text32, uint32_t fg,
                                     uint32_t bg)
{
    return text(pos.first, pos.second, text32, fg, bg);
}

std::pair<int, int> PixConsole::text(int x, int y, std::u32string const& text32,
                                     uint32_t fg, uint32_t bg)
{
    if (x < 0 || x >= cols || y < 0 || y >= rows) { return {x, y}; }
    auto [w0, w1] = make_col(fg, bg);
    for (auto c : text32) {
        if (c == 10) {
            x = 0;
            y++;
            continue;
        }

        uvdata[x + cols * y] = tile_set->get_offset(c) | w0;
        coldata[x + cols * y] = w1;
        x++;
        if (x >= cols) {
            x = 0;
            y++;
        }
        if(y >= rows) { break; }
    }
    uv_dirty = col_dirty = true;
    return {x, y};
}

void PixConsole::put_char(int x, int y, char32_t c)
{
    if (x < 0 || x >= cols || y < 0 || y >= rows) { return; }
    uv_dirty = col_dirty = true;
    auto& u = uvdata[x + cols * y];
    u = (u & 0xffff0000) | tile_set->get_offset(c);
}

void PixConsole::put(int x, int y, uint32_t fg, uint32_t bg, char32_t c)
{
    if (x < 0 || x >= cols || y < 0 || y >= rows) { return; }
    uv_dirty = col_dirty = true;
    auto [w0, w1] = make_col(fg, bg);
    uvdata[x + cols * y] = tile_set->get_offset(c) | w0;
    coldata[x + cols * y] = w1;
}

uint32_t PixConsole::get_char(int x, int y)
{
    if (x < 0 || x >= cols || y < 0 || y >= rows) { return 0; }
    uint32_t uv = uvdata[x + cols * y] & 0xffff;
    return tile_set->get_char_from_uv(uv);
}

std::vector<uint32_t> PixConsole::get_tiles()
{
    std::vector<uint32_t> result(cols*rows*3);
    for(int i=0; i<cols*rows; i++) {
        uint32_t uv = uvdata[i] & 0xffff;
        auto fg = ((coldata[i] & 0xff000000)>>16) | (uvdata[i] & 0xffff0000);
        auto bg = coldata[i] & 0xffffff;
        result[i*3] = tile_set->get_char_from_uv(uv);
        result[i*3+1] = fg;
        result[i*3+2] = bg;
    }
    return result;
}

void PixConsole::set_tiles(std::vector<uint32_t> const& data)
{
    size_t size = cols*rows;
    if (size > data.size() * 3) {
        size = data.size() * 3;
    }
    for(size_t i=0; i<size; i++) {
        auto [w0,w1] = make_col(data[i*3+1], data[i*3+2]);
        uvdata[i] = tile_set->get_offset(data[i*3]) | w0;
        coldata[i] = w1;
    }
    uv_dirty = true;
    col_dirty = true;
}

void PixConsole::put_color(int x, int y, uint32_t fg, uint32_t bg)
{
    if (x < 0 || x >= cols || y < 0 || y >= rows) { return; }
    uv_dirty = col_dirty = true;
    auto [w0, w1] = make_col(fg, bg);
    uvdata[x + cols * y] = (uvdata[x + cols * y] & 0xffff) | w0;
    coldata[x + cols * y] = w1;
}

void PixConsole::fill(uint32_t fg, uint32_t bg)
{
    uv_dirty = col_dirty = true;
    auto [w0, w1] = make_col(fg, bg);
    w0 |= tile_set->char_uvs[' '];
    for (size_t i = 0; i < uvdata.size(); i++) {
        uvdata[i] = w0;
        coldata[i] = w1;
    }
}

void PixConsole::fill(uint32_t bg)
{
    uv_dirty = col_dirty = true;
    auto [w0, w1] = make_col(0, bg);
    for (auto& c : coldata) {
        c = (c & 0xff000000) | w1;
    }
}

void PixConsole::clear_area(int32_t x, int32_t y, int32_t w, int32_t h,
                            uint32_t fg, uint32_t bg)
{
    uv_dirty = col_dirty = true;
    if (w == -1) { w = cols; }
    if (h == -1) { h = rows; }
    auto [w0, w1] = make_col(fg, bg);
    w0 |= tile_set->char_uvs[' '];
    for (int32_t yy = 0; yy < h; yy++) {
        for (int32_t xx = 0; xx < w; xx++) {
            auto offs = (xx + x) + (yy + y) * cols;
            uvdata[offs] = w0;
            coldata[offs] = w1;
        }
    }
}

void PixConsole::scroll(int dy, int dx)
{
    uv_dirty = col_dirty = true;
    // TODO: Optimize
    auto uc = uvdata;
    auto cc = coldata;
    for (int32_t y = 0; y < rows; y++) {
        auto ty = y + dy;
        if (ty >= 0 && ty < rows) {
            for (int32_t x = 0; x < cols; x++) {
                auto tx = x + dx;
                if (tx < cols && ty < rows) {
                    uvdata[tx + ty * cols] = uc[x + y * cols];
                    coldata[tx + ty * cols] = cc[x + y * cols];
                }
            }
        }
    }
}

void PixConsole::render(float x0, float y0, float x1, float y1)
{
    if (uv_dirty) { uv_texture.update(uvdata.data()); }
    if (col_dirty) { col_texture.update(coldata.data()); }
    uv_dirty = col_dirty = false;
    glDisable(GL_BLEND);
    col_texture.bind(2);
    uv_texture.bind(1);
    tile_set->tile_texture->bind(0);

    program.use();

    std::array vertexData{x0,  y0,  x1,  y0,  x1,  y1,  x0,  y1,
                          0.F, 0.F, 1.F, 0.F, 1.F, 1.F, 0.F, 1.F};
    gl::ArrayBuffer<GL_STREAM_DRAW> vbo{vertexData};

    vbo.bind();
    auto pos = program.getAttribute("in_pos");
    auto uv = program.getAttribute("in_uv");
    pos.enable();
    uv.enable();
    gl::vertexAttrib(pos, 2, gl::Type::Float, 0 * sizeof(GLfloat), 0);
    gl::vertexAttrib(uv, 2, gl::Type::Float, 0 * sizeof(GLfloat), 8 * 4);
    gl::drawArrays(gl::Primitive::TriangleFan, 0, 4);
    pos.disable();
    uv.disable();

    glEnable(GL_BLEND);
}

std::pair<int, int> PixConsole::get_pixel_size() const
{
    return {cols * tile_set->char_width, rows * tile_set->char_height};
}
