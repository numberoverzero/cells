import math
import compute
import pyglet
import pyglet.gl as gl


class MutatingProperty:
    '''Marks obj dirty when value is set.'''
    def __init__(self, name):
        self._name = name

    def __set__(self, obj, value):
        # TODO: is it worth the perf hit to check existing value
        obj._dirty = True
        obj.__dict__[self._name] = value


class Shape:
    '''Stores general flags and settings.'''
    _vertices = None
    _dirty = True

    def __init__(self, *, batch=None, group=None, **kwargs):
        self.batch = batch or pyglet.graphics.Batch()
        self.group = group

        # Can be one of ['static', 'dynamic', 'stream']
        # http://pyglet.readthedocs.org/en/latest/programming_guide/graphics.html#data-usage
        # static -  Data is never or rarely modified after initialisation
        # dynamic - Data is occasionally modified (default)
        # stream -  Data is updated every frame

        self._update_frequency = kwargs.get('update', 'dynamic')

    def _generate_vertices(self):
        '''Called whenever a property that mutates verts is changed.'''
        raise NotImplementedError

    def update(self, dt=0):
        if self._dirty:
            self._generate_vertices()
            self._dirty = False

    def delete(self):
        if self._vertices:
            self._vertices.delete()
        self._vertices = None


class Circle(Shape):

    x = MutatingProperty('x')
    y = MutatingProperty('y')
    z = MutatingProperty('z')
    r = MutatingProperty('r')

    resolution = MutatingProperty('resolution')
    color = MutatingProperty('color')

    def __init__(self, *, x, y, z=0, r, color, resolution=0.25, **kwargs):
        self.resolution, self.color = resolution, color
        self.x, self.y, self.z, self.r = x, y, z, r
        super().__init__(**kwargs)

    def _generate_vertices(self):
        # Derive theta from resolution, to calculate number of steps.
        # See http://slabode.exofire.net/circle_draw.html for info
        # Solve for theta: (1 - cos(theta)) * r = resolution
        # theta = acos(1 - (resolution / r))
        theta = math.acos(1 - (self.resolution / self.r))
        # Add 2 because we're using triangle_fan
        steps = int(2 * math.pi / theta) + 2
        # center vertex of the fan
        verts = steps + 1

        # precalculate sin, cos
        c = math.cos(theta)
        s = math.sin(theta)

        vertices = []
        colors = self.color * verts

        # Local uses LOAD_FAST
        rot, push = compute.rotate, vertices.extend

        x, y = self.r, 0

        # Center of fan
        push((0, 0, 0))
        for i in range(steps):
            push((x, y, 0))
            x, y = rot(x, y, c, s)
        compute.offset(vertices, self.x, self.y, self.z)

        # Replace existing vertices
        # Vertex count may change with self.r or self.resolution
        if self._vertices:
            if verts != len(self._vertices.vertices):
                self._vertices.resize(verts)
            self._vertices.vertices = vertices
            self._vertices.colors = colors
        # First render
        else:
            # WARNING - adjacent GL_TRIANGLE_FAN are rendered together,
            # because of how pyglet's allocater works.  Circles rendered in
            # the same batch MAY use the central point for a different circle
            # as their own fan center.  It mostly depends on the state of the
            # allocater when the circle's verts are added below.
            #
            # For more information:
            #   https://bitbucket.org/pyglet/pyglet/issues/64
            self._vertices = self.batch.add(
                verts, gl.GL_TRIANGLE_FAN, self.group,
                ('v3f/' + self._update_frequency, vertices),
                ('c3B/' + self._update_frequency, colors))


class Rectangle(Shape):

    x = MutatingProperty('x')
    y = MutatingProperty('y')
    z = MutatingProperty('z')
    w = MutatingProperty('w')
    h = MutatingProperty('h')
    r = MutatingProperty('r')

    color = MutatingProperty('color')

    def __init__(self, *, x, y, z=0, w, h, r=0, color, **kwargs):
        self.x, self.y, self.z = x, y, z
        self.w, self.h, self.r = w, h, r
        self.color = color
        super().__init__(**kwargs)

    def _generate_vertices(self):
        # precalculate sin, cos
        c = math.cos(self.r)
        s = math.sin(self.r)

        # Local uses LOAD_FAST
        sx, sy, sz = self.x, self.y, self.z
        w, h = self.w, self.h

        vertices = [
            # x, y, z (degenerate)
            sx, sy, sz,

            # x, y, z
            sx, sy, sz,
            # x, y + h, z
            sx - h * s, sy + h * c, sz,
            # x + w, y, z
            sx + w * c, sy + w * s, sz,
            # x + w, y + h, z
            sx + (w * c - h * s), sy + (w * s + h * c), sz,

            # x + w, y + h, z (degenerate)
            sx + (w * c - h * s), sy + (w * s + h * c), sz
        ]

        # 4 verts + 2 degenerate
        colors = self.color * 6

        # Replace existing vertices
        if self._vertices:
            self._vertices.vertices = vertices
            self._vertices.colors = colors
        # First render
        else:
            self._vertices = self.batch.add(
                6, gl.GL_TRIANGLE_STRIP, self.group,
                ('v3f/' + self._update_frequency, vertices),
                ('c3B/' + self._update_frequency, colors))
