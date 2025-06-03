#pragma once

#include "gl/texture.hpp"

#include "context.hpp"
#include <iterator>

namespace pix {

class ImageView : public Context
{
    gl::TexRef tex;

public:
    gl::TexRef& get_tex() { return tex; }
    gl::TexRef const& get_tex() const { return tex; }

    explicit ImageView(gl::TexRef const& tr) : Context{tr}, tex{tr} {}
    ImageView(int w, int h) : ImageView{gl::TexRef(w, h)} {}
    ImageView() : ImageView{gl::TexRef()} {}

    void bind() const { tex.bind(); }

    const auto& uvs() const { return tex.uvs(); }

    void set_texture_filter(bool min, bool max) { tex.set_texture_filter(min, max); }
    void copy_from(ImageView const& src) const { tex.copy_from(src.tex); }
    void copy_to(ImageView const& target) const { target.copy_from(*this); }
    double width() const { return tex.width(); }
    double height() const { return tex.height(); }
    double y() const { return tex.y(); }
    double x() const { return tex.x(); }

    ImageView crop(double x, double y, double w, double h) const
    {
        return ImageView{tex.crop(x, y, w, h)};
    }

    std::vector<ImageView> split(int w, int h)
    {
        auto res = tex.split(w, h);
        std::vector<ImageView> res2;
        std::transform(res.begin(), res.end(), std::back_inserter(res2),
                       [](gl::TexRef const& t) { return ImageView{t}; });
        return res2;
    }
};

} // namespace pix
