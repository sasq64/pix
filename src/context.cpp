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

void Context::lines(std::vector<Vec2f> const& points)
{
    glLineWidth(line_width);

    std::vector<float> result;
    result.reserve(points.size() * 2);
    for(auto&& p : points) {
        auto&& p2 = to_screen(p);
        result.push_back(p2.x);
        result.push_back(p2.y);
    }
    draw_filled(result, gl::Primitive::LineStrip);
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

Context::Context(Context const& other) :
    fg{other.fg},
    colored{
        ProgramCache::get_instance()
            .get_program<ProgramCache::Colored, ProgramCache::NoTransform>()},
    textured{ProgramCache::get_instance()
                 .get_program<ProgramCache::Textured>()}, // NOLINT
    filled{ProgramCache::get_instance().get_program<>()} // NOLINT
{
   target = other.target;
   offset = other.offset;
   view_size = other.view_size;
   target_size = other.target_size;
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

template <typename CO, typename T>
void Context::draw_indexed(const CO& container, std::vector<T> indices, gl::Primitive primitive)
{
    set_target();

    filled.use();
    filled.setUniform("frag_color", fg);
    auto pos = filled.getAttribute("in_pos");
    pos.enable();
    gl::ArrayBuffer<GL_STREAM_DRAW> vbo{container};
    gl::ElementBuffer<GL_STREAM_DRAW> elements{indices};
    vbo.bind();
    elements.bind();
    gl::vertexAttrib(pos, gl::Size<2>{}, gl::Type::Float,
                     0 * sizeof(GLfloat), 0);
    int len = static_cast<int>(container.size()) / 2;
    //gl::drawArrays(primitive, 0, len);
    gl::drawElements(primitive, indices.size(), gl::Type::UnsignedShort, 0);
    pos.disable();
}

bool instersects(Vec2f v11, Vec2f v12, Vec2f v21, Vec2f v22)
{
    double d1, d2;
    double a1, a2, b1, b2, c1, c2;

    // Convert vector 1 to a line (line 1) of infinite length.
    // We want the line in linear equation standard form: A*x + B*y + C = 0
    // See: http://en.wikipedia.org/wiki/Linear_equation
    a1 = v12.y - v11.y;
    b1 = v11.x - v12.x;
    c1 = (v12.x * v11.y) - (v11.x * v12.y);

    // Every point (x,y), that solves the equation above, is on the line,
    // every point that does not solve it, is not. The equation will have a
    // positive result if it is on one side of the line and a negative one
    // if is on the other side of it. We insert (x1,y1) and (x2,y2) of vector
    // 2 into the equation above.
    d1 = (a1 * v21.x) + (b1 * v21.y) + c1;
    d2 = (a1 * v22.x) + (b1 * v22.y) + c1;

    // If d1 and d2 both have the same sign, they are both on the same side
    // of our line 1 and in that case no intersection is possible. Careful,
    // 0 is a special case, that's why we don't test ">=" and "<=",
    // but "<" and ">".
    if (d1 > 0 && d2 > 0) return false;
    if (d1 < 0 && d2 < 0) return false;

    // The fact that vector 2 intersected the infinite line 1 above doesn't
    // mean it also intersects the vector 1. Vector 1 is only a subset of that
    // infinite line 1, so it may have intersected that line before the vector
    // started or after it ended. To know for sure, we have to repeat the
    // the same test the other way round. We start by calculating the
    // infinite line 2 in linear equation standard form.
    a2 = v22.y - v21.y;
    b2 = v21.x - v22.x;
    c2 = (v22.x * v21.y) - (v21.x * v22.y);

    // Calculate d1 and d2 again, this time using points of vector 1.
    d1 = (a2 * v11.x) + (b2 * v11.y) + c2;
    d2 = (a2 * v12.x) + (b2 * v12.y) + c2;

    // Again, if both have the same sign (and neither one is 0),
    // no intersection is possible.
    if (d1 > 0 && d2 > 0) return false;
    if (d1 < 0 && d2 < 0) return false;

    // If we get here, only two possibilities are left. Either the two
    // vectors intersect in exactly one point or they are collinear, which
    // means they intersect in any number of points from zero to infinite.
    //if ((a1 * b2) - (a2 * b1) == 0.0f) return COLLINEAR;

    // If they are not collinear, they must intersect in exactly one point.
    return true;
}
 

double cross(Vec2f a, Vec2f b)
{
    return a.x * b.y - b.x * a.y;
}

bool same_side(Vec2f const& p1, Vec2f const& p2, Vec2f const& a, Vec2f const& b)
{
    Vec2f ab = {b.x - a.x, b.y - a.y};
    Vec2f ap1 = {p1.x - a.x, p1.y - a.y};
    Vec2f ap2 = {p2.x - a.x, p2.y - a.y};
    auto cp1 = cross(ab, ap1);
    auto cp2 = cross(ab, ap2);
    return (cp1 * cp2 >= 0);
}

bool in_triangle(Vec2f const& p, Vec2f const& a, Vec2f const& b, Vec2f const& c)
{
    return same_side(p, a, b, c) && same_side(p, b, a, c) && same_side(p, c, a, b);
}

bool is_convex(Vec2f a, Vec2f b, Vec2f c)
{
    // Check if the triangle a-b-c is convex.
    // Assuming a clockwise order of points, if the cross product
    // of vectors (b - a) and (c - b) is positive, it is convex.
    Vec2f ab = {b.x - a.x, b.y - a.y};
    Vec2f bc = {c.x - b.x, c.y - b.y};
    return cross(ab, bc) > 0;
}

bool is_ear(Vec2f a, Vec2f b, Vec2f c, Vec2f const* vertices, size_t count)
{
    if (!is_convex(a, b, c)) {
        return false; // The triangle is not convex
    }

    for (size_t i=0; i<count; i++) {
        auto p = vertices[i];
        if (p != a && p != b && p != c && in_triangle(p, a, b, c)) {
            return false; // Found a point inside the triangle
        }
    }

    return true; // No points inside the triangle and it is convex
}

void Context::draw_inconvex_polygon(Vec2f const* points, size_t count)
{
    std::vector<uint16_t> triangles;
    std::vector<uint16_t> indexes;
    indexes.resize(count);
    for(size_t i=0; i<count; i++) {
        indexes[i] = i;
    }
    std::vector<float> data;
    int removed = 0;
    double sum = 0;

    for(unsigned i=0; i<count-1; i++)
    {
        auto &&q = points[i];
        auto &&p = points[i+1];
        sum += (p.x - q.x) * (p.y + q.y);
    }
    {
        auto&& q = points[count - 1];
        auto&& p = points[0];
        sum += (p.x - q.x) * (p.y + q.y);
    }

    if (sum > 0) { return; }

    for(unsigned i=0; i<count; i++) {

        auto&& p = to_screen(points[i]);
        data.push_back(p.x);
        data.push_back(p.y);
    }
    count -= removed;
    while (indexes.size() > 3) {
        bool ok = false;
        for (size_t j = 0; j < indexes.size(); ++j) {
            auto i0 = indexes[j];
            auto i1 = indexes[(j + 1) % count];
            auto i2 = indexes[(j + 2) % count];
            auto&& a = points[i0];
            auto&& b = points[i1];
            auto&& c = points[i2];

            if (is_ear(a, b, c, points, count)) {
                triangles.push_back(i0);
                triangles.push_back(i1);
                triangles.push_back(i2);
                // Remove the vertex 'b' from the list
                indexes.erase(indexes.begin() + (j + 1) % count);
                ok = true;
                break;
            }
        }
        if (!ok) {
            triangles.push_back(indexes[0]);
            triangles.push_back(indexes[1]);
            triangles.push_back(indexes[2]);
            indexes.erase(indexes.begin());
            //fprintf(stderr, "BROKEN POLYGON\n");
            //for (size_t j = 0; j < indexes.size(); ++j) {
            //    auto&& p = points[indexes[j]];
            //    fprintf(stderr, "X: %.3f Y: %.3f\n", p.x, p.y);
            //}
            //break;
        }
    }
    triangles.push_back(indexes[0]);
    triangles.push_back(indexes[1]);
    triangles.push_back(indexes[2]);
    draw_indexed(data, triangles, gl::Primitive::Triangles);
}

void Context::draw_polygon(Vec2f const* points, size_t count)
{
    std::vector<float> data;
    data.resize(count*2);
    for(unsigned i=0; i<count; i++) {
        auto&& p = to_screen(points[i]);
        data[(count-i-1)*2] = p.x;
        data[(count-i-1)*2+1] = p.y;
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
    set_target();
    glClearColor(col.red, col.green, col.blue, col.alpha);
    glClear(GL_COLOR_BUFFER_BIT);
}

void Context::plot(Vec2f point, gl::Color col)
{
    auto p = to_screen(point);
    point_cache.push_back(p.x);
    point_cache.push_back(p.y);
    point_cache.push_back(col.red);
    point_cache.push_back(col.green);
    point_cache.push_back(col.blue);
    point_cache.push_back(col.alpha);

    if (point_cache.size() > 32000) {
        draw_points();
        point_cache.clear();
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
    gl::ArrayBuffer<GL_STREAM_DRAW> vbo{point_cache};
    vbo.bind();
    gl::vertexAttrib(pos, gl::Size<2>{}, gl::Type::Float,
                          6 * sizeof(GLfloat), 0);
    gl::vertexAttrib(cola, gl::Size<4>{}, gl::Type::Float,
                          6 * sizeof(GLfloat), 8);
    int len = static_cast<int>(point_cache.size()) / 6;
    gl::drawArrays(gl::Primitive::Points, 0, len);
    pos.disable();
    cola.disable();
}
void Context::flush()
{
    if (!point_cache.empty()) {
        draw_points();
        point_cache.clear();
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
