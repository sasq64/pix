#pragma once
#include "context.hpp"
#include "system.hpp"

namespace pix {

    class Screen : public Context
    {
        std::shared_ptr<Display> display;
    public:
        bool visible;
        explicit Screen(std::shared_ptr<Display> const& d) : Context(d->get_size().first, d->get_size().second, 0), display{d} {}

        void swap() { display->swap(); }
        void set_fps(int fps) { display->set_fps(fps); }
        [[nodiscard]] Display::Time get_time() const { return display->get_time(); }
        void set_target(){ display->set_target(); }
        float get_scale() const { return display->get_scale(); }
        [[nodiscard]] std::pair<int, int> get_size() const { return display->get_size(); }

        void set_size(Vec2i new_size) {
            display->set_size(new_size.x, new_size.y);
        }
        void set_visible(bool on) {
            display->set_visible(on);
            visible = on;
        }
    };
}
