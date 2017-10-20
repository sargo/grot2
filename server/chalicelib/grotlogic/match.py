import math


class Match:

    def __init__(self, player, board, score=0, moves=5):
        self.player = player
        self.board = board
        self.old_score = self.score = score
        self.moves = moves

    def start_move(self, x, y):
        """
        Set initial values and start chain reaction.
        """
        field = self.board.get_field(x, y)
        self.moves -= 1

        self.move_score = 0
        self.move_length = 0

        self.move_next_field(field)

    def skip_move(self):
        """
        Skip the move
        """
        self.moves -= 1

    def move_next_field(self, start_field):
        """
        One step in chain reaction.
        """
        next_field = self.board.get_next_field(start_field)
        start_field.direction = None
        self.move_score += start_field.points
        self.move_length += 1

        if next_field is None:
            self.finish_move()
        else:
            self.move_next_field(next_field)

    def get_bonus_multiplier(self):
        return 100 / (self.score + 200)

    def update_score(self):
        """
        Update game score.
        """
        self.moves += math.floor(self.move_length * self.get_bonus_multiplier())
        self.score += self.move_score

    def finish_move(self):
        """
        Finish the move.
        """
        self.move_score += self.board.get_extra_points()

        self.board.lower_fields()
        self.board.fill_empty_fields()

        self.update_score()

    def get_state(self, board=True):
        """
        Get the status of the game.
        """
        return {
            'score': self.score,
            'moves': self.moves,
            'board': self.board.get_state() if board else None,
            'preview': self.board.get_preview() if board else None,
            'bonus-multiplier': self.get_bonus_multiplier(),
        }

    def is_active(self):
        """
        Return whether the game is still active or not.
        """
        return self.moves > 0
