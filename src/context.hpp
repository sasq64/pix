#pragma once

#include "colors.hpp"
#include "gl/buffer.hpp"
#include "gl/color.hpp"
#include "gl/functions.hpp"
#include "gl/program.hpp"
#include "gl/program_cache.hpp"
#include "gl/texture.hpp"

#include "vec2.hpp"

namespace pix {

class Context
{
    // The GL target frame buffer
    GLuint target = 0;

    // The XY offset of our view into the framebuffer
    Vec2f offset{0, 0};
    // The size of our view into the framebuffer
    Vec2f view_size{0, 0};
public:
    // Actual size of framebuffer
    Vec2f target_size;

    // Clip (scissor) area
    Vec2i clip_start{0,0};
    Vec2i clip_size{0,0};

    std::shared_ptr<gl_wrap::Texture> texture;

    // Viewport scale (for when window size != framebuffer size)
    float vpscale = 1.0F;

    mutable bool dirty = false;

    std::unique_ptr<uint32_t[]> pixels; // NOLINT

    float line_width = 1;
    float point_size = 2;
    gl_wrap::Color fg;

    std::vector<float> points;

private:
    Vec2f last_point{0,0};

    gl_wrap::Program& colored;
    gl_wrap::Program& textured;
    gl_wrap::Program& filled;

    template <typename CO>
    void draw_filled(CO const& container, gl_wrap::Primitive primitive);

    template <typename CO>
    void draw_textured(CO const& container, gl_wrap::Primitive primitive);

    std::vector<float> generate_circle(Vec2f center, float radius,
                                       bool include_center = true) const;
    std::array<float, 4> generate_line(Vec2f from, Vec2f to) const;
    std::vector<float> generate_lines(float const* screen_cords, int count) const;
    std::array<float, 8> generate_quad(Vec2f top_left, Vec2f size) const;
    std::array<float, 8> rotated_quad(Vec2f center, Vec2f sz, float rot) const;
    std::array<float, 16> generate_quad_with_uvs(Vec2f pos, Vec2f size) const;

    std::array<float, 16> rotated_quad_with_uvs(Vec2f center, Vec2f sz,
                                                float rot) const;

    void draw_points();

public:
    constexpr Vec2<float> to_screen(Vec2f const& v) const
    {
        auto res = (v + offset) * Vec2f{2, -2} / target_size + Vec2f{-1, 1};
        return {static_cast<float>(res.x), static_cast<float>(res.y)};
    }

    constexpr Vec2<float> to_screen(float x, float y) const
    {
        return to_screen(Vec2f{x, y});
    }

    Context(float w, float h, GLuint fb = 0);
    Context(Vec2f _offset, Vec2f _view_size, Vec2f _target_size, GLuint fb = 0);

    Vec2f screen_size() const { return target_size; }

    void set_target() const;

    void resize(Vec2f size, float scale)
    {
        target_size = size;
        vpscale = scale;
    }
    void set_pixel(int x, int y, uint32_t col);

    void flush_pixels();


    void set_color(gl_wrap::Color const& col);

    void circle(Vec2f const& v, float r);
    void filled_circle(Vec2f const& v, float r);
    void line(Vec2f from, Vec2f to);
    void line(Vec2f to);
    void filled_rect(Vec2f top_left, Vec2f size);
    void rect(Vec2f top_left, Vec2f size);
    void blit(gl_wrap::TexRef const& tex, Vec2f pos, Vec2f size);
    void draw(gl_wrap::TexRef const& tex, Vec2f center, Vec2f size, float rot);

    void plot(Vec2f point, gl_wrap::Color col);
    void flush();


    void clear(gl_wrap::Color const& col) const;
    void draw_polygon(const Vec2f* points, size_t count);
};
} // namespace pix
