

def rotate(x, y, c=None, s=None):
    ''' c and s are the precomputed sin and cos of the angle of rotation '''
    # https://en.wikipedia.org/wiki/Rotation_matrix
    # [x'] = [cos(θ), -sin(θ)] * [x]
    # [y']   [sin(θ),  cos(θ)]   [y]

    # x' = x*cos(θ) - y*sin(θ)
    # y' = x*sin(θ) + y*cos(θ)
    return (
        x * c - y * s,
        x * s + y * c)


def offset(verts, x, y, z):
    for i in range(0, len(verts), 3):
        verts[i] += x
        verts[i+1] += y
        verts[i+2] += z


class Discretizer:
    def __init__(self, interval):
        self._interval = interval
        self._accumulator = 0

    def advance(self, dt):
        self._accumulator += dt
        # For callers that will immediately consume any steps
        return iter(self)

    def __iter__(self):
        i = self._interval
        while self._accumulator > i:
            yield i
            self._accumulator -= i
        raise StopIteration


class RollingAverage:
    def __init__(self, samples, initial=0):
        assert samples > 0

        # Circular buffer
        self.samples = [initial] * samples
        self._head = 0

        # Cache average value for O(1) updates
        self._average = initial

    @property
    def average(self):
        return self._average

    @property
    def latest(self):
        return self.samples[self._head]

    def push(self, value):
        count = len(self.samples)

        # Advance head, save old value, push new value
        self._head = (self._head + 1) % count
        old_sample = self.samples[self._head]
        self.samples[self._head] = value

        # Update average
        self._average -= old_sample / count
        self._average += value / count
