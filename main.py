import pyglet
import math
import shapes
import pyglet.gl as gl
import event


class Handler:
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        for shape in shape_list:
            shape.update(0)
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        # for shape in shape_list:
        for shape in shape_list:
            shape.update(0)
        pass

    def on_update_fixed(self, dt):
        label.text = "{} fps | {} verts".format(
            int(fps.average),
            # sum(c._verts for c in shape_list)
            sum(6 for r in shape_list)
        )


window = pyglet.window.Window(width=900, height=900, resizable=True, vsync=0)
event.inject_update_hook(window, 1/60)
fps = event.debug_fps(window, 60)
window.push_handlers(Handler())

b = pyglet.graphics.Batch()


class ExpandingCircle(shapes.Circle):
    def __init__(self, *, min_r, max_r, rate, **kwargs):
        self.min_r = min_r
        self.max_r = max_r
        self.rate = rate
        super().__init__(**kwargs)

    def update(self, dt):
        self.r *= self.rate
        if self.r > self.max_r:
            self.r = self.min_r
        super().update(dt)


class RotatingRectangle(shapes.Rectangle):
    def __init__(self, *, rate, **kwargs):
        self.rate = 2 * math.pi / rate
        super().__init__(**kwargs)

    def update(self, dt):
        self.r += self.rate
        super().update(dt)

groups = [pyglet.graphics.OrderedGroup(x) for x in range(10)]
coeffs = [
    # Bottom left
    (-1, -1),
    # Top left
    (-1, 1),
    # Bottom right
    (1, -1),
    # Top right
    (1, 1)
]


def circle_cluster(x, y, r, rate, color, level, max_level, batch):
    if level == max_level:
        raise StopIteration

    yield ExpandingCircle(
        min_r=r, r=r, max_r=r*2,
        x=x, y=y, rate=rate,
        color=color,
        batch=batch,
        group=groups[level],
        resolution=1)

    for (xo, yo) in coeffs:
        sub_x = x + (xo * r)
        sub_y = y + (yo * r)
        sub_r = r / 2
        for shape in circle_cluster(sub_x, sub_y, sub_r, rate,
                                    [int(255 - c/(level+1)) for c in color],
                                    level+1, max_level, batch):
            yield shape


def rect_cluster(x, y, w, h, rate, color, level, max_level, batch):
    if level == max_level:
        raise StopIteration

    yield RotatingRectangle(
        x=x, y=y, w=w, h=h,
        rate=rate,
        color=color,
        batch=batch,
        group=groups[level])

    for (xo, yo) in coeffs:
        sub_x = x + (xo * w/2)
        sub_y = y + (yo * h/2)
        sub_w = w / 2
        sub_h = w / 2
        for shape in rect_cluster(sub_x, sub_y, sub_w, sub_h, rate,
                                  [int(255 // (level+1)**2)] * 3,
                                  level+1, max_level, batch):
            yield shape


circles = list(circle_cluster(
    x=450, y=450, r=200,
    rate=1.01, color=[255, 0, 0],
    level=0,
    max_level=3,
    batch=b))
rects = list(rect_cluster(
    x=450, y=450, w=400, h=400,
    rate=128, color=[255, 255, 255],
    level=0,
    max_level=5,
    batch=b))
shape_list = rects
label = pyglet.text.Label(
    'fps',
    font_name='Times New Roman',
    font_size=18,
    x=0, y=0,
    anchor_x='left', anchor_y='bottom',
    batch=b)


@window.event
def on_draw():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    b.draw()

pyglet.app.run()
