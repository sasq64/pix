#include "context.hpp"
#include "colors.hpp"
#include "gl/functions.hpp"
#include "image_view.hpp"
#include "vec2.hpp"

#include <cmath>
#include <tesselator.h>

static const std::string str(Vec2f const& v)
{
    return v.repr();
}

template <typename T> std::string str(T const& t)
{
    return std::to_string(t);
}

namespace pix {

using gl::ProgramCache;

void Context::set_color(gl::Color const& col)
{
    fg = col;
}

void Context::set_blend_mode(uint32_t mode)
{
    blend_source = (mode >> 16);
    blend_dest = mode & 0xffff;
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

std::vector<float> Context::generate_line(Vec2f p0, float r0, Vec2f p1,
                                          float r1) const
{
    int t = static_cast<int>(M_PI * 1.5 / asin(sqrt(1.0 / r0)));
    std::vector<float> result;
    result.reserve(t * 2);
    auto n = (p1 - p0).norm();

    auto n0 = n * r0;
    for (int i = 0; i < t; i++) {
        auto angle = (M_PI * 3 / 2) - (M_PI * i / t);
        auto s = sinf(angle);
        auto c = cosf(angle);
        auto ab = Vec2f(n0.x * c - n0.y * s, n0.x * s + n0.y * c) + p0;
        add_to(result, to_screen(ab));
    }
    auto n1 = n * r1;
    t = static_cast<int>(M_PI * 1.5 / asin(sqrt(1.0 / r1)));
    for (int i = 0; i < t; i++) {
        auto angle = (M_PI / 2) - (M_PI * i / t);
        auto s = sinf(angle);
        auto c = cosf(angle);
        auto ab = Vec2f(n1.x * c - n1.y * s, n1.x * s + n1.y * c) + p1;
        add_to(result, to_screen(ab));
    }
    return result;
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
    if (rot == 0.0) { return generate_quad_with_uvs(center - sz / 2, sz); }
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
    if (log_fp) {
        fprintf(log_fp, "flled_rect top_left=%s size=%s\n",
                str(top_left).c_str(), str(size).c_str());
        fflush(log_fp);
    }
    draw_filled(generate_quad(top_left, size), gl::Primitive::TriangleFan);
}

void Context::rect(Vec2f top_left, Vec2f size)
{
    if (log_fp) {
        fprintf(log_fp, "rect top_left=%s size=%s\n", str(top_left).c_str(),
                str(size).c_str());
        fflush(log_fp);
    }
    glLineWidth(line_width);
    draw_filled(generate_quad(top_left + Vec2f{0.5, 0.5}, size),
                gl::Primitive::LineLoop);
}

void Context::line(Vec2f from, Vec2f to)
{
    if (log_fp) {
        fprintf(log_fp, "line from=%s to=%s\n", str(from).c_str(),
                str(to).c_str());
        fflush(log_fp);
    }
    glLineWidth(line_width);
    draw_filled(generate_line(from + Vec2f{0.5, 0.5}, to + Vec2f{0.5, 0.5}),
                gl::Primitive::Lines);
    last_point = to;
    last_rad = 1;
}

void Context::line(Vec2f to)
{
    if (log_fp) {
        fprintf(log_fp, "line to=%s\n", str(to).c_str());
        fflush(log_fp);
    }
    if (last_rad > 0) {
        glLineWidth(line_width);
        draw_filled(
            generate_line(last_point + Vec2f{0.5, 0.5}, to + Vec2f{0.5, 0.5}),
            gl::Primitive::Lines);
    }
    last_point = to;
    last_rad = 1;
}

void Context::lines(std::vector<Vec2f> const& points)
{
    glLineWidth(line_width);

    std::vector<float> result;
    result.reserve(points.size() * 2);
    for (auto&& p : points) {
        auto&& p2 = to_screen(p + Vec2f{0.5, 0.5});
        result.push_back(p2.x);
        result.push_back(p2.y);
    }
    draw_filled(result, gl::Primitive::LineStrip);
}
void Context::round_line(Vec2f from, float rad_from, Vec2f to, float rad_to)
{
    if (log_fp) {
        fprintf(log_fp,
                "rounded_line from=%s rad_from=%.1f to=%s rad_to=%.1f\n",
                str(from).c_str(), rad_from, str(to).c_str(), rad_to);
        fflush(log_fp);
    }
    auto points = generate_line(from, rad_from, to, rad_to);
    draw_filled(points, gl::Primitive::TriangleFan);

    last_point = to;
    last_rad = rad_to;
}

void Context::round_line(Vec2f to, float radius)
{
    if (log_fp) {
        fprintf(log_fp, "rounded_line to=%s radius=%.1f\n", str(to).c_str(),
                radius);
        fflush(log_fp);
    }
    if (last_rad > 0) {
        auto points = generate_line(last_point, last_rad, to, radius);
        draw_filled(points, gl::Primitive::TriangleFan);
    }
    last_point = to;
    last_rad = radius;
}

void Context::circle(Vec2f const& v, float r)
{
    glLineWidth(line_width);
    if (log_fp) {
        fprintf(log_fp, "circle center=%s radius=%.1f\n", str(v).c_str(), r);
        fflush(log_fp);
    }
    draw_filled(generate_circle(v, r, false), gl::Primitive::LineLoop);
}

void Context::filled_circle(Vec2f const& v, float r)
{
    if (log_fp) {
        fprintf(log_fp, "filled_circle center=%s radius=%.1f\n", str(v).c_str(),
                r);
        fflush(log_fp);
    }
    draw_filled(generate_circle(v, r, true), gl::Primitive::TriangleFan);
}

void Context::blit(pix::ImageView const& tex, Vec2f pos, Vec2f size)
{
    if (log_fp) {
        auto id = tex.get_tex().tex->tex_id;
        fprintf(log_fp, "draw image=%d top_left=%s size=%s\n", id,
                str(pos).c_str(), str(size).c_str());
        fflush(log_fp);
    }
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

void Context::draw(pix::ImageView const& tex, Vec2f center, Vec2f size,
                   float rot)
{
    if (log_fp) {
        auto id = tex.get_tex().tex->tex_id;
        fprintf(log_fp, "draw image=%d center=%s size=%s rot=%.2f\n", id,
                str(center).c_str(), str(size).c_str(), rot);
        fflush(log_fp);
    }
    tex.bind();
    if (size.x == 0) {
        size = {static_cast<float>(tex.width()),
                static_cast<float>(tex.height())};
    }
    auto vdata = rotated_quad_with_uvs(center, size, rot);
    std::copy(tex.uvs().begin(), tex.uvs().end(), vdata.begin() + 8);
    draw_textured(vdata, gl::Primitive::TriangleFan);
}

Context::Context(Context const& other)
    : fg{other.fg},
      colored{
          ProgramCache::get_instance()
              .get_program<ProgramCache::Colored, ProgramCache::NoTransform>()},
      textured{ProgramCache::get_instance()
                   .get_program<ProgramCache::Textured>()}, // NOLINT
      filled{ProgramCache::get_instance().get_program<>()} // NOLINT
{
    target = other.target;
    view_size = other.view_size;
    offset = other.offset;
    target_size = other.target_size;
    target_scale = other.target_scale;
    // clip_start = other.clip_start;
    // clip_size = other.clip_size;
    vpscale = other.vpscale;

    backface_culling = other.backface_culling;
    line_width = other.line_width;
    point_size = other.point_size;
    blend_source = other.blend_source;
    blend_dest = other.blend_dest;
}

Context::Context(Vec2f _offset, Vec2f _view_size, Vec2f _target_size, GLuint fb)
    : target{fb}, view_size{_view_size}, offset{_offset},
      target_size{_target_size}, fg{color::white},
      colored{
          ProgramCache::get_instance()
              .get_program<ProgramCache::Colored, ProgramCache::NoTransform>()},
      textured{ProgramCache::get_instance()
                   .get_program<ProgramCache::Textured>()}, // NOLINT
      filled{ProgramCache::get_instance().get_program<>()} // NOLINT
{
    // auto in_color = textured->getUniformLocation("in_color");
    // auto in_pos = textured->getAttribute("in_pos");
}

Context::Context(float w, float h, GLuint fb)
    : Context(Vec2f{0, 0}, Vec2f{w, h}, Vec2f{w, h}, fb)
{
    static constexpr std::array<float, 16> mat{1, 0, 0, 0, 0, 1, 0, 0,
                                               0, 0, 1, 0, 0, 0, 0, 1};
    const gl::Color color = 0xffffffff;
    filled->setUniform("frag_color", color);
    filled->setUniform("in_transform", mat);
    textured->setUniform("frag_color", color);
    textured->setUniform("in_transform", mat);
}

template <typename CO>
void Context::draw_filled(const CO& container, gl::Primitive primitive)
{
    set_target();

    filled->use();
    filled->setUniform("frag_color", fg);
    auto pos = filled->getAttribute("in_pos");
    pos.enable();
    gl::ArrayBuffer<GL_STREAM_DRAW> vbo{container};
    vbo.bind();
    gl::vertexAttrib(pos, gl::Size<2>{}, gl::Type::Float, 0 * sizeof(GLfloat),
                     0);
    int len = static_cast<int>(container.size()) / 2;
    gl::drawArrays(primitive, 0, len);
    pos.disable();
}

template <typename CO, typename T>
void Context::draw_indexed(const CO& container, std::vector<T> indices,
                           gl::Primitive primitive)
{
    set_target();

    filled->use();
    filled->setUniform("frag_color", fg);
    auto pos = filled->getAttribute("in_pos");
    pos.enable();
    gl::ArrayBuffer<GL_STREAM_DRAW> vbo{container};
    gl::ElementBuffer<GL_STREAM_DRAW> elements{indices};
    vbo.bind();
    elements.bind();
    gl::vertexAttrib(pos, gl::Size<2>{}, gl::Type::Float, 0 * sizeof(GLfloat),
                     0);
    int len = static_cast<int>(container.size()) / 2;
    // gl::drawArrays(primitive, 0, len);
    gl::drawElements(primitive, indices.size(), gl::Type::UnsignedShort, 0);
    pos.disable();
}

template <typename F, typename I>
void Context::draw_indexed(F const* coords, size_t c_count, I const* indices,
                           size_t i_count, gl::Primitive primitive)
{
    set_target();

    filled->use();
    filled->setUniform("frag_color", fg);
    auto pos = filled->getAttribute("in_pos");
    pos.enable();
    gl::ArrayBuffer<GL_STREAM_DRAW> vbo{coords, c_count};
    gl::ElementBuffer<GL_STREAM_DRAW> elements{indices, i_count};
    vbo.bind();
    elements.bind();
    if constexpr (sizeof(F) == 4) {
        gl::vertexAttrib(pos, gl::Size<2>{}, gl::Type::Float,
                         0 * sizeof(GLfloat), 0);
    } else {
        gl::vertexAttrib(pos, gl::Size<2>{}, gl::Type::Double,
                         0 * sizeof(GLdouble), 0);
    }
    if constexpr (sizeof(I) == 2) {
        gl::drawElements(primitive, i_count, gl::Type::UnsignedShort, 0);
    } else {
        gl::drawElements(primitive, i_count, gl::Type::UnsignedInt, 0);
    }
    pos.disable();
}

bool intersects(Vec2f v11, Vec2f v12, Vec2f v21, Vec2f v22)
{
    // Convert vector 1 to a line (line 1) of infinite length.
    // We want the line in linear equation standard form: A*x + B*y + C = 0
    // See: http://en.wikipedia.org/wiki/Linear_equation
    double const a1 = v12.y - v11.y;
    double const b1 = v11.x - v12.x;
    double const c1 = (v12.x * v11.y) - (v11.x * v12.y);

    // Every point (x,y), that solves the equation above, is on the line,
    // every point that does not solve it, is not. The equation will have a
    // positive result if it is on one side of the line and a negative one
    // if is on the other side of it. We insert (x1,y1) and (x2,y2) of vector
    // 2 into the equation above.
    double d1 = (a1 * v21.x) + (b1 * v21.y) + c1;
    double d2 = (a1 * v22.x) + (b1 * v22.y) + c1;

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
    double const a2 = v22.y - v21.y;
    double const b2 = v21.x - v22.x;
    double const c2 = (v22.x * v21.y) - (v21.x * v22.y);

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
    // if ((a1 * b2) - (a2 * b1) == 0.0f) return COLLINEAR;

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
    return same_side(p, a, b, c) && same_side(p, b, a, c) &&
           same_side(p, c, a, b);
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

    for (size_t i = 0; i < count; i++) {
        auto p = vertices[i];
        if (p != a && p != b && p != c && in_triangle(p, a, b, c)) {
            return false; // Found a point inside the triangle
        }
    }

    return true; // No points inside the triangle and it is convex
}

void Context::draw_complex_polygon(
    std::vector<std::vector<Vec2f>> const& polygons)
{
    auto* tess = tessNewTess(nullptr);
    for (auto const& vec : polygons) {
        tessAddContour(tess, 2, vec.data(), 16, static_cast<int>(vec.size()));
    }

    tessTesselate(tess, TessWindingRule::TESS_WINDING_ODD,
                  TessElementType::TESS_POLYGONS, 3, 2, nullptr);
    auto* verts = tessGetVertices(tess);
    auto* elems = tessGetElements(tess);
    float f[8 * 1024];
    const auto ec = tessGetElementCount(tess) * 3;
    const auto vc = tessGetVertexCount(tess);
    for (int i = 0; i < vc; i++) {
        auto const v = to_screen(verts[i * 2], verts[i * 2 + 1]);
        f[i * 2] = v.x;
        f[i * 2 + 1] = v.y;
    }
    draw_indexed(f, vc * 2, elems, ec, gl::Primitive::Triangles);
    tessDeleteTess(tess);
}

void Context::draw_inconvex_polygon(Vec2f const* points, size_t count)
{
    std::vector<uint16_t> triangles;
    std::vector<uint16_t> indexes;
    indexes.resize(count);
    for (size_t i = 0; i < count; i++) {
        indexes[i] = i;
    }
    std::vector<float> data;
    int removed = 0;
    double sum = 0;

    for (unsigned i = 0; i < count - 1; i++) {
        auto&& q = points[i];
        auto&& p = points[i + 1];
        sum += (p.x - q.x) * (p.y + q.y);
    }
    {
        auto&& q = points[count - 1];
        auto&& p = points[0];
        sum += (p.x - q.x) * (p.y + q.y);
    }

    if (sum > 0) { return; }

    for (unsigned i = 0; i < count; i++) {

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
            // fprintf(stderr, "BROKEN POLYGON\n");
            // for (size_t j = 0; j < indexes.size(); ++j) {
            //     auto&& p = points[indexes[j]];
            //     fprintf(stderr, "X: %.3f Y: %.3f\n", p.x, p.y);
            // }
            // break;
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
    data.resize(count * 2);
    for (unsigned i = 0; i < count; i++) {
        auto&& p = to_screen(points[i]);
        data[(count - i - 1) * 2] = p.x;
        data[(count - i - 1) * 2 + 1] = p.y;
    }

    if (backface_culling) { glEnable(GL_CULL_FACE); }
    draw_filled(data, gl::Primitive::TriangleFan);
    if (backface_culling) { glDisable(GL_CULL_FACE); }
}

void Context::set_target() const
{
    // printf("%f,%f / %f,%f / %f : %d\n", view_size.x, view_size.y,
    // target_size.x, target_size.y, vpscale, target);
    glBindFramebuffer(GL_FRAMEBUFFER, target);
    gl::setViewport({target_size.x * vpscale, target_size.y * vpscale});
    if (offset.x != 0 || view_size != target_size) {
        glEnable(GL_SCISSOR_TEST);
        glScissor(offset.x * vpscale,
                  (target_size.y - offset.y - view_size.y) * vpscale,
                  view_size.x * vpscale, view_size.y * vpscale);
    } else {
        glDisable(GL_SCISSOR_TEST);
    }
    glBlendFunc(blend_source, blend_dest);
}

template <typename CO>
void Context::draw_textured(const CO& container, gl::Primitive primitive)
{
    set_target();

    textured->use();
    textured->setUniform("frag_color", fg);
    auto pos = textured->getAttribute("in_pos");
    pos.enable();
    auto uv = textured->getAttribute("in_uv");
    uv.enable();
    gl::ArrayBuffer<GL_STREAM_DRAW> vbo{container};
    vbo.bind();
    int len = static_cast<int>(container.size()) / 2;
    gl::vertexAttrib(pos, gl::Size<2>{}, gl::Type::Float, 0 * sizeof(GLfloat),
                     0);
    gl::vertexAttrib(uv, gl::Size<2>{}, gl::Type::Float, 0 * sizeof(GLfloat),
                     len * 4);

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

    colored->use();
    auto pos = colored->getAttribute("in_pos");
    auto cola = colored->getAttribute("in_color");
    pos.enable();
    cola.enable();
    gl::ArrayBuffer<GL_STREAM_DRAW> vbo{point_cache};
    vbo.bind();
    gl::vertexAttrib(pos, gl::Size<2>{}, gl::Type::Float, 6 * sizeof(GLfloat),
                     0);
    gl::vertexAttrib(cola, gl::Size<4>{}, gl::Type::Float, 6 * sizeof(GLfloat),
                     8);
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
    auto const width = static_cast<int>(view_size.x);
    auto const height = static_cast<int>(view_size.y);
    if (pixels == nullptr) {
        pixels = std::unique_ptr<uint32_t[]>(new uint32_t[width * height]);
        glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE,
                     pixels.get());
    }
    dirty = true;
    pixels[x + width * (height - y)] = col;
}

void Context::flood_fill(int x, int y, uint32_t col)
{
    col = (col & 0x0000FFFF) << 16 | (col & 0xFFFF0000) >> 16;
    col = (col & 0x00FF00FF) << 8 | (col & 0xFF00FF00) >> 8;

    glBindFramebuffer(GL_FRAMEBUFFER, target);
    auto const width = static_cast<int>(view_size.x);
    auto const height = static_cast<int>(view_size.y);

    if (x < 0 || x >= width || y < 0 || y >= height) { return; }
    if (pixels == nullptr) {
        pixels = std::unique_ptr<uint32_t[]>(new uint32_t[width * height]);
        glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE,
                     pixels.get());
    }

    uint32_t target_color = pixels[x + width * (height - y)];
    if (target_color == col) { return; }

    std::vector<std::pair<int, int>> stack;
    stack.push_back({x, y});

    while (!stack.empty()) {
        auto [px, py] = stack.back();
        stack.pop_back();

        if (px < 0 || px >= width || py < 0 || py >= height) { continue; }

        if (pixels[px + width * (height - py)] != target_color) { continue; }

        pixels[px + width * (height - py)] = col;

        stack.push_back({px + 1, py});
        stack.push_back({px - 1, py});
        stack.push_back({px, py + 1});
        stack.push_back({px, py - 1});
    }

    dirty = true;
    flush_pixels();
}

pix::ImageView Context::to_image() const
{
    glBindFramebuffer(GL_FRAMEBUFFER, target);
    auto const width = static_cast<int>(view_size.x);
    auto const height = static_cast<int>(view_size.y);
    auto temp = std::unique_ptr<uint32_t[]>(new uint32_t[width * height]);
    int x = offset.x;
    int y = offset.y;
    // TODO: Read correct rectangle
    glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, temp.get());
    auto tex = std::make_shared<gl::Texture>(width, height, temp.get());
    return pix::ImageView{gl::TexRef{tex}};
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
        auto tex = std::make_shared<gl::Texture>(width, height, pixels.get());
        auto oldfg = fg;
        fg = 0xffffffff;
        blit(pix::ImageView{gl::TexRef{tex}}, {0, 0}, view_size);
        fg = oldfg;
        dirty = false;
        pixels = nullptr;
    }
}

} // namespace pix
