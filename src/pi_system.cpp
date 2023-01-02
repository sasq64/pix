#include "keycodes.h"
#include "system.hpp"

#include <EGL/egl.h>
#include <GLES2/gl2.h>
#include <bcm_host.h>
#include <cctype>
#include <chrono>
#include <deque>
#include <fcntl.h>
#include <filesystem>
#include <linux/input.h>
#include <unordered_map>
#include <vector>

using namespace std::chrono_literals;
namespace fs = std::filesystem;

using std::chrono::duration_cast;

class display_exception : public std::exception
{
public:
    explicit display_exception(const std::string& msg) : msg(msg) {}
    const char* what() const noexcept override { return msg.c_str(); }

private:
    std::string msg;
};

/*constexpr */ bool test_bit(const std::vector<uint8_t>& v, int n)
{
    return (v[n / 8] & (1 << (n % 8))) != 0;
}

bool initEGL(EGLConfig& eglConfig, EGLContext& eglContext,
             EGLDisplay& eglDisplay, EGLSurface& eglSurface,
             EGLNativeWindowType nativeWin);

class PiScreen : public Screen
{
    EGLDisplay eglDisplay;
    EGLSurface eglSurface;
    int width;
    int height;
    int frame_counter = 0;
    int fps = 60;
    using clk = std::chrono::steady_clock;
    clk::time_point real_t{};
    clk::time_point first{};
    clk::duration delta = std::chrono::microseconds(1000000 / 60);

public:
    PiScreen(EGLDisplay d, EGLSurface s, int w, int h)
        : eglDisplay(d), eglSurface(s), width(w), height(h)
    {
    }

    static inline constexpr double to_sec(clk::duration d)
    {
        return static_cast<double>(duration_cast<std::chrono::microseconds>(d)
            .count()) /
            1000'000.0;
    }

    Time get_time() const override
    {
        auto secs = to_sec(real_t - first);
        auto f = to_sec(delta);
        return {secs, frame_counter, f, fps};
    }

    void swap() override
    {
        if (eglDisplay != EGL_NO_DISPLAY) {
            eglSwapBuffers(eglDisplay, eglSurface);
            // eglQuerySurface(eglDisplay, eglSurface, EGL_WIDTH, &screenWidth);
            // eglQuerySurface(eglDisplay, eglSurface, EGL_HEIGHT,
            // &screenHeight);
        }
        auto t = clk::now();
        if (frame_counter > 0) {
            delta = t - real_t;
        }
        real_t = t;
        frame_counter++;
    }
    std::pair<int, int> get_size() const override { return {width, height}; }
};

class PiSystem : public System
{
    EGL_DISPMANX_WINDOW_T nativewindow{};

    EGLConfig eglConfig{};
    EGLContext eglContext{};
    EGLDisplay eglDisplay{};
    EGLSurface eglSurface{};

    std::vector<int> fdv;

    int32_t display_width{};
    int32_t display_height{};

public:
    std::shared_ptr<Screen> init_screen(Screen::Settings const&) override
    {
        bcm_host_init();

        DISPMANX_ELEMENT_HANDLE_T dispman_element = 0;
        DISPMANX_DISPLAY_HANDLE_T dispman_display = 0;
        DISPMANX_UPDATE_HANDLE_T dispman_update = 0;
        VC_RECT_T dst_rect;
        VC_RECT_T src_rect;

        uint32_t dw = 0;
        uint32_t dh = 0;
        // create an EGL window surface, passing context width/height
        int success = graphics_get_display_size(0 /* LCD */, &dw, &dh);
        if (success < 0) {
            throw display_exception("Cound not get display size");
        }

        display_width = static_cast<int32_t>(dw);
        display_height = static_cast<int32_t>(dh);

        dst_rect.x = 0;
        dst_rect.y = 0;
        dst_rect.width = display_width;
        dst_rect.height = display_height;

        uint16_t dwa = 0;
        uint16_t dha = 0;

        // Scale 50% on hires screens
        if (display_width > 2024) {
            display_width /= 2;
            display_height /= 2;
            dwa = display_width;
            dha = display_height;
        }

        src_rect.x = 0;
        src_rect.y = 0;
        src_rect.width = display_width << 16 | dwa;
        src_rect.height = display_height << 16 | dha;

        dispman_display = vc_dispmanx_display_open(0 /* LCD */);
        dispman_update = vc_dispmanx_update_start(0);

        dispman_element = vc_dispmanx_element_add(
            dispman_update, dispman_display, 0 /*layer*/, &dst_rect, 0 /*src*/,
            &src_rect, DISPMANX_PROTECTION_NONE, nullptr /*alpha*/,
            nullptr /*clamp*/, DISPMANX_NO_ROTATE);

        nativewindow.element = dispman_element;
        nativewindow.width = display_width;
        nativewindow.height = display_height;
        vc_dispmanx_update_submit_sync(dispman_update);

        initEGL(eglConfig, eglContext, eglDisplay, eglSurface, &nativewindow);
        return std::make_shared<PiScreen>(eglDisplay, eglSurface, display_width,
                                          display_height);

        glColorMask(true, true, true, false);
    }

    std::vector<int> letters = {
        KEY_A, KEY_B, KEY_C, KEY_D, KEY_E, KEY_F, KEY_G, KEY_H, KEY_I,
        KEY_J, KEY_K, KEY_L, KEY_M, KEY_N, KEY_O, KEY_P, KEY_Q, KEY_R,
        KEY_S, KEY_T, KEY_U, KEY_V, KEY_W, KEY_X, KEY_Y, KEY_Z,
    };
    void init_input() override
    {
        int c = 'a';
        for (auto key : letters) {
            map_key(key, c, 0);
            map_key(key, toupper(c), 1);
        }

        map_key(KEY_ENTER, Key::ENTER);
        map_key(KEY_ESC, Key::ESCAPE);
        map_key(KEY_LEFT, Key::LEFT);
        map_key(KEY_RIGHT, Key::RIGHT);
        map_key(KEY_DOWN, Key::DOWN);
        map_key(KEY_UP, Key::UP);
        map_key(KEY_BACKSPACE, Key::BACKSPACE);
        map_key(KEY_SPACE, Key::SPACE);

        fs::path idir{"/dev/input"};
        std::vector<uint8_t> evbit((EV_MAX + 7) / 8);
        std::vector<uint8_t> keybit((KEY_MAX + 7) / 8);
        int keyboardCount = 0;

        int fd = -1;
        if (fs::is_directory(idir)) {
            for (auto&& p : fs::directory_iterator(idir)) {
                auto real_path = idir / p.path().filename();
                if (!fs::is_directory(real_path)) {
                    fd = ::open(real_path.c_str(), O_RDONLY, 0);
                    if (fd >= 0) {
                        ioctl(fd, EVIOCGBIT(0, evbit.size()), &evbit[0]);
                        if (test_bit(evbit, EV_KEY)) {
                            ioctl(fd, EVIOCGBIT(EV_KEY, keybit.size()),
                                  &keybit[0]);
                            if (test_bit(keybit, KEY_F8)) keyboardCount++;
                            if (test_bit(keybit, KEY_LEFT) ||
                                test_bit(keybit, BTN_LEFT)) {
                                ioctl(fd, EVIOCGRAB, 1);
                                fdv.push_back(fd);
                                continue;
                            }
                        }
                        ::close(fd);
                    }
                }
                // fmt::print("{}, {:02x} -- {:02x}\n", p.path().string(),
                // evbit, keybit);
            }
        }

        // fmt::print("Found {} devices with keys\n", fdv.size());
    }

    std::unordered_map<uint32_t, uint32_t> mappings;

    void map_key(uint32_t code, Key target, int mods = 0)
    {
        map_key(code, static_cast<uint32_t>(target), mods);
    }

    void map_key(uint32_t code, uint32_t target, int mods = 0)
    {
        mappings[code | (mods << 24)] = target;
    }

    bool shift_down = false;
    int mouse_x = 0;
    int mouse_y = 0;
    int mouse_buttons = 0;

    std::deque<AnyEvent> events;

    template <typename E> void putEvent(E const& e) { events.push_back(e); }

    std::deque<AnyEvent> internal_all_events() override
    {
        int maxfd = -1;

        fd_set readset;
        struct timeval tv
        {};

        std::vector<uint8_t> buf(256);

        FD_ZERO(&readset);
        for (auto fd : fdv) {
            FD_SET(fd, &readset);
            if (fd > maxfd) maxfd = fd;
        }
        tv.tv_sec = 0;
        tv.tv_usec = 1000;
        int sr = select(maxfd + 1, &readset, nullptr, nullptr, &tv);
        if (sr > 0) {
            // fmt::print("Got signal\n");
            //  static uint8_t buf[2048];
            for (auto fd : fdv) {
                if (FD_ISSET(fd, &readset)) {
                    int rc = read(fd, &buf[0], sizeof(struct input_event) * 4);
                    auto* ptr = (struct input_event*)&buf[0];

                    while (rc >= (int)sizeof(struct input_event)) {
                        if (ptr->type == EV_REL) {
                            if (ptr->code == REL_X) {
                                mouse_x += ptr->value;
                                if (mouse_x > display_width) {
                                    mouse_x = display_width;
                                } else if (mouse_x < 0) {
                                    mouse_x = 0;
                                }
                                putEvent(MoveEvent{(float)mouse_x,
                                                   (float)mouse_y,
                                                   mouse_buttons});
                            } else if (ptr->code == REL_Y) {
                                mouse_y += ptr->value;
                                if (mouse_y > display_height) {
                                    mouse_y = display_height;
                                } else if (mouse_y < 0) {
                                    mouse_y = 0;
                                }
                                putEvent(MoveEvent{(float)mouse_x,
                                                   (float)mouse_y,
                                                   mouse_buttons});
                            }
                        } else if (ptr->type == EV_KEY) {
                            uint32_t k = ptr->code;
                            uint32_t mods = 0;
                            if (k == KEY_LEFTSHIFT || k == KEY_RIGHTSHIFT) {
                                shift_down = ptr->value != 0;
                            }
                            if (k == BTN_LEFT) {
                                if (ptr->value == 0) {
                                    mouse_buttons &= (~1);
                                } else {
                                    mouse_buttons |= 1;
                                    putEvent(ClickEvent{(float)mouse_x,
                                                        (float)mouse_y,
                                                        mouse_buttons});
                                }
                            }
                            if (ptr->value) {
                                mods = 0;
                                if (k == KEY_ESC && shift_down) {
                                    putEvent(QuitEvent{});
                                } else {
                                    if (shift_down) mods |= 1;
                                    auto it = mappings.find(k | (mods << 24));
                                    if (it != mappings.end()) {
                                        //fmt::print("Converted to {:x} > {:x}\n",
                                        //           k, it->second);
                                        k = it->second;
                                        putEvent(KeyEvent{k, mods, 0});
                                    } else {
                                        //fmt::print("Unhandled key {:x}\n",
                                        //           ptr->code);
                                    }
                                }
                            }
                        } else if (ptr->type != 0) {
                            // fmt::print("TYPE {} CODE {} VALUE {}\n",
                            // ptr->type, ptr->code, ptr->value);
                        }
                        ptr++;
                        rc -= sizeof(struct input_event);
                    }
                }
            }
        }
        return events;
    }
};

std::unique_ptr<System> create_pi_system()
{
    return std::make_unique<PiSystem>();
}
