#define GLAD_GL_IMPLEMENTATION
#include "gl/gl.hpp"
#ifdef USE_ASOUND
#    include "player_linux.h"
#endif
#include "system.hpp"
#include "utf8.h"

#include <GLFW/glfw3.h>

#include <array>
#include <chrono>
#include <deque>
#include <filesystem>
#include <optional>
#include <thread>
#include <unordered_map>
#include <unordered_set>

namespace fs = std::filesystem;

using namespace std::chrono_literals;

static bool swapped = false;

class GLFWWindow : public Screen
{
    using clk = std::chrono::steady_clock;

    int frame_counter = 0;
#ifdef __APPLE__
    int fps = 60;
    clk::duration frame_time = std::chrono::microseconds(1000000 / 60);
#else
    int fps = 0;
    clk::duration frame_time = std::chrono::microseconds(0);
#endif
    clk::time_point last_end{};
    clk::time_point real_t{};
    clk::time_point first{};
    clk::duration delta = std::chrono::microseconds(1000000 / 60);

public:
    GLFWwindow* window = nullptr;

    explicit GLFWWindow(GLFWwindow* win) : window(win)
    {
        update_scale();
        first = clk::now();
    }

    void update_scale()
    {
        int fw = 0;
        int fh = 0;
        glfwGetFramebufferSize(window, &fw, &fh);
        log("fb size %d %d\n", fw, fh);

        int w = 0;
        int h = 0;
        glfwGetWindowSize(window, &w, &h);
        log("win size %d %d\n", w, h);
        scale = static_cast<float>(fw) / static_cast<float>(w);
    }

    ~GLFWWindow() override
    {
        if (window != nullptr) { glfwDestroyWindow(window); }
    }

    float scale = 1.0F;
    float get_scale() override
    {
        update_scale();
        return scale;
    }

    void swap() override
    {
        glfwSwapBuffers(window);
        clk::time_point t = clk::now();
        auto d = t - real_t;
        swapped = true;
        if (frame_time != 0us) {
            if (d + 1ms < frame_time) {
                //printf("Sleeping %dms\n", to_ms(frame_time - d)- 1);
                std::this_thread::sleep_for(frame_time - d - 1ms);
            }
        }
        t = clk::now();
        //printf("Actually slept %dms\n", to_ms(t - real_t));
        if (frame_counter > 0) {
            delta = t - real_t;
        }
        real_t = t;
        frame_counter++;
    }
    void set_fps(int fps) override
    {
        this->fps = fps;
        if (fps == 0) {
            frame_time = 0us;
        } else {
            frame_time = 1000000us / fps;
        }
    }

    static inline constexpr int to_ms(clk::duration d)
    {
        return duration_cast<std::chrono::milliseconds>(d).count();
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

    void set_target() override
    {
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        auto [w, h] = get_size();
        glViewport(0, 0, w, h);
    }

    std::pair<int, int> get_size() const override
    {
        int w = -1;
        int h = -1;
        glfwGetWindowSize(window, &w, &h);
        return {w, h};
    }
};

class GLFWSystem : public System
{
    static inline std::unordered_map<uint32_t, Key> glfw_map = {
        {GLFW_KEY_LEFT, Key::LEFT},      {GLFW_KEY_RIGHT, Key::RIGHT},
        {GLFW_KEY_PAGE_UP, Key::PAGEUP}, {GLFW_KEY_PAGE_DOWN, Key::PAGEDOWN},
        {GLFW_KEY_UP, Key::UP},          {GLFW_KEY_DOWN, Key::DOWN},
        {GLFW_KEY_END, Key::END},        {GLFW_KEY_HOME, Key::HOME},
        {GLFW_KEY_TAB, Key::TAB},        {GLFW_KEY_ESCAPE, Key::ESCAPE},
        {GLFW_KEY_ENTER, Key::ENTER},    {GLFW_KEY_INSERT, Key::INSERT},
        {GLFW_KEY_DELETE, Key::DELETE},  {GLFW_KEY_BACKSPACE, Key::BACKSPACE},
        {GLFW_KEY_F1, Key::F1},          {GLFW_KEY_F2, Key::F2},
        {GLFW_KEY_F3, Key::F3},          {GLFW_KEY_F4, Key::F4},
        {GLFW_KEY_F5, Key::F5},          {GLFW_KEY_F6, Key::F6},
        {GLFW_KEY_F7, Key::F7},          {GLFW_KEY_F8, Key::F8},
        {GLFW_KEY_F9, Key::F9},          {GLFW_KEY_F10, Key::F10},
        {GLFW_KEY_F11, Key::F11},        {GLFW_KEY_F12, Key::F12},
    };

    static inline std::unordered_map<Key, uint32_t> reverse_map;
    static inline GLFWSystem* system = nullptr;

    std::unordered_set<uint32_t> pressed;
    std::unordered_set<uint32_t> released;
    GLFWwindow* window = nullptr;

public:
    GLFWSystem()
    {
        auto save = fs::current_path();
        glfwInit();
        fs::current_path(save);
        for (auto [a, b] : glfw_map) {
            reverse_map[b] = a;
        }
    };

    std::shared_ptr<Screen>
    init_screen(Screen::Settings const& settings) override
    {
        glfwWindowHint(GLFW_SAMPLES, 4);
        glfwWindowHint(GLFW_COCOA_RETINA_FRAMEBUFFER, GLFW_TRUE);
        glfwWindowHint(GLFW_SCALE_TO_MONITOR, GLFW_TRUE);
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);
        glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_ANY_PROFILE);

        int width = settings.display_width;
        int height = settings.display_height;
        GLFWmonitor* monitor = nullptr;
        if (settings.screen == ScreenType::Full) {
            monitor = glfwGetPrimaryMonitor();
            if (width <= 0) {
                auto const* mode = glfwGetVideoMode(monitor);
                glfwWindowHint(GLFW_RED_BITS, mode->redBits);
                glfwWindowHint(GLFW_GREEN_BITS, mode->greenBits);
                glfwWindowHint(GLFW_BLUE_BITS, mode->blueBits);
                glfwWindowHint(GLFW_REFRESH_RATE, mode->refreshRate);
                width = mode->width;
                height = mode->height;
            }
        }
        if (width <= 0 || height <= 0) {
            throw system_exception("Illegal window size");
        }
        window = glfwCreateWindow(width, height, settings.title.c_str(),
                                  monitor, nullptr);
        if (window == nullptr) {
            throw system_exception("Could not open graphics window");
        }
        glfwMakeContextCurrent(window);

        glfwSwapInterval(1);

#ifndef USE_GLES
        // glewInit();
        int version = gladLoadGL(glfwGetProcAddress);
        if (version == 0) {
            throw system_exception("Failed to initialize GL");
            return nullptr;
        }
        // printf("GL %d.%d\n", GLAD_VERSION_MAJOR(version),
        // GLAD_VERSION_MINOR(version));
#endif
        glfwSwapInterval(1);
        // printf("%s\n", glGetString(GL_VERSION));
        glDisable(GL_CULL_FACE);
        glCullFace(GL_BACK);
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glBindFramebuffer(GL_FRAMEBUFFER, 0);

        system = this;
        glfwSetCharCallback(window, [](GLFWwindow*, unsigned int codepoint) {
            system->char_was_pressed(codepoint);
        });
        glfwSetKeyCallback(window, [](GLFWwindow*, int key, int scancode,
                                      int action, int mods) {
            system->key_was_pressed(key, scancode, action, mods);
        });
        glfwSetMouseButtonCallback(
            window, [](GLFWwindow*, int button, int action, int mods) {
                system->mouse_was_pressed(button, action, mods);
            });
        glfwSetCursorPosCallback(window, [](GLFWwindow*, double x, double y) {
            system->mouse_move(x, y);
        });
        glfwSetWindowSizeCallback(
            window, [](GLFWwindow*, int w, int h) { system->resized(w, h); });
        glViewport(0, 0, settings.display_width, settings.display_height);
        return std::make_shared<GLFWWindow>(window);
    }

    std::deque<AnyEvent> event_queue;

    void post_event(AnyEvent const& event) override
    {
        event_queue.emplace_back(event);
    }

    void mouse_move(double x, double y)
    {
        int buttons = glfwGetMouseButton(window, 0);
        event_queue.emplace_back(
            MoveEvent{static_cast<float>(x), static_cast<float>(y), buttons});
    }

    void mouse_was_pressed(int button, int action, int mods)
    {
        if (action == 1) {
            double x = 0;
            double y = 0;
            pressed.insert(static_cast<uint32_t>(Key::LEFT_MOUSE) + button);
            glfwGetCursorPos(window, &x, &y);
            event_queue.emplace_back(ClickEvent{static_cast<float>(x),
                                                static_cast<float>(y), button,
                                                static_cast<uint32_t>(mods)});
        }  else {
            released.insert(static_cast<uint32_t>(Key::LEFT_MOUSE) + button);
        }
    }
    std::pair<float, float> get_pointer() override
    {
        double x = 0;
        double y = 0;
        glfwGetCursorPos(window, &x, &y);
        return {x, y};
    }

    void char_was_pressed(unsigned codepoint)
    {
        auto s = utf8::utf8_encode(
            std::u32string(1, static_cast<char32_t>(codepoint)));
        event_queue.emplace_back(TextEvent{s, 0});
    }

    std::optional<std::pair<int, int>> new_size;

    void resized(int w, int h) { new_size = {w, h}; }

    void key_was_pressed(int key, int /* scancode */, int action, int mods)
    {
        auto down = (action != GLFW_RELEASE);
        if (key >= 0x20 && key <= 0x7f) {
            auto c = static_cast<uint32_t>(std::tolower(key));
            if (down) {
                event_queue.emplace_back(
                    KeyEvent{c, static_cast<uint32_t>(mods), 0});
                pressed.insert(c);
            } else {
                released.insert(c);
            }
        } else {
            auto it = glfw_map.find(key);
            if (it != glfw_map.end()) {
                auto k32 = static_cast<uint32_t>(it->second);
                if (down) {
                    pressed.insert(k32);
                    event_queue.emplace_back(
                        KeyEvent{k32, static_cast<uint32_t>(mods), 0});
                } else {
                    released.insert(k32);
                }
            }
        }
    }

    bool is_pressed(uint32_t code, int device) override
    {
        auto key = static_cast<Key>(code);
        if (key == Key::LEFT_MOUSE) {
            return glfwGetMouseButton(window, 0) != GLFW_RELEASE;
        }
        if (key == Key::RIGHT_MOUSE) {
            return glfwGetMouseButton(window, 1) != GLFW_RELEASE;
        }
        if (key == Key::MIDDLE_MOUSE) {
            return glfwGetMouseButton(window, 2) != GLFW_RELEASE;
        }
        if (code >= 0x20 && code <= 0x7f) {
            return glfwGetKey(window, std::toupper(static_cast<int>(code))) !=
                   GLFW_RELEASE;
        }

        auto it = reverse_map.find(key);
        if (it != reverse_map.end()) {
            return glfwGetKey(window, it->second) != GLFW_RELEASE;
        }
        return false;
    }

    bool loop_called = false;

    bool was_pressed(uint32_t code, int device = -1) override
    {
        if (!loop_called) {
            throw system_exception(
                "run_loop() must be called before reading events");
        }
        return pressed.contains(code);
    }

    bool was_released(uint32_t code, int device = -1) override
    {
        if (!loop_called) {
            throw system_exception(
                "run_loop() must be called before reading events");
        }
        return released.contains(code);
    }

    std::deque<AnyEvent> internal_all_events() override
    {
        if (!swapped) {
            std::this_thread::sleep_for(std::chrono::milliseconds(5));
        }
        swapped = false;
        loop_called = true;
        //event_queue.clear();
        pressed.clear();
        released.clear();
        glfwPollEvents();
        if (new_size) {
            auto w = new_size->first;
            auto h = new_size->second;
            new_size = std::nullopt;
            event_queue.emplace_back(ResizeEvent{w, h});
        }
        auto should_close = glfwWindowShouldClose(window) != 0;
        if (should_close) { event_queue.emplace_back(QuitEvent{}); }
        auto qcp = event_queue;
        event_queue.clear();
        return qcp;
    }
};

std::unique_ptr<System> create_glfw_system()
{
    return std::make_unique<GLFWSystem>();
}
