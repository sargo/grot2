POINTS = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
DIRECTIONS = ['up', 'down', 'right', 'left']


class Field:
    """
    Holds field state.
    """

    def __init__(self, x, y, random):
        self.x = x
        self.y = y
        self.random = random
        self.reset()

    def reset(self):
        self.points = self.random.choice(POINTS)
        self.direction = self.random.choice(DIRECTIONS)

    def get_state(self):
        result = {'points': self.points, 'direction': self.direction}
        if self.x is not None:
            result['x'] = self.x
        if self.y is not None:
            result['y'] = self.y
        return result
