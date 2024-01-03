
#pragma once
#include "functions.hpp"
#include "gl.hpp"
#include "program.hpp"

#include <cassert>
#include <memory>
#include <string>
#include <string_view>

namespace gl {

struct ProgramCache
{
    std::string vertex_shader{R"gl(
    #ifdef GL_ES
        precision mediump float;
    #endif
        attribute vec2 in_pos;
        uniform mat4 in_transform;
#ifdef COLORED
       attribute vec4 in_color;
       varying vec4 frag_color;
#endif
        #ifdef TEXTURED
          attribute vec2 in_uv;
          varying vec2 out_uv;
        #endif
        void main() {
#ifdef COLORED
  frag_color = in_color;
#endif
#ifdef NO_TRANSFORM
            gl_Position = vec4(in_pos.x, in_pos.y, 0, 1);
#else
            vec4 v = in_transform * vec4(in_pos, 0, 1);
            gl_Position = vec4( v.x, v.y, 0, 1 );
#endif
            #ifdef TEXTURED
              out_uv = in_uv;
            #endif
        })gl"};

    std::string fragment_shader{R"gl(
    #ifdef GL_ES
        precision mediump float;
    #endif
    #ifdef COLORED
        varying vec4 frag_color;
    #else
        uniform vec4 frag_color;
    #endif
        #ifdef TEXTURED
          uniform sampler2D in_tex;
          varying vec2 out_uv;
        #endif
        void main() {
            #ifdef TEXTURED
#ifdef NO_TRANSFORM
              gl_FragColor = texture2D(in_tex, out_uv);
#else
              gl_FragColor = texture2D(in_tex, out_uv) * frag_color;
#endif
            #else
              gl_FragColor = frag_color;
            #endif
        })gl"};

    // #ifdef EMSCRIPTEN
    //     static const inline std::string version = "#version 150 es\n";
    // #else
    static const inline std::string version;
    // #endif

    Program get_program(std::string_view prefix) const
    {
        // printf("PREFIX: '%s'\n", std::string(prefix).c_str());
        using namespace std::string_literals;
        Shader<ShaderType::Vertex> vs{version + std::string(prefix) +
                                      vertex_shader};
        if (!vs) {
            // Get info log
            auto info = getShaderInfoLog(vs.shader);
            fprintf(stderr, "%s\n", info.c_str());
            throw gl_exception("Could not compile vertex shader");
        }
        Shader<ShaderType::Fragment> fs{version + std::string(prefix) +
                                        fragment_shader};
        if (!fs) {
            // Get info log
            auto info = getShaderInfoLog(fs.shader);
            fprintf(stderr, "%s\n", info.c_str());
            throw gl_exception("Could not compile shaders");
        }
        return {vs, fs};
    }

    struct Colored
    {
        static inline std::string code = "#define COLORED\n";
    };
    struct Textured
    {
        static inline std::string code = "#define TEXTURED\n";
    };
    struct NoTransform
    {
        static inline std::string code = "#define NO_TRANSFORM\n";
    };

    template <typename... FLAGS> struct ProgramHolder
    {
        static inline Program cached;
    };

    template <typename... ARGS> std::string join(ARGS... args)
    {
        return (args + ... + "");
    }

    template <typename... ARGS> Program& get_program()
    {
        auto& program = ProgramHolder<ARGS...>::cached;
        if (!program) { program = get_program(join(ARGS::code...)); }
        return program;
    }

    ProgramCache() = default;

    static inline std::unique_ptr<ProgramCache> pc;
    static void destroy_instance() { pc = nullptr; }

    static ProgramCache& get_instance()
    {
        if (pc == nullptr) { pc = std::make_unique<ProgramCache>(); }
        return *pc;
    }
};

} // namespace gl_wrap
