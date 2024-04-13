#pragma once
#include "buffer.hpp"
#include "functions.hpp"
#include "gl.hpp"
#include "program_cache.hpp"

#include <array>
#include <cmath>
#include <memory>
#include <vector>

namespace gl {

struct Texture
{
    GLuint tex_id = 0;
    GLuint fb_id = 0;
    GLuint width = 0;
    GLuint height = 0;
    GLint format = GL_RGBA;

    Texture() = default;

    void init()
    {
        // fmt::print("Created {}x{} = {}\n", width, height, (void*)this);
        glGenTextures(1, &tex_id);
        glBindTexture(GL_TEXTURE_2D, tex_id);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    }

    void set_filter(bool min, bool max)
    {
        glBindTexture(GL_TEXTURE_2D, tex_id);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, min ? GL_LINEAR : GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, max ? GL_LINEAR : GL_NEAREST);
    }

    template <typename T, size_t N>
    Texture(GLint w, GLint h, std::array<T, N> const& data,
            GLint target_format = GL_RGBA, GLint source_format = -1,
            GLenum type = GL_UNSIGNED_BYTE)
        : width(w), height(h), format(target_format)
    {
        if (source_format < 0) {
            constexpr static std::array translate{0, GL_ALPHA, 0, GL_RGB,
                                                  GL_RGBA};
            source_format = translate[sizeof(T)];
        }
        init();
        glTexImage2D(GL_TEXTURE_2D, 0, target_format, w, h, 0,
                     // Defines how many of the underlying elements form a pixel
                     source_format,
                     // Underlying type in array
                     type, data.data());
        gl_check("glTexImage2D");
    }

    template <typename T>
    Texture(GLint w, GLint h, std::vector<T> const& data,
            GLint target_format = GL_RGBA, GLint source_format = -1,
            GLenum type = GL_UNSIGNED_BYTE)
        : width(w), height(h), format(target_format)
    {
        if (source_format < 0) {
            constexpr static std::array translate{0, GL_ALPHA, 0, GL_RGB,
                                                  GL_RGBA};
            source_format = translate[sizeof(T)];
        }
        init();
        glTexImage2D(GL_TEXTURE_2D, 0, target_format, w, h, 0,
                     // Defines how many of the underlying elements form a pixel
                     source_format,
                     // Underlying type in array
                     type, data.data());
        gl_check("glTexImage2D");
    }

    template <typename T>
    Texture(GLint w, GLint h, T const* data, GLint target_format = GL_RGBA,
            GLint source_format = -1, GLenum type = GL_UNSIGNED_BYTE)
        : width(w), height(h), format(target_format)
    {
        init();
        if (source_format < 0) {
            constexpr static std::array translate{0, GL_ALPHA, 0, GL_RGB,
                                                  GL_RGBA};
            source_format = translate[sizeof(T)];
        }
        glTexImage2D(GL_TEXTURE_2D, 0, target_format, w, h, 0,
                     // Defines how many of the underlying elements form a pixel
                     source_format,
                     // Underlying type in array
                     type, data);
    }

    Texture(GLint w, GLint h) : width(w), height(h)
    {
        init();
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, nullptr);
    }

    void fill(uint32_t col)
    {
        auto old = fb_id;
        set_target();
        clearColor({col});
        glClear(GL_COLOR_BUFFER_BIT);
        if (old == 0) { untarget(); }
    }

    void untarget()
    {
        glDeleteFramebuffers(1, &fb_id);
        fb_id = 0;
    }

    void move_from(Texture&& other) noexcept
    {
        tex_id = other.tex_id;
        fb_id = other.fb_id;
        width = other.width;
        height = other.height;
        other.tex_id = 0;
        other.fb_id = 0;
    }

    Texture(Texture const&) = delete;
    Texture(Texture&& other) noexcept { move_from(std::move(other)); }

    ~Texture()
    {

        if (tex_id != 0) { glDeleteTextures(1, &tex_id); }
        if (fb_id != 0) { glDeleteFramebuffers(1, &fb_id); }
    };

    Texture& operator=(Texture const&) = delete;

    Texture& operator=(Texture&& other) noexcept
    {
        move_from(std::move(other));
        return *this;
    }

    void bind(int unit = 0) const
    {
        glActiveTexture(GL_TEXTURE0 + unit);
        glBindTexture(GL_TEXTURE_2D, tex_id);
    }

    void set_target()
    {
        if(!alloc_framebuffer()) {
            glBindFramebuffer(GL_FRAMEBUFFER, fb_id);
        }
        setViewport({width, height});
    }

    GLuint get_target()
    {
        alloc_framebuffer();
        return fb_id;
    }

    bool alloc_framebuffer()
    {
        if (fb_id == 0) {
            glBindTexture(GL_TEXTURE_2D, tex_id);
            glGenFramebuffers(1, &fb_id);
            glBindFramebuffer(GL_FRAMEBUFFER, fb_id);
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                                   GL_TEXTURE_2D, tex_id, 0);
            gl_check("glFrameBufferTexture2d");
            return true;
        }
        return false;
    }

    std::vector<std::byte> read_pixels(int x = 0, int y = 0, int w = -1,
                                       int h = -1)
    {
        if (w < 0) { w = width; }
        if (h < 0) { h = height; }

        set_target();
        std::vector<std::byte> data(width * height * 4);
        auto type = GL_UNSIGNED_BYTE;
        glReadPixels(x, height - y - h, w, h, format, type, data.data());
        gl_check("glReadPixels");
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        return data;
    }

    template <typename T>
    void update(T const* ptr, GLint source_format = -1,
                GLenum type = GL_UNSIGNED_BYTE) const
    {
        if (source_format < 0) {
            constexpr static std::array translate{0, GL_ALPHA, 0, GL_RGB,
                                                  GL_RGBA};
            source_format = translate[sizeof(T)];
        }
        glBindTexture(GL_TEXTURE_2D, tex_id);
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, width, height, source_format,
                        type, ptr);
    }

    template <typename T>
    void update(int x, int y, int w, int h, T const* ptr,
                GLint source_format = -1, GLenum type = GL_UNSIGNED_BYTE) const
    {
        if (source_format < 0) {
            constexpr static std::array translate{0, GL_ALPHA, 0, GL_RGB,
                                                  GL_RGBA};
            source_format = translate[sizeof(T)];
        }
        glBindTexture(GL_TEXTURE_2D, tex_id);
        glTexSubImage2D(GL_TEXTURE_2D, 0, x, y, w, h, source_format, type, ptr);
    }

    std::pair<float, float> size() const
    {
        return {static_cast<float>(width), (float)height};
    }
};

struct TexRef
{
    std::shared_ptr<void> data;
    std::shared_ptr<Texture> tex;

private:
    std::array<float, 8> _uvs{0.F, 1.F, 1.F, 1.F, 1.F, 0.F, 0.F, 0.F};

public:
    // Constructors
    TexRef() = default;
    TexRef(int w, int h) : tex{std::make_shared<Texture>(w, h)} {}
    explicit TexRef(std::pair<int, int> size)
        : tex{std::make_shared<Texture>(size.first, size.second)}
    {
    }
    explicit TexRef(std::shared_ptr<Texture> const& t) : tex(t) {}
    TexRef(std::shared_ptr<Texture> const& t, std::array<float, 8> const& u)
        : tex(t), _uvs(u)
    {
    }

    void set_texture_filter(bool min, bool max)
    {
        tex->set_filter(min, max);
    }

    const auto& uvs() const { return _uvs; }

    void bind(int unit = 0) const { tex->bind(unit); }
    bool operator==(TexRef const& other) const { return tex == other.tex; }
    std::vector<std::byte> read_pixels() const
    {
        return tex->read_pixels(x(), y(), width(), height());
    };

    operator bool() const { return tex != nullptr; }

    void copy_from(gl::TexRef const& src) const
    {
        using gl::ProgramCache;
        GLint fb = 0;
        glGetIntegerv(GL_FRAMEBUFFER_BINDING, &fb);
        auto old = gl::getViewport();
        set_target();
        src.bind();
        float dx = 0;
        float dy = 0;
        // Transform UVs to clip space
        auto x0 = _uvs[0] * 2.0F - 1.0F;
        auto y0 = (_uvs[1] + dy) * 2.0F - 1.0F;
        auto x1 = _uvs[4] * 2.0F - 1.0F;
        auto y1 = (_uvs[5] + dy) * 2.0F - 1.0F;

        std::array vertexData{x0,  y0,  x1,  y0,  x1,  y1,  x0,  y1,
                              0.F, 1.F, 1.F, 1.F, 1.F, 0.F, 0.F, 0.F};
        std::copy(src._uvs.begin(), src._uvs.end(), vertexData.begin() + 8);
        gl::ArrayBuffer<GL_STREAM_DRAW> vbo{vertexData};

        // TODO: It might be better to let Texture have its own program
        //       then to depend on ProgramCache.
        auto& program = ProgramCache::get_instance()
                            .get_program<ProgramCache::Textured,
                                         ProgramCache::NoTransform>();
        vbo.bind();
        program.use();
        auto pos = program.getAttribute("in_pos");
        auto uv = program.getAttribute("in_uv");
        pos.enable();
        uv.enable();
        gl::vertexAttrib(pos, 2, gl::Type::Float, 0 * sizeof(GLfloat),
                              0);
        gl::vertexAttrib(uv, 2, gl::Type::Float, 0 * sizeof(GLfloat),
                              8 * 4);
        gl::drawArrays(gl::Primitive::TriangleFan, 0, 4);
        pos.disable();
        uv.disable();
        glBindFramebuffer(GL_FRAMEBUFFER, fb);
        gl::setViewport(old);
    }

    void set_target() const { tex->set_target(); }

    GLuint get_target() const { return tex->get_target(); }

    void copy_to(TexRef const& target) const { target.copy_from(*this); }

    float ytou(double yy) const
    {
        return static_cast<float>(1.0 - yy / tex->height);
    }
    float xtov(double xx) const { return static_cast<float>(xx / tex->width); }

    TexRef crop(double x, double y, double w, double h) const
    {
        float u0 = xtov(this->x() + x);
        float v0 = ytou(this->y() + y);
        float u1 = u0 + static_cast<float>(w / tex->width);
        float v1 = v0 - static_cast<float>(h / tex->height);
        // printf("%f %f %f %f => %f %f %f %f\n", x, y, w, h, u0, v0, u1, v1);
        return {tex, std::array{u0, v0, u1, v0, u1, v1, u0, v1}};
    }

    std::vector<TexRef> split(int w, int h)
    {
        float u0 = _uvs[0];
        float v0 = _uvs[1];
        float u1 = _uvs[4];
        float v1 = _uvs[5];
        auto du = (u1 - u0) / static_cast<float>(w);
        auto dv = (v1 - v0) / static_cast<float>(h);

        std::vector<TexRef> images;

        float u = u0;
        float v = v0;
        int x = 0;
        int y = 0;
        while (true) {
            if (x == w) {
                u = u0;
                v += dv;
                x = 0;
                y++;
            }
            if (y == h) { break; }
            images.emplace_back(
                tex, std::array{u, v, u + du, v, u + du, v + dv, u, v + dv});

            u += du;
            x++;
        }
        return images;
    }

    void yflip()
    {
        auto y0 = _uvs[1];
        auto y1 = _uvs[5];
        _uvs[1] = _uvs[3] = y1;
        _uvs[5] = _uvs[7] = y0;
    }

    double width() const
    {
        return static_cast<double>(tex->width) * (_uvs[4] - _uvs[0]);
    }

    double height() const
    {
        return std::abs(static_cast<double>(tex->height) * (_uvs[5] - _uvs[1]));
    }
    double x() const { return static_cast<double>(tex->width) * _uvs[0]; }
    double y() const
    {
        auto uy = 1.0F - _uvs[1];
        return static_cast<double>(tex->height) * uy;
    }
};

} // namespace gl_wrap
