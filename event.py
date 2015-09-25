import pyglet
import compute


def inject_update_hook(window, dt=1/60):
    window.register_event_type("on_update_variable")
    window.register_event_type("on_update_fixed")
    discretizer = compute.Discretizer(dt)

    def update(dt):
        window.dispatch_event("on_update_variable", dt)
        for stable_dt in discretizer.advance(dt):
            window.dispatch_event("on_update_fixed", stable_dt)
    pyglet.clock.schedule(update)


def debug_fps(window, samples=60):
    fps = compute.RollingAverage(samples)
    sample = pyglet.clock.get_fps
    window.push_handlers(on_update_variable=lambda dt: fps.push(sample()))
    return fps
