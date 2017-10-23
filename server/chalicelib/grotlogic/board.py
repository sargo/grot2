import random

from .field import Field
from .random import DenseStateRandom
from .. import settings


class Board:

    def __init__(self, random, fields=None):
        self.size = size = settings.BOARD_SIZE
        self.random = random

        if fields:
            self.fields = fields
        else:
            self.fields = [
                [Field(row, col, self.random) for col in range(size)]
                for row in range(size)
            ]

    @classmethod
    def from_seed(cls, seed):
        return cls(DenseStateRandom(seed))

    @classmethod
    def from_state(cls, state):
        size = settings.BOARD_SIZE
        random = DenseStateRandom()
        random.setstate(state['random'])

        points_state = state['points'].split('\n')
        directions_state = state['directions'].split('\n')
        fields = [
            [
                Field(
                    row,
                    col,
                    random,
                    int(points_state[row][col]),
                    directions_state[row][col],
                )
                for col in range(size)
            ]
            for row in range(size)
        ]
        return cls(random, fields)

    def get_state(self):
        return {
            'points': '\n'.join(
                ''.join([
                    str(self.get_field(row, col).points)
                    for col in range(self.size)
                ])
                for row in range(self.size)
            ),
            'directions': '\n'.join(
                ''.join([
                    self.get_field(row, col).direction
                    for col in range(self.size)
                ])
                for row in range(self.size)
            ),
            'random': self.random.getstate(),
        }

    def get_field(self, row, col):
        """
        Returns the field at the given coordinates.
        """
        return self.fields[row][col]

    def get_next_field(self, field, direction=None):
        """
        Returns next field in chain reaction and information is it last step
        in this chain reaction.
        """
        direction = direction or field.direction

        if direction == '<':
            if field.col == 0:
                return None
            next_field = self.get_field(field.row, field.col - 1)

        elif direction == '>':
            if field.col == (self.size - 1):
                return None
            next_field = self.get_field(field.row, field.col + 1)

        elif direction == '^':
            if field.row == 0:
                return None
            next_field = self.get_field(field.row - 1, field.col)

        elif direction == 'v':
            if field.row == (self.size - 1):
                return None
            next_field = self.get_field(field.row + 1, field.col)

        if next_field.direction == 'O':
            # if next was alread cleared than go further in the same direction
            return self.get_next_field(next_field, direction)

        return next_field

    def lower_field(self, field):
        """
        When chain reaction is over fields that are 'flying' should be lowered.
        """
        new_row = field.row
        while new_row < self.size - 1:
            if self.get_field(new_row + 1, field.col).direction != 'O':
                # next field below is not empty, so finish lowering
                break
            new_row += 1

        if new_row != field.row:
            next_field = self.get_field(new_row, field.col)
            # swap fields values
            field.points, next_field.points = next_field.points, field.points
            field.direction, next_field.direction = \
                next_field.direction, field.direction

    def lower_fields(self):
        """
        Lower fields (use gravity).
        """
        for row in reversed(range(self.size - 1)):
            for col in range(self.size):
                self.lower_field(self.get_field(row, col))

    def fill_empty_fields(self):
        """
        Reset fields in empty places.
        """
        for row in range(self.size):
            for col in range(self.size):
                field = self.get_field(row, col)
                if field.direction == 'O':
                    field.reset()

    def get_extra_points(self):
        """
        Return extra points for the empty rows and columns.
        """
        extra_points = 0

        for row in range(self.size):
            # add extra points if all cols of a row are empty
            if all(
                    self.get_field(row, col).direction == 'O'
                    for col in range(self.size)
                ):
                extra_points += self.size * 10

        for col in range(self.size):
            # add extra points if all rows of a column are empty
            if all(
                    self.get_field(row, col).direction == 'O'
                    for row in range(self.size)
                ):
                extra_points += self.size * 10

        return extra_points

    def get_preview(self):
        """
        Preview, a set of fields are next in the random generator.
        """
        saved_state = random.Random.getstate(self.random)
        result = [
            Field(None, None, self.random)
            for i in range(settings.PREVIEW_SIZE)
        ]
        random.Random.setstate(self.random, saved_state)
        return result

    def get_preview_state(self):
        """
        Preview as a strings.
        """
        preview = self.get_preview()
        return {
            'directions': ''.join(field.direction for field in preview),
            'points': ''.join(str(field.points) for field in preview),
        }
