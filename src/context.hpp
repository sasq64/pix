#pragma once

#include "gl/color.hpp"
#include "gl/functions.hpp"
#include "gl/program.hpp"
#include "gl/texture.hpp"

#include "vec2.hpp"

#include <filesystem>
namespace fs = std::filesystem;

namespace pix {

class ImageView;

class Context
{
    // The GL target frame buffer
    GLuint target = 0;

protected:
    FILE* log_fp = nullptr;

public:
    void log_to(fs::path const& target)
    {
        if (log_fp) fclose(log_fp);
        log_fp = fopen(target.c_str(), "w");
    }

    // The size of our view into the framebuffer
    Vec2f view_size{0, 0};

    // The XY offset of our view into the framebuffer
    Vec2f offset{0, 0};
    // Actual size of framebuffer or texture
    // Used to set correcct viewport transformation
    Vec2f target_size;

    Vec2f target_scale{1, 1};

    // Clip (scissor) area
    // Vec2i clip_start{0, 0};
    // Vec2i clip_size{0, 0};

    // Viewport scale (for when window size != framebuffer size)
    float vpscale = 1.0F;

    mutable bool dirty = false;

    bool backface_culling = true;

    std::unique_ptr<uint32_t[]> pixels; // NOLINT

    float line_width = 1;
    float point_size = 2;
    gl::Color fg;
    unsigned blend_source = GL_SRC_ALPHA;
    unsigned blend_dest = GL_ONE_MINUS_SRC_ALPHA;

    std::vector<float> point_cache;

private:
    Vec2f last_point{0, 0};
    float last_rad = -1.0F;

    gl::Program& colored;
    gl::Program& textured;
    gl::Program& filled;

    template <typename CO>
    void draw_filled(CO const& container, gl::Primitive primitive);

    template <typename CO, typename T>
    void draw_indexed(CO const& container, std::vector<T> indices,
                      gl::Primitive primitive);

    template <typename F, typename I>
    void draw_indexed(F const* coords, size_t c_count, I const* indices,
                      size_t i_count, gl::Primitive primitive);

    std::vector<float> generate_circle(Vec2f center, float radius,
                                       bool include_center = true) const;
    std::array<float, 4> generate_line(Vec2f from, Vec2f to) const;
    std::vector<float> generate_lines(float const* screen_cords,
                                      int count) const;
    std::vector<float> generate_line(Vec2f p0, float r0, Vec2f p1,
                                     float r1) const;
    std::array<float, 8> generate_quad(Vec2f top_left, Vec2f size) const;
    std::array<float, 8> rotated_quad(Vec2f center, Vec2f sz, float rot) const;
    std::array<float, 16> rotated_quad_with_uvs(Vec2f center, Vec2f sz,
                                                float rot) const;

    void draw_points();

public:
    std::array<float, 16> generate_quad_with_uvs(Vec2f pos, Vec2f size) const;

    template <typename CO>
    void draw_textured(CO const& container, gl::Primitive primitive);

    constexpr Vec2<float> to_screen(Vec2f const& v) const
    {
        auto const res =
            (v * target_scale + offset) * Vec2f{2, -2} / target_size +
            Vec2f{-1, 1};
        return {static_cast<float>(res.x), static_cast<float>(res.y)};
    }

    template <typename F> constexpr Vec2<float> to_screen(F x, F y) const
    {
        return to_screen(Vec2f{static_cast<float>(x), static_cast<float>(y)});
    }

    Context(Context const& other);
    Context(float w, float h, GLuint fb = 0);
    Context(Vec2f _offset, Vec2f _view_size, Vec2f _target_size, GLuint fb = 0);

    Context(gl::TexRef const& tr)
        : Context{
              {static_cast<float>(tr.x()), static_cast<float>(tr.y())},
              {static_cast<float>(tr.width()), static_cast<float>(tr.height())},
              {static_cast<float>(tr.tex->width),
               static_cast<float>(tr.tex->height)},
              tr.get_target()}
    {
    }

    void begin_lines() { last_rad = -1; }

    std::shared_ptr<Context> copy()
    {
        return std::make_shared<Context>(*this);
    };

    Vec2f screen_size() const { return target_size; }

    void set_target() const;

    void resize(Vec2f size, float scale)
    {
        view_size = size;
        target_size = size;
        vpscale = scale;
    }
    void set_pixel(int x, int y, uint32_t col);
    void flood_fill(int x, int y, uint32_t col);

    void flush_pixels();

    void set_color(gl::Color const& col);
    void set_blend_mode(uint32_t mode);

    void circle(Vec2f const& v, float r);
    void filled_circle(Vec2f const& v, float r);
    void line(Vec2f from, Vec2f to);
    void line(Vec2f to);
    void lines(std::vector<Vec2f> const& points);
    void round_line(Vec2f from, float rad_from, Vec2f to, float rad_to);
    void round_line(Vec2f to, float radius);
    void filled_rect(Vec2f top_left, Vec2f size);
    void rect(Vec2f top_left, Vec2f size);
    void blit(pix::ImageView const& tex, Vec2f pos = {0, 0},
              Vec2f size = {0, 0});
    void draw(pix::ImageView const& tex, Vec2f center, Vec2f size, float rot);

    void plot(Vec2f point, gl::Color col);
    void flush();

    void clear(gl::Color const& col) const;
    void draw_polygon(const Vec2f* points, size_t count);
    void draw_inconvex_polygon(const Vec2f* points, size_t count);
    void draw_complex_polygon(std::vector<std::vector<Vec2f>> const& points);
    pix::ImageView to_image() const;
};

bool intersects(Vec2f v11, Vec2f v12, Vec2f v21, Vec2f v22);

} // namespace pix
