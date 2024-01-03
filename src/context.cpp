#include "context.hpp"

namespace pix {

using gl::ProgramCache;

void Context::set_color(gl::Color const& col)
{
    fg = col;
}

void add_to(std::vector<float>& target, Vec2<float> const& v)
{
    target.push_back(v.x);
    target.push_back(v.y);
}

std::vector<float> Context::generate_circle(Vec2f center, float radius,
                                            bool include_center) const
{
    if (radius < 1) { return {}; }
    int steps = static_cast<int>(M_PI * 1.5 / asin(sqrt(1.0 / radius)));

    std::vector<float> vertexData;
    vertexData.reserve(steps + 2);

    if (include_center) { add_to(vertexData, to_screen(center)); }
    for (int i = 0; i <= steps; i++) {
        auto v = Vec2f::from_angle(M_PI * 2.0 * i / steps) * radius + center;
        add_to(vertexData, to_screen(v));
    }
    return vertexData;
}

std::array<float, 4> Context::generate_line(Vec2f from, Vec2f to) const
{
    auto a = to_screen(from + Vec2f{0.5, 0.5});
    auto b = to_screen(to + Vec2f{0.5, 0.5});
    return {a.x, a.y, b.x, b.y};
}

std::vector<float> Context::generate_lines(const float* screen_cords,
                                           int count) const
{
    std::vector<float> result;
    result.reserve(count * 2);
    for (int i = 0; i < count * 2; i += 2) {
        add_to(result, to_screen(screen_cords[i], screen_cords[i + 1]));
    }
    return result;
}

std::array<float, 8> Context::generate_quad(Vec2f top_left, Vec2f size) const
{
    auto p0 = to_screen(top_left);
    auto p1 = to_screen(top_left + size);
    return std::array{p0.x, p0.y, p1.x, p0.y, p1.x, p1.y, p0.x, p1.y};
}

std::array<float, 16> Context::generate_quad_with_uvs(Vec2f pos,
                                                      Vec2f size) const
{
    auto p0 = to_screen(pos);
    auto p1 = to_screen(pos + size);
    return std::array{p0.x, p0.y, p1.x, p0.y, p1.x, p1.y, p0.x, p1.y,
                      0.F,  1.F,  1.F,  1.F,  1.F,  0.F,  0.F,  0.F};
}

static Vec2f rotate(Vec2f v, float rot)
{
    auto ca = cosf(rot);
    auto sa = sinf(rot);
    return {v.x * ca - v.y * sa, v.x * sa + v.y * ca};
}

std::array<float, 8> Context::rotated_quad(Vec2f center, Vec2f sz,
                                           float rot) const
{
    sz = sz / 2;
    auto p0 = to_screen(rotate(Vec2f{-sz.x, -sz.y}, rot) + center);
    auto p1 = to_screen(rotate(Vec2f{sz.x, -sz.y}, rot) + center);
    auto p2 = to_screen(rotate(Vec2f{sz.x, sz.y}, rot) + center);
    auto p3 = to_screen(rotate(Vec2f{-sz.x, sz.y}, rot) + center);

    return std::array{p0.x, p0.y, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y};
}

std::array<float, 16> Context::rotated_quad_with_uvs(Vec2f center, Vec2f sz,
                                                     float rot) const
{
    sz = sz / 2;
    auto p0 = to_screen(rotate(Vec2f{-sz.x, -sz.y}, rot) + center);
    auto p1 = to_screen(rotate(Vec2f{sz.x, -sz.y}, rot) + center);
    auto p2 = to_screen(rotate(Vec2f{sz.x, sz.y}, rot) + center);
    auto p3 = to_screen(rotate(Vec2f{-sz.x, sz.y}, rot) + center);

    return std::array{p0.x, p0.y, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y,
                      0.F,  1.F,  1.F,  1.F,  1.F,  0.F,  0.F,  0.F};
}

void Context::filled_rect(Vec2f top_left, Vec2f size)
{
    draw_filled(generate_quad(top_left, size), gl::Primitive::TriangleFan);
}

void Context::rect(Vec2f top_left, Vec2f size)
{
    glLineWidth(line_width);
    draw_filled(generate_quad(top_left, size), gl::Primitive::LineLoop);
}

void Context::line(Vec2f from, Vec2f to)
{
    glLineWidth(line_width);
    draw_filled(generate_line(from, to), gl::Primitive::Lines);
    last_point = to;
}

void Context::line(Vec2f to)
{
    glLineWidth(line_width);
    draw_filled(generate_line(last_point, to), gl::Primitive::Lines);
    last_point = to;
}

void Context::circle(Vec2f const& v, float r)
{
    glLineWidth(line_width);
    draw_filled(generate_circle(v, r, false), gl::Primitive::LineLoop);
}

void Context::filled_circle(Vec2f const& v, float r)
{
    draw_filled(generate_circle(v, r, true), gl::Primitive::TriangleFan);
}

void Context::blit(gl::TexRef const& tex, Vec2f pos, Vec2f size)
{
    tex.bind();
    if (size.x == 0) {
        size = {static_cast<float>(tex.width()),
                static_cast<float>(tex.height())};
    }
    // auto vdata = generate_quad_with_uvs(pos.x, pos.y, size.x, size.y);
    auto vdata = generate_quad_with_uvs(pos, size);
    std::copy(tex.uvs().begin(), tex.uvs().end(), vdata.begin() + 8);
    draw_textured(vdata, gl::Primitive::TriangleFan);
}

void Context::draw(gl::TexRef const& tex, Vec2f center, Vec2f size, float rot)
{
    tex.bind();
    if (size.x == 0) {
        size = {static_cast<float>(tex.width()),
                static_cast<float>(tex.height())};
    }
    auto vdata = rotated_quad_with_uvs(center, size, rot);
    std::copy(tex.uvs().begin(), tex.uvs().end(), vdata.begin() + 8);
    draw_textured(vdata, gl::Primitive::TriangleFan);
}

Context::Context(Vec2f _offset, Vec2f _view_size, Vec2f _target_size, GLuint fb)
    : target{fb}, offset{_offset}, view_size{_view_size}, target_size{_target_size}, fg{color::white},
      colored{
          ProgramCache::get_instance()
              .get_program<ProgramCache::Colored, ProgramCache::NoTransform>()},
      textured{ProgramCache::get_instance()
                   .get_program<ProgramCache::Textured>()}, // NOLINT
      filled{ProgramCache::get_instance().get_program<>()} // NOLINT
{
    // auto in_color = textured.getUniformLocation("in_color");
    // auto in_pos = textured.getAttribute("in_pos");
}

Context::Context(float w, float h, GLuint fb)
    : Context(Vec2f{0, 0}, Vec2f{w, h}, Vec2f{w,h}, fb)
{
    static const std::array<float, 16> mat{1, 0, 0, 0, 0, 1, 0, 0,
                                           0, 0, 1, 0, 0, 0, 0, 1};
    gl::Color color = 0xffffffff;
    filled.setUniform("frag_color", color);
    filled.setUniform("in_transform", mat);
    textured.setUniform("frag_color", color);
    textured.setUniform("in_transform", mat);
}

template <typename CO>
void Context::draw_filled(const CO& container, gl::Primitive primitive)
{
    set_target();

    filled.use();
    filled.setUniform("frag_color", fg);
    auto pos = filled.getAttribute("in_pos");
    pos.enable();
    gl::ArrayBuffer<GL_STREAM_DRAW> vbo{container};
    vbo.bind();
    gl::vertexAttrib(pos, gl::Size<2>{}, gl::Type::Float,
                          0 * sizeof(GLfloat), 0);
    int len = static_cast<int>(container.size()) / 2;
    gl::drawArrays(primitive, 0, len);
    pos.disable();
}

void Context::draw_polygon(Vec2f const* points, size_t count)
{
    std::vector<float> data;
    for(unsigned i=0; i<count; i++) {
        auto&& p = to_screen(points[i]);
        data.push_back(p.x);
        data.push_back(p.y);
    }

    glEnable(GL_CULL_FACE);
    draw_filled(data, gl::Primitive::TriangleFan);
    glDisable(GL_CULL_FACE);

}

void Context::set_target() const
{
    glBindFramebuffer(GL_FRAMEBUFFER, target);
    gl::setViewport({target_size.x * vpscale, target_size.y * vpscale});
    if (clip_size.x != 0) {
        glEnable(GL_SCISSOR_TEST);
        glScissor(clip_start.x,
                  static_cast<int>(target_size.y) -
                      (clip_start.y + clip_size.y),
                  clip_size.x, clip_size.y);
    } else {
        glDisable(GL_SCISSOR_TEST);
    }
}

template <typename CO>
void Context::draw_textured(const CO& container, gl::Primitive primitive)
{
    set_target();

    textured.use();
    textured.setUniform("frag_color", fg);
    auto pos = textured.getAttribute("in_pos");
    pos.enable();
    auto uv = textured.getAttribute("in_uv");
    uv.enable();
    gl::ArrayBuffer<GL_STREAM_DRAW> vbo{container};
    vbo.bind();
    int len = static_cast<int>(container.size()) / 2;
    gl::vertexAttrib(pos, gl::Size<2>{}, gl::Type::Float,
                          0 * sizeof(GLfloat), 0);
    gl::vertexAttrib(uv, gl::Size<2>{}, gl::Type::Float,
                          0 * sizeof(GLfloat), len * 4);

    gl::drawArrays(primitive, 0, len / 2);
    pos.disable();
    uv.disable();
}

void Context::clear(const gl::Color& col) const
{
    glBindFramebuffer(GL_FRAMEBUFFER, target);
    gl::setViewport({target_size.x * vpscale, target_size.y * vpscale});
    glClearColor(col.red, col.green, col.blue, col.alpha);
    glClear(GL_COLOR_BUFFER_BIT);
}

void Context::plot(Vec2f point, gl::Color col)
{
    auto p = to_screen(point);
    points.push_back(p.x);
    points.push_back(p.y);
    points.push_back(col.red);
    points.push_back(col.green);
    points.push_back(col.blue);
    points.push_back(col.alpha);

    if (points.size() > 32000) {
        draw_points();
        points.clear();
    }
}

void Context::draw_points()
{
    glBindFramebuffer(GL_FRAMEBUFFER, target);
    gl::setViewport({target_size.x * vpscale, target_size.y * vpscale});

    glPointSize(point_size);

    colored.use();
    auto pos = colored.getAttribute("in_pos");
    auto cola = colored.getAttribute("in_color");
    pos.enable();
    cola.enable();
    gl::ArrayBuffer<GL_STREAM_DRAW> vbo{points};
    vbo.bind();
    gl::vertexAttrib(pos, gl::Size<2>{}, gl::Type::Float,
                          6 * sizeof(GLfloat), 0);
    gl::vertexAttrib(cola, gl::Size<4>{}, gl::Type::Float,
                          6 * sizeof(GLfloat), 8);
    int len = static_cast<int>(points.size()) / 6;
    gl::drawArrays(gl::Primitive::Points, 0, len);
    pos.disable();
    cola.disable();
}
void Context::flush()
{
    if (!points.empty()) {
        draw_points();
        points.clear();
    }
    flush_pixels();
}
void Context::set_pixel(int x, int y, uint32_t col)
{
    col = (col & 0x0000FFFF) << 16 | (col & 0xFFFF0000) >> 16;
    col = (col & 0x00FF00FF) << 8 | (col & 0xFF00FF00) >> 8;

    glBindFramebuffer(GL_FRAMEBUFFER, target);
    int width = view_size.x;
    int height = view_size.y;
    if (pixels == nullptr) {
        pixels = std::unique_ptr<uint32_t[]>(
            new uint32_t[width * height]); // NOLINT
        glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE,
                     pixels.get());
    }
    dirty = true;
    pixels[x + width * y] = col;
}

void Context::flush_pixels()
{
    if (dirty) {
        // TODO: Better way of drawing to a FBO than creating a temporary
        // texture and drawing a quad?

        int width = view_size.x;
        int height = view_size.y;
        int x = offset.x;
        int y = offset.y;

        if (texture != nullptr)
        {
            texture->update(x, y, width, height, pixels.get());
        }
        else
        {
//        GLuint tex_id;
//        glGenTextures(1, &tex_id);
//        glBindTexture(GL_TEXTURE_2D, tex_id);
//        glBindFramebuffer(GL_FRAMEBUFFER, target);
//        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
//                               GL_TEXTURE_2D, tex_id, 0);
//        glTexSubImage2D(GL_TEXTURE_2D, 0, x, y, w, h, GL_RGBA, GL_UNSIGNED_BYTE, pixels.get());
//        glDeleteTextures(1, &tex_id);

            auto tex = std::make_shared<gl::Texture>(width, height, pixels.get());
            auto oldfg = fg;
            fg = 0xffffffff;
            blit(gl::TexRef{tex}, {0,0}, view_size);
            fg = oldfg;
        }
        dirty = false;
        pixels = nullptr;
    }
}
} // namespace pix
