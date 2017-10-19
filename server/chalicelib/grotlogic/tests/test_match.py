from unittest import TestCase

from ..match import Match
from ..board import Board
from .utils import assert_fields_directions, set_fields_directions


class GameTestCase(TestCase):

    def setUp(self):
        self.match = Match(None, Board.from_seed(0))

    def test_new_game_is_clean(self):
        self.assertEqual(self.match.moves, 5)
        self.assertEqual(self.match.score, 0)

    def test_skip_move(self):
        moves = self.match.moves
        self.match.skip_move()

        self.assertEqual(self.match.moves, moves - 1)
        self.assertEqual(self.match.score, 0)

    def test_simple_move(self):
        set_fields_directions(
            self.match.board,
            '''
            >v>^>
            v^v>>
            vv<>>
            >>^>^
            >^<v^
            '''
        )

        moves = self.match.moves
        self.match.start_move(4, 0)

        assert_fields_directions(
            self.match.board,
            '''
            >v>^X
            v^v>>
            vv<>>
            >>^>^
            >^<v^
            '''
        )
        self.assertEqual(self.match.old_score, 0)
        self.assertEqual(self.match.moves, moves - 1)
        self.assertEqual(self.match.score, 1)
        self.assertEqual(self.match.move_length, 1)

    def test_complex_move_through_gaps(self):
        set_fields_directions(
            self.match.board,
            '''
            >v>^>
            v^v>>
            vv<>>
            >>^>^
            >^<v^
            '''
        )

        # setting points for a field that will be hit
        self.match.board.get_field(2, 2).points = 4

        # setting points for a fields that will not change
        self.match.board.get_field(4, 4).points = 8
        self.match.board.get_field(2, 4).points = 8
        self.match.board.get_field(0, 0).points = 8

        # setting points for fields that will change,
        # but not because of being hit
        self.match.board.get_field(1, 0).points = 6
        self.match.board.get_field(4, 1).points = 6
        self.match.board.get_field(2, 1).points = 6

        moves = self.match.moves
        self.match.start_move(2, 3)

        assert_fields_directions(
            self.match.board,
            '''
            >XXXX
            vXX^X
            vv>>>
            >^v>>
            >^<v^
            '''
        )
        # Extra three moves for long move
        self.assertEqual(self.match.moves, moves + 2)
        # 6 arrows for 1 point and 1 arrow for 4 points = 10 extra points
        self.assertEqual(self.match.score, 10)
        self.assertEqual(self.match.move_length, 7)

    def test_score_is_properly_added(self):
        set_fields_directions(
            self.match.board,
            '''
            <^^<<
            v^vv>
            ^v<v>
            >^<>^
            >^vv^
            '''
        )

        self.match.start_move(2, 2)
        self.match.board.get_field(4, 2).points = 2

        assert_fields_directions(
            self.match.board,
            '''
            <XX<<
            vX^v>
            ^Xvv>
            >X<>^
            >^vv^
            '''
        )
        # 5 arrows hit = 5 extra points
        self.assertEqual(self.match.score, 5)

        self.match.start_move(3, 3)

        assert_fields_directions(
            self.match.board,
            '''
            <XXXX
            vX^<X
            ^Xvv<
            >X<v>
            >^vv^
            '''
        )
        # 2 arrows for 1 point and 1 for 2 points hit = 4 extra points
        self.assertEqual(self.match.score, 9)

    def test_clearing_vertical_lines(self):
        set_fields_directions(
            self.match.board,
            '''
            <^^<<
            v^vv>
            ^v<v>
            >v<>^
            >^vv^
            '''
        )

        self.match.board.get_field(1, 3).points = 4
        self.match.start_move(1, 2)

        assert_fields_directions(
            self.match.board,
            '''
            <X^<<
            vXvv>
            ^X<v>
            >X<>^
            >Xvv^
            '''
        )
        self.assertEqual(self.match.score, 58)

    def test_clearing_horizontal_lines(self):
        set_fields_directions(
            self.match.board,
            '''
            <^^<<
            v^vv>
            ><<<>
            >v<>^
            >^vv^
            '''
        )

        self.match.board.get_field(0, 2).points = 7
        self.match.start_move(3, 2)

        assert_fields_directions(
            self.match.board,
            '''
            XXXXX
            <^^<<
            v^vv>
            >v<>^
            >^vv^
            '''
        )
        self.assertEqual(self.match.score, 61)
