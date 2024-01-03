#pragma once

#ifdef USE_GLES
#include <GLES/gl.h>
#include <GLES2/gl2.h>
#else
#include "glad.h"
#endif
#include <cstdint>
#include <type_traits>

namespace gl {

template <typename T>
constexpr typename std::enable_if_t<std::is_enum_v<T>, GLint> to_glenum(T f)
{
    return static_cast<GLint>(f);
}


template <typename T>
constexpr typename std::enable_if_t<std::is_arithmetic_v<T>, GLint> to_glint(T f)
{
    return static_cast<GLint>(f);
}

} // namespace gl_wrap
