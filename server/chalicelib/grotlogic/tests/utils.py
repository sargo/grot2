
from ..board import Board


def _clean(text):
    return text.replace(' ', '').strip()


def set_fields_directions(board, directions_state=None, points_state=None):
    state = board.get_state()
    if directions_state:
        state['directions'] = _clean(directions_state)
    if points_state:
        state['points'] = _clean(points_state)
    board.fields = Board.from_state(state).fields


def assert_fields_directions(board, directions_state):
    data = _clean(directions_state).split('\n')
    for row in range(board.size):
        for col in range(board.size):
            field = board.get_field(row, col)
            direction = data[row][col]

            if direction == 'X':
                continue
            elif direction == 'O':
                direction == None

            assert field.direction == direction, \
                "Direction {} != {} at {},{}".format(
                    field.direction,
                    direction,
                    row,
                    col,
                )
