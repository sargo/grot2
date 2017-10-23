from unittest import TestCase

from ..board import Board
from .utils import assert_fields_directions, set_fields_directions
from ... import settings


class BoardTestCase(TestCase):

    def setUp(self):
        self.board = Board.from_seed(0)

    def test_get_field(self):
        for row in range(self.board.size):
            for col in range(self.board.size):
                field = self.board.get_field(row, col)
                self.assertEqual(field.row, row)
                self.assertEqual(field.col, col)

    def test_empty_lines(self):
        set_fields_directions(
            self.board,
            '''
            >v>^>
            vOO>>
            OOOOO
            >OO>O
            >OOv^
            '''
        )
        self.assertEqual(self.board.get_extra_points(), 50)

        set_fields_directions(
            self.board,
            '''
            >vO^>
            vOO>>
            OOOOO
            >OO>O
            >OOv^
            '''
        )
        self.assertEqual(self.board.get_extra_points(), 100)

        set_fields_directions(
            self.board,
            '''
            >OO^>
            vOO>>
            OOOOO
            >OO>O
            >OOv^
            '''
        )
        self.assertEqual(self.board.get_extra_points(), 150)

    def test_get_next_field(self):
        set_fields_directions(
            self.board,
            '''
            >vv^v
            >>O<<
            >OOO>
            v^>v<
            <>v>^
            '''
        )

        # going right
        field = self.board.get_field(0, 0)
        next_field = self.board.get_next_field(field)
        self.assertEqual((next_field.row, next_field.col), (0, 1))

        # going left
        field = self.board.get_field(1, 4)
        next_field = self.board.get_next_field(field)
        self.assertEqual((next_field.row, next_field.col), (1, 3))

        # going up
        field = self.board.get_field(4, 4)
        next_field = self.board.get_next_field(field)
        self.assertEqual((next_field.row, next_field.col), (3, 4))

        # going down
        field = self.board.get_field(0, 1)
        next_field = self.board.get_next_field(field)
        self.assertEqual((next_field.row, next_field.col), (1, 1))

        # going right out of map
        field = self.board.get_field(2, 4)
        next_field = self.board.get_next_field(field)
        self.assertEqual(next_field, None)

        # going left out of map
        field = self.board.get_field(4, 0)
        next_field = self.board.get_next_field(field)
        self.assertEqual(next_field, None)

        # going up out of map
        field = self.board.get_field(0, 3)
        next_field = self.board.get_next_field(field)
        self.assertEqual(next_field, None)

        # going down out of map
        field = self.board.get_field(4, 2)
        next_field = self.board.get_next_field(field)
        self.assertEqual(next_field, None)

        # going left through a gap
        field = self.board.get_field(1, 1)
        next_field = self.board.get_next_field(field)
        self.assertEqual((next_field.row, next_field.col), (1, 3))

        # going right through a gap
        field = self.board.get_field(1, 3)
        next_field = self.board.get_next_field(field)
        self.assertEqual((next_field.row, next_field.col), (1, 1))

        # going up through a gap
        field = self.board.get_field(3, 1)
        next_field = self.board.get_next_field(field)
        self.assertEqual((next_field.row, next_field.col), (1, 1))

        # going down through a gap
        field = self.board.get_field(0, 2)
        next_field = self.board.get_next_field(field)
        self.assertEqual((next_field.row, next_field.col), (3, 2))

    def test_lower_fields(self):
        set_fields_directions(
            self.board,
            '''
            >vvOO
            >>OOO
            >OO>O
            v^>OO
            <OvOO
            '''
        )
        self.board.lower_fields()
        assert_fields_directions(
            self.board,
            '''
            >OOOO
            >OOOO
            >vvOO
            v>>OO
            <^v>O
            '''
        )

    def test_fill_empty_fields(self):
        set_fields_directions(
            self.board,
            '''
            >OOOO
            >OOOO
            >vvOO
            v>>OO
            <^v>O
            '''
        )

        self.board.fill_empty_fields()
        assert_fields_directions(
            self.board,
            '''
            >XXXX
            >XXXX
            >vvXX
            v>>XX
            <^v>X
            '''
        )

    def test_get_state(self):
        board = Board.from_seed(0)
        state = board.get_state()
        self.assertEqual(
            state['points'],
            '13422\n21113\n11342\n12122\n11111',
        )
        self.assertEqual(
            state['directions'],
            '><>>v\n^^<^^\n>^>>^\n><^^<\nvv<^^',
        )
        self.assertEqual(state['random'], '0-50')

    def test_preview_do_not_change_state(self):
        # generation of preview shouldn't change random state
        # so generating second time we should get same preview
        points_1 = [f.points for f in self.board.get_preview()]
        points_2 = [f.points for f in self.board.get_preview()]
        directions_1 = [f.direction for f in self.board.get_preview()]
        directions_2 = [f.direction for f in self.board.get_preview()]
        self.assertListEqual(points_1, points_2)
        self.assertListEqual(directions_1, directions_2)

    def test_fill_empty_fields_as_preview_predicted(self):
        set_fields_directions(
            self.board,
            '''
            OOOOO
            OOOOO
            OOOOO
            vvvvv
            vvvvv
            '''
        )

        preview = ''.join(field.direction for field in self.board.get_preview())
        self.board.fill_empty_fields()

        assert_fields_directions(
            self.board,
            '''
            {}X
            {}XX
            {}XX
            vvvvv
            vvvvv
            '''.format(preview[::3], preview[1::3], preview[2::3])
        )
