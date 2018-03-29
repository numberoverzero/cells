import contextlib
import pyglet.gl as gl


def _no_proj(camera, context):
    '''Default projection function.'''
    pass


class Camera:
    '''Manage projections for rendering.

    Example pipeline that swaps perspective per batch:

        pipeline = [
            ("background", bg_verts),
            ("game", game_verts),
            ("effects", fx_verts),
            ("overlay", over_verts),
            ("hud", hud_verts),
            ("menu", menu_verts)
        ]

        for projection, batch in pipeline:
            with camera.projection(projection):
                batch.draw()
    '''
    def __init__(self, **kwargs):
        '''
        Each projection is a callable that takes a camera and context.'''
        self.projections = {}
        self.default = _no_proj
        # Base context for each projection swap
        self.context = dict(kwargs)

    @contextlib.contextmanager
    def projection(self, name, **context):
        '''Load projections by name for rendering.
        camera.context['debug'] = False

        ctx = {'debug': True}
        with camera.projection('game', **ctx):
            game_batch.draw()
        with camera.projection('hud'):
            hud_batch.draw()

        Can safely be nested:

            with camera.projection('game'):
                with camera.projection('game-background', debug=True):
                    scene.draw()
                with camera.projection('game-foreground', debug=False):
                    units.draw()
        '''
        # Apply
        self.apply(name, **context)
        yield
        # Restore default projection
        self._apply(self.default, **context)

    def apply(self, name, **context):
        '''Apply projection by name'''
        projection = self.projections.get(name, _no_proj)
        self._apply(projection, **context)

    def _apply(self, projection, **context):
        projection(self, {**self.context, **context})


def ortho(near=-1, far=1):
    '''Returns a function that sets up an ortho projection for a window.'''
    def projection(camera, context):
        window = context['window']

        # viewport
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glViewport(0, 0, window.width, window.height)

        gl.glDisable(gl.GL_CLIP_PLANE0)
        gl.glDisable(gl.GL_CLIP_PLANE1)
        gl.glDisable(gl.GL_CLIP_PLANE2)
        gl.glDisable(gl.GL_CLIP_PLANE3)

        # ortho
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glOrtho(0, window.width, 0, window.height, near, far)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    return projection
