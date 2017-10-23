from unittest import TestCase

from ..match import Match
from ..board import Board
from .utils import assert_fields_directions, set_fields_directions


class MatchTestCase(TestCase):

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
            ''',
            '''
            11111
            11111
            11111
            11111
            11111
            '''
        )

        moves = self.match.moves
        self.match.start_move(0, 4)

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
            ''',
            '''
            11111
            11111
            12212
            12222
            11111
            '''
        )
        moves = self.match.moves
        self.match.start_move(3, 2)

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
        self.assertEqual(self.match.moves, moves + 2)
        self.assertEqual(self.match.score, 14)
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
            ''',
            '''
            11111
            11111
            11111
            11111
            11111
            '''
        )
        self.match.start_move(2, 2)
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
        self.assertEqual(self.match.score, 8)

    def test_clearing_vertical_lines(self):
        set_fields_directions(
            self.match.board,
            '''
            <^^<<
            v^vv>
            ^v<v>
            >v<>^
            >^vv^
            ''',
            '''
            12111
            13111
            14111
            13111
            12111
            '''
        )
        self.assertEqual(self.match.score, 0)
        self.assertEqual(self.match.moves, 5)
        self.match.start_move(2, 1)
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
        self.assertEqual(self.match.score, 64)
        self.assertEqual(self.match.moves, 6)

    def test_clearing_horizontal_lines(self):
        set_fields_directions(
            self.match.board,
            '''
            <^^<<
            v^vv>
            ><<<>
            >v<>^
            >^vv^
            ''',
            '''
            11111
            11111
            23432
            11111
            11111
            '''
        )
        self.assertEqual(self.match.score, 0)
        self.assertEqual(self.match.moves, 5)
        self.match.start_move(2, 3)
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
        self.assertEqual(self.match.score, 64)
        self.assertEqual(self.match.moves, 6)

    def test_get_state(self):
        state = self.match.get_state()
        self.assertEqual(
            state['preview']['points'],
            '1222121111111143113243112',
        )
        self.assertEqual(
            state['preview']['directions'],
            '<v^^^v>vvvv^v^vv<^>>v>^<^',
        )
        self.assertEqual(state['score'], 0)
        self.assertEqual(state['moves'], 5)
        self.assertEqual(state['bonus-multiplier'], 0.5)