#pragma once

#include "gl/buffer.hpp"
#include "gl/program_cache.hpp"
#include "gl/texture.hpp"

#include "context.hpp"

namespace pix {

class ImageView : public Context
{
    gl::TexRef tex;
public:
    gl::TexRef& get_tex() { return tex; }
    explicit ImageView(gl::TexRef const& tr) :
        Context(
        {static_cast<float>(tr.x()), static_cast<float>(tr.y())},
        {static_cast<float>(tr.width()), static_cast<float>(tr.height())},
        {static_cast<float>(tr.tex->width), static_cast<float>(tr.tex->height)},
        tr.get_target()), tex{tr} {}

    void set_texture_filter(bool min, bool max) {
        tex.set_texture_filter(min, max);
    }
    void copy_from(ImageView const& src) const {
        tex.copy_from(src.tex);
    }
    void copy_to(ImageView const& target) const { target.copy_from(*this); }
    double width() const { return tex.width(); }
    double height() const { return tex.height(); }
    double y() const { return tex.y(); }
    double x() const { return tex.x(); }

    ImageView crop(double x, double y, double w, double h) const { return ImageView{tex.crop(x,y,w,h) };}

    std::vector<ImageView> split(int w, int h) {
        auto res = tex.split(w, h);
        std::vector<ImageView> res2(res.size());
        std::transform(res.begin(), res.end(), res2.begin(), [](auto const& t) { return {t}; });
        return res2;
    }

};

}
