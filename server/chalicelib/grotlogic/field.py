POINTS = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
DIRECTIONS = ['^', 'v', '>', '<']


class Field:
    """
    Holds field state.
    """

    def __init__(self, row, col, random, points=None, direction=None):
        self.row = row
        self.col = col
        self.random = random
        if points is not None and direction is not None:
            self.points = points
            self.direction = direction
        else:
            self.reset()

    def reset(self):
        self.points = self.random.choice(POINTS)
        self.direction = self.random.choice(DIRECTIONS)
