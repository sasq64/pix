cmake_minimum_required(VERSION 3.12)
set(CMAKE_OSX_DEPLOYMENT_TARGET "10.15" CACHE STRING "Minimum OS X deployment version")
project(pix VERSION 1.0)
if(POLICY CMP0135)
  cmake_policy(SET CMP0135 NEW)
endif()

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if (EXISTS /opt/vc)
    set(RASPBERRY_PI 1)
endif ()

set(FT_REQUIRE_ZLIB OFF)
set(FT_REQUIRE_BZIP2 OFF)
set(FT_REQUIRE_PNG OFF)
set(FT_REQUIRE_HARFBUZZ OFF)
set(FT_REQUIRE_BROTLI OFF)

set(FT_DISABLE_ZLIB ON CACHE BOOL "")
set(FT_DISABLE_BZIP2 ON CACHE BOOL "")
set(FT_DISABLE_PNG ON CACHE BOOL "")
set(FT_DISABLE_HARFBUZZ ON CACHE BOOL "")
set(FT_DISABLE_BROTLI ON CACHE BOOL "")
set(FT_DISABLE_ZLIB ON CACHE BOOL "")
set(FT_DISABLE_BZIP2 ON CACHE BOOL "")
set(FT_DISABLE_PNG ON CACHE BOOL "")
set(FT_DISABLE_HARFBUZZ ON CACHE BOOL "")
set(FT_DISABLE_BROTLI ON CACHE BOOL "")

if (NOT RASPBERRY_PI)
  set(GLFW_BUILD_DOCS OFF CACHE BOOL "")
   add_subdirectory(external/glfw EXCLUDE_FROM_ALL)
endif()

add_subdirectory(external/freetype EXCLUDE_FROM_ALL)

#FetchContent_MakeAvailable(glfw freetype)
add_library(Freetype::Freetype ALIAS freetype)

set(CMAKE_EXPORT_COMPILE_COMMANDS 1)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address -g")

cmake_policy(SET CMP0072 NEW)

# System wide directories and flags

if (RASPBERRY_PI)
    set(VC /opt/vc)
    include_directories(SYSTEM
        ${VC}/include
        ${VC}/include/interface/vcos/pthreads
        ${VC}/include/interface/vmcs_host/linux)
    link_directories(${VC}/lib)
    add_compile_options(-Wno-psabi)
    add_compile_definitions(RASPBERRY_PI)
endif ()

if (WIN32)
    add_compile_options(/utf-8)
    add_definitions(/D_CRT_SECURE_NO_WARNINGS /D_USE_MATH_DEFINES
        /D_SILENCE_CXX17_ITERATOR_BASE_CLASS_DEPRECATION_WARNING)
endif ()

if (APPLE)
    include_directories(SYSTEM /usr/local/include /opt/homebrew/include)
    link_directories(/usr/local/lib /opt/homebrew/lib)
    #add_compile_options(-target x86_64-apple-macos10.15)
endif ()

if (CMAKE_CXX_COMPILER MATCHES "/em\\+\\+(-[a-zA-Z0-9.])?$")
    message(" * Emscripten")
    set(CMAKE_CXX_COMPILER_ID "Emscripten")
    set(EMSCRIPTEN 1)
else ()
    message(" * ${CMAKE_CXX_COMPILER_ID}")
endif ()

# Warning level setup #######################################################

# GCC/Clang common warnings
set(GCC_CLANG_WARNINGS
    -Werror
    -Wall
    -Wextra
    -Wnon-virtual-dtor
    -pedantic
    -Wno-psabi
    -Wno-unused-variable
    -Wno-unused-parameter
    -Wno-unused-function)

set(MSVC_WARNINGS /W2 /wd4244)

# GCC specific warnings
set(GCC_WARNINGS -Wno-duplicated-branches -Wduplicated-cond -Wlogical-op
    -Wno-error=stringop-overflow
    -Wno-missing-field-initializers)

if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    set(WARNINGS ${WARNINGS} ${GCC_WARNINGS} ${GCC_CLANG_WARNINGS})
elseif (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    set(WARNINGS ${WARNINGS} ${CLANG_WARNINGS} ${GCC_CLANG_WARNINGS})
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC")
    set(WARNINGS ${WARNINGS} ${MSVC_WARNINGS})
endif ()

add_library(Warnings INTERFACE)
target_compile_options(Warnings INTERFACE ${WARNINGS})

add_library(Extra INTERFACE)

if (RASPBERRY_PI)

    include(FindFreetype)
    find_package(Freetype REQUIRED)
    find_package(OpenGL)

    target_link_libraries(Extra INTERFACE stdc++fs asound)

    add_library(Graphics OBJECT src/eglutil.cpp)
    target_link_libraries(Graphics INTERFACE vcos vchiq_arm bcm_host GLESv2 EGL)
    target_compile_definitions(Graphics INTERFACE USE_GLES NO_GLCHECK)

elseif (EMSCRIPTEN)

    add_library(_freetype INTERFACE)
    target_compile_options(_freetype INTERFACE -sUSE_FREETYPE=1)
    target_link_options(_freetype INTERFACE -sUSE_FREETYPE=1)
    add_library(Freetype::Freetype ALIAS _freetype)

    add_library(Graphics INTERFACE)
    target_link_options(Graphics INTERFACE "-sUSE_SDL=2")
    target_compile_options(Graphics INTERFACE "-sUSE_SDL=2")
    target_compile_definitions(Graphics INTERFACE USE_GLES)

elseif (WIN32)

    find_package(OpenGL)
    add_library(Graphics INTERFACE)
    target_link_libraries(Graphics INTERFACE OpenGL::GL glfw)

else ()

    find_package(OpenGL)
    add_library(Graphics INTERFACE)
    target_link_libraries(Graphics INTERFACE OpenGL::GL glfw)

endif ()

find_package(Threads REQUIRED)

if (RASPBERRY_PI)
    set(SYSTEM src/pi_system.cpp)
else ()
    set(SYSTEM src/glfw_system.cpp)
endif ()


set(PIX src/)
add_library(pix STATIC
    ${SYSTEM}
    ${PIX}/image.cpp
    ${PIX}/font.cpp
    ${PIX}/context.cpp
    ${PIX}/pixel_console.cpp
    ${PIX}/full_console.cpp
    ${PIX}/tile_set.cpp
    external/lodepng/lodepng.cpp)
target_include_directories(pix PRIVATE external/lodepng external/earcut PUBLIC src)
target_compile_options(pix PUBLIC -fvisibility=hidden)
target_link_libraries(pix PRIVATE Warnings PUBLIC
    Threads::Threads
    Graphics
    Freetype::Freetype)

add_library(pix::pix ALIAS pix)

add_executable(pixtest src/test.cpp)
target_link_libraries(pixtest PRIVATE pix::pix)

if (PYTHON_MODULE)
    add_subdirectory(external/pybind11)
    pybind11_add_module(_pixpy src/python.cpp)
    target_link_libraries(_pixpy PUBLIC Warnings pix Extra)
    install(TARGETS _pixpy DESTINATION .)
endif()
